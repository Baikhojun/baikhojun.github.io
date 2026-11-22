/* 예비부부 맞춤 내집마련 강의 — 화면 동작
   - 그래프: 막대·히스토그램·선(SVG). 색은 CSS 변수(--s1…)를 쓴다.
   - 질문 트리: window.CLASS_DATA.tree 로 대화형 질문지를 만든다.
   - 목차: 지금 보는 장을 표시하고 읽은 만큼 막대를 채운다. */
(function () {
  'use strict';
  var D = window.CLASS_DATA || {};
  var NS = 'http://www.w3.org/2000/svg';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function txt(parent, x, y, s, cls, anchor) {
    var t = el('text', { x: x, y: y, 'class': cls || null, 'text-anchor': anchor || null }, parent);
    t.textContent = s; return t;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(v, d) { return (Math.round(v * Math.pow(10, d || 0)) / Math.pow(10, d || 0)).toLocaleString('ko-KR'); }
  function niceMax(v) { if (v <= 0) return 1; var p = Math.pow(10, Math.floor(Math.log10(v))); var m = v / p; return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10) * p; }

  /* 말풍선 */
  var tip = document.createElement('div'); tip.className = 'viz-tip'; tip.setAttribute('role', 'status');
  document.body.appendChild(tip);
  function showTip(e, html) {
    tip.innerHTML = html; tip.classList.add('on');
    var x = (e.touches ? e.touches[0].clientX : e.clientX) + 12, y = (e.touches ? e.touches[0].clientY : e.clientY) + 12;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > innerWidth - 8) x = innerWidth - w - 8;
    if (y + h > innerHeight - 8) y -= h + 24;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { tip.classList.remove('on'); }
  function bindTip(node, html) {
    node.addEventListener('mousemove', function (e) { showTip(e, html); });
    node.addEventListener('mouseleave', hideTip);
    node.addEventListener('touchstart', function (e) { showTip(e, html); }, { passive: true });
    node.setAttribute('tabindex', '0');
    node.addEventListener('focus', function () { var r = node.getBoundingClientRect(); showTip({ clientX: r.left + r.width / 2, clientY: r.top }, html); });
    node.addEventListener('blur', hideTip);
  }
  document.addEventListener('scroll', hideTip, { passive: true });

  function goLinks(g) {
    if (!g) return '';
    var list = typeof g === 'string' ? [{ href: g, text: '이 길을 자세히 보기' }] : g;
    return '<p class="res__go">' + list.map(function (x) { return '<a href="' + esc(x.href) + '">' + esc(x.text) + ' →</a>'; }).join('') + '</p>';
  }

  /* 좁은 화면에서는 좌표 폭을 줄여 글자를 키운다 */
  function chartW(host) { var w = host.clientWidth || 640; return w < 520 ? Math.max(300, Math.round(w)) : 640; }

  /* 세로 막대(범주) — spec: {labels, series:[{name, values, color}], unit, max, note[], highlight} */
  function barChart(host, spec) {
    var W = chartW(host), H = spec.height || 300, L = 44, R = 12, T = 18, B = 54;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'viz', role: 'img', 'aria-label': spec.title || '' });
    var all = []; spec.series.forEach(function (s) { all = all.concat(s.values); });
    var max = spec.max || niceMax(Math.max.apply(null, all));
    var pw = W - L - R, ph = H - T - B, n = spec.labels.length, sn = spec.series.length;
    var gw = pw / n, bw = Math.min(40, (gw - 14) / sn);
    for (var i = 0; i <= 4; i++) {
      var gy = T + ph - ph * i / 4;
      el('line', { x1: L, x2: W - R, y1: gy, y2: gy, 'class': i ? 'gridline' : 'axis' }, svg);
      txt(svg, L - 6, gy + 4, fmt(max * i / 4, spec.dec || 0), 't-muted', 'end');
    }
    if (spec.refLine != null) {
      var ry = T + ph - ph * spec.refLine.value / max;
      el('line', { x1: L, x2: W - R, y1: ry, y2: ry, stroke: 'var(--warm)', 'stroke-width': 2, 'stroke-dasharray': '5 4' }, svg);
      txt(svg, W - R, ry - 6, spec.refLine.label, 't-strong', 'end');
    }
    spec.labels.forEach(function (lab, i) {
      var gx = L + gw * i + (gw - bw * sn - 2 * (sn - 1)) / 2;
      spec.series.forEach(function (s, j) {
        var v = s.values[i]; if (v == null) return;
        var h = Math.max(1, ph * v / max), x = gx + j * (bw + 2), y = T + ph - h;
        var r = Math.min(4, bw / 2);
        var p = el('path', { d: 'M' + x + ',' + (T + ph) + 'V' + (y + r) + 'q0,-' + r + ' ' + r + ',-' + r + 'h' + (bw - 2 * r) + 'q' + r + ',0 ' + r + ',' + r + 'V' + (T + ph) + 'Z', fill: s.colors ? s.colors[i] : s.color }, svg);
        bindTip(p, '<b>' + esc(lab) + '</b><br>' + esc(s.name) + ': ' + fmt(v, spec.tipDec != null ? spec.tipDec : (spec.dec || 0)) + esc(spec.unit || ''));
        if (spec.valueLabels) txt(svg, x + bw / 2, y - 6, fmt(v, spec.dec || 0), 't-strong', 'middle');
      });
      var lines = String(lab).split('\n');
      lines.forEach(function (ln, k) { txt(svg, L + gw * i + gw / 2, T + ph + 18 + k * 15, ln, k ? 't-muted' : null, 'middle'); });
    });
    host.appendChild(svg);
    if (sn > 1) legend(host, spec.series);
  }

  /* 가로 막대 — spec: {rows:[{label, value, color, note}], unit, max} */
  function hbar(host, spec) {
    var W = chartW(host), narrow = W < 520;
    var rowH = narrow ? 46 : 34, L = narrow ? 0 : (spec.labelW || 150), R = narrow ? 56 : 70, T = 8;
    var H = T + rowH * spec.rows.length + 22;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'viz', role: 'img', 'aria-label': spec.title || '' });
    var max = spec.max || niceMax(Math.max.apply(null, spec.rows.map(function (r) { return r.value; })));
    var pw = W - L - R;
    if (spec.refLine) {
      var rx = L + pw * spec.refLine.value / max;
      el('line', { x1: rx, x2: rx, y1: 2, y2: H - 18, stroke: 'var(--warm)', 'stroke-width': 2, 'stroke-dasharray': '5 4' }, svg);
      txt(svg, rx, H - 4, spec.refLine.label, 't-strong', 'middle');
    }
    spec.rows.forEach(function (r, i) {
      var y = T + i * rowH, w = Math.max(2, pw * r.value / max);
      var by = narrow ? y + 20 : y + 7;
      if (narrow) txt(svg, 0, y + 13, r.label, r.strong ? 't-strong' : null, 'start');
      else txt(svg, L - 10, y + 21, r.label, r.strong ? 't-strong' : null, 'end');
      var p = el('rect', { x: L, y: by, width: w, height: narrow ? 18 : 20, rx: 4, fill: r.color || 'var(--s1)' }, svg);
      bindTip(p, '<b>' + esc(r.label) + '</b><br>' + fmt(r.value, spec.dec || 0) + esc(spec.unit || '') + (r.note ? '<br>' + esc(r.note) : ''));
      txt(svg, L + w + 6, by + 14, fmt(r.value, spec.dec || 0) + (spec.unit || ''), 't-strong');
    });
    host.appendChild(svg);
  }

  /* 선 그래프 — spec: {x:[labels], series:[{name, values, color, dash}], unit, max, yLabel} */
  function lineChart(host, spec) {
    var W = chartW(host), H = spec.height || 300, L = 46, R = 16, T = 18, B = 46;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'viz', role: 'img', 'aria-label': spec.title || '' });
    var all = []; spec.series.forEach(function (s) { all = all.concat(s.values.filter(function (v) { return v != null; })); });
    var max = spec.max || niceMax(Math.max.apply(null, all));
    var pw = W - L - R, ph = H - T - B, n = spec.x.length;
    var X = function (i) { return L + (n === 1 ? pw / 2 : pw * i / (n - 1)); }, Y = function (v) { return T + ph - ph * v / max; };
    for (var i = 0; i <= 4; i++) {
      var gy = Y(max * i / 4);
      el('line', { x1: L, x2: W - R, y1: gy, y2: gy, 'class': i ? 'gridline' : 'axis' }, svg);
      txt(svg, L - 6, gy + 4, fmt(max * i / 4, spec.dec || 0) + (i === 4 && spec.unitShort ? spec.unitShort : ''), 't-muted', 'end');
    }
    var step = Math.ceil(n / (spec.xTicks || (W < 640 ? 4 : 7)));
    spec.x.forEach(function (lab, i) { if (i % step === 0 || i === n - 1) txt(svg, X(i), H - B + 20, lab, 't-muted', 'middle'); });
    spec.series.forEach(function (s) {
      var d = ''; s.values.forEach(function (v, i) { if (v == null) return; d += (d ? 'L' : 'M') + X(i) + ',' + Y(v); });
      el('path', { d: d, fill: 'none', stroke: s.color, 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-dasharray': s.dash || null }, svg);
      s.values.forEach(function (v, i) {
        if (v == null) return;
        if (s.marks !== false) el('circle', { cx: X(i), cy: Y(v), r: 4, fill: s.color, stroke: 'var(--paper)', 'stroke-width': 2 }, svg);
      });
      if (s.endLabel !== false) { var li = s.values.length - 1; while (li > 0 && s.values[li] == null) li--; }
    });
    /* 세로 십자선 */
    var hair = el('line', { y1: T, y2: T + ph, stroke: 'var(--ink-3)', 'stroke-width': 1, opacity: 0 }, svg);
    var hit = el('rect', { x: L, y: T, width: pw, height: ph, fill: 'transparent' }, svg);
    function move(e) {
      var pt = svg.createSVGPoint(); var src = e.touches ? e.touches[0] : e; pt.x = src.clientX; pt.y = src.clientY;
      var p = pt.matrixTransform(svg.getScreenCTM().inverse());
      var i = Math.round((p.x - L) / pw * (n - 1)); i = Math.max(0, Math.min(n - 1, i));
      hair.setAttribute('x1', X(i)); hair.setAttribute('x2', X(i)); hair.setAttribute('opacity', 1);
      var h = '<b>' + esc(spec.x[i]) + '</b>';
      spec.series.forEach(function (s) { if (s.values[i] != null) h += '<br><span style="color:' + s.color + '">●</span> ' + esc(s.name) + ': ' + fmt(s.values[i], spec.dec || 1) + esc(spec.unit || ''); });
      showTip(src, h);
    }
    hit.addEventListener('mousemove', move); hit.addEventListener('touchmove', move, { passive: true }); hit.addEventListener('touchstart', move, { passive: true });
    hit.addEventListener('mouseleave', function () { hair.setAttribute('opacity', 0); hideTip(); });
    if (spec.annotations) spec.annotations.forEach(function (a) {
      var ax = X(a.i), ay = Y(a.v);
      el('circle', { cx: ax, cy: ay, r: 7, fill: 'none', stroke: 'var(--warm)', 'stroke-width': 2 }, svg);
      txt(svg, ax + (a.dx || 10), ay + (a.dy || -12), a.text, 't-strong', a.anchor || 'start');
    });
    host.appendChild(svg);
    if (spec.series.length > 1) legend(host, spec.series);
  }

  function legend(host, series) {
    var lg = document.createElement('div'); lg.className = 'legend';
    lg.innerHTML = series.map(function (s) { return '<span><i style="background:' + s.color + '"></i>' + esc(s.name) + '</span>'; }).join('');
    host.insertBefore(lg, host.firstChild);
  }

  /* 차트 자리 채우기: <div data-chart="키"> */
  var CH = D.charts || {};
  $$('[data-chart]').forEach(function (host) {
    var spec = CH[host.getAttribute('data-chart')]; if (!spec) return;
    if (spec.type === 'bar') barChart(host, spec);
    else if (spec.type === 'hbar') hbar(host, spec);
    else if (spec.type === 'line') lineChart(host, spec);
  });

  /* ── 질문 트리 ── */
  /* 형식: {start, nodes:[{id,q,why,options:[{label,short,next,sets}]}], cards:[{id,title,oneLine,summary3,actions:[{date,text}],notFor,go}],
     cardRules:[{if,unless,card}], addonRules:[{id,if,title,text}]}. next: 노드 id | 'card:<id>' | '@result' */
  var T = D.tree, qtHost = $('#qt');
  function ruleMatch(cond, tags) {
    for (var k in cond) { if (!(k in tags) || cond[k].indexOf(tags[k]) < 0) return false; }
    return true;
  }
  if (T && qtHost) {
    var nodeById = {}, cardById = {};
    T.nodes.forEach(function (n) { nodeById[n.id] = n; });
    T.cards.forEach(function (c) { cardById[c.id] = c; });
    var stepsBox = $('.qt__steps', qtHost), resBox = $('.qt__result', qtHost), meter = $('.qt__meter', qtHost);
    var answers = {};
    var total = T.nodes.length;
    function render(focusLast) {
      stepsBox.innerHTML = '';
      var id = T.start, tags = {}, path = [], guard = 0, cardId = null, done = false;
      while (guard++ < 40) {
        var node = nodeById[id]; if (!node) break;
        var div = document.createElement('div'); div.className = 'q';
        var answered = answers[id] != null;
        div.innerHTML = '<div class="q__no">질문 ' + (path.length + 1) + '</div><div class="q__t">' + esc(node.q) + '</div>' + (node.why ? '<p class="q__why">' + esc(node.why) + '</p>' : '') + '<div class="q__opts" role="group"></div>';
        var opts = $('.q__opts', div);
        node.options.forEach(function (o, k) {
          var b = document.createElement('button'); b.type = 'button'; b.textContent = o.label;
          b.setAttribute('aria-pressed', answers[id] === k ? 'true' : 'false');
          b.addEventListener('click', (function (nid, kk) { return function () {
            // 이 질문 뒤의 답은 갈래가 바뀔 수 있으므로 지운다
            var order = []; var cur = T.start, g = 0; while (nodeById[cur] && g++ < 40) { order.push(cur); if (answers[cur] == null) break; cur = nodeById[cur].options[answers[cur]].next; }
            var idx = order.indexOf(nid); order.slice(idx + 1).forEach(function (a) { delete answers[a]; });
            answers[nid] = kk; render(true);
          }; })(id, k));
          opts.appendChild(b);
        });
        stepsBox.appendChild(div);
        if (!answered) break;
        var o = node.options[answers[id]];
        path.push(o.short || o.label);
        if (o.sets) for (var t in o.sets) tags[t] = o.sets[t];
        if (o.next.indexOf('card:') === 0) { cardId = o.next.slice(5); done = true; break; }
        if (o.next === '@result') {
          for (var r = 0; r < T.cardRules.length; r++) {
            var rule = T.cardRules[r];
            if (ruleMatch(rule.if || {}, tags) && !(rule.unless && ruleMatch(rule.unless, tags))) { cardId = rule.card; break; }
          }
          done = true; break;
        }
        id = o.next;
      }
      if (meter) meter.style.width = (done ? 100 : Math.round(path.length / total * 100)) + '%';
      if (focusLast) {
        var last = done ? resBox : stepsBox.lastElementChild;
        if (last && matchMedia('(max-width: 899px)').matches) setTimeout(function () { last.scrollIntoView({ behavior: 'smooth', block: done ? 'start' : 'center' }); }, 30);
        window.__qtFocus = done ? 'res' : 'q';
      }
      var c = cardId && cardById[cardId];
      if (!c) {
        resBox.innerHTML = '<div class="card res"><div class="chip chip--key">답하는 중 · ' + path.length + ' / ' + total + '</div><div class="res__title">질문에 답하면 두 사람에게 맞는 길이 여기에 나타납니다</div><p class="cap">답은 이 화면 안에서만 쓰이고 어디에도 보내지 않습니다.</p></div>';
        if (window.__qtFocus === 'q') { var nb = $('.q:last-child .q__opts button', stepsBox); if (nb) nb.focus({ preventScroll: true }); window.__qtFocus = null; }
        return;
      }
      var addons = (T.addonRules || []).filter(function (a) { return ruleMatch(a.if || {}, tags) && !(a.unless && ruleMatch(a.unless, tags)); });
      resBox.innerHTML = '<div class="card res" tabindex="-1"><div class="chip chip--good">두 사람의 길</div><div class="res__title">' + esc(c.title) + '</div>' +
        (c.oneLine ? '<p style="margin:0 0 10px;color:var(--ink-2)">' + esc(c.oneLine) + '</p>' : '') +
        '<ul class="three">' + c.summary3.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ul>' +
        '<h3 class="res__h">지금부터 할 일</h3><ol class="res__acts">' + c.actions.map(function (a) { return '<li>' + (a.date ? '<b class="num">' + esc(a.date) + '</b> ' : '') + esc(a.text || a) + '</li>'; }).join('') + '</ol>' +
        (addons.length ? '<h3 class="res__h">두 분 답에 따라 덧붙이는 것</h3><div class="res__adds">' + addons.map(function (a) { return '<details class="add"><summary>' + esc(a.title) + '</summary><p>' + esc(a.text) + '</p></details>'; }).join('') + '</div>' : '') +
        (c.notFor ? '<p class="cap"><b>이런 경우엔 맞지 않습니다.</b> ' + esc(c.notFor) + '</p>' : '') +
        '<div class="res__path">' + path.map(function (p) { return '<span class="chip">' + esc(p) + '</span>'; }).join('') + '</div>' +
        goLinks(c.go) +
        '<button type="button" class="qt__reset">처음부터 다시</button></div>';
      if (window.__qtFocus === 'res') { var rc = $('.res', resBox); if (rc) rc.focus({ preventScroll: true }); window.__qtFocus = null; }
      $('.qt__reset', resBox).addEventListener('click', function () { answers = {}; render(); qtHost.scrollIntoView({ behavior: 'smooth' }); });
    }
    render(false);
  }

  /* ── 본문 표·목록 채우기 (D.content) ── */
  var C = D.content || {};
  function chip(s) {
    if (!s) return '';
    var m = { good: 'chip--good', warn: 'chip--warn', bad: 'chip--bad', key: 'chip--key' };
    return '<span class="chip ' + (m[s.tone] || '') + '">' + esc(s.text) + '</span>';
  }
  function rows(id, list, fn) { var b = document.getElementById(id); if (b && list) b.innerHTML = list.map(fn).join(''); }
  rows('doors', C.doors, function (r) { return '<tr><td><b>' + esc(r.name) + '</b></td><td>' + esc(r.open) + '</td><td>' + esc(r.close) + '</td><td>' + chip(r.verdict) + (r.note ? '<br><small>' + esc(r.note) + '</small>' : '') + '</td></tr>'; });
  rows('towns', C.towns, function (r) { return '<tr><td><b>' + esc(r.name) + '</b></td><td>' + chip(r.req) + (r.more ? '<br><small>' + esc(r.more) + '</small>' : '') + '</td><td><small>' + esc(r.src) + '</small></td></tr>'; });
  rows('supply', C.supply, function (r) { return '<tr><td><b>' + esc(r.name) + '</b></td><td>' + esc(r.left) + '</td><td>' + esc(r.price) + '</td><td>' + esc(r.reg) + '</td></tr>'; });
  rows('risks', C.risks, function (r) { return '<tr><td><b>' + esc(r.why) + '</b></td><td>' + esc(r.fix) + '</td></tr>'; });
  rows('checks', C.checks, function (r, i) { return '<li><label><input type="checkbox" data-k="' + (r.k || i) + '"><span><b class="num">' + esc(r.when) + '</b> · ' + esc(r.text) + '</span></label></li>'; });
  rows('timeline', C.timeline, function (r) { return '<div class="tl__item' + (r.tone ? ' tl__item--' + r.tone : '') + '"><div class="tl__when">' + esc(r.when) + '</div><div class="tl__what">' + esc(r.what) + '</div>' + (r.note ? '<div class="tl__note">' + esc(r.note) + '</div>' : '') + '</div>'; });
  var srcBox = $('#sources');
  if (srcBox && C.sources) srcBox.innerHTML = '<ol>' + C.sources.map(function (s) { return '<li>' + esc(s.label) + (s.url ? ' — <a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.url.replace(/^https?:\/\//, '').slice(0, 60)) + '</a>' : '') + (s.note ? ' <small>(' + esc(s.note) + ')</small>' : '') + '</li>'; }).join('') + '</ol>' + (C.method ? '<p>' + esc(C.method) + '</p>' : '');
  var scr = $('#script');
  if (scr && D.tree && D.tree.script) scr.innerHTML = '<ol>' + D.tree.script.map(function (s) { if (typeof s === 'string') return '<li>' + esc(s) + '</li>'; return '<li><b>' + esc(s.say || '') + '</b>' + (s.listen ? '<br><span class="cap">들을 것: ' + esc(s.listen) + '</span>' : '') + '</li>'; }).join('') + '</ol>';

  /* ── 기회의 창(간트) ── */
  var winHost = $('#winChart'), winCtl = $('#winCtl');
  if (winHost && winCtl) {
    var Y0 = 2026 + 10 / 12, Y1 = 2032;            // 2026-11 ~ 2031-12
    var ym = function (s) { var p = s.split('-'); return +p[0] + (+p[1] - 1) / 12; };
    var pos = function (v) { return Math.max(0, Math.min(100, (v - Y0) / (Y1 - Y0) * 100)); };
    var months = []; for (var yy = 2026; yy <= 2030; yy++) for (var mm = 1; mm <= 12; mm++) { if (yy === 2026 && mm < 12) continue; months.push(yy + '-' + (mm < 10 ? '0' : '') + mm); }
    var store = {}; try { store = JSON.parse(localStorage.getItem('house-class:win') || '{}'); } catch (e) {}
    var defs = { move: store.move || '2027-03', city: store.city || '1', wed: store.wed || '2027-10', birth: store.birth || '2028-12', age40: store.age40 || '2028-06' };
    function sel(name, label, opts) {
      return '<label>' + label + '<select name="' + name + '">' + opts.map(function (o) { return '<option value="' + o[0] + '"' + (defs[name] === o[0] ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') + '</select></label>';
    }
    var monOpts = months.map(function (m) { return [m, m.replace('-', '년 ') + '월']; });
    winCtl.innerHTML = sel('move', '신청자 전입', monOpts) +
      sel('city', '그 도시 조건', [['1', '1년 (남양주·고양·부천)'], ['2', '2년 (하남·과천·광명)']]) +
      sel('wed', '혼인신고', monOpts.concat([['none', '아직 미정']])) +
      sel('birth', '첫 아이 출생(예상)', monOpts.concat([['none', '계획 없음·미정']])) +
      sel('age40', '먼저 만 40세 되는 달', monOpts);
    function addM(s, n) { var v = ym(s) + n / 12; return v; }
    function draw() {
      var f = {}; $$('select', winCtl).forEach(function (s) { f[s.name] = s.value; });
      try { localStorage.setItem('house-class:win', JSON.stringify(f)); } catch (e) {}
      var mv = ym(f.move), wed = f.wed === 'none' ? null : ym(f.wed), birth = f.birth === 'none' ? null : ym(f.birth), a40 = ym(f.age40);
      var rowsW = [
        { l: '경기 몫 20%', s: '비규제 지구, 전입 6개월 뒤부터', a: mv + 0.5, b: Y1, c: 'var(--s3)' },
        { l: '그 시 몫 30%', s: (f.city === '2' ? '전입 2년' : '전입 1년') + ' 뒤부터', a: mv + (f.city === '2' ? 2 : 1), b: Y1, c: 'var(--s1)' },
        { l: '신혼 특공', s: '예비신혼 포함, 혼인 7년', a: Y0, b: wed ? wed + 7 : Y1, c: 'var(--s7)' },
        { l: '신생아 문', s: '임신 확인 ~ 만 2세', a: birth ? birth - 0.75 : null, b: birth ? birth + 2 : null, c: 'var(--s2)' },
        { l: '청년 특공(덤)', s: '미혼·만 39세까지', a: Y0, b: Math.min(wed || Y1, a40), c: 'var(--s4)' },
        { l: '2027 왕숙 블록', s: '5,373호 예고', a: 2027 + 2 / 12, b: 2028, c: 'var(--ink-3)' }
      ];
      // 가장 좋은 창: 그 시 몫 ∩ 신생아 문
      var bestA = null, bestB = null;
      if (birth) { bestA = Math.max(rowsW[1].a, birth - 0.75); bestB = Math.min(Y1, birth + 2); if (bestB <= bestA) bestA = bestB = null; }
      var ticks = ''; for (var y = 2027; y <= 2031; y++) ticks += '<span style="left:' + pos(y) + '%">' + y + '</span>';
      var grid = ''; for (var y2 = 2027; y2 <= 2031; y2++) grid += '<i class="win-grid" style="left:' + pos(y2) + '%"></i>';
      var html = '<div class="win-wrap">';
      rowsW.forEach(function (r) {
        html += '<div class="win-row"><div class="win-row__l">' + esc(r.l) + '<small>' + esc(r.s) + '</small></div><div class="win-track">' + grid;
        if (bestA != null) html += '<i class="win-best" style="left:' + pos(bestA) + '%;width:' + (pos(bestB) - pos(bestA)) + '%"></i>';
        if (r.a != null && r.b > r.a) html += '<i class="win-bar" style="left:' + pos(r.a) + '%;width:' + (pos(r.b) - pos(r.a)) + '%;background:' + r.c + '"></i>';
        html += '<i class="win-now" style="left:' + pos(2026 + 10.7 / 12) + '%"></i></div></div>';
      });
      html += '<div class="win-axis"><div></div><div class="win-axis__in">' + ticks + '</div></div></div>';
      html += bestA != null
        ? '<div class="callout callout--good" style="margin-bottom:0"><b>노릴 창: ' + fmtYm(bestA) + ' ~ ' + fmtYm(bestB) + '</b>그 시 몫과 신생아 문이 함께 열립니다. 이 기간 공고는 세 단계 추첨 + 신생아 특공 + 일반공급 신생아 우선공급(50%)으로 들어가고, 신생아 유형으로 당첨되면 아이가 2세를 넘어도 신생아 특례대출을 잔금에 쓸 수 있습니다.</div>'
        : '<div class="callout callout--warn" style="margin-bottom:0"><b>두 창이 겹치지 않습니다</b>그 시 몫(거주)과 신생아 문이 겹치는 기간이 없습니다. 전입을 앞당기거나, 신혼 특공·경기 몫을 주력으로 잡습니다.</div>';
      winHost.innerHTML = html;
    }
    function fmtYm(v) { var y = Math.floor(v + 1e-6), m = Math.round((v - y) * 12) + 1; if (m > 12) { y++; m = 1; } return y + '-' + (m < 10 ? '0' : '') + m; }
    winCtl.addEventListener('change', draw); draw();
  }

  /* ── 3기 신도시 지도(SVG) — D.geo: {seoulOutline, hanRiver, hubs, towns} ── */
  var mapHost = $('#ntMap'), mapInfo = $('#ntInfo');
  if (mapHost && D.geo && D.geo.towns) {
    var G = D.geo;
    var reqColor = function (r) { return r === '2y' ? 'var(--warm)' : r === 'none' ? 'var(--s3)' : 'var(--s1)'; };
    var selectTown = function (id) {
      var t = G.towns.filter(function (x) { return x.id === id; })[0]; if (!t || !mapInfo) return;
      $$('.ntmap__town', mapHost).forEach(function (g) { var on = g.getAttribute('data-id') === id; g.classList.toggle('on', on); g.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      var line = function (l, v) { return v ? '<div class="nt__row"><span>' + l + '</span><b>' + esc(v) + '</b></div>' : ''; };
      var tierCls = /인기|브랜드/.test(t.tier || '') ? 'chip--key' : /가성비/.test(t.tier || '') ? 'chip--good' : '';
      mapInfo.innerHTML = '<div class="card nt"><div class="chip ' + tierCls + '">' + esc(t.tier || '') + '</div>' +
        '<div class="res__title">' + esc(t.name) + '</div>' + (t.oneLine ? '<p class="nt__one">' + esc(t.oneLine) + '</p>' : '') +
        (t.rows || []).map(function (r) { return line(r[0], r[1]); }).join('') +
        (t.transit && t.transit.length ? '<h3 class="res__h">교통</h3><ul class="nt__tr">' + t.transit.map(function (x) {
          var sc = /운행|개통/.test(x.status || '') ? ' chip--good' : /공사/.test(x.status || '') ? ' chip--key' : '';
          return '<li><b>' + esc(x.line) + '</b> <span class="chip' + sc + '">' + esc(x.status || '') + (x.openYear ? ' ' + esc(x.openYear) : '') + '</span>' + (x.note ? ' <small>' + esc(x.note) + '</small>' : '') + '</li>';
        }).join('') + '</ul>' : '') + '</div>';
    };
    var drawMap = function () {
      mapHost.innerHTML = '';
      var W = chartW(mapHost), narrow = W < 520, H = Math.round(W * (narrow ? 1.0 : 0.95));
      var pts = (G.seoulOutline || []).slice();
      G.towns.forEach(function (t) { pts.push([t.lon, t.lat]); });
      var lons = pts.map(function (p) { return p[0]; }), lats = pts.map(function (p) { return p[1]; });
      var lon0 = Math.min.apply(null, lons), lon1 = Math.max.apply(null, lons), la0 = Math.min.apply(null, lats), la1 = Math.max.apply(null, lats);
      var cl = Math.cos((la0 + la1) / 2 * Math.PI / 180), padX = narrow ? 74 : 72, padY = narrow ? 30 : 40;
      var k = Math.min((W - 2 * padX) / ((lon1 - lon0) * cl), (H - 2 * padY) / (la1 - la0));
      var ox = (W - (lon1 - lon0) * cl * k) / 2, oy = (H - (la1 - la0) * k) / 2;
      var P = function (lon, lat) { return [ox + (lon - lon0) * cl * k, oy + (la1 - lat) * k]; };
      var path = function (arr) { return arr.map(function (p) { var q = P(p[0], p[1]); return q[0].toFixed(1) + ',' + q[1].toFixed(1); }).join('L'); };
      var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'viz ntmap', role: 'group', 'aria-label': '서울과 3기 신도시 위치 지도. 지구를 고르면 거리·교통·가격이 나옵니다.' });
      var ch = (G.hubs || []).filter(function (h) { return /시청|광화문/.test(h.name); })[0];
      if (ch) {
        var c = P(ch.lon, ch.lat);
        [10, 20, 30].forEach(function (km) {
          var r = km / 111 * k;
          el('circle', { cx: c[0], cy: c[1], r: r, fill: 'none', stroke: 'var(--ink-3)', 'stroke-opacity': .35, 'stroke-dasharray': '3 5' }, svg);
          txt(svg, c[0], c[1] - r - 4, km + 'km', 't-muted', 'middle');
        });
      }
      if (G.seoulOutline) el('path', { d: 'M' + path(G.seoulOutline) + 'Z', fill: 'var(--wash)', stroke: 'var(--ink-3)', 'stroke-width': 1.5 }, svg);
      if (G.hanRiver) el('path', { d: 'M' + path(G.hanRiver), fill: 'none', stroke: 'var(--s1)', 'stroke-opacity': .35, 'stroke-width': narrow ? 4 : 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
      (G.hubs || []).forEach(function (h) {
        var p = P(h.lon, h.lat);
        el('rect', { x: p[0] - 4, y: p[1] - 4, width: 8, height: 8, fill: 'var(--ink)', transform: 'rotate(45 ' + p[0] + ' ' + p[1] + ')' }, svg);
        txt(svg, p[0], p[1] + 17, h.short || h.name, 't-muted', 'middle');
      });
      G.towns.forEach(function (t) {
        var p = P(t.lon, t.lat), r = Math.max(7, Math.min(15, Math.sqrt(t.units || 10000) / 14));
        var g = el('g', { 'class': 'ntmap__town', 'data-id': t.id, tabindex: '0', role: 'button', 'aria-label': t.name + ' 자세히 보기' }, svg);
        el('circle', { cx: p[0], cy: p[1], r: r + 10, fill: 'transparent' }, g);
        el('circle', { 'class': 'ntmap__dot', cx: p[0], cy: p[1], r: r, fill: reqColor(t.req), stroke: 'var(--paper)', 'stroke-width': 2 }, g);
        var side = t.labelSide || (p[0] < W * 0.6 ? 'right' : 'left');
        var dx = side === 'right' ? r + 5 : -(r + 5), anchor = side === 'right' ? 'start' : 'end';
        var dy = t.labelDy || 0;
        txt(g, p[0] + dx, p[1] - 1 + dy, t.short || t.name, 't-strong', anchor);
        if (t.kmToGangnam != null) txt(g, p[0] + dx, p[1] + 14 + dy, '강남 ' + fmt(t.kmToGangnam, 0) + 'km', 't-muted', anchor);
        g.addEventListener('click', function () { selectTown(t.id); });
        g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectTown(t.id); } });
      });
      mapHost.appendChild(svg);
    };
    drawMap();
    selectTown(G.defaultTown || G.towns[0].id);
  }


  /* ── 이번 달·다음 달 전입 확률 표 — D.moveNow ── */
  var mnHost = $('#moveNowRows');
  if (mnHost && D.moveNow) {
    var pcTxt = function (v) { return v == null ? '-' : v >= 99.95 ? '약 100%' : fmt(v, v === 0 ? 0 : 1) + '%'; };
    mnHost.innerHTML = D.moveNow.rows.map(function (r) {
      return '<tr><th scope="row">' + esc(r.town) + '</th><td>' + esc(r.req) + '</td><td>' + esc(r.qualifies) + '</td>' +
        '<td><b>' + pcTxt(r.p3) + '</b>' + (r.ci3 ? '<br><small>' + fmt(r.ci3[0], 0) + '~' + fmt(r.ci3[1], 0) + '%</small>' : '') + '</td>' +
        '<td>' + pcTxt(r.p3late) + '</td><td>' + pcTxt(r.p5) + '</td><td>' + fmt(r.e2, 1) + '건 → ' + fmt(r.e2late, 1) + '건</td><td>' + pcTxt(r.p3half) + '</td></tr>';
    }).join('');
    $$('[data-mn]').forEach(function (n) { var v = D.moveNow.nam[n.getAttribute('data-mn')]; if (v != null) n.textContent = fmt(v, v % 1 ? 1 : 0); });
  }

  /* ── 아깝게 놓침(SVG) ── */
  var missHost = $('#miss');
  if (missHost) {
    var W = chartW(missHost), H = 150, L = 20, R = 20;
    var sv = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'viz', role: 'img', 'aria-label': '2026-12-01 전입, 2027-10-29 공고, 2027-12-01 자격일을 표시한 시간선' }, missHost);
    var a = new Date('2026-11-01').getTime(), b = new Date('2028-06-01').getTime();
    var X = function (d) { return L + (new Date(d).getTime() - a) / (b - a) * (W - L - R); };
    el('line', { x1: L, x2: W - R, y1: 80, y2: 80, stroke: 'var(--line)', 'stroke-width': 6, 'stroke-linecap': 'round' }, sv);
    el('rect', { x: X('2026-12-01'), y: 74, width: X('2027-12-01') - X('2026-12-01'), height: 12, rx: 6, fill: 'var(--s1)', opacity: .85 }, sv);
    el('rect', { x: X('2027-06-01'), y: 92, width: X('2028-06-01') - X('2027-06-01'), height: 8, rx: 4, fill: 'var(--s3)' }, sv);
    txt(sv, X('2027-06-01') + 4, 116, '경기 6개월 단계는 열려 있음', 't-muted');
    [['2026-12-01', '전입', 'var(--s1)', 52], ['2027-10-29', '공고(안내대로)', 'var(--warm)', 52], ['2027-12-01', '그 시 1년 충족', 'var(--s1)', 52]].forEach(function (p, i) {
      var x = X(p[0]);
      el('line', { x1: x, x2: x, y1: p[3] + 6, y2: 80, stroke: p[2], 'stroke-width': 2, 'stroke-dasharray': i === 1 ? '4 3' : null }, sv);
      el('circle', { cx: x, cy: 80, r: 6, fill: p[2], stroke: 'var(--paper)', 'stroke-width': 2 }, sv);
      txt(sv, x + (i === 1 ? -6 : 6), p[3], p[1], 't-strong', i === 1 ? 'end' : 'start');
      txt(sv, x + (i === 1 ? -6 : 6), p[3] - 16, p[0], 't-muted', i === 1 ? 'end' : 'start');
    });
    var gx1 = X('2027-10-29'), gx2 = X('2027-12-01');
    el('path', { d: 'M' + gx1 + ',132 H' + gx2, stroke: 'var(--warm)', 'stroke-width': 2 }, sv);
    txt(sv, (gx1 + gx2) / 2, 146, '33일 모자람', 't-strong', 'middle');
  }

  /* ── 목차 ── */
  var links = $$('.toc a'), bar = $('.toc__bar');
  var secs = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function onScroll() {
    var y = scrollY + 120, cur = 0;
    secs.forEach(function (s, i) { if (s && s.offsetTop <= y) cur = i; });
    links.forEach(function (a, i) {
      var on = i === cur;
      if (on !== (a.getAttribute('aria-current') === 'true')) {
        a.setAttribute('aria-current', on ? 'true' : 'false');
        if (on) { var box = a.parentNode; box.scrollTo({ left: a.offsetLeft - box.clientWidth / 2 + a.offsetWidth / 2, behavior: 'smooth' }); }
      }
    });
    if (bar) { var h = document.documentElement.scrollHeight - innerHeight; bar.style.width = (h > 0 ? Math.min(100, scrollY / h * 100) : 0) + '%'; }
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* ── 할 일 확인(이 기기에만 저장) ── */
  $$('.check input[data-k]').forEach(function (inp) {
    var k = 'house-class:ck:' + inp.getAttribute('data-k');
    try { inp.checked = localStorage.getItem(k) === '1'; } catch (e) {}
    inp.addEventListener('change', function () { try { localStorage.setItem(k, inp.checked ? '1' : '0'); } catch (e) {} });
  });
})();
