import { expect, it } from 'vitest';
import { BASE_BANK, fingerprint, validateQuestion, SUBJECTS } from '../src/model';
// Independent verification by inverse equations / energy and mass balances.
// The Python generator evaluates the forward formulas; this file never imports it.
const balances: Record<string, (r:number,v:number[])=>number> = {
 sensible:(r,[m,c,t])=>r/(m*c)-t,
 conduction:(r,[k,a,t,l])=>r*l/(a*t)-k,
 idealGas:(r,[p,v,R,t])=>r*R*t-p*v,
 boilerEfficiency:(r,[out,input])=>input*r/100-out,
 coolingCOP:(r,[q,w])=>r*w-q,
 carnot:(r,[l,h])=>h*r-l*(r+1),
 airSensible:(r,[rho,c,v,t])=>r/(rho*c*v)-t,
 mixing:(r,[m,t,n,u])=>m*(t-r)-n*(r-u),
 latent:(r,[m,h])=>r/h-m,
 heatingCOP:(r,[q,w])=>q/r-w,
 refrigerantFlow:(r,[q,h])=>r*h-q,
 condenser:(r,[q,w])=>r-q-w,
 ductVelocity:(r,[q,a])=>r*a-q,
 pumpPower:(r,[v,p,e])=>r*e-v*p,
 waterFlow:(r,[q,c,t])=>r*c*t-q,
 airChanges:(r,[q,v])=>r*v/3600-q,
 wallU:(r,[hi,l,k,ho])=>1/r-1/hi-1/ho-l/k,
 lmtd:(r,[a,b])=>Math.exp((a-b)/r)-a/b,
 condensate:(r,[m,wi,wo])=>m*wi-r-m*wo,
 pipeResistance:(r,[a,b,k,l])=>Math.exp(r*2*Math.PI*k*l)*a-b,
 threePhase:(r,[u,a,p])=>r*1000/(u*a*p)-Math.sqrt(3),
 insulation:(r,[v,ma])=>r*1e6*(ma/1000)-v,
 fanFlow:(r,[q,n,m])=>r/m-q/n,
 fanPressure:(r,[p,n,m])=>Math.sqrt(r/p)*n-m,
 rotationFrequency:(r,[n])=>60*r-n,
 absolutePressure:(r,[g,a])=>r-a-g,
 manometer:(r,[rho,g,h])=>r*1000/(rho*g)-h,
 balanceRatio:(r,[a,d])=>r*d/100-a,
 testDuration:(r,v)=>r*60-v.reduce((a,b)=>a+b,0),
 shaftTorque:(r,[p,n])=>r*n/9550-p,
 fouling:(r,[d,c])=>1/(r+1/c)-d,
 lossFraction:(r,[a,b])=>a*(1-r/100)-b,
 superheat:(r,[a,s])=>r+s-a,
 subcool:(r,[s,a])=>r+a-s,
 savedEnergy:(r,[o,n,t])=>r/t+n-o,
 filterDrop:(r,[c,n])=>r+c-n,
 effectiveness:(r,[h,o,c])=>(h-c)*r/100+o-h,
 oilFraction:(r,[o,t])=>r*t/100-o,
 runDays:(r,[t,d])=>r*d-t,
 beltSpeed:(r,[d,n])=>r*60/n/Math.PI-d,
};
it('중복 제거 후 내부 검수 1000문항, 과목별250, 자체제작·연도 없음·40유형×25',()=>{
 expect(BASE_BANK).toHaveLength(1000);
 expect(new Set(BASE_BANK.map(q=>q.id)).size).toBe(1000);
 expect(new Set(BASE_BANK.map(fingerprint)).size).toBe(1000);
 for(const subject of SUBJECTS) expect(BASE_BANK.filter(q=>q.subject===subject)).toHaveLength(250);
 expect(new Set(BASE_BANK.map(q=>q.family)).size).toBe(40);
 for(const family of new Set(BASE_BANK.map(q=>q.family))) {
  const qs=BASE_BANK.filter(q=>q.family===family);
  expect(qs).toHaveLength(25);
  expect(new Set(qs.map(q=>JSON.stringify(q.calculation!.values))).size).toBe(25);
 }
});
for(const q of BASE_BANK) it(`독립 역산·반올림·보기·메타데이터 ${q.id}`,()=>{
 expect(()=>validateQuestion(q)).not.toThrow();
 expect(q.type).toBe('original'); expect(q.year).toBeNull(); expect(q.session).toBeNull();
 expect(q.verificationStatus).toBe('reviewed'); expect(q.rights).toContain('CC BY 4.0');
 const {kind,values,result,unit,precision}=q.calculation!;
 expect(balances[kind]).toBeDefined();
 const half=.5*10**-precision! + 1e-10;
 const a=balances[kind](result-half,values), b=balances[kind](result+half,values);
 expect(Math.min(a,b)).toBeLessThanOrEqual(1e-7);
 expect(Math.max(a,b)).toBeGreaterThanOrEqual(-1e-7);
 const numbers=q.choices.map(c=>Number.parseFloat(c));
 expect(new Set(numbers).size).toBe(4);
 expect(numbers[q.answer-1]).toBe(result);
 expect(q.choices.every(c=>c.endsWith(unit))).toBe(true);
 expect(q.explanation).toContain(String(result));
 expect(q.reviewNote).toContain('전문가 검수 미완료');
});
