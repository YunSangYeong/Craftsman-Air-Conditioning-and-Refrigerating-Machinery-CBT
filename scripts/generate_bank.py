"""Deterministic original HVAC calculation exercises. No external exam text.
40 authored templates x 25 parameter sets; Decimal half-up at 2 places.
This script is NOT its own independent verifier: tests/bank.test.ts uses inverse balances.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json, math, csv
ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ['에너지관리', '공조냉동설계', '시운전 및 안전관리', '유지보수 공조냉동']
# kind, topic, unit, parameters(i), result(parameters), stem, equation
F = [
('sensible','현열량','kJ',lambda i:[10+i,4.2,5+i],lambda m,c,t:m*c*t,'물 {0} kg을 비열 {1} kJ/(kg·K), 온도차 {2} K만큼 가열한다. 손실이 없을 때 필요한 열량은?','Q=m·c·ΔT'),
('conduction','평판 열전도','W',lambda i:[0.04,10+i,20,0.1],lambda k,a,t,l:k*a*t/l,'열전도율 {0} W/(m·K), 면적 {1} m², 온도차 {2} K, 두께 {3} m인 평판의 정상 열전도량은? 접촉·표면 저항은 무시한다.','Q̇=k·A·ΔT/L'),
('idealGas','이상기체 질량','kg',lambda i:[100,1+i*.1,.287,300],lambda p,v,r,t:p*v/(r*t),'이상기체 공기의 절대압력 {0} kPa, 체적 {1} m³, 기체상수 {2} kJ/(kg·K), 절대온도 {3} K일 때 질량은?','m=p·V/(R·T), 1 kPa·m³=1 kJ'),
('boilerEfficiency','열원 효율','%',lambda i:[60+i,100],lambda useful,supply:100*useful/supply,'열원 장치에 {1} kW의 에너지를 공급하여 유효 열출력 {0} kW를 얻는다. 열효율은?','η=유효 출력/입력×100'),
('coolingCOP','냉동 성능계수','',lambda i:[30+i,10],lambda q,w:q/w,'냉동기의 증발기 냉동능력이 {0} kW, 압축기 입력이 {1} kW이다. 냉동 성능계수(COP)는? 보조동력은 제외한다.','COP_R=Q̇_L/Ẇ'),
('carnot','카르노 냉동기','',lambda i:[250+i,320],lambda l,h:l/(h-l),'저온 열원 {0} K, 고온 열원 {1} K 사이에서 작동하는 카르노 냉동기의 COP는? 절대온도를 사용한다.','COP_Carnot=T_L/(T_H−T_L)'),
('airSensible','공기 현열부하','kW',lambda i:[1.2,1.0,1+i*.1,10],lambda rho,c,v,t:rho*c*v*t,'밀도 {0} kg/m³, 비열 {1} kJ/(kg·K)인 공기가 {2} m³/s로 흐른다. 건구온도를 {3} K 낮출 때 현열 냉각부하는? 응축은 없다.','Q̇=ρ·c_p·V̇·ΔT'),
('mixing','물 혼합온도','°C',lambda i:[10+i,40,10,20],lambda m1,t1,m2,t2:(m1*t1+m2*t2)/(m1+m2),'비열이 같은 물 {0} kg({1} °C)과 {2} kg({3} °C)을 단열 혼합한다. 상변화가 없을 때 최종온도는?','T=(m₁T₁+m₂T₂)/(m₁+m₂)'),
('latent','잠열량','kJ',lambda i:[1+i*.1,2257],lambda m,h:m*h,'포화수 {0} kg이 같은 압력에서 완전히 증발한다. 증발잠열이 {1} kJ/kg일 때 필요한 잠열량은?','Q=m·h_fg'),
('heatingCOP','히트펌프 난방','',lambda i:[40+i,10],lambda q,w:q/w,'히트펌프 응축기 난방출력이 {0} kW, 압축기 입력이 {1} kW이다. 보조동력을 제외한 난방 COP는?','COP_H=Q̇_H/Ẇ'),
('refrigerantFlow','냉매 질량유량','kg/s',lambda i:[20+i,150],lambda q,dh:q/dh,'증발기 냉동능력 {0} kW, 냉매의 증발기 입출구 엔탈피 차 {1} kJ/kg이다. 정상상태에서 필요한 냉매 질량유량은?','ṁ=Q̇_L/(h_out−h_in)'),
('condenser','응축기 방열','kW',lambda i:[30+i,10],lambda q,w:q+w,'정상 냉동사이클의 증발기 흡열량이 {0} kW, 압축기 입력이 {1} kW이다. 다른 열손실이 없을 때 응축기 방열량은?','Q̇_H=Q̇_L+Ẇ'),
('ductVelocity','덕트 평균풍속','m/s',lambda i:[1+i*.1,.5],lambda v,a:v/a,'덕트 체적유량이 {0} m³/s, 단면적이 {1} m²이다. 균일한 유동을 가정할 때 평균풍속은?','u=V̇/A'),
('pumpPower','펌프 축동력','kW',lambda i:[.01+i*.001,200,.8],lambda v,p,e:v*p/e,'펌프 물 유량 {0} m³/s, 펌프 전후 압력 상승 {1} kPa, 효율 {2}일 때 필요한 축동력은? 위치·속도차는 무시한다.','Ẇ=V̇·Δp/η, 1 kPa·m³/s=1 kW'),
('waterFlow','냉수 유량','kg/s',lambda i:[20+i,4.2,5],lambda q,c,t:q/(c*t),'냉각코일 부하 {0} kW, 냉수 비열 {1} kJ/(kg·K), 입출구 온도차 {2} K이다. 필요한 물 질량유량은?','ṁ=Q̇/(c_p·ΔT)'),
('airChanges','환기횟수','회/h',lambda i:[.5+i*.05,300],lambda v,vol:3600*v/vol,'실내 체적 {1} m³, 외기 공급량 {0} m³/s이다. 완전 혼합을 가정한 시간당 환기횟수는?','N=3600·V̇/V_room'),
('wallU','종합 열관류율','W/(m²·K)',lambda i:[10,.05+i*.002,.04,20],lambda hi,l,k,ho:1/(1/hi+l/k+1/ho),'단층 벽의 실내 표면 열전달률 {0} W/(m²·K), 두께 {1} m, 열전도율 {2} W/(m·K), 실외 표면 열전달률 {3} W/(m²·K)이다. 열교 없이 면적 기준 열관류율은?','U=1/(1/h_i+L/k+1/h_o)'),
('lmtd','대수평균 온도차','K',lambda i:[20+i,10+i*.5],lambda a,b:(a-b)/math.log(a/b),'열교환기의 두 끝단 온도차가 각각 {0} K와 {1} K이다. 대수평균 온도차(LMTD)는? 온도차는 모두 양수이다.','ΔT_lm=(ΔT₁−ΔT₂)/ln(ΔT₁/ΔT₂)'),
('condensate','제습 응축수','kg/s',lambda i:[1+i*.1,.016,.009],lambda m,wi,wo:m*(wi-wo),'건공기 질량유량 {0} kg(DA)/s, 입구 절대습도 {1} kg/kg(DA), 출구 {2} kg/kg(DA)이다. 수분 누출이 없을 때 응축수량은?','ṁ_water=ṁ_DA·(w_in−w_out)'),
('pipeResistance','원통 단열 열저항','K/W',lambda i:[.02,.04+i*.001,.04,1],lambda r1,r2,k,l:math.log(r2/r1)/(2*math.pi*k*l),'배관 단열층 내반경 {0} m, 외반경 {1} m, 열전도율 {2} W/(m·K), 길이 {3} m이다. 표면저항을 제외한 원통 전도 열저항은? π=3.141592653589793을 사용한다.','R=ln(r₂/r₁)/(2πkL)'),
('threePhase','3상 유효전력','kW',lambda i:[380,10+i,.8],lambda u,a,p:math.sqrt(3)*u*a*p/1000,'평형 3상 전동기의 선간전압 {0} V, 선전류 {1} A, 역률 {2}이다. 입력 유효전력은? √3=1.7320508075688772를 사용한다.','P=√3·U_L·I_L·cosφ/1000'),
('insulation','절연저항 측정 계산','MΩ',lambda i:[500,.1+i*.01],lambda v,ma:v/ma/1000,'가상 절연저항 계산에서 시험전압 {0} V, 누설전류 {1} mA가 일정하다. 옴의 법칙으로 구한 저항은? 실제 시험 절차·허용기준을 묻는 문제가 아니다.','R=V/I, I[A]=I[mA]/1000; R[MΩ]=R[Ω]/10⁶'),
('fanFlow','송풍기 유량 상사','m³/s',lambda i:[2,1000,1050+i*10],lambda q,n1,n2:q*n2/n1,'같은 송풍기에서 회전수 {1} rpm일 때 유량 {0} m³/s이다. 밀도 일정, 상사법칙 적용 시 {2} rpm에서 유량은?','V̇₂=V̇₁·n₂/n₁'),
('fanPressure','송풍기 압력 상사','Pa',lambda i:[500,1000,1050+i*10],lambda p,n1,n2:p*(n2/n1)**2,'같은 송풍기가 {1} rpm에서 압력 {0} Pa를 낸다. 밀도 일정, 상사법칙 적용 시 {2} rpm의 압력은?','Δp₂=Δp₁·(n₂/n₁)²'),
('rotationFrequency','회전 주파수','Hz',lambda i:[900+i*30],lambda n:n/60,'회전체가 {0} rpm으로 일정하게 돈다. 1회전당 1주기인 회전 주파수는?','f=n/60'),
('absolutePressure','절대압력 환산','kPa',lambda i:[200+i*10,101.3],lambda pg,pa:pg+pa,'장치의 게이지압력이 {0} kPa, 현장 대기압력이 {1} kPa이다. 절대압력은?','p_abs=p_gauge+p_atm'),
('manometer','액주 압력차','kPa',lambda i:[1000,9.81,.1+i*.01],lambda rho,g,h:rho*g*h/1000,'밀도 {0} kg/m³인 액주의 높이차가 {2} m이다. 중력가속도 {1} m/s², 기체 밀도 무시 시 액주 압력차는?','Δp=ρgh, kPa=Pa/1000'),
('balanceRatio','풍량 밸런싱','%',lambda i:[800+i*10,1200],lambda actual,design:100*actual/design,'단말 설계풍량이 {1} m³/h, 측정풍량이 {0} m³/h이다. 설계값 대비 측정 비율은? 합격허용범위를 판정하지 않는다.','측정 비율=실측/설계×100'),
('testDuration','시운전 계측시간','min',lambda i:[120+i*10,60,180],lambda a,b,c:(a+b+c)/60,'시운전 기록에서 서로 겹치지 않는 세 계측 구간이 {0} s, {1} s, {2} s이다. 총 소요시간은 몇 분인가?','t_total=(t₁+t₂+t₃)/60'),
('shaftTorque','전동기 축토크','N·m',lambda i:[5+i*.2,1500],lambda p,n:9550*p/n,'전동기 축출력 {0} kW, 회전수 {1} rpm이다. T=9550P/n의 근사식을 사용할 때 축토크는?','T[N·m]=9550·P[kW]/n[rpm]'),
('fouling','오염 추가 열저항','m²·K/W',lambda i:[500+i*10,1000],lambda dirty,clean:1/dirty-1/clean,'동일 면적 기준 청정 열관류율 {1} W/(m²·K), 오염 후 {0} W/(m²·K)이다. 추가된 오염 열저항은? 이 문항만 소수점 여섯째 자리까지 반올림한다.','R_f=1/U_dirty−1/U_clean'),
('lossFraction','냉매 질량 감소율','%',lambda i:[100,70+i],lambda initial,current:100*(initial-current)/initial,'회수 전후 장부상 초기 냉매 질량 {0} kg, 현재 확인 질량 {1} kg이다. 초기 대비 감소율은? 실제 누설 진단을 대체하지 않는다.','감소율=(초기−현재)/초기×100'),
('superheat','과열도','K',lambda i:[10+i,0],lambda actual,sat:actual-sat,'증발기 출구에서 같은 압력의 포화온도 {1} °C, 측정 냉매온도 {0} °C이다. 과열도는?','과열도=T_actual−T_sat'),
('subcool','과냉각도','K',lambda i:[45,10+i],lambda sat,actual:sat-actual,'응축기 출구에서 같은 압력의 포화온도 {0} °C, 측정 액온 {1} °C이다. 과냉각도는?','과냉각도=T_sat−T_liquid'),
('savedEnergy','소비전력 절감량','kWh',lambda i:[20,10+i*.2,8],lambda old,new,t:(old-new)*t,'같은 운전 조건에서 개선 전 소비전력 {0} kW, 개선 후 {1} kW이다. 하루 {2} h 운전할 때 절감 전력량은?','E_saved=(P_old−P_new)·t'),
('filterDrop','필터 차압 증가','Pa',lambda i:[80,100+i*5],lambda clean,current:current-clean,'같은 풍량에서 청정 필터 차압 {0} Pa, 현재 필터 차압 {1} Pa이다. 차압 증가량은? 교체 기준 판정은 포함하지 않는다.','Δp_increase=Δp_current−Δp_clean'),
('effectiveness','현열교환 온도효율','%',lambda i:[40,25+i*.2,20],lambda hot,out,cold:100*(hot-out)/(hot-cold),'고온측 입구 {0} °C, 출구 {1} °C, 저온측 입구 {2} °C이다. 고온측 열용량률이 최소인 현열교환기의 유용도는?','ε=(T_h,in−T_h,out)/(T_h,in−T_c,in)×100'),
('oilFraction','혼합액 체적비','%',lambda i:[1+i*.1,10],lambda oil,total:100*oil/total,'체적 가산성이 성립하는 가상 혼합액 {1} L 중 오일이 {0} L이다. 오일 체적백분율은? 실제 냉매·오일 혼합 특성은 적용하지 않는다.','체적분율=V_oil/V_total×100'),
('runDays','운전일수 환산','일',lambda i:[800+i*8,8],lambda total,daily:total/daily,'누적 운전시간 {0} h, 운전일마다 일정하게 {1} h 가동한다. 누적시간에 해당하는 운전일수는?','D=총 운전시간/일 운전시간'),
('beltSpeed','벨트 선속도','m/s',lambda i:[.2+i*.01,1200],lambda d,n:math.pi*d*n/60,'풀리 지름 {0} m, 회전수 {1} rpm이다. 미끄럼 없는 벨트의 선속도는? π=3.141592653589793을 사용한다.','v=πDn/60'),
]
# Worked numeric substitution for each reviewed template, in stem parameter order.
SUBSTITUTIONS = [
 '{0}×{1}×{2}', '{0}×{1}×{2}/{3}', '{0}×{1}/({2}×{3})', '{0}/{1}×100', '{0}/{1}', '{0}/({1}−{0})',
 '{0}×{1}×{2}×{3}', '({0}×{1}+{2}×{3})/({0}+{2})', '{0}×{1}', '{0}/{1}',
 '{0}/{1}', '{0}+{1}', '{0}/{1}', '{0}×{1}/{2}', '{0}/({1}×{2})', '3600×{0}/{1}',
 '1/(1/{0}+{1}/{2}+1/{3})', '({0}−{1})/ln({0}/{1})', '{0}×({1}−{2})', 'ln({1}/{0})/(2×π×{2}×{3})',
 '√3×{0}×{1}×{2}/1000', '{0}/({1}/1000)/1000000', '{0}×{2}/{1}', '{0}×({2}/{1})²', '{0}/60', '{0}+{1}',
 '{0}×{1}×{2}/1000', '{0}/{1}×100', '({0}+{1}+{2})/60', '9550×{0}/{1}',
 '1/{0}−1/{1}', '({0}−{1})/{0}×100', '{0}−{1}', '{0}−{1}', '({0}−{1})×{2}', '{1}−{0}',
 '({0}−{1})/({0}−{2})×100', '{0}/{1}×100', '{0}/{1}', 'π×{0}×{1}/60',
]
def rnd(x,places): return Decimal(str(x)).quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP)
def text(x): return format(x,'f').rstrip('0').rstrip('.') if '.' in format(x,'f') else str(x)
def fmt(x): return format(x,'.12g')
bank=[]
for f,(kind,topic,unit,params,calc,stem,eq) in enumerate(F):
 for i in range(25):
  vals=params(i); precision=6 if kind=='fouling' else 4 if kind in ['condensate','refrigerantFlow','waterFlow'] else 2
  result=rnd(calc(*vals),precision)
  # Separated distractors on the same scale, all distinct even after rounding.
  options=[result,rnd(result*Decimal('1.25')+Decimal(1).scaleb(-precision),precision),rnd(result*Decimal('1.5')+Decimal(2).scaleb(-precision),precision),rnd(result*Decimal('2')+Decimal(3).scaleb(-precision),precision)]
  shift=(f+i)%4; options=options[shift:]+options[:shift]
  answer=options.index(result)+1
  question=stem.format(*map(fmt,vals))
  if precision==4: question+=' 최종값은 소수점 다섯째 자리에서 반올림하여 넷째 자리까지 구한다.'
  if precision==2: question+=' 최종값은 소수점 셋째 자리에서 반올림하여 둘째 자리까지 구한다.'
  bank.append(dict(id=f'HVAC-{f+1:02}-{i+1:03}',subject=SUBJECTS[f//10],topic=topic,question=question,choices=[f'{text(x)} {unit}'.strip() for x in options],answer=answer,explanation=f'적용식: {eq}. 단위는 문제에 제시된 SI 단위에 맞춘다. 수치 대입: '+SUBSTITUTIONS[f].format(*map(fmt,vals))+f' = 반올림 전 {calc(*vals):.12g} {unit}이며, 최종 {text(result)} {unit}이다. 온도차 K와 °C의 수치 차이는 같고, 명시한 이상화 조건 안에서 계산한다.',difficulty='중',year=None,session=None,type='original',sourceUrl='https://github.com/YunSangYeong/Craftsman-Air-Conditioning-and-Refrigerating-Machinery-CBT/blob/cbt/hvac-engineer-standard-20261102/docs/question-review.md',verificationStatus='reviewed',reviewNote='AI 일반 공학 지식에 기초한 자체 제작 수치 변형. 템플릿 내부 검토·역산/보존식 자동 검증. 외부 문헌·공식 출제기준 대조 및 전문가 검수 미완료. 작성 위치 URL은 외부 정답 증빙이 아닙니다.',version='main',rights='자체 제작 학습 자료 · CC BY 4.0. 원문 기출·복원 아님.',family='HVAC-'+kind,calculation=dict(kind=kind,values=vals,result=float(result),unit=unit,precision=precision)))
assert len(bank)==1000
path=ROOT/'src/data/questions.json'; path.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'public/templates';p.mkdir(parents=True,exist_ok=True)
sample={**bank[0],'id':'LOCAL-SAMPLE-001','question':'등록 예제: 물 2 kg, 비열 4.2 kJ/(kg·K), 온도차 10 K일 때 현열량은?','choices':['84 kJ','42 kJ','8.4 kJ','420 kJ'],'answer':1,'explanation':'Q=m·c·ΔT=2×4.2×10=84 kJ. 자체 제작 등록 양식 예제.','verificationStatus':'pending','reviewNote':'양식 예제. 승인 전 출처·권한·정답을 확인하세요.'}
sample.pop('calculation');sample.pop('family')
(p/'questions.json').write_text(json.dumps([sample],ensure_ascii=False,indent=2)+'\n')
row={**sample};row.pop('choices');row.update({f'choice{i+1}':c for i,c in enumerate(sample['choices'])})
with (p/'questions.csv').open('w',newline='') as file:
 w=csv.DictWriter(file,fieldnames=list(row),lineterminator='\n');w.writeheader();w.writerow(row)
print('Generated',len(bank),'questions /',len(F),'formula families / 25 variants each')
