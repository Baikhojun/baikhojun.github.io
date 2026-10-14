<div align="center">

# unfade

**로그인 없이, 서버 없이. 바로 열어 쓰는 실용 데이터 도구 모음**

[unfade.is-a.dev](https://unfade.is-a.dev/)

![GitHub Pages](https://img.shields.io/badge/hosting-GitHub%20Pages-111214?style=flat-square)
![Static](https://img.shields.io/badge/stack-HTML%20%C2%B7%20CSS%20%C2%B7%20JS-17334b?style=flat-square)
![No backend](https://img.shields.io/badge/backend-none-ff8c86?style=flat-square)
![Design](https://img.shields.io/badge/design-UNFADE%20Light-99f0dc?style=flat-square)

</div>

---

이 저장소 하나가 `unfade.is-a.dev`의 **배포본이자 원본 관리처**입니다.
모든 도구는 정적 파일이라 GitHub Pages가 `main` 브랜치를 그대로 서빙하고, 계산과 저장은 방문자의 브라우저 안에서 끝납니다.

## 목차

- [도구 한눈에 보기](#도구-한눈에-보기)
- [도구별 소개](#도구별-소개)
- [공통 디자인 시스템](#공통-디자인-시스템)
- [저장소 구조](#저장소-구조)
- [빌드와 배포](#빌드와-배포)
- [검색 노출·개인정보 원칙](#검색-노출개인정보-원칙)
- [데이터와 상표 고지](#데이터와-상표-고지)

## 도구 한눈에 보기

| 경로 | 도구 | 한 줄 소개 | 기준 시점 | 원본 |
| --- | --- | --- | --- | --- |
| `/` | **unfade 홈** | 도구 모음 첫 화면(프로젝트 인덱스) | — | `index.html`, `css/home.css` |
| `/house/` · `/house/m/` | **신혼부부 내집마련의 정석** | 서울·경기 예비 신혼부부를 위한 71개 선택지 진단과 계산기 | 2026-10-08 | `projects/house-guide/` |
| `/cukoo/` · `/cukoo/m/` | **쿠쿠 밥솥 모델코드 해독기 v3** | 모델명과 제시 가격으로 “진짜 특가”인지 5단계 판정 | 2026-09-16 (213개 모델) | `projects/cuckoo-decoder/` |
| `/tv/` · `/tv/m/` | **대형 TV 해독기** | 75~86인치 TV를 모델코드·오늘 가격·실측 화질로 판정 | 2026-09-15 (178개 모델) | `projects/cuckoo-decoder/TV/` |
| `/lk1800/` | **LK1800 매트리스 비교** | 라지킹 매트리스 10개 모델을 6개 항목 100점으로 비교 | 2026-08 (v2.1) | `lk1800/` |
| `/ai-trend/` | **AI 트렌드 브리핑** | AI를 처음 접하는 사람을 위한 글로벌 AI 뉴스와 토목설계 특집 | 제1호 2026-10-14 | `ai-trend/_system/` |

> `/cuckoo/`는 `/cukoo/`로 넘겨 주는 이전 주소입니다. 개인용 일정표는 목록·메뉴에 싣지 않습니다.

## 도구별 소개

### 🏠 신혼부부 내집마련의 정석 · `/house/`

서울·경기 예비 신혼부부가 쓸 수 있는 내집마련 선택지 71개를 법령과 공고로 확인해 정리한 안내서입니다.

- **우리 부부 진단**: 혼인 단계·고용 형태·소득·자산 등을 넣으면 71개 선택지를 *지금 가능 / 혼인신고 후 / 임신·출산 후 / 확인 필요 / 어려움*으로 나눕니다.
- **계산기**: 목표 달성률(과거 20년 변동률로 1만 경로 시뮬레이션), 청약 가점, 누적 당첨 확률, 증여세, 부모 차입 규칙
- **숫자로 보는 서울**: 집값·PIR·청약 경쟁률 20년 차트(KB·한국부동산원·통계청 등 공개 자료)
- **선택지 사전**: 9개 분류 71개 항목, 국가법령정보센터 링크, `Ctrl+K` 검색과 관심 항목 표시
- 입력값은 서버로 보내지 않고 브라우저에만 저장합니다. 인쇄용 레이아웃도 제공합니다.
- 휴대폰으로 PC판을 열면 `/house/m/`으로 자동으로 넘어갑니다(`?pc`를 붙이면 PC판 유지).

### 🍚 쿠쿠 밥솥 모델코드 해독기 v3 · `/cukoo/`

쿠쿠 공식몰 전 모델의 모델명 규칙을 역으로 풀어, 홈쇼핑·오픈마켓의 “특가”가 진짜인지 판정합니다.

- **가격 판정 5단계**: 역대급 · 특가 · 적정 · 보류 · 금지. 모델코드 해부, 기준선, 가격 관측 이력, 후속작 위험, 실측 스펙(압력·소비전력·에너지등급)을 함께 보여 줍니다.
- **상황별 추천**(8개 상황 × 3단계), **1:1 비교**(헤도닉 회귀 가중치로 가격 차이를 분해), **조건으로 찾기**, **전체 목록**(정렬 11종)
- 데이터: 213개 모델(판매 중 204), 가격 스냅샷 4회(2026-08-18 ~ 2026-09-16)
- 모바일판 `/cukoo/m/`은 하단 탭 6개와 최근 판정 기록을 제공합니다.

### 📺 대형 TV 해독기 · `/tv/`

국내 정식 유통 75~86인치 TV를 모델코드와 오늘 본 가격으로 “지금 사도 될까?” 판정합니다. 화질 점수는 제조사 스펙이 아니라 **제3자 실측값**입니다.

- **판정 5단계**와 같은 돈으로 살 수 있는 더 나은 대안, 결제 전 체크리스트
- **추천**: 크기·용도·예산·AS 걱정 정도를 고르면 3단계 추천과 브랜드별 최선 1개
- **가중치 프리셋 5종**과 슬라이더로 순위 다시 계산, 점수 불확실성 구간 표시
- 데이터: 178개 모델(2024~2026년형, 6개 브랜드), 가격 스냅샷 2026-09-15

### 🛏️ LK1800 매트리스 비교 · `/lk1800/`

라지킹(LK1800) 매트리스 10개 모델을 내장재·품질·가성비 등 6개 항목 100점으로 채점한 비교 리포트입니다.

- 요약 · 원가성 · 품질 · 가성비(가중치 8개 시나리오) · 렌탈 vs 구매 · 1:1 매칭 · 교차검증 · 사양 원장 · 주의 사항
- 휴대폰 화면 기준(본문 최대 520px)의 단일 HTML이며 빌드 과정 없이 직접 고칩니다.

### 📰 AI 트렌드 브리핑 · `/ai-trend/`

AI를 처음 접하는 사람을 위한 글로벌 AI 뉴스와 **토목설계 AI 특집**을, 직전 호와 달라진 점 중심으로 정리해 발행합니다.

- 매 호 산출물: 7개 탭 대시보드(HTML) · A4 가로 PDF · 16:9 PPTX · 조사근거(`research.md`) · 데이터 원본(`data.json`)
- 모든 산출물을 `data.json` 하나에서 생성하므로 화면·PDF·PPTX의 수치와 출처가 같습니다.
- 모든 수치에 출처와 확인일을 붙이고, 결론·순위·가격 표는 공식 출처 1곳 또는 전문 매체 2곳 이상으로 확인합니다.
- 항상 최신호로 열리는 고정 주소 `/ai-trend/latest/`, 지난 호는 `/ai-trend/reports/<발행 ID>/`에 그대로 보존합니다.
- 작성 기준: [`ai-trend/_system/AI_Trend_Briefing_Master_Instruction.md`](ai-trend/_system/AI_Trend_Briefing_Master_Instruction.md) · 디자인: [`AI_Trend_Light_Design_System.md`](ai-trend/_system/AI_Trend_Light_Design_System.md)

## 공통 디자인 시스템

사이트 전체는 **UNFADE Light** 디자인 시스템을 따릅니다. 밝은 회색 바탕에 흰 면을 올리고, 제목은 굵고 촘촘하게, 본문은 한 단계 낮은 회색으로 씁니다.

| 토큰 | 값 | 쓰임 |
| --- | --- | --- |
| `ink` | `#111214` | 제목·본문 |
| `muted` | `#626871` | 보조 설명 |
| `paper` / `wash` | `#ffffff` / `#f3f4f6` | 카드·히어로 면 / 페이지 바탕 |
| `line` | `#dfe2e7` | 구분선 |
| `coral` / `coral-wash` | `#ff8c86` / `#ffe4e1` | 표지 포인트 |
| `lime` / `lime-wash` | `#a7e982` / `#e9f8df` | 카드 강조·안내 영역 |
| `mint` | `#99f0dc` | 헤더 배지·주요 버튼 |
| `navy` | `#17334b` | 표지 도형·보조 강조 |

- **글꼴**: Pretendard Variable(한글) + Inter(영문·숫자)
- **공용 셸**: `css/unfade-shell.css` + `js/unfade-shell.js` — 고정 UNFADE 헤더, 프로젝트 메뉴(서랍), 모든 도구에 같은 내비게이션. 인쇄할 때는 자동으로 숨겨집니다.
- **테마 레이어**
  - `css/unfade-tool-theme.css`: 결정 도구 4종(house·cukoo·tv·lk1800)의 기존 색을 UNFADE 토큰에 연결
  - `css/unfade-premium.css`: 쇼핑 도구 3종(cukoo·tv·lk1800)에 따뜻한 화이트·샌드 톤(“Atelier”) 적용
- **화면 구성 패턴**: A 매거진 표지 히어로 → B 익스플레이너 카드 → (필요할 때) C 이슈 레저

## 저장소 구조

```text
.
├── index.html                    # 사이트 홈(프로젝트 인덱스)
├── css/
│   ├── unfade-shell.css          # 공용 셸 + 디자인 토큰
│   ├── unfade-tool-theme.css     # 결정 도구 4종 토큰 연결
│   ├── unfade-premium.css        # 쇼핑 도구 3종 Atelier 테마
│   ├── home.css                  # 홈 레이아웃
│   └── style.css                 # 개인용 페이지 스타일
├── js/
│   ├── unfade-shell.js           # 셸 생성·프로젝트 메뉴
│   └── 그 밖의 .js               # 개인용 페이지 모듈
├── house/  (+ m/)                # 신혼부부 내집마련의 정석 배포본
├── cukoo/  (+ m/)                # 쿠쿠 해독기 배포본 · cuckoo/ = 이전 주소
├── tv/     (+ m/)                # 대형 TV 해독기 배포본
├── lk1800/                       # 매트리스 비교(단일 HTML)
├── plan/ · m/ · schedule/ · data/  # 개인용 페이지(목록·메뉴에 싣지 않음)
├── ai-trend/                     # AI 트렌드 브리핑
│   ├── index.html · latest/ · reports.json   # 아카이브 첫 화면 · 최신호 고정 주소 · 발행 목록
│   ├── reports/<발행 ID>/        # 호별 발행본(HTML·PDF·PPTX·조사근거·데이터)
│   ├── assets/fonts/             # Pretendard(OFL) 로컬 사본
│   └── _system/                  # 작성 지시서 · 디자인 시스템 · 설정 · 템플릿 · 생성 스크립트
├── projects/
│   ├── house-guide/              # 내집마련 가이드 원본 + deploy_house.py
│   └── cuckoo-decoder/           # 쿠쿠 해독기 빌드 파이프라인·데이터·가격 스냅샷, TV/ 원본 포함
├── scripts/
│   ├── build_deploy.py           # house·cukoo·tv 재생성 + 셸 재적용
│   └── inject_site_shell.py      # 공용 셸 블록 주입(여러 번 실행해도 결과 같음)
├── docs/MIGRATION.md             # 저장소 통합 기록과 배포 흐름
└── CNAME · .nojekyll · robots.txt · favicon.* · apple-touch-icon.png
```

## 빌드와 배포

`main`에 푸시하면 GitHub Pages가 `https://unfade.is-a.dev/`로 바로 서빙합니다(`CNAME` = `unfade.is-a.dev`). 별도 서버나 빌드 서비스는 없습니다.

**house · cukoo · tv** — 원본을 고친 뒤 저장소 루트에서:

```bash
python scripts/build_deploy.py
```

체크인된 데이터만으로 배포 HTML을 다시 만들고 공용 셸을 다시 넣습니다(웹 수집은 하지 않음). 결과 diff를 확인한 뒤 커밋·푸시합니다.

**lk1800** — 빌드 과정 없이 `lk1800/index.html`을 직접 고칩니다.

**AI 트렌드 브리핑** — `ai-trend/_system/scripts/`의 Python 스크립트(Jinja2 · Playwright · python-pptx)가 `data.json` 하나로 모든 산출물을 만듭니다.

```bash
python ai-trend/_system/scripts/build.py --issue <발행 ID>          # 대시보드 + A4 인쇄 페이지
python ai-trend/_system/scripts/update_archive.py --issue <발행 ID> # reports.json · 아카이브 · latest
python ai-trend/_system/scripts/make_pdf.py --issue <발행 ID>       # PDF · og.png · 넘침 검사
python ai-trend/_system/scripts/make_pptx.py --issue <발행 ID>      # PPTX
python ai-trend/_system/scripts/make_research.py --issue <발행 ID>  # 조사근거 research.md
```

발행 절차와 검수 기준은 작성 지시서 8장·10장, 도구 변경 내역은 [`ai-trend/_system/CHANGELOG.md`](ai-trend/_system/CHANGELOG.md)에 있습니다.

## 검색 노출·개인정보 원칙

- **검색 노출**: `robots.txt`가 홈(`/`)만 허용하고 도구 경로(`/house`, `/cukoo`, `/cuckoo`, `/tv`, `/lk1800`, `/ai-trend` 등)는 막습니다. AI 트렌드 브리핑과 개인용 페이지에는 `noindex, nofollow`도 넣었습니다. 링크를 아는 사람만 찾아오는 구조입니다.
- **로그인·서버 없음**: 진단 입력값, 최근 판정 기록, 오늘 본 가격 같은 데이터는 방문자의 브라우저(localStorage)에만 저장합니다.
- **방문 집계**: 일부 페이지(house·cukoo·tv·ai-trend)는 [GoatCounter](https://www.goatcounter.com/)로 쿠키 없이 방문 수만 셉니다. 웹으로 접속했을 때만 작동합니다.

## 데이터와 상표 고지

- 가격·스펙·점수는 각 도구에 적힌 **기준 시점**의 공개 정보이며, 이후 바뀔 수 있습니다. 구매 결정은 판매처의 최신 정보로 다시 확인해 주세요.
- 쿠쿠, 삼성, LG, TCL, 하이센스 등 제품명과 브랜드는 각 소유자의 상표입니다. 이 사이트는 어느 제조사·판매처와도 제휴하지 않은 개인 프로젝트입니다.
- AI 트렌드 브리핑은 정보 정리용이며 투자 조언이나 특정 종목 추천을 하지 않습니다.
- 글꼴: [Pretendard](https://github.com/orioncactus/pretendard) · [Inter](https://rsms.me/inter/) (SIL Open Font License 1.1)

<div align="center">

<sub>Made by <b>Unfade</b> · <a href="https://unfade.is-a.dev/">unfade.is-a.dev</a></sub>

</div>
