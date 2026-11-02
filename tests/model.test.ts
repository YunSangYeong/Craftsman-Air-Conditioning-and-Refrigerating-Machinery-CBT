import { describe, it, expect } from 'vitest';
import { PROFILE } from "../src/profile";
import type { Store } from "../src/model";
import { answerExam, BASE_BANK as bank, checkPractice, createExam, emptyStore, grade, importQuestions, nextPractice, parseCsv, remainingSeconds, restoreStore, startPractice, SUBJECTS, submitExam } from '../src/model';
const exam=()=>createExam(bank,'main',1000);
function answered(counts:number[]) {
 const e=exam();
 SUBJECTS.forEach((subject,i)=>e.questions.filter(q=>q.subject===subject).slice(0,counts[i]).forEach(q=>e.answers[q.id]=q.answer));
 return e;
}
describe('기사 시험·시간·과락',()=>{
 it('과목 목록은 자격증 설정과 일치한다',()=>expect([...SUBJECTS]).toEqual(PROFILE.subjects));
 it('80문항, 과목별20, 120분, 고유ID·pending 제외·family 최대2',()=>{
  for(let i=0;i<10;i++) {
   const e=createExam([...bank,{...bank[0],id:'PENDING',verificationStatus:'pending'}],'main',1000);
   expect(e.questions).toHaveLength(80); expect(new Set(e.questions.map(q=>q.id)).size).toBe(80);
   expect(e.deadline).toBe(7201000); expect(e.questions.some(q=>q.id==='PENDING')).toBe(false);
   for(const s of SUBJECTS) expect(e.questions.filter(q=>q.subject===s)).toHaveLength(20);
   for(const f of new Set(e.questions.map(q=>q.family))) expect(e.questions.filter(q=>q.family===f).length).toBeLessThanOrEqual(2);
  }
 });
 it('최소 과목 문항 미달은 시작 거부',()=>expect(()=>createExam(bank.filter(q=>q.subject!==SUBJECTS[0]),'main')).toThrow());
 it.each([[12,12,12,12,true,60],[12,12,12,11,false,58.8],[20,20,20,7,false,83.8],[20,20,20,8,true,85],[0,0,0,0,false,0]])('정답수 %i/%i/%i/%i', (a,b,c,d,passed,score)=>{
  const g=grade(answered([a as number,b as number,c as number,d as number]));expect(g.passed).toBe(passed);expect(g.score).toBe(score);
 });
 it('답안 변경·만료 경계·중복 제출',()=>{
  const e=exam();let s:Store={...emptyStore(),exam:e}; const q=e.questions[0];
  s=answerExam(s,q.id,1,1001); s=answerExam(s,q.id,2,1002);expect(s.exam!.answers[q.id]).toBe(2);
  expect(answerExam(s,q.id,5,1002)).toBe(s);
  const finished=answerExam(s,q.id,3,e.deadline);expect(finished.exam).toBeNull();expect(finished.results[0].answers[q.id]).toBe(2);
  expect(finished.results[0].reason).toBe('timeout');expect(submitExam(finished)).toBe(finished);
 });
 it('절대 종료시각 보존과 잔여초 올림·하한0',()=>{
  const s={...emptyStore(),exam:exam()};const restored=restoreStore(JSON.stringify(s));expect(restored.exam!.deadline).toBe(s.exam!.deadline);
  expect(remainingSeconds(1001,1000)).toBe(1);expect(remainingSeconds(1000,1001)).toBe(0);
 });
 it('잘못된 시험 시간과 과목 분포 거부',()=>{
  const s={...emptyStore(),exam:exam()};s.exam.deadline++;expect(()=>restoreStore(JSON.stringify(s))).toThrow();
  s.exam=exam();s.exam.questions[0]={...s.exam.questions[0],subject:SUBJECTS[0]};
  s.exam.questions.forEach(q=>q.subject=SUBJECTS[0]);expect(()=>restoreStore(JSON.stringify(s))).toThrow();
 });
});
describe('학습·등록·저장',()=>{
 it('순회 ID 중복 방지·채점 한 번·정답 복습 시 오답 해제',()=>{
  let s=emptyStore(); s.practice=startPractice(bank,'main',SUBJECTS[0]);const ids=new Set();
  for(let i=0;i<250;i++) {
   const id=s.practice!.currentId;expect(ids.has(id)).toBe(false);ids.add(id);
   const q=bank.find(q=>q.id===id)!;s.practice!.selected=q.answer;
   s.wrongIds=[id];s=checkPractice(s,bank,10+i);expect(s.wrongIds).not.toContain(id);
   expect(checkPractice(s,bank)).toBe(s);s.practice=nextPractice(s.practice!,bank);
  }
  expect(s.attempts).toHaveLength(250);expect(s.practice!.streak).toBe(250);
 });
 it('가져오기 pending·ID/본문/보기재배치 중복 제거·원자성',()=>{
  const q={...bank[0],id:'LOCAL',question:'독립 등록 문제'};
  const result=importQuestions([q,bank[0],{...bank[0],id:'OTHER',choices:[...bank[0].choices].reverse()}],bank);
  expect(result.added).toHaveLength(1);expect(result.duplicates).toBe(2);expect(result.added[0].verificationStatus).toBe('pending');
  expect(()=>importQuestions([q,{}],bank)).toThrow('2번');
 });
 it('CSV 따옴표·빈 연도회차·잘못된 인용 처리',()=>{
  expect(parseCsv('id,question,year,session,answer,choice1,choice2,choice3,choice4\nLOCAL,"A,B",,,1,a,b,c,d')[0]).toMatchObject({year:null,session:null,question:'A,B'});
  expect(()=>parseCsv('id\n"broken')).toThrow();
 });
 it('손상 저장 거부와 원문 유지',()=>{const raw='{broken';expect(()=>restoreStore(raw)).toThrow();expect(raw).toBe('{broken');});
 it('응답5000·시험30회 보관',()=>{
  const s=emptyStore();s.exam=exam();s.results=Array(30).fill({...exam(),submittedAt:1,reason:'manual'});s.attempts=Array(5000).fill({questionId:bank[0].id,subject:bank[0].subject,correct:true,at:1,mode:'exam'});
  const done=submitExam(s,2000);expect(done.results).toHaveLength(30);expect(done.attempts).toHaveLength(5000);
 });
});
