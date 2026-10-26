/* BRITA 신혼부부 정수기 비교 — 웹·모바일 공용 화면 로직
 * 각 구역은 id가 있는 빈 요소에 그린다. 웹(index.html)과 모바일(m/index.html)은 같은 함수를 쓴다.
 */
(() => {
  const D = window.BRITA;
  const R = D.review;
  const ASSET = document.body.dataset.asset || 'assets/';
  const $ = (id) => document.getElementById(id);
  const won = (n) => (n == null ? '—' : Math.round(n).toLocaleString('ko-KR') + '원');
  const num = (n, d = 0) => Number(n).toLocaleString('ko-KR', { maximumFractionDigits: d, minimumFractionDigits: d });
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const store = {
    get(k, d) { try { const v = localStorage.getItem('brita:' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem('brita:' + k, JSON.stringify(v)); } catch { /* 저장 불가 환경 */ } }
  };

  /* ───────── 상태 ───────── */
  const state = {
    mode: store.get('mode', 'member'),      // member=멤버십쿠폰가, sale=화면 판매가
    daily: store.get('daily', 3),           // 2인 하루 정수 사용량(L)
    rule: store.get('rule', 28),            // 교체 상한(일): 28=권장 4주, 56=저사용 예외 8주
    bottle: store.get('bottle', 600),       // 생수 2L 한 병 가격(가정)
    reviewFilter: 'all'
  };
  const price = (s) => (state.mode === 'member' ? s.member : s.sale);
  const modeLabel = () => (state.mode === 'member' ? '멤버십쿠폰가' : '화면 판매가');

  /* ───────── 계산 ───────── */
  const byId = Object.fromEntries(D.models.map((m) => [m.id, m]));
  const skusOf = (mid) => D.skus.filter((s) => s.model === mid);
  const baseSku = (mid) => skusOf(mid).filter((s) => s.total === 1).sort((a, b) => a.member - b.member)[0] || null;
  const filterPacks = () => D.skus.filter((s) => s.kind === 'F')
    .map((s) => ({ ...s, unit: price(s) / s.total, type: s.pure && s.lime ? 'mix' : s.pure ? 'pure' : 'lime' }))
    .sort((a, b) => a.unit - b.unit);
  const bestPure = () => filterPacks().find((p) => p.type === 'pure');

  // 같은 본체·같은 색상의 기본(1입) 대비 큰 묶음의 추가 필터 1개 값
  function marginals() {
    const out = [];
    D.models.forEach((m) => {
      skusOf(m.id).filter((s) => s.total > 1).forEach((s) => {
        const base = skusOf(m.id).find((b) => b.total === 1 && (b.color === s.color || m.id === 'B03'));
        if (!base) return;
        out.push({ model: m, sku: s, base, unit: (price(s) - price(base)) / (s.total - 1) });
      });
    });
    return out.sort((a, b) => a.unit - b.unit);
  }

  // 퓨어 필터 N개 이상을 가장 싸게 사는 조합(단독 패키지만, 무제한 배낭)
  function cheapestPure(n) {
    const packs = filterPacks().filter((p) => p.type === 'pure');
    const max = n + 16;
    const best = Array(max + 1).fill(Infinity); const pick = Array(max + 1).fill(null);
    best[0] = 0;
    for (let i = 1; i <= max; i++) packs.forEach((p) => {
      const prev = Math.max(0, i - p.total);
      if (best[prev] + price(p) < best[i]) { best[i] = best[prev] + price(p); pick[i] = p; }
    });
    let bi = n; for (let i = n; i <= max; i++) if (best[i] < best[bi]) bi = i;
    const combo = {}; let i = bi;
    while (i > 0 && pick[i]) { combo[pick[i].id] = (combo[pick[i].id] || 0) + 1; i = Math.max(0, i - pick[i].total); }
    return { cost: best[bi], count: bi, combo };
  }

  function annual() {
    const life = Math.min(D.filterSpec.liters / state.daily, state.rule);
    const perYear = Math.max(1, Math.round(365 / life));   // 4주 교체 = 연 13개
    const unit = bestPure().unit;
    const brita = perYear * unit;
    const bottles = (state.daily / 2) * 365;
    const bottled = bottles * state.bottle;
    return { life, perYear, unit, brita, bottles, bottled, save: bottled - brita, perL: brita / (state.daily * 365) };
  }

  /* 신혼부부 적합도(편집 판단). 기준은 화면에 함께 공개한다 */
  const fitScore = {
    B06: { value: 5, cap: 5, ease: 5, material: 3, rank: 1, tag: '추천 1위' },
    B05: { value: 4, cap: 4, ease: 3, material: 3, rank: 2, tag: '추천 2위' },
    B02: { value: 4, cap: 3, ease: 5, material: 3, rank: 3, tag: '좁은 냉장고' },
    B03: { value: 2, cap: 3, ease: 4, material: 5, rank: 4, tag: '유리 선호' },
    B04: { value: 2, cap: 3, ease: 4, material: 5, rank: 5, tag: '한정판' },
    B01: { value: 3, cap: 2, ease: 3, material: 3, rank: 6, tag: '최저가 입문' },
    B07: { value: 3, cap: 2, ease: 2, material: 3, rank: 7, tag: '2인엔 과함' }
  };
  const scoreKeys = [['value', '가성비'], ['cap', '2인 용량 적합'], ['ease', '편의·알림'], ['material', '소재·세척']];

  /* ───────── 공통 조각 ───────── */
  const img = (file, alt, cls = '') => `<img class="${cls}" src="${ASSET}${file}" alt="${esc(alt)}" loading="lazy" decoding="async">`;
  const vBadge = (v) => { const [t, c] = R.verdicts[v]; return `<span class="verdict ${c}">${t}</span>`; };
  const dots = (n) => `<span class="dots" aria-label="${n}점 / 5점">${'●'.repeat(n)}<i>${'●'.repeat(5 - n)}</i></span>`;
  const extLink = (href, label, cls = 'btn') => `<a class="${cls}" href="${href}" target="_blank" rel="noopener">${label}</a>`;

  function bars(rows, { max, min = 0, fmt = won, hi } = {}) {
    const m = max || Math.max(...rows.map((r) => r.value));
    return `<div class="bars">${rows.map((r) => `
      <div class="bar-row${(hi != null && r.id === hi) || r.hi ? ' is-hi' : ''}">
        <span class="bar-label">${r.label}</span>
        <span class="bar-track"><span class="bar-fill ${r.cls || ''}" style="width:${Math.max(2, ((r.value - min) / (m - min)) * 100).toFixed(1)}%"></span></span>
        <span class="bar-val">${fmt(r.value)}</span>
      </div>`).join('')}</div>`;
  }

  /* ───────── 구역: 요약 ───────── */
  function renderSummary() {
    const el = $('summary'); if (!el) return;
    const a = annual();
    const xl = byId.B06; const xlBase = baseSku('B06'); const xlYear = D.skus.find((s) => s.id === 'SKU026');
    el.innerHTML = `
      <div class="pick-card">
        <div class="pick-media">${img(xl.img, '브리타 스타일에센셜 XL 3.6L 제품 사진')}</div>
        <div class="pick-body">
          <span class="eyebrow">신혼부부 결론 · ${D.asOf} 기준</span>
          <h3>스타일에센셜 XL 3.6L <small>+ 퓨어 퍼포먼스 필터</small></h3>
          <p>같은 가격대에서 정수된 물을 가장 많이(2.3L) 담고, 스마트라이트·한 손 뚜껑·출수구 덮개까지 갖췄습니다. 7개 본체 모두 같은 필터를 쓰므로 <b>비싼 본체가 물을 더 깨끗하게 만들지는 않습니다.</b></p>
          <div class="pick-prices">
            <div><small>처음 써보기 (필터 1개)</small><b>${won(price(xlBase))}</b></div>
            <div><small>1년 구성팩 (필터 13개)</small><b>${won(price(xlYear))}</b></div>
            <div><small>2년차부터 필터비/년</small><b>${won(a.brita)}</b></div>
          </div>
          <div class="pick-actions">${extLink(xl.naver, '네이버 공식 스토어에서 보기 ↗')}${extLink('#models', '7개 본체 비교', 'btn ghost')}</div>
        </div>
      </div>
      <div class="kpis">
        <div class="kpi"><small>생수 대비 연간 절약</small><b>${won(a.save)}</b><span>하루 ${num(state.daily, 1)}L · 생수 2L ${won(state.bottle)} 가정</span></div>
        <div class="kpi"><small>정수 1L당 필터비</small><b>${num(a.perL, 0)}원</b><span>생수는 1L당 ${num(state.bottle / 2)}원</span></div>
        <div class="kpi"><small>필터 개당 최저가</small><b>${won(a.unit)}</b><span>${bestPure().name}</span></div>
        <div class="kpi"><small>박사 총평</small><b class="kpi-text">물맛 ○ · 건강 효과 △ · 위생 관리 필수</b><span>42개 항목 검토</span></div>
      </div>
      <div class="three-points">
        <div><b>1</b><p><strong>정수 성능은 7개 본체가 모두 같습니다.</strong> 같은 막스트라 프로 필터 1개를 끼웁니다. 본체는 용량·소재·편의로 고르세요.</p></div>
        <div><b>2</b><p><strong>한국은 퓨어 퍼포먼스면 충분합니다.</strong> 한국 수돗물은 이미 연수라 석회질 강화형(라임스케일)의 이득이 작습니다.</p></div>
        <div><b>3</b><p><strong>상품명의 용량 ≠ 마실 수 있는 양.</strong> 3.6L 저그의 정수 보관량은 2.3L입니다. 비교는 정수 보관량으로.</p></div>
      </div>`;
  }

  /* ───────── 구역: 한국 vs 유럽 ───────── */
  function renderKorea() {
    const el = $('korea'); if (!el) return;
    const max = 420;
    const rows = D.hardness.map((h) => `
      <div class="hard-row${h.kr ? ' is-kr' : ''}">
        <span class="hard-city">${h.city}</span>
        <span class="hard-track">
          <span class="hard-zone soft" style="width:${(60 / max) * 100}%"></span>
          <span class="hard-zone mid" style="left:${(60 / max) * 100}%;width:${(60 / max) * 100}%"></span>
          <span class="hard-range" style="left:${(h.lo / max) * 100}%;width:${Math.max(1.6, ((h.hi - h.lo) / max) * 100)}%"></span>
        </span>
        <span class="hard-val">${h.lo === h.hi ? h.lo : h.lo + '~' + h.hi}<small>mg/L</small></span>
      </div>`).join('');
    el.innerHTML = `
      <div class="split">
        <div class="card">
          <h3>수돗물 경도(석회질) 비교</h3>
          <p class="muted">CaCO₃ 환산 mg/L. 막대가 길수록 물때가 잘 생기는 '센물'입니다.</p>
          <div class="hard-chart">${rows}
            <div class="hard-axis"><span>0</span><span>연수 ~60</span><span>~120</span><span>센물 →</span><span>${max}</span></div>
          </div>
          <p class="fine">서울은 서울시 소개값(측정 시점 원문 확인 불가), 유럽은 공개 자료의 °dH 환산 추정 범위입니다.</p>
        </div>
        <div class="card compare-kr">
          <h3>그래서 한국에서는 효과가 이렇게 달라집니다</h3>
          <table class="mini">
            <thead><tr><th></th><th>한국</th><th>유럽(독일·영국)</th></tr></thead>
            <tbody>
              <tr><th>수원</th><td>강·댐(지표수)</td><td>석회암 지하수 비중 큼</td></tr>
              <tr><th>물의 성질</th><td><b>연수</b> · 미네랄 약 41mg/L</td><td><b>경수~매우 경수</b></td></tr>
              <tr><th>잔류염소</th><td>수도꼭지까지 유지(0.1~0.3mg/L 관리)</td><td>최소화하거나 쓰지 않는 곳 많음</td></tr>
              <tr><th>주된 불만</th><td>염소 냄새 · 여름 흙냄새 · 녹물</td><td>석회 물때 · 커피머신 고장</td></tr>
              <tr><th>브리타 핵심 가치</th><td class="good">활성탄의 <b>염소 냄새 제거</b></td><td>이온교환의 <b>석회질 제거</b></td></tr>
              <tr><th>라임스케일 필터</th><td class="bad">대부분 불필요</td><td>유용</td></tr>
            </tbody>
          </table>
          <div class="note">한국에서 브리타의 가치 = <b>석회질 제거(유럽의 강점) 작음</b> + <b>염소 냄새 제거 크게 체감</b>. 대신 염소가 빠진 물은 세균을 막지 못하므로 <b>냉장 보관·24시간 내 음용</b>이 필수입니다.</div>
        </div>
      </div>
      <div class="card stages">
        <div class="stages-media">${img('filter-structure.webp', '브리타 저그의 분해 구조: 뚜껑, 필터, 깔때기, 물통')}</div>
        <div>
          <h3>필터 하나 안의 4단계 — 무엇을 하고, 무엇을 못 하나</h3>
          <ol class="stage-list">${R.stages.map(([n, t, d, s]) => `<li><b>${n}. ${t}</b><span>${d}</span><em>비유: ${s}</em></li>`).join('')}</ol>
          <p class="note warn">이 장치는 <b>흡착·교환</b> 장치이지 <b>살균</b> 장치가 아닙니다. 세균(약 1μm)·바이러스는 30μm 거름망을 그대로 통과합니다.</p>
        </div>
      </div>`;
  }

  /* ───────── 구역: 본체 7종 ───────── */
  function renderModels() {
    const el = $('models'); if (!el) return;
    const list = [...D.models].sort((a, b) => fitScore[a.id].rank - fitScore[b.id].rank);
    const perL = D.models.map((m) => {
      const b = baseSku(m.id);
      let v = b ? price(b) / m.filtered : null; let est = false;
      if (!b && m.id === 'B04') { v = price(D.skus.find((s) => s.id === 'SKU010')) / m.filtered; est = true; }
      if (!b && m.id === 'B07') { const y = D.skus.find((s) => s.id === 'SKU027'); v = (price(y) - 12 * marginalsAvg()) / m.filtered; est = true; }
      return { id: m.id, label: `${m.name} ${m.size}${est ? ' *' : ''}`, value: v, hi: m.id === 'B06' };
    }).sort((a, b) => a.value - b.value);

    el.innerHTML = `
      <div class="model-grid">${list.map((m) => modelCard(m)).join('')}</div>
      <div class="split">
        <div class="card">
          <h3>정수 1L 담는 데 드는 본체값</h3>
          <p class="muted">본체+필터 1개 구성 ${modeLabel()} ÷ 정수 보관량. 짧을수록 같은 돈에 많이 담깁니다.</p>
          ${bars(perL, { fmt: (v) => won(v) + '/L' })}
          <p class="fine">* 리미티드는 포함 필터 수 미확정 구성 가격, 플로우는 13개 구성에서 추가 필터 12개(평균 한계비용)를 뺀 추정치입니다.</p>
        </div>
        <div class="card">
          <h3>2인 가구 하루 몇 번 채우나</h3>
          <p class="muted">하루 정수 사용량 <b class="js-daily">${num(state.daily, 1)}L</b> 기준 (계산기에서 변경)</p>
          ${bars(D.models.map((m) => ({ id: m.id, label: `${m.name} ${m.size}`, value: state.daily / m.filtered, hi: m.id === 'B06' }))
            .sort((a, b) => a.value - b.value), { fmt: (v) => num(v, 1) + '회/일' })}
          <p class="fine">플로우는 한 번에 5.2L를 담지만 2인 가구는 24시간 안에 다 마시기 어렵습니다(박사 의견).</p>
        </div>
      </div>
      <div class="card">
        <h3>7개 본체 사양 한눈에</h3>
        <div class="table-box"><table class="spec">
          <thead><tr><th>본체</th><th>총용량</th><th>정수 보관량</th><th>교체 알림</th><th>소재</th><th>크기(가로×깊이×높이 cm)</th><th>색상</th><th>필터 1개 구성</th></tr></thead>
          <tbody>${D.models.map((m) => { const b = baseSku(m.id); return `<tr${m.id === 'B06' ? ' class="is-hi"' : ''}>
            <th>${m.name} ${m.size}</th><td>${m.total}L</td><td><b>${m.filtered}L</b></td><td>${m.timer}</td><td>${m.material}</td><td>${m.dims}</td><td>${m.colors.join(' · ')}</td><td>${b ? won(price(b)) : '<span class="muted">화면에 없음</span>'}</td></tr>`; }).join('')}</tbody>
        </table></div>
        <div class="score-legend"><b>적합도 기준</b> 가성비 = 정수 1L당 본체값 · 2인 용량 = 하루 3L에 1~2회 보충이 가장 좋음(너무 작거나 커도 감점) · 편의 = 한 손 뚜껑·출수구 덮개·스마트라이트 · 소재 = 유리·세척 편의. 편집 판단이며 실측 성능 점수가 아닙니다.</div>
      </div>`;
  }
  function marginalsAvg() {
    const m = marginals().filter((x) => x.sku.total === 13);
    return m.reduce((s, x) => s + x.unit, 0) / m.length;
  }
  function modelCard(m) {
    const f = fitScore[m.id]; const b = baseSku(m.id); const opts = skusOf(m.id).sort((x, y) => (x.total ?? 99) - (y.total ?? 99));
    return `<article class="model${f.rank <= 2 ? ' is-top' : ''}" id="model-${m.id}">
      <div class="model-media">${img(m.img, `브리타 ${m.name} ${m.size} 제품 사진`)}<span class="rank">${f.rank}</span><span class="tag">${f.tag}</span></div>
      <div class="model-body">
        <h4>${m.name} <span>${m.size}</span></h4>
        <p class="one">${m.one}</p>
        <div class="cap"><span class="cap-total" style="width:${(m.total / 8.2) * 100}%"></span><span class="cap-fill" style="width:${(m.filtered / 8.2) * 100}%"></span></div>
        <p class="cap-text">정수 보관 <b>${m.filtered}L</b> / 총 ${m.total}L · ${m.timer}</p>
        <ul class="scores">${scoreKeys.map(([k, t]) => `<li><span>${t}</span>${dots(f[k])}</li>`).join('')}</ul>
        <ul class="pc"><li class="pro">${m.pros.join('</li><li class="pro">')}</li><li class="con">${m.cons.join('</li><li class="con">')}</li></ul>
        <p class="fit">👫 ${m.fit}</p>
        <div class="opts">${opts.map((s) => `<span class="opt"><b>${s.total == null ? '필터 ?' : '필터 ' + s.total}</b>${s.color ? ' ' + s.color : ''} · ${won(price(s))}</span>`).join('')}</div>
        <div class="model-actions">${extLink(m.naver, '네이버 공식 ↗')}${extLink(m.official, '공식 사양', 'btn ghost')}</div>
      </div>
    </article>`;
  }

  /* ───────── 구역: 필터 ───────── */
  function renderFilters() {
    const el = $('filters'); if (!el) return;
    const packs = filterPacks();
    const best = packs[0];
    const mg = marginals();
    el.innerHTML = `
      <div class="filter-duo">${D.filters.map((f) => `
        <article class="card filter-card ${f.id === 'F-PURE' ? 'is-rec' : ''}">
          ${img(f.img, f.name + ' 상자 사진')}
          <div>
            <span class="eyebrow">${f.en}</span>
            <h3>${f.name}</h3>
            <p>${f.purpose}</p>
            <ul class="checks">${f.does.map((d) => `<li>${d}</li>`).join('')}</ul>
            <div class="verdict-line">${f.id === 'F-PURE' ? '<span class="verdict v-big">한국 기본 추천</span> 서울 등 광역상수도 가정' : '<span class="verdict v-lim">조건부</span> 경도 150mg/L 이상 지역·에스프레소 머신 요구 시'}</div>
            <div class="model-actions">${extLink(f.naver, '네이버 공식 ↗')}${extLink(f.official, '공식 사양', 'btn ghost')}</div>
          </div>
        </article>`).join('')}</div>
      <div class="card note-card">
        <h3>광고 문구, 정확히 읽기</h3>
        <dl class="ad-read">
          <div><dt>"라임스케일 50% 강화"</dt><dd>퓨어 퍼포먼스 대비 <b>석회질 감소 성능</b>만의 제조사 수치. 모든 오염물질 제거가 50% 좋다는 뜻이 아닙니다.</dd></div>
          <div><dt>"4배"</dt><dd><b>구형 막스트라 플러스</b>와 비교한 문구. 측정 방법은 공개되지 않았습니다.</dd></div>
          <div><dt>"30μm"</dt><dd>0.03mm 입자 거름. 세균·바이러스·모든 미세플라스틱 100% 제거를 뜻하지 않습니다.</dd></div>
          <div><dt>"4단계 필터"</dt><dd>필터 1개 안의 구조입니다. 필터 4개를 끼우는 것이 아닙니다.</dd></div>
        </dl>
      </div>
      <div class="split">
        <div class="card">
          <h3>필터만 살 때 — 개당 가격</h3>
          <p class="muted">${modeLabel()} ÷ 필터 수. 혼합 묶음은 두 종류 평균 단가입니다.</p>
          ${bars(packs.map((p) => ({ id: p.id, label: `${p.name}${p.status !== '확인' ? ' †' : ''}`, value: p.unit, cls: 'c-' + p.type })), { hi: best.id, max: Math.max(...packs.map((p) => p.unit)) })}
          <p class="note"><b>최저가: ${best.name}</b> 개당 ${won(best.unit)}. <b>16개 대용량(8입+8입)이 8개 묶음보다 개당 더 비쌉니다.</b> "많이 살수록 싸다"가 여기선 틀립니다.</p>
          <p class="fine">† 상품명 후반이 잘려 상자 사진으로 수량을 판독한 추정값입니다.</p>
        </div>
        <div class="card">
          <h3>본체 묶음에 붙은 필터는 더 쌀까?</h3>
          <p class="muted">(큰 묶음 − 같은 본체·색상의 필터 1개 구성) ÷ 추가 필터 수</p>
          ${bars(mg.map((x) => ({ label: `${x.model.name} 총 ${x.sku.total}개`, value: x.unit, hi: x.unit < best.unit })), { max: Math.max(best.unit, ...mg.map((x) => x.unit)) })}
          <div class="ref-line">단독 최저가 기준선: <b>${won(best.unit)}</b></div>
          <p class="note">본체를 살 때 <b>총 5입 구성</b>으로 사면 추가 필터가 단독 최저가보다 쌉니다. 단, 본체 동봉 필터는 퓨어/라임스케일 구분이 화면에서 확인되지 않았습니다.</p>
        </div>
      </div>`;
  }

  /* ───────── 구역: 계산기 ───────── */
  function renderCalc() {
    const el = $('calc'); if (!el) return;
    el.innerHTML = `
      <div class="calc">
        <div class="card calc-in">
          <h3>우리 집 조건</h3>
          <label class="field"><span>2인 하루 정수 사용량 <b id="dailyOut">${num(state.daily, 1)}L</b></span>
            <input type="range" id="dailyIn" min="1" max="8" step="0.5" value="${state.daily}">
            <small>음용만 ≈ 2~3L · 커피·차 포함 ≈ 3~4L · 조리까지 ≈ 5L 이상</small></label>
          <div class="field"><span>필터 교체 기준</span>
            <div class="seg" role="group" aria-label="교체 기준">
              <button data-rule="28" aria-pressed="${state.rule === 28}">4주 (권장)</button>
              <button data-rule="56" aria-pressed="${state.rule === 56}">최대 8주 (저사용 예외)</button>
            </div><small>박사 의견: 물을 적게 써도 위생상 4주 교체를 권장</small></div>
          <label class="field"><span>생수 2L 한 병 가격 <b id="bottleOut">${won(state.bottle)}</b></span>
            <input type="range" id="bottleIn" min="300" max="1500" step="50" value="${state.bottle}">
            <small>가정값: 저가 묶음 ≈ 600원 · 브랜드 묶음 ≈ 1,000원</small></label>
          <div class="field"><span>가격 기준</span>
            <div class="seg" role="group" aria-label="가격 기준">
              <button data-mode="member" aria-pressed="${state.mode === 'member'}">멤버십쿠폰가</button>
              <button data-mode="sale" aria-pressed="${state.mode === 'sale'}">화면 판매가</button>
            </div></div>
        </div>
        <div class="card calc-out" id="calcOut"></div>
      </div>
      <div class="split">
        <div class="card"><h3>5년 누적 비용 — 브리타 vs 생수</h3><div id="lineChart"></div></div>
        <div class="card"><h3>첫해 13개 필터, 어떻게 사야 쌀까</h3><div id="buyPlans"></div></div>
      </div>`;
    $('dailyIn').addEventListener('input', (e) => { state.daily = +e.target.value; store.set('daily', state.daily); refreshCalc(); });
    $('bottleIn').addEventListener('input', (e) => { state.bottle = +e.target.value; store.set('bottle', state.bottle); refreshCalc(); });
    el.querySelectorAll('[data-rule]').forEach((b) => b.addEventListener('click', () => { state.rule = +b.dataset.rule; store.set('rule', state.rule); renderCalc(); refreshCalc(); }));
    el.querySelectorAll('[data-mode]').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));
    refreshCalc();
  }
  function refreshCalc() {
    const a = annual();
    $('dailyOut').textContent = num(state.daily, 1) + 'L';
    $('bottleOut').textContent = won(state.bottle);
    document.querySelectorAll('.js-daily').forEach((n) => { n.textContent = num(state.daily, 1) + 'L'; });
    const max = Math.max(a.bottled, a.brita);
    $('calcOut').innerHTML = `
      <h3>계산 결과</h3>
      <div class="out-big"><small>생수 대신 브리타로 연간</small><b class="${a.save > 0 ? 'good' : 'bad'}">${a.save > 0 ? won(a.save) + ' 절약' : won(-a.save) + ' 더 듦'}</b></div>
      ${bars([
        { label: '생수', value: a.bottled, cls: 'c-bottle' },
        { label: '브리타 필터', value: a.brita, cls: 'c-pure', hi: true }
      ], { max })}
      <ul class="out-list">
        <li><span>필터 1개 수명</span><b>${num(a.life, 0)}일</b><em>${a.life < state.rule ? '150L 먼저 도달' : `${state.rule / 7}주 기준 먼저 도달`}</em></li>
        <li><span>연간 필터</span><b>${a.perYear}개</b><em>개당 ${won(a.unit)}</em></li>
        <li><span>정수 1L당</span><b>${num(a.perL, 0)}원</b><em>생수 ${num(state.bottle / 2)}원/L</em></li>
        <li><span>줄어드는 페트병</span><b>${num(a.bottles, 0)}병/년</b><em>2L 기준</em></li>
      </ul>
      <p class="fine">수돗물 요금(연 수천 원 이하 추정)은 계산에서 뺐습니다. 생수 가격은 가정값입니다.</p>`;
    renderLine(a); renderPlans(); renderSummary();
  }
  function renderLine(a) {
    const W = 560, H = 240, P = { l: 56, r: 16, t: 14, b: 30 };
    const body = price(baseSku('B06'));
    const yrs = [0, 1, 2, 3, 4, 5];
    const brita = yrs.map((y) => body + a.brita * y);
    const bottle = yrs.map((y) => a.bottled * y);
    const max = Math.max(...brita, ...bottle) * 1.05;
    const x = (i) => P.l + (i / 5) * (W - P.l - P.r);
    const y = (v) => H - P.b - (v / max) * (H - P.t - P.b);
    const path = (arr) => arr.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join('');
    const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => max * t);
    $('lineChart').innerHTML = `<svg viewBox="0 0 ${W} ${H}" class="line-svg" role="img" aria-label="5년 누적 비용 선 그래프">
      ${ticks.map((t) => `<line x1="${P.l}" x2="${W - P.r}" y1="${y(t)}" y2="${y(t)}" class="grid"/><text x="${P.l - 8}" y="${y(t) + 4}" class="axis" text-anchor="end">${num(t / 10000, 0)}만</text>`).join('')}
      ${yrs.map((v, i) => `<text x="${x(i)}" y="${H - 8}" class="axis" text-anchor="middle">${i ? i + '년' : '구입'}</text>`).join('')}
      <path d="${path(bottle)}" class="ln ln-bottle"/><path d="${path(brita)}" class="ln ln-brita"/>
      ${bottle.map((v, i) => `<circle cx="${x(i)}" cy="${y(v)}" r="3.5" class="pt-bottle"/>`).join('')}
      ${brita.map((v, i) => `<circle cx="${x(i)}" cy="${y(v)}" r="3.5" class="pt-brita"/>`).join('')}
      <text x="${x(5) - 4}" y="${y(bottle[5]) - 8}" class="lbl lbl-bottle" text-anchor="end">생수 ${num(bottle[5] / 10000, 0)}만원</text>
      <text x="${x(5) - 4}" y="${y(brita[5]) - 8}" class="lbl lbl-brita" text-anchor="end">브리타 ${num(brita[5] / 10000, 0)}만원</text>
    </svg>
    <p class="fine">브리타 = 스타일에센셜 XL 본체(필터 1개 구성 ${won(body)}) + 해마다 필터 ${a.perYear}개 × ${won(a.unit)}.</p>`;
  }
  function renderPlans() {
    const el = $('buyPlans'); if (!el) return;
    const xl1 = D.skus.find((s) => s.id === 'SKU016'); const xl5 = D.skus.find((s) => s.id === 'SKU019'); const xl13 = D.skus.find((s) => s.id === 'SKU026');
    const p12 = cheapestPure(12); const p8 = cheapestPure(8);
    const comboTxt = (c) => Object.entries(c).map(([id, n]) => `${D.skus.find((s) => s.id === id).name}${n > 1 ? ' ×' + n : ''}`).join(' + ');
    const plans = [
      { t: '1년 구성팩 한 번에', d: `${xl13.name}`, v: price(xl13) },
      { t: '총 5입 + 필터 8개 보충', d: `${xl5.name} 5입 + ${comboTxt(p8.combo)}`, v: price(xl5) + p8.cost },
      { t: '필터 1개 + 필터 12개 따로', d: `${xl1.name} + ${comboTxt(p12.combo)}`, v: price(xl1) + p12.cost }
    ].sort((a, b) => a.v - b.v);
    el.innerHTML = `${bars(plans.map((p, i) => ({ label: p.t, value: p.v, hi: i === 0 })), { max: plans[plans.length - 1].v, min: plans[0].v * 0.9 })}
      <ol class="plan-list">${plans.map((p, i) => `<li><b>${i + 1}. ${p.t}</b> — ${won(p.v)}<br><small>${p.d}</small></li>`).join('')}</ol>
      <p class="note">1년팩이 가장 싸지만, 처음 쓰는 부부라면 <b>총 5입으로 4~5개월 써 본 뒤 보충</b>하는 방법도 차이가 ${won(plans.find((p) => p.t.startsWith('총 5입')).v - plans[0].v)} 정도라 위험이 작습니다(박사 권고).</p>`;
  }

  /* ───────── 구역: 박사 검토 ───────── */
  function renderReview() {
    const el = $('review'); if (!el) return;
    const count = {}; R.items.forEach((i) => { count[i.v] = (count[i.v] || 0) + 1; });
    const order = ['big', 'yes', 'rule', 'lim', 'no', 'warn', 'na'];
    el.innerHTML = `
      <div class="doctor">
        <div class="doctor-badge" aria-hidden="true">🔬</div>
        <div>
          <span class="eyebrow">독립 검토 · 수질공학 박사 관점 (AI 검토자)</span>
          <blockquote>${R.verdict}</blockquote>
          <p class="fine">별도 Claude 인스턴스가 공개 자료·문헌·제조사 안내로 작성한 검토입니다. 실제 수질 시험을 하지 않았으며, 확인하지 못한 수치는 '추정' 또는 '확인 불가'로 표시했습니다.</p>
        </div>
      </div>
      <div class="card">
        <h3>42개 항목 판정 분포</h3>
        <div class="stack">${order.filter((k) => count[k]).map((k) => `<span class="${R.verdicts[k][1]}" style="flex:${count[k]}" title="${R.verdicts[k][0]} ${count[k]}개">${count[k]}</span>`).join('')}</div>
        <div class="stack-legend">${order.filter((k) => count[k]).map((k) => `<button class="chip" data-v="${k}">${vBadge(k)} ${count[k]}</button>`).join('')}<button class="chip" data-v="all">전체 보기</button></div>
      </div>
      <div class="card">
        <div class="review-tools"><input type="search" id="reviewQ" placeholder="항목 검색 (예: 분유, 세균, 커피)" aria-label="검토 항목 검색"><span id="reviewCount" class="muted"></span></div>
        <div id="reviewList" class="review-list"></div>
      </div>
      <div class="split">
        <div class="card"><h3>신혼부부 상황별 권고</h3>
          <ul class="scen">${R.scenarios.map(([s, v, c, d]) => `<li class="s-${c}"><b>${v}</b><div><strong>${s}</strong><span>${d}</span></div></li>`).join('')}</ul></div>
        <div class="card doctor-final"><h3>박사의 최종 의견</h3>
          <ol>${R.final.map((l) => `<li>${l}</li>`).join('')}</ol>
          <details><summary>검토에서 확인하지 못한 사항 ${R.unknown.length}개</summary><ul>${R.unknown.map((u) => `<li>${u}</li>`).join('')}</ul></details>
          <details><summary>검토 근거 자료</summary><ul class="refs">${R.refs.map(([t, u]) => `<li><a href="${u}" target="_blank" rel="noopener">${t}</a></li>`).join('')}</ul></details>
        </div>
      </div>`;
    el.querySelectorAll('.chip').forEach((c) => c.addEventListener('click', () => { state.reviewFilter = c.dataset.v; drawReview(); }));
    $('reviewQ').addEventListener('input', drawReview);
    drawReview();
  }
  function drawReview() {
    const q = ($('reviewQ').value || '').trim();
    const rows = R.items.filter((i) => (state.reviewFilter === 'all' || i.v === state.reviewFilter)
      && (!q || (i.item + i.basis + i.say + i.group).includes(q)));
    document.querySelectorAll('#review .chip').forEach((c) => c.classList.toggle('on', c.dataset.v === state.reviewFilter));
    $('reviewCount').textContent = `${rows.length} / ${R.items.length}개`;
    $('reviewList').innerHTML = rows.map((i) => `
      <article class="ri">
        <div class="ri-head"><span class="ri-no">${i.no}</span><span class="ri-group">${i.group}</span><h4>${i.item}</h4>${vBadge(i.v)}</div>
        <p class="ri-basis">${i.basis}</p>
        <p class="ri-say">💬 ${i.say}</p>
      </article>`).join('') || '<p class="muted">조건에 맞는 항목이 없습니다.</p>';
  }

  /* ───────── 구역: 사용법 ───────── */
  function renderCare() {
    const el = $('care'); if (!el) return;
    const steps = [
      ['🧽', '물통·깔때기 세척', '처음 쓰기 전과 주 2~3회.'],
      ['💧', '새 필터 공기 빼기', '차가운 물에 담가 부드럽게 흔든 뒤 장착.'],
      ['🚰', '처음 두 번은 버리기', '세 번째로 정수한 물부터 마십니다.'],
      ['⏱️', '알림 초기화', '메모는 START, 스마트라이트는 버튼을 눌러 초기화.'],
      ['❄️', '냉장 보관', '정수된 물은 냉장고에서 24시간 안에 마십니다.'],
      ['📅', '4주마다 교체', '물을 적게 써도 4주. 2개월 초과 사용 금지.']
    ];
    el.innerHTML = `
      <div class="care-grid">${steps.map(([i, t, d], n) => `<div class="care"><span class="care-i">${i}</span><b>${n + 1}. ${t}</b><p>${d}</p></div>`).join('')}</div>
      <div class="split">
        <div class="card dont"><h3>하지 말아야 할 것</h3><ul>
          <li>뜨거운 물을 넣거나 햇빛 드는 창가에 두기</li>
          <li>지하수·약수·빗물 넣기 — 수돗물 전용입니다</li>
          <li>분유용 물을 끓이지 않고 쓰기 — 70℃ 이상으로 끓입니다</li>
          <li>스마트라이트 초록불을 "물이 깨끗하다"로 믿기 — 시간·사용량 알림일 뿐입니다</li>
          <li>오픈마켓 초저가 필터 — 가품 유통 사례가 보도되었습니다. 공식 스토어에서 삽니다</li>
        </ul></div>
        <div class="card"><h3>공식 이미지로 보는 사용 장면</h3>
          <div class="scene-grid">${img('scene-coffee.webp', '정수한 물로 내린 커피와 차')}${img('scene-kettle.webp', '전기포트에 정수한 물을 쓰는 모습')}${img('smartlight.webp', '스타일에센셜 뚜껑의 스마트라이트 표시등')}${img('style-essential-colours.webp', '스타일에센셜 색상 3종')}</div>
          <p class="fine">이미지 출처: 브리타 한국·호주 공식 사이트. 비교·안내 목적으로 축소해 사용했습니다.</p></div>
      </div>`;
  }

  /* ───────── 구역: 구매처 ───────── */
  function renderBuy() {
    const el = $('buy'); if (!el) return;
    const items = [...D.models.map((m) => ({ name: `${m.name} ${m.size}`, img: m.img, href: m.naver, p: baseSku(m.id) })),
      ...D.filters.map((f) => ({ name: f.name, img: f.img, href: f.naver, p: bestPure() && f.id === 'F-PURE' ? bestPure() : filterPacks().find((x) => x.type === 'lime') }))];
    el.innerHTML = `
      <div class="store-hero card">
        <div><span class="eyebrow">OFFICIAL STORE</span><h3>${D.store.name}</h3><p>${D.store.note} 가격·쿠폰은 수시로 바뀌므로 결제 전에 스토어에서 마지막으로 확인하세요.</p>
          ${extLink(D.store.home, '브랜드스토어 열기 ↗')}</div>
        ${img('filter-both.webp', '막스트라 프로 필터 두 종류')}
      </div>
      <div class="buy-grid">${items.map((i) => `<a class="buy" href="${i.href}" target="_blank" rel="noopener">${img(i.img, i.name)}<b>${i.name}</b><span>${i.p ? won(price(i.p)) + (i.p.kind === 'F' ? ` (${i.p.total}개)` : '') : '13개 구성만'}</span><em>네이버에서 보기 ↗</em></a>`).join('')}</div>
      <p class="fine">링크는 브리타 한국 공식 홈페이지의 구매 버튼이 연결하는 네이버 상품입니다. 이 페이지는 제휴 링크·광고를 쓰지 않습니다. 가격은 ${D.asOf} 첨부 화면의 ${modeLabel()}입니다.</p>`;
  }

  /* ───────── 구역: 데이터 원장 ───────── */
  let ledgerSort = { k: 'id', dir: 1 };
  function renderLedger() {
    const el = $('ledger'); if (!el) return;
    const cols = [['id', '판매 ID'], ['kind', '구분'], ['name', '구성'], ['color', '색상'], ['total', '필터 수'], ['sale', '화면 판매가'], ['member', '멤버십쿠폰가'], ['unit', '필터 1개 환산'], ['status', '판독 상태']];
    const rows = D.skus.map((s) => ({ ...s, unit: s.kind === 'F' && s.total ? price(s) / s.total : null }))
      .sort((a, b) => { const k = ledgerSort.k; const x = a[k] ?? Infinity, y = b[k] ?? Infinity; return (x > y ? 1 : x < y ? -1 : 0) * ledgerSort.dir; });
    el.innerHTML = `<div class="card">
      <div class="table-box"><table class="spec ledger"><thead><tr>${cols.map(([k, t]) => `<th><button data-k="${k}">${t}${ledgerSort.k === k ? (ledgerSort.dir > 0 ? ' ↑' : ' ↓') : ''}</button></th>`).join('')}</tr></thead>
      <tbody>${rows.map((s) => `<tr><td>${s.id}</td><td>${s.kind === 'F' ? '필터' : '본체+필터'}</td><td>${s.name}</td><td>${s.color || ''}</td><td>${s.total ?? '<span class="muted">미확정</span>'}</td><td>${won(s.sale)}</td><td>${won(s.member)}</td><td>${s.unit ? won(s.unit) : ''}</td><td>${s.status}</td></tr>`).join('')}</tbody></table></div>
      <div class="ledger-foot"><button class="btn ghost" id="csvBtn">CSV 내려받기</button><span class="fine">판매 구성 33개 = 본체 포함 24 + 필터 단독 9. 미확정 수량은 빈칸으로 둡니다.</span></div>
      <details><summary>공식 사양 출처 ${D.sources.length}개</summary><ul class="refs">${D.sources.map(([id, t, u]) => `<li>[${id}] <a href="${u}" target="_blank" rel="noopener">${t}</a></li>`).join('')}</ul></details>
    </div>`;
    el.querySelectorAll('th button').forEach((b) => b.addEventListener('click', () => {
      ledgerSort = { k: b.dataset.k, dir: ledgerSort.k === b.dataset.k ? -ledgerSort.dir : 1 }; renderLedger();
    }));
    $('csvBtn').addEventListener('click', () => {
      const head = 'sku_id,kind,model_id,name,color,pure_count,lime_count,total_filter_count,quantity_status,sale_price_krw,member_price_krw';
      const body = D.skus.map((s) => [s.id, s.kind === 'F' ? '필터' : '본체+필터', s.model || '', s.name, s.color || '', s.pure ?? '', s.lime ?? '', s.total ?? '', s.status, s.sale, s.member]
        .map((v) => (/[,"]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : v)).join(','));
      const blob = new Blob(['﻿' + [head, ...body].join('\n')], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `brita-skus-${D.asOf}.csv`; a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    });
  }

  /* ───────── 전체 ───────── */
  function setMode(m) {
    state.mode = m; store.set('mode', m);
    document.querySelectorAll('[data-mode]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === m)));
    renderModels(); renderFilters(); renderBuy(); renderLedger(); refreshCalc();
  }
  function renderAll() {
    renderSummary(); renderKorea(); renderModels(); renderFilters(); renderCalc(); renderReview(); renderCare(); renderBuy(); renderLedger();
    document.querySelectorAll('[data-mode-global]').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.modeGlobal)));
  }
  window.BritaApp = { renderAll, setMode, state };
  renderAll();
})();
