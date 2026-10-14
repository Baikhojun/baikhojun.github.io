# AI 트렌드 브리핑 — 변경 기록

지시서·디자인 토큰·템플릿·스크립트의 변경을 기록한다. 발행본(reports/…)의 내용 변경은 여기 적지 않는다(정정 발행 규칙 3.3).

## 2026-10-14 — 제1호 정정 재발행(_r2) 지원

- `_local/data_src/issue1.py --r2`: 같은 제1호·같은 비교 기간으로 `reports/<ID>_r2/` 에 쓴다(지시서 3.3). 그 뒤 순서는 평소와 같고 `update_archive.py --supersede <이전 ID>` 로 이전 호를 superseded 로 남긴다.
- 사용 예: 제1호 `[core-kr-audit]` 제목 정정(‘1% 남짓’ → 224분의 1, 약 0.45%). 이전 폴더는 그대로 보존.
- 템플릿(디자인 토큰·배치 변경 없음, 문구만): 대시보드 '신규' 카드, 인쇄 통계와 2쪽 '숫자로 본 이번 호' 출처 줄에 정정 건수가 있으면 "이 밖에 정정 n건"을 붙인다(4칸 배치 유지). 아카이브 첫 화면 목록의 호 번호 옆에 '정정본'/'정정 전'을 붙인다.
- `report.css` 인쇄 규칙: PDF에서는 `font-variant-numeric: normal`. 고정폭 숫자(tnum) 대체 글리프가 Chrome PDF에서 사용자 영역 코드(U+E07x)로 들어가 숫자·쉼표·마침표를 복사·검색할 수 없던 문제. 화면은 그대로 tabular-nums. 51쪽·넘침 0 유지 확인.

## 2026-10-14 — 제1호(신규 기준선) 준비, 생성 도구 v1.0

**지시서**: v1.1 그대로 사용.

**생성 도구 신설** (`_system/`)
- `scripts/calc_dates.py` — 기준일·주차·비교 기간·발행 ID 계산. 지시서 2.2 예시 3건 자체 시험 통과(`--selftest`).
- `scripts/build.py` — data.json → 대시보드 HTML + A4 가로 고정 인쇄 페이지. 각 블록 높이를 헤드리스 Chromium으로 실제 글꼴로 재서 페이지에 나눠 담는다(긴 표는 행 단위로 나누고 머리글 반복, 카드는 줄 단위). 차트는 인라인 SVG(타임라인·점 그림·막대·타일 지도·생애주기).
- `scripts/make_pdf.py` — PDF 생성(Playwright, A4 가로), 문서 속성(제목·작성자 Unfade), 넘침·9pt 미만 글자·SVG 글자 크기·쪽수 일치 검사, og.png(1200×630), 페이지 PNG, 대시보드 탭별 화면 캡처(`--screens`).
- `scripts/make_pptx.py` — data.json → PPTX(16:9, 맑은 고딕, 본문 18pt 이상, 편집 가능한 차트·표). LibreOffice가 없는 환경을 위해 PPTX를 다시 읽어 그리는 미리보기·넘침 검사(`--preview`) 포함.
- `scripts/diff.py` — 직전 data.json 과 비교(신규·변경·직전 추적 항목·리더보드 순위 변동·요금 변동).
- `scripts/update_archive.py` — reports.json·아카이브 첫 화면·latest 갱신, 정정 재발행(`--supersede`).
- `templates/` — `report.html.j2`(페이지 뼈대), `_dash.j2`(대시보드), `_print.j2`(인쇄 블록), `report.css`, `report.js`, `index.html.j2`, `latest.html.j2`.
  - 지시서 1.4의 템플릿 목록에 `_dash.j2`·`_print.j2`·`report.css`·`report.js`를 추가했다(발행 폴더에 이 호 전용 사본을 둔다).
- `config/design_tokens.json` — 7.4 토큰 + 변화 태그 8종·판정 기호·성숙도·출처 등급 색(색+아이콘+글자), 회사별 고정색.
  - 인쇄용 `--p-teal`(#0E8F84)·`--p-orange`(#C76A12)는 흰 바탕 작은 글자 대비가 4.5:1 미만이라, 작은 글자용 `--p-teal-text`(#0A7369)·`--p-orange-text`(#A0520C)를 추가했다(굵은 그래픽에는 원래 값 사용).
- `config/tracking_list.yaml`, `config/sources.yaml` — 2026-10-14 기준 추적 목록·필수 출처와 접근 제약.
- 글꼴: `assets/fonts/PretendardVariable.woff2`(Pretendard v1.3.9 공식 저장소, OFL — `LICENSE.txt` 동봉).

**보류**
- 디자인 시안 승인 전이므로 `design_tokens.json` 의 `locked` 는 false. 승인되면 true 로 바꾸고 여기에 기록한다.
- 게시(커밋·푸시)와 `robots.txt` 한 줄 추가는 사용자 결정에 따라 보류.

## 2026-10-14 — 생성 도구 v1.1 (제1호 검수 단계 보완, 같은 날)

검수(지시서 10장) 중 찾은 결함과 개선. 발행 전이라 제1호 산출물은 이 도구로 다시 생성했다.

**결함 수정**
- `calc_dates.py` — 이미 `reports.json` 에 올라간 호를 다시 계산하면 그 호 자신을 직전 발행본으로 잡아 제2호·'직전 발행일 대비'가 되던 문제. 계산 중인 발행 ID를 직전 발행본 후보에서 뺀다. 자체 시험 2건 추가(같은 호 재계산 → 제1호·기준선, 다음 호 → 제2호·10-15~).
- `build.py` `archive_entries` — 이번 호가 `reports.json` 에 이미 있으면 옛 항목(호수·요약)을 그대로 쓰던 문제. 지금 data.json 기준 항목으로 바꿔 끼운다.
- `report.js` 링크 복사 — 앱 안 브라우저 등에서 Clipboard API 쓰기 권한이 거부되면 실패하던 것을 예전 복사 방식으로 다시 시도.
- `make_pptx.py` — 추적 항목 칩을 넘침 검사 전에 그려 바닥글과 겹치던 문제, 추적 항목을 6건까지만 싣던 문제(→ 전부, 여러 장·장마다 고르게), Arena 점수·오차 반올림 표기(1525 ±9 → 1,525 ±8.8), 환율 쉼표 누락, 출처 장 제목의 검색 횟수 누락, 그림에 없는 '가로선'을 설명하던 문구.

**개선**
- 좁은 화면(860px 이하): 상단 고정 바를 2줄(제목+아이콘 버튼 / 가로로 밀어 넘기는 한 줄 탭)로 줄임(360px에서 약 440px → 99px), 선택한 탭이 보이게 탭 줄 자동 이동. 작성 기준·조사 방법 표는 위아래로 쌓고, 인라인 스타일로 고정돼 접히지 않던 3열 흐름·2열 구역을 클래스로 바꿔 한 열로 접음. 날짜가 하이픈에서 끊기지 않게 `.nw`.
- PC에서 파일을 직접 연 경우(file://): 폴더 주소로 된 내부 링크·과거 호 선택에 `index.html` 을 붙임(보고서·아카이브 첫 화면).
- 인쇄 페이지 나눔: 타임라인 인쇄용 줄 간격 −3px, 조사 한계 목록 간격(`.p-list.tight`), 추적 표 열 너비(39/11/32/18%) 조정 — 제목만 남은 쪽·표 1행만 넘어간 쪽이 사라져 54 → 51쪽.
- 점수 표기 `fmt_score`(원래 소수 자릿수 유지 + 천 단위 쉼표)를 대시보드·인쇄·research.md에 적용.
- PPTX: 한글을 띄어쓰기 단위로 줄바꿈(`eaLnBrk=0`, `lang=ko-KR`) — PowerPoint가 단어 중간에서 끊던 문제. 출처 목록 11pt → 14pt, 칸 높이에 맞춰 자동 배치, 날짜를 발행처 바로 뒤로(하이픈 끊김 방지), 마지막 장 두 열 균형. 긴 문구는 문장 끝에서 자름(말줄임 최소화).
- `make_research.py` — 착수 시각·조사 방식·환율 교차 확인 문구를 data.json(`search_log.started_kst`·`method`, `basis.fx.cross_check`)에서 읽고, 주차 규칙 설명·API 확인일을 기준일에서 계산(이번 호 값 고정 제거). 검수 결과 '보류' 표시 추가.

**신설**
- `scripts/pptx_check_powerpoint.ps1` — PowerPoint(COM)로 PPTX를 읽기 전용으로 열어 글상자마다 실제 글자 영역으로 넘침·바닥글 침범·슬라이드 밖을 검사하고 슬라이드 PNG를 내보낸다. LibreOffice가 없는 Windows 환경의 지시서 8.6 렌더링 검수용. PowerPoint가 이미 실행 중이면 사용자의 문서를 건드리지 않도록 검사하지 않고 끝낸다. (UTF-8 BOM 필수 — Windows PowerShell 5.1)

## 2026-10-14 — 디자인 v1.1: 밝은 뉴스 디자인 시스템 (사용자 결정, 제1호 게시)

사용자가 준 `AI_Trend_Light_Design_System.md`(사본: `_system/AI_Trend_Light_Design_System.md`)를 기준으로 화면·PDF·PPTX·og 이미지를 모두 밝은 톤으로 바꿨다. 지시서 7.3에 결정 사항을 적고 부록 D에 v1.2로 기록했다. 이 디자인으로 제1호를 게시하면서 `design_tokens.json` 을 잠근다(`locked: true`).

- **토큰** (`config/design_tokens.json` v1.1): 화면 = wash `#f3f4f6`·paper `#fff`·ink `#111214`·muted `#626871`·line `#dfe2e7`, 강조 = 표지 산호색(`#ff8c86`)·카드/안내 라임(`#a7e982`·`#e9f8df`)·근거 블록 밝은 파랑(`#e2efff`)·남색 `#17334b`. 태그·판정·성숙도·등급의 화면 색은 흰 지면용(인쇄와 같은 값, 대비 4.5:1 이상). 토목 특집 보라색 식별색 유지. 모서리 각진 모양(radius 0, 칩 3px).
- **글꼴**: 웹은 Pretendard 동적 부분 집합(jsdelivr) + Inter(Google Fonts), 연결이 없을 때(PDF 생성·PC에서 직접 열기)는 로컬 사본 `"Pretendard Local"`. PDF 측정·생성은 외부 요청을 막으므로 항상 로컬 사본으로 같게 그린다.
- **사이트 공용 셸**: 보고서·아카이브 첫 화면에 `/css/unfade-shell.css`·`/js/unfade-shell.js`(UNFADE 헤더·프로젝트 메뉴)를 상대 경로로 연결만 한다(사이트 파일은 수정하지 않음, 셸 메뉴에 ai-trend 링크 추가 없음). 셸 헤더는 스크롤하면 지나가므로 보고서 탭 바는 화면 맨 위에 고정.
- **대시보드**: 머리 정보 줄(주차·기준일·대비 여부·보기 전환) + 한 줄 고정 탭 바(링크 복사·인쇄하기·PDF로 저장하기). 첫 화면을 A형 매거진 표지 → B형 숫자 카드 → 3분 요약 띠(라임) → 작성 기준 띠(밝은 파랑) 순서로, 핵심 변화 탭 끝에 C형 이슈 레저(RELEASE·COST·RISK / SOURCE·PRICE·GRADE)를 추가. 섹션은 회색 바탕 위 흰 면, 표 머리글은 2px 먹선.
- **차트**: `build.THEME["screen"]` 을 밝은 지면용으로, 점 그림 눈금 간격을 그림 폭에 맞춰 자동으로(이름표 겹침 방지).
- **PDF**: 표지를 A형(흰 지면 + 산호색 격자·남색 원판·산호색 고리)으로, 머리띠를 흰 바탕 + 먹선으로, 표 머리글을 밝은 회청색으로. 넘침 검사는 잘라 내는 상자(overflow hidden) 안의 장식은 넘침으로 보지 않음.
- **PPTX**: 표지 A형, 머리띠 흰 바탕 + 먹선, 표·묶음 머리글 밝은 회청색, 요약 번호 라임.
- **og.png·아카이브 첫 화면**: A형 표지 축소판, 아카이브는 A 표지(최신호) + B 카드(이번 호 핵심·고정 주소) + 발행 목록 띠. `reports.json` 항목에 `headline`(표지 제목) 추가.
