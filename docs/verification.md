# 실제 검증 및 배포 차단 기록

2026-11-02, 작업 디렉터리 `/workspace/Craftsman-Air-Conditioning-and-Refrigerating-Machinery-CBT`.

## 검증한 소스와 환경

- 대상 시작 HEAD `c32792909824f87e64d54fcf44992773c1d826f4`: README만 존재, 작업 트리 깨끗함, AGENTS.md 없음.
- 표준 최신 main `76b990b8720adfa85c22a0a8f699b17094aa357b`: CBT 스킬 v1.4.0과 references 전체를 읽음. 스킬 파일 9개를 바이트 동일 복사하고 AGENTS.md로 연결함.
- 앱 재사용 원본 `b9a682ccff1b460334b78d5bfad9375b7ec4fbb6`: git archive로 고정 소스 확인. 앱·모델·CSS·테스트 구조·배포 workflow를 재사용. 원본 전기 문항과 생성기는 포함하지 않음.
- Node 24.19.0 / npm 11.9.0 / Python 3.12.14. npm ci 잠금 설치 완료(종료 0). Chromium `/usr/bin/chromium`, Playwright 1.64.1(잠금 파일 기준). 별도 서버·키 없음.

## 최종 실행 결과

| 검사 | 명령 / 방법 | 결과 |
| --- | --- | --- |
| 단위 검사 | `npm test` | 종료 0, 2파일/1,017개 통과, 실패0/skip0 |
| 타입 검사·프로덕션 빌드 | `npm run build` (`test:e2e` 안에서 실행) | 종료 0, tsc -b와 Vite 빌드 성공 |
| 브라우저 | `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npm run test:e2e` | 종료 0, 22통과/2skip/0실패 |
| 문항 생성 재현 | `python3 scripts/generate_bank.py` 전후 SHA-256 | 종료 0, questions.json 및 JSON/CSV 양식 3파일 동일 |
| 스킬 복사 무결성 | 원본 9파일과 byte 비교 | 종료 0, 전체 일치 |
| 화면 검사 | Playwright Chromium screenshot + 실제 화면 이미지 확인 | PC 1440×1000, 모바일390×844에서 대시보드·실전 화면 가로 넘침 없음 |

설치 초기에는 실행 샌드박스가 프록시 연결을 차단해 npm이 실패했다. 해당 프로세스를 종료하고 허용된 실행 권한으로 잠금 설치를 완료했다. 배포 사전 확인과는 별개인 로컬 개발 의존성 설치다. 로컬 브라우저 검사 초기에 원본의 마지막 번호59 조건이 남아 60번 다음 버튼이 비활성화되는 결함을 발견했다. 최종 코드에서 설정 기반 마지막 번호79로 수정하고 60→61번 Space 이동 회귀를 추가한 후 위 최종 결과를 얻었다. 실패를 숨기거나 기대값을 완화하지 않았다.

Vite는 JSON을 포함한 단일 JS chunk 약1.72MB(gzip 약145KB)에 대해 500KB 경고를 출력했다. 빌드는 성공했으며 청크 경고 임계값을 높여 숨기지 않았다. 코드 분할은 미실행이다.

## 브라우저 실제 동작 범위

- Desktop Chrome와 Pixel 7 에뮬레이션. 실전80문항 이동/답안/과목별12정답=전체60점 합격, 북마크, 새로고침·절대 deadline 보존, 제출 취소/확정, 전체80개 해설/오답32개 필터와 재학습.
- 120분 만료, 만료 재접속·콜백 전 클릭 거부, 중복 제출 방지. 평균60점과 과목40점 경계/과락 불합격은 별도 단위검사.
- 랜덤 즉시 채점/한 번 기록, 오답→정답 복습 해제, 연속 정답, 통계·북마크·학습 이어하기.
- JSON/CSV 가져오기·중복 제외·pending·근거 및 확인 체크 후 로컬 승인·잘못된 파일 원자적 거부·초기화 확인.
- 실제 keyboard.press에 따른 keydown/keyup: 두 모드 Space, 미응답 보호, 본문 포커스, 수정키 보호, 실전60→61/마지막80번 유지, 네이티브 버튼 동작. IME/repeat/입력/메뉴/대화상자 보호 조건을 코드에서 유지하며 repeat·대화상자 경계 일부는 합성 이벤트로 확인. OS별 실제 IME 조합은 미실행.
- 손상 localStorage 원본 보존과 저장 공간 제한 DOMException에 대한 실제 경고. 학습 기준 메뉴/상단 criteria-note 없음.
- 메뉴390×480과740×360: 메뉴 애니메이션 종료 후 실제 mouse.wheel로 아래/위 이동, 하단이 뷰포트에 들어온 뒤 백업 다운로드·초기화 대화상자 입력, 상단 대시보드 재접근. 별도로 CDP Input.dispatchTouchEvent touchStart/move/end로 아래/위 이동, 하단 백업 tap 다운로드, 상단 대시보드 tap 선택/메뉴 닫힘 확인. scrollTop 값을 설정하여 검사를 대신하지 않음. root font-size125% 조건도 적용함.
- 2개 skip은 위 모바일 전용 메뉴 시나리오를 desktop 프로젝트에서 중복 실행하지 않은 것이다. 모바일 프로젝트에서는 두 시나리오 모두 통과했다. 실제 휴대폰·Safari·iOS 주소창 변화·OS 글자 확대·블로그 iframe 입력과 저장은 미실행이다. root font-size 변경은 모든 고정 px 글자의 실제 확대를 의미하지 않는다.

스크린샷은 로컬 ignored `test-results/desktop-dashboard.png`, `mobile-exam.png`, `menu-390-bottom.png`, `menu-740-bottom.png` 등에 있다. 프로덕션 배포 화면이 아니라 로컬 preview 산출물이다.

## 공식 규칙·문항 검토 한계

Q-Net 후보 공식 페이지 요청: `curl -I --max-time 30 'https://www.q-net.or.kr/crf005.do?id=crf00503&jmCd=1730'`.
응답 `HTTP/1.1 403 Forbidden`, `curl: (56) CONNECT tunnel failed, response 403`(종료56). 실제 페이지 본문은 읽지 못했다. 자격증 공식 규칙/출제기준 적용판/권리조건 원문 대조는 **차단**이며 공식 확인 통과가 아니다. 네트워크 설정을 우회하지 않았다.

기본 JSON은 1000개 reviewed, 과목별250, ID/정규화 본문·정렬 보기 중복0. 자체제작 계산40 family×25조건이며 추가 수치변형960, 기출0/복원0/비계산개념0, 수량 부족0. 의미상 같은 계산의 변형임을 공개한다. 내부 검토와 자동계산 검사만 수행했고 전문가 검수·공식 출제기준 대조는 미완료이다. [문항 검토 기록](question-review.md)에 유형별 검토 범위를 기록했다. 개인 로컬 등록은 이 수량에 포함하지 않는다.

## 배포 사전 확인: 최초1회 차단 후 중단

2026-11-02 실제 최초 명령:

```text
gh api repos/YunSangYeong/Craftsman-Air-Conditioning-and-Refrigerating-Machinery-CBT --jq '{full_name,default_branch,permissions,has_pages}'
Get "https://api.github.com/repos/YunSangYeong/Craftsman-Air-Conditioning-and-Refrigerating-Machinery-CBT": Forbidden
exit 1
```

이 응답만으로 토큰 만료·계정 권한 부족·Pages 비활성화 중 어느 것이 원인인지 확정할 수 없다. 플랫폼 Git HTTPS 읽기는 클론으로 성공했으며 GitHub API 접근과 구별한다. API 재조회나 다른 도구의 API 우회 시도는 하지 않았다. 최초 Pages 설정/환경 승인 필요 여부도 미확인이다.

- main 푸시: **미실행**.
- CI·Pages workflow 시작/수동 실행/재실행: **미실행**.
- Pages 설정 변경: **미실행**.
- Pages 배포 성공 및 기존 사이트 게시 여부: **미확인**.
- 공개 사이트 화면/기능 확인: **미실행**. 예상 URL은 README에만 기록하며 성공 증거로 제시하지 않는다.
- 원격 보존: 자동 배포 없는 `cbt/hvac-engineer-standard-20261102` 브랜치만 사용한다. workflow push는 main만 받으며 `[skip ci]` 커밋으로 보존한다. PR/API/수동 실행/추가 main push를 통해 첫 차단을 우회하지 않는다. 원격 커밋은 최종 응답 및 `git log -1`로 확인한다.

현재 사용자에게 필요한 첫 동작은 **클라우드 환경 설정에서 네트워크 허용 목록에 `api.github.com`을 추가**하는 것이다. 공식 규칙 조사는 별도로 `www.q-net.or.kr` 접근이 필요하다. 이후 배포 마무리는 사용자가 직접 하며, 네트워크 허용만으로 에이전트가 자동 재시도하지 않는다. 별도 배포된 프로젝트에는 변경·재배포를 수행하지 않았다.
