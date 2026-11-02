# 자체 제작 문항 내부 검토 기록

작성일: 2026-11-02. 작성·내부 검토: AI 코딩 에이전트. 사람/외부 전문가 검수 아님.

## 실제 근거와 이용 조건

AI 일반 공학 지식에서 작성한 이상화 계산 연습이다. 외부 교재·Q-Net 본문·기출 원문은 읽지 못했으며 그 자료를 근거로 인용하지 않는다. 작성 위치 URL은 외부 정답 증빙이 아니다. 모든 문항은 자체 제작/CC BY 4.0, 연도·회차 null이다. 공식 문제의 권리 상태를 추정하지 않는다.

## 내부 검토 범위

40개 템플릿에 대해 열·일 에너지수지, 질량수지, 이상기체 가정, 액주·유동·전기 SI 단위와 양의 입력/유효 온도차/효율 조건을 검토했다. 각 템플릿의 질문은 가정과 필요한 상수를 제공하며 숫자 대입식을 해설에 기록한다. 과열/과냉각은 같은 압력의 포화온도를 명시하고, 유용도는 고온측 최소 열용량률을 가정한다. 물 혼합은 비열 동일·단열·상변화 없음을, 원통 열저항은 면적당 저항과 다른 K/W 단위를 명시했다. 단순 시운전 시간·체적비 연습은 법정 안전기준을 뜻하지 않는다.

내부 의미 검토 단위는 40개 템플릿이다. 매개변수 25조건은 모두 양수이며 물리식의 정의역을 유지한다. 각 인스턴스의 계산 결과는 Python forward 생성과 분리된 TypeScript 역산/보존식으로 검증한다. 정답 반올림 구간이 역산 근을 포함하는지 확인하므로 생성 결과를 그대로 기대값으로 복사하지 않는다. 보기는 같은 단위의 서로 다른 수치 4개이며 정답은 하나다. 실제 기사 시험의 문제 분포·난이도·안전 규정 전체를 검토하지 않았다.

## 수량과 중복

기본 JSON 1,000 / 내부 reviewed 1,000 / pending 0 / 제외 0 / 개인 로컬 등록 0 / 목표 부족 0. 원문 기출 0, 복원 0, 자체 제작 계산 1,000, 비계산 개념 0. ID 및 NFKC·공백 제거·보기 순서 정렬 fingerprint 중복 0. 의미상 동형인 family 내부 문항은 의도한 숫자 조건 변형으로 분리 공개한다. family 간 관련 공학 개념이 있어 40 family는 독립 개념 수가 아니다. 각 family당 기본 조건 1+추가변형24=25, 전체 추가변형960.

| 과목 | family | 주제 | 적용식 | 조건 수 |
| --- | --- | --- | --- | ---: |
| 에너지관리 | HVAC-sensible | 현열량 | Q=m·c·ΔT | 25 |
| 에너지관리 | HVAC-conduction | 평판 열전도 | Q̇=k·A·ΔT/L | 25 |
| 에너지관리 | HVAC-idealGas | 이상기체 질량 | m=p·V/(R·T), 1 kPa·m³=1 kJ | 25 |
| 에너지관리 | HVAC-boilerEfficiency | 열원 효율 | η=유효 출력/입력×100 | 25 |
| 에너지관리 | HVAC-coolingCOP | 냉동 성능계수 | COP_R=Q̇_L/Ẇ | 25 |
| 에너지관리 | HVAC-carnot | 카르노 냉동기 | COP_Carnot=T_L/(T_H−T_L) | 25 |
| 에너지관리 | HVAC-airSensible | 공기 현열부하 | Q̇=ρ·c_p·V̇·ΔT | 25 |
| 에너지관리 | HVAC-mixing | 물 혼합온도 | T=(m₁T₁+m₂T₂)/(m₁+m₂) | 25 |
| 에너지관리 | HVAC-latent | 잠열량 | Q=m·h_fg | 25 |
| 에너지관리 | HVAC-heatingCOP | 히트펌프 난방 | COP_H=Q̇_H/Ẇ | 25 |
| 공조냉동설계 | HVAC-refrigerantFlow | 냉매 질량유량 | ṁ=Q̇_L/(h_out−h_in) | 25 |
| 공조냉동설계 | HVAC-condenser | 응축기 방열 | Q̇_H=Q̇_L+Ẇ | 25 |
| 공조냉동설계 | HVAC-ductVelocity | 덕트 평균풍속 | u=V̇/A | 25 |
| 공조냉동설계 | HVAC-pumpPower | 펌프 축동력 | Ẇ=V̇·Δp/η, 1 kPa·m³/s=1 kW | 25 |
| 공조냉동설계 | HVAC-waterFlow | 냉수 유량 | ṁ=Q̇/(c_p·ΔT) | 25 |
| 공조냉동설계 | HVAC-airChanges | 환기횟수 | N=3600·V̇/V_room | 25 |
| 공조냉동설계 | HVAC-wallU | 종합 열관류율 | U=1/(1/h_i+L/k+1/h_o) | 25 |
| 공조냉동설계 | HVAC-lmtd | 대수평균 온도차 | ΔT_lm=(ΔT₁−ΔT₂)/ln(ΔT₁/ΔT₂) | 25 |
| 공조냉동설계 | HVAC-condensate | 제습 응축수 | ṁ_water=ṁ_DA·(w_in−w_out) | 25 |
| 공조냉동설계 | HVAC-pipeResistance | 원통 단열 열저항 | R=ln(r₂/r₁)/(2πkL) | 25 |
| 시운전 및 안전관리 | HVAC-threePhase | 3상 유효전력 | P=√3·U_L·I_L·cosφ/1000 | 25 |
| 시운전 및 안전관리 | HVAC-insulation | 절연저항 측정 계산 | R=V/I, I[A]=I[mA]/1000; R[MΩ]=R[Ω]/10⁶ | 25 |
| 시운전 및 안전관리 | HVAC-fanFlow | 송풍기 유량 상사 | V̇₂=V̇₁·n₂/n₁ | 25 |
| 시운전 및 안전관리 | HVAC-fanPressure | 송풍기 압력 상사 | Δp₂=Δp₁·(n₂/n₁)² | 25 |
| 시운전 및 안전관리 | HVAC-rotationFrequency | 회전 주파수 | f=n/60 | 25 |
| 시운전 및 안전관리 | HVAC-absolutePressure | 절대압력 환산 | p_abs=p_gauge+p_atm | 25 |
| 시운전 및 안전관리 | HVAC-manometer | 액주 압력차 | Δp=ρgh, kPa=Pa/1000 | 25 |
| 시운전 및 안전관리 | HVAC-balanceRatio | 풍량 밸런싱 | 측정 비율=실측/설계×100 | 25 |
| 시운전 및 안전관리 | HVAC-testDuration | 시운전 계측시간 | t_total=(t₁+t₂+t₃)/60 | 25 |
| 시운전 및 안전관리 | HVAC-shaftTorque | 전동기 축토크 | T[N·m]=9550·P[kW]/n[rpm] | 25 |
| 유지보수 공조냉동 | HVAC-fouling | 오염 추가 열저항 | R_f=1/U_dirty−1/U_clean | 25 |
| 유지보수 공조냉동 | HVAC-lossFraction | 냉매 질량 감소율 | 감소율=(초기−현재)/초기×100 | 25 |
| 유지보수 공조냉동 | HVAC-superheat | 과열도 | 과열도=T_actual−T_sat | 25 |
| 유지보수 공조냉동 | HVAC-subcool | 과냉각도 | 과냉각도=T_sat−T_liquid | 25 |
| 유지보수 공조냉동 | HVAC-savedEnergy | 소비전력 절감량 | E_saved=(P_old−P_new)·t | 25 |
| 유지보수 공조냉동 | HVAC-filterDrop | 필터 차압 증가 | Δp_increase=Δp_current−Δp_clean | 25 |
| 유지보수 공조냉동 | HVAC-effectiveness | 현열교환 온도효율 | ε=(T_h,in−T_h,out)/(T_h,in−T_c,in)×100 | 25 |
| 유지보수 공조냉동 | HVAC-oilFraction | 혼합액 체적비 | 체적분율=V_oil/V_total×100 | 25 |
| 유지보수 공조냉동 | HVAC-runDays | 운전일수 환산 | D=총 운전시간/일 운전시간 | 25 |
| 유지보수 공조냉동 | HVAC-beltSpeed | 벨트 선속도 | v=πDn/60 | 25 |

## 재생성

Python 3.12.14 / Node 24.19.0. 외부 난수 없음. family 순서와 i=0..24 입력식 및 고정 ID를 보존한다.

```sh
python3 scripts/generate_bank.py
npm test
```

재생성 전후 questions.json 및 public/templates 양식의 SHA-256이 동일한지 검사했다. 반올림은 Python Decimal ROUND_HALF_UP이며 TypeScript 검사는 소수 2/4/6자리 반올림 구간의 역산 근 포함을 별도로 검사한다. 전문가의 문장/개념 재검토와 공식 출제기준 대조는 별도 미완료 작업이다.
