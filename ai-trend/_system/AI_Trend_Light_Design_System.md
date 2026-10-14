# AI 트렌드 브리핑 · 밝은 뉴스 디자인 시스템

적용 조합은 **A 매거진 표지형 히어로 + B 익스플레이너 카드형 본문**이다.  
배경은 밝은 회색, 콘텐츠는 흰색 면으로 두고, 산호색은 표지의 포인트로만 사용한다. 다크 모드용 색상은 포함하지 않는다.

## 1. 폰트와 공통 토큰

HTML의 `<head>`에 아래 두 줄을 넣는다.

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css">
```

```css
:root {
  --font-kr: "Pretendard Variable", Pretendard, SUIT, "Apple SD Gothic Neo",
    "Malgun Gothic", sans-serif;
  --font-en: Inter, var(--font-kr);

  --ink: #111214;
  --muted: #626871;
  --paper: #ffffff;
  --wash: #f3f4f6;
  --line: #dfe2e7;
  --coral: #ff8c86;
  --coral-wash: #ffe4e1;
  --mint: #99f0dc;
  --lime: #a7e982;
  --lime-wash: #e9f8df;
  --navy: #17334b;
  --content-width: 1200px;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  margin: 0;
  background: var(--wash);
  color: var(--ink);
  font: 16px/1.55 var(--font-kr);
}

button,
input,
select,
textarea { font: inherit; }

a { color: inherit; }
```

## 2. 상단 헤더와 좌측 메뉴

헤더는 흰색 한 줄, 가운데 워드마크, 왼쪽 메뉴 버튼, 오른쪽 발행일 또는 구독 버튼으로 구성한다. 메뉴 버튼은 화면이 좁아져도 숨기지 않는다.

```css
.site-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: var(--paper);
  border-bottom: 1px solid var(--line);
}

.sitebar {
  min-height: 72px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0 38px;
}

.menu-toggle {
  justify-self: start;
  appearance: none;
  border: 0;
  background: transparent;
  color: var(--ink);
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-height: 44px;
  padding: 0;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.menu-icon,
.menu-icon::before,
.menu-icon::after {
  display: block;
  width: 15px;
  height: 1.5px;
  background: currentColor;
}

.menu-icon {
  position: relative;
}

.menu-icon::before,
.menu-icon::after {
  content: "";
  position: absolute;
  left: 0;
}

.menu-icon::before { top: -5px; }
.menu-icon::after { top: 5px; }

.wordmark {
  font: 800 25px/1 var(--font-en);
  letter-spacing: -0.075em;
  text-align: center;
}

.header-meta {
  justify-self: end;
  font: 650 13px/1 var(--font-en);
}

.header-meta strong {
  display: inline-block;
  margin-left: 10px;
  padding: 10px 13px;
  background: var(--mint);
  color: var(--ink);
}

/* 좌측 메뉴를 눌렀을 때 body에 .menu-open을 붙인다. */
.menu-scrim {
  position: fixed;
  inset: 0;
  z-index: 39;
  background: rgb(17 18 20 / 18%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 180ms ease;
}

.side-menu {
  position: fixed;
  z-index: 40;
  inset: 0 auto 0 0;
  width: min(380px, 88vw);
  padding: 30px;
  background: var(--paper);
  border-right: 1px solid var(--line);
  box-shadow: 16px 0 45px rgb(17 18 20 / 10%);
  transform: translateX(-105%);
  transition: transform 220ms ease;
}

.menu-open .menu-scrim {
  opacity: 1;
  pointer-events: auto;
}

.menu-open .side-menu { transform: translateX(0); }

.side-menu__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 22px;
  border-bottom: 1px solid var(--line);
}

.side-menu__close {
  appearance: none;
  border: 1px solid var(--ink);
  background: var(--paper);
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 20px;
}

.side-menu nav { padding-top: 20px; }

.side-menu a {
  display: flex;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
  text-decoration: none;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.04em;
}

.side-menu a::after {
  content: "↗";
  font: 500 16px/1 var(--font-en);
}
```

메뉴 작동에 필요한 최소 스크립트다.

```js
const body = document.body;
const openMenu = () => body.classList.add("menu-open");
const closeMenu = () => body.classList.remove("menu-open");

document.querySelector(".menu-toggle").addEventListener("click", openMenu);
document.querySelector(".side-menu__close").addEventListener("click", closeMenu);
document.querySelector(".menu-scrim").addEventListener("click", closeMenu);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMenu();
});
```

## 3. A형: 매거진 표지 히어로

히어로는 **왼쪽의 긴 제목·소개·메타 정보**와 **오른쪽의 산호색 기하 도형**으로 나눈다. 실제 이미지가 없어도 표지처럼 보이도록 만든다.

```css
.page-shell {
  max-width: var(--content-width);
  margin: 0 auto 72px;
}

.cover-hero {
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  min-height: 540px;
  background: var(--paper);
}

.cover-copy {
  display: flex;
  flex-direction: column;
  padding: 58px 60px 44px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font: 600 13px/1 var(--font-en);
  letter-spacing: 0.04em;
}

.eyebrow::before {
  content: "";
  width: 9px;
  height: 9px;
  background: var(--coral);
}

.cover-title {
  max-width: 510px;
  margin: 24px 0 18px;
  font-size: clamp(42px, 5.3vw, 71px);
  line-height: 1.02;
  letter-spacing: -0.065em;
}

.cover-summary {
  max-width: 470px;
  margin: 0;
  color: var(--muted);
  font-size: 17px;
}

.cover-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 14px;
  align-items: center;
  margin-top: auto;
  font-size: 13px;
}

.cover-meta__tag {
  padding: 6px 9px;
  background: var(--coral);
  font-weight: 700;
}

.cover-meta__link {
  border-bottom: 1.5px solid currentColor;
  padding-bottom: 2px;
  font: 800 12px/1 var(--font-en);
  letter-spacing: 0.07em;
  text-decoration: none;
}

.cover-art {
  position: relative;
  overflow: hidden;
  min-height: 370px;
  background:
    linear-gradient(90deg, transparent 0 50%, rgb(255 255 255 / 55%) 50% 100%),
    linear-gradient(0deg, transparent 0 50%, rgb(255 255 255 / 55%) 50% 100%),
    var(--coral-wash);
  background-size: 118px 118px;
}

.cover-art__disc {
  position: absolute;
  right: -56px;
  top: 54px;
  width: 410px;
  height: 410px;
  border-radius: 50%;
  background: var(--navy);
}

.cover-art__ring {
  position: absolute;
  right: 48px;
  top: 112px;
  width: 290px;
  height: 290px;
  border: 58px solid var(--coral);
  border-radius: 50%;
}

.cover-art__type {
  position: absolute;
  left: 48px;
  bottom: 40px;
  color: var(--navy);
  font: 800 70px/.84 var(--font-en);
  letter-spacing: -0.09em;
}
```

## 4. B형: 익스플레이너 카드 본문

카드는 같은 비중으로 보여 주되, 제목 길이가 조금 달라도 흐트러지지 않도록 최소 높이를 둔다. 기본값은 데스크톱 4열이다.

```css
.explainer-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  background: var(--paper);
  border-top: 1px solid var(--line);
}

.explainer-card {
  min-height: 238px;
  padding: 25px 23px;
  border-right: 1px solid var(--line);
}

.explainer-card:last-child { border-right: 0; }

.explainer-card__index {
  color: #727a84;
  font: 600 12px/1 var(--font-en);
}

.explainer-card h2,
.explainer-card h3 {
  margin: 18px 0 12px;
  font-size: 20px;
  line-height: 1.18;
  letter-spacing: -0.05em;
}

.explainer-card p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.explainer-card:hover {
  background: var(--lime-wash);
}

.explainer-card:focus-within {
  outline: 3px solid var(--lime);
  outline-offset: -3px;
}

/* 카드 아래의 ‘시작하기’ 안내 영역 */
.start-band {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  margin-top: 22px;
  background: var(--paper);
}

.start-band__title {
  padding: 46px 42px;
  background: var(--lime-wash);
}

.start-band__title h2 {
  margin: 8px 0 0;
  font-size: 37px;
  line-height: 1.04;
  letter-spacing: -0.06em;
}

.start-list { padding: 0 42px; }

.start-list a {
  display: grid;
  grid-template-columns: 82px 1fr auto;
  gap: 18px;
  align-items: center;
  padding: 22px 0;
  border-bottom: 1px solid var(--line);
  text-decoration: none;
}

.start-list a:last-child { border-bottom: 0; }
.start-list small { font: 700 12px/1 var(--font-en); }
.start-list b { font-size: 18px; letter-spacing: -0.035em; }
.start-list span { color: var(--muted); font: 13px/1 var(--font-en); }
```

## 5. 모바일 규칙

```css
@media (max-width: 800px) {
  .sitebar {
    min-height: 58px;
    padding: 0 18px;
  }

  .wordmark { font-size: 20px; }
  .header-meta { display: none; }

  .page-shell {
    margin: 0 12px 48px;
  }

  .cover-hero,
  .start-band {
    grid-template-columns: 1fr;
  }

  .cover-copy {
    min-height: 390px;
    padding: 36px 28px;
  }

  .cover-art { min-height: 340px; }
  .cover-art__type { left: 30px; font-size: 56px; }
  .cover-art__disc { right: -100px; }

  .explainer-grid { grid-template-columns: 1fr; }

  .explainer-card {
    min-height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .start-band__title { padding: 34px 28px; }
  .start-list { padding: 0 24px; }

  .start-list a {
    grid-template-columns: 58px 1fr;
  }

  .start-list span { display: none; }
}
```

## 5-1. C형을 살리는 방법: 선택형 이슈 레저 모듈

C형 전체를 별도 페이지로 쓰는 대신, **A 표지 → B 설명 카드 → C 이슈 레저** 순서로 페이지 하단에 넣는다.  
이 모듈은 가격, 출시 범위, 보안·거버넌스처럼 **근거와 확인 항목이 중요한 주제**에만 사용한다. 평소에는 숨기거나 빼도 A+B 레이아웃은 유지된다.

```css
/* 본문 마지막에 붙이는 C형 요약 리포트 블록 */
.issue-ledger {
  --ledger-blue: #c5ddff;
  --ledger-blue-wash: #e2efff;
  --ledger-border: #4f81aa;
  margin-top: 22px;
  background: var(--paper);
  border-top: 1px solid var(--line);
}

.issue-ledger__head {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  min-height: 250px;
}

.issue-ledger__intro {
  padding: 42px;
  background: var(--ledger-blue-wash);
}

.issue-ledger__intro h2 {
  max-width: 390px;
  margin: 10px 0 0;
  font-size: clamp(31px, 4vw, 48px);
  line-height: 1.04;
  letter-spacing: -0.065em;
}

.issue-ledger__summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.ledger-stat {
  padding: 35px 28px;
  border-left: 1px solid var(--line);
}

.ledger-stat:first-child { border-left: 0; }

.ledger-stat__label {
  color: #647080;
  font: 700 12px/1 var(--font-en);
  letter-spacing: 0.05em;
}

.ledger-stat strong {
  display: block;
  margin: 16px 0 9px;
  font-size: 22px;
  line-height: 1.18;
  letter-spacing: -0.05em;
}

.ledger-stat p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.ledger-checks {
  padding: 0 42px;
}

.ledger-check {
  display: grid;
  grid-template-columns: 90px 1fr auto;
  gap: 18px;
  align-items: center;
  padding: 22px 0;
  border-bottom: 1px solid var(--line);
}

.ledger-check:last-child { border-bottom: 0; }

.ledger-check__type {
  color: #506f8d;
  font: 800 12px/1 var(--font-en);
  letter-spacing: 0.07em;
}

.ledger-check b {
  font-size: 17px;
  letter-spacing: -0.035em;
}

.ledger-check__state {
  color: #506f8d;
  font: 700 12px/1 var(--font-en);
}

@media (max-width: 800px) {
  .issue-ledger__head,
  .issue-ledger__summary {
    grid-template-columns: 1fr;
  }

  .issue-ledger__intro { padding: 34px 28px; }

  .ledger-stat {
    border-top: 1px solid var(--line);
    border-left: 0;
  }

  .ledger-checks { padding: 0 24px; }

  .ledger-check {
    grid-template-columns: 66px 1fr;
  }

  .ledger-check__state { display: none; }
}
```

### 권장 HTML 구조

```html
<section class="issue-ledger" aria-labelledby="ledger-title">
  <div class="issue-ledger__head">
    <div class="issue-ledger__intro">
      <div class="eyebrow">ISSUE LEDGER</div>
      <h2 id="ledger-title">이번 호에서 확인한 기준.</h2>
    </div>

    <div class="issue-ledger__summary">
      <article class="ledger-stat">
        <div class="ledger-stat__label">RELEASE</div>
        <strong>출시일과 공식 범위를 함께 기록</strong>
        <p>발표일, 지원 지역, 플랜, 실제 사용 가능 여부를 분리한다.</p>
      </article>
      <article class="ledger-stat">
        <div class="ledger-stat__label">COST</div>
        <strong>가격 기준과 단위를 분리</strong>
        <p>월 구독료, API 사용량, 추가 도구 비용을 섞지 않는다.</p>
      </article>
      <article class="ledger-stat">
        <div class="ledger-stat__label">RISK</div>
        <strong>사람의 승인 지점을 남긴다</strong>
        <p>외부 행동 전 승인자와 로그 보관 원칙을 명시한다.</p>
      </article>
    </div>
  </div>

  <div class="ledger-checks">
    <div class="ledger-check">
      <span class="ledger-check__type">SOURCE</span>
      <b>공식 발표 원문과 적용 범위를 직접 확인했다</b>
      <span class="ledger-check__state">CHECKED</span>
    </div>
    <div class="ledger-check">
      <span class="ledger-check__type">PRICE</span>
      <b>통화, 기준일, 플랜 및 사용량 기준을 적었다</b>
      <span class="ledger-check__state">CHECKED</span>
    </div>
    <div class="ledger-check">
      <span class="ledger-check__type">ACTION</span>
      <b>조직 도입 시 필요한 검토자와 승인 절차를 적었다</b>
      <span class="ledger-check__state">CHECKED</span>
    </div>
  </div>
</section>
```

### 사용 기준

- **매 호 사용:** A 표지형 + B 익스플레이너 카드
- **숫자·가격·정책·위험 이슈가 있는 호:** 위에 C 이슈 레저를 본문 마지막에 추가
- **깊이 읽기 페이지:** B 카드 대신 C 이슈 레저를 본문 첫 섹션으로 올려도 된다.

## 적용 시 고정할 기준

- 콘텐츠 최대 폭: `1200px`
- 본문 배경: `#f3f4f6`, 카드·히어로 면: 흰색
- 강조색: 표지는 산호색, 카드·학습 안내는 라임색, 근거·리포트 블록은 밝은 파랑
- 제목은 굵고 촘촘하게, 본문은 회색으로 한 단계 낮춘다.
- 이미지를 넣어도 카드의 여백·테두리·타이포 규칙은 유지한다.
