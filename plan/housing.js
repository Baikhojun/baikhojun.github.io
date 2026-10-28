// 월별 주거비 화면이다. 실제 가계 금액은 코드에 포함하지 않는다.
(function () {
  'use strict';
  var fields = [ ['common_fee', '공통 관리비'], ['electricity', '전기료'], ['water', '수도료'], ['gas', '가스비'], ['rent', '월세'], ['interest', '이자'] ];
  var rows = [], root, ctx, selected, dirty = false, saving = false, loaded = false, failed = false, request = 0, active = true;
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function won(n) { return n == null ? '미입력' : Number(n).toLocaleString('ko-KR') + '원'; }
  function total(r, keys) { return keys.reduce(function (s, k) { return s + (r[k] == null ? 0 : r[k]); }, 0); }
  function complete(r, keys) { return keys.every(function (k) { return r[k] != null; }); }
  var all = fields.map(function (f) { return f[0]; });
  function row() { return rows.find(function (r) { return r.month.slice(0, 7) === selected; }); }
  function moneyInput(f, r) {
    return '<label class="cost-field">' + f[1] + '<span><input name="' + f[0] + '" type="text" inputmode="numeric" autocomplete="off" placeholder="미입력" value="' + (r[f[0]] == null ? '' : Number(r[f[0]]).toLocaleString('ko-KR')) + '"><b>원</b></span></label>';
  }
  function render() {
    if (!root || !active || dirty || saving) return;
    var r = row(), draft = r || {}, maintenance = ['common_fee', 'electricity', 'water'];
    var prior = rows.filter(function (v) { return v.month.slice(0, 7) < selected && v.rent != null; })[0];
    var suggested = !r && prior ? prior.rent : null;
    root.innerHTML = '<div class="cost-heading"><div><p class="eyebrow">우리 집 한 달</p><h2>월별 주거비</h2></div><label class="cost-month-label">기준 사용월<input id="cost-month" type="month" min="2000-01" max="2100-12" value="' + selected + '"></label></div>' +
      '<p id="cost-status" class="cost-status" role="status">' + (!loaded ? (rows.length ? '기기 저장본 · 최신 내역 확인 중' : '주거비 내역 확인 중…') : failed ? '기기 저장본 · 갱신하지 못하였다. 연결 후 다시 불러온다.' : '최신 내역을 확인하였다') + '</p>' +
      '<div class="cost-summary"><div><span>' + esc(selected.replace('-', '년 ') + '월') + ' · ' + (r ? complete(r, all) ? '총 주거비' : '입력한 금액 합계' : '저장된 기록 없음') + '</span><strong>' + (r ? won(total(r, all)) : '—') + '</strong><small>' + (r ? complete(r, all) ? '관리비 · 가스비 · 월세 · 이자' : '미입력 항목은 합계에 포함하지 않는다' : '금액을 입력하고 저장하면 기록된다') + '</small></div><div class="cost-subtotal"><span>관리비 소계</span><b>' + (r ? won(total(r, maintenance)) + (complete(r, maintenance) ? '' : ' (일부 입력)') : '—') + '</b><small>공통 관리비 + 전기료 + 수도료<br>가스비는 별도 합산한다</small></div></div>' +
      '<form id="cost-form"><div class="cost-form-grid"><fieldset><legend>관리비</legend><p>기준 사용월의 청구액을 기록한다.</p>' + fields.slice(0, 3).map(function (f) { return moneyInput(f, draft); }).join('') + '</fieldset>' +
      '<fieldset><legend>가스비</legend><p>관리비와 별도로 기록한다.</p>' + moneyInput(fields[3], draft) + '<label class="cost-field">가스 사용월<input name="gas_month" type="month" min="2000-01" max="2100-12" value="' + esc((draft.gas_month || selected).slice(0, 7)) + '"></label></fieldset>' +
      '<fieldset><legend>월세 · 이자</legend><p>이자는 실제 청구된 금액을 기록한다.</p>' + moneyInput(fields[4], Object.assign({}, draft, suggested != null ? {rent: suggested} : {})) + (suggested != null ? '<small>월세는 이전 기록을 가져온 제안이다. 저장하면 이번 달에 반영된다.</small>' : '') + moneyInput(fields[5], draft) + '</fieldset></div>' +
      '<label class="cost-memo">메모<textarea name="memo" maxlength="500" rows="2" placeholder="청구 내용이나 참고 사항">' + esc(draft.memo) + '</textarea></label>' +
      '<p id="cost-message" class="cost-message" role="status">' + (r ? '마지막 저장 ' + esc(new Date(r.updated_at).toLocaleString('ko-KR')) : '빈 금액은 미입력, 0은 0원으로 저장한다.') + '</p>' +
      '<div class="cost-actions"><button type="button" id="cost-reset" class="pill">입력 취소</button><button type="submit" id="cost-save" class="pill primary"' + (!ctx.verified() ? ' disabled' : '') + '>이 달 저장</button></div></form>' +
      '<div class="cost-history"><h3>월별 내역</h3>' + (rows.length ? '<ul>' + rows.map(function (v) { return '<li><button type="button" data-cost-month="' + v.month.slice(0, 7) + '"' + (v.month.slice(0, 7) === selected ? ' aria-current="true"' : '') + '><span>' + esc(v.month.slice(0, 7)) + '<small>' + (complete(v, all) ? '모두 입력' : '일부 미입력') + '</small></span><b>' + won(total(v, all)) + '</b></button></li>'; }).join('') + '</ul>' : '<p>' + (!loaded ? '내역을 확인하는 중이다.' : failed ? '서버에 연결하지 못하였다.' : '저장된 주거비가 없다.') + '</p>') + '</div>';
    root.querySelector('form')._original = r ? Object.assign({}, r) : null;
  }
  function showMessage(message) { var el = root.querySelector('#cost-message'); if (el) el.textContent = message; }
  function setSelected(month) { selected = month; dirty = false; ctx.onMonth(month); render(); }
  function readCache() { var v = ctx.read('housing'); if (v && Array.isArray(v.rows)) rows = v.rows; }
  async function refresh() {
    if (!active || !ctx || saving) return;
    var seq = ++request;
    try {
      var data = await ctx.api.loadHousing();
      if (!active || seq !== request) return;
      rows = data; loaded = true; failed = false;
      ctx.write('housing', { rows: rows }); render();
      var status = root.querySelector('#cost-status'); if (status) status.textContent = '최신 내역을 확인하였다' + (dirty ? ' · 입력 중인 내용은 유지된다' : '');
    } catch (e) {
      if (!active || seq !== request) return;
      loaded = true; failed = true; ctx.error(e, '주거비를 불러오지 못했다'); render();
    }
  }
  async function save(e) {
    e.preventDefault();
    if (saving) return;
    if (!ctx.verified()) { showMessage('인터넷 연결과 계정 확인 후 저장할 수 있다.'); return; }
    var form = root.querySelector('form'), payload = { month: selected + '-01' }, before = form._original, seq = request;
    try {
      all.forEach(function (key) {
        var raw = form.elements[key].value.trim();
        if (!raw) { payload[key] = null; return; }
        if (!/^(\d+|\d{1,3}(,\d{3})+)$/.test(raw)) throw new Error('금액은 0 이상의 정수로 입력한다.');
        var n = Number(raw.replace(/,/g, ''));
        if (!Number.isSafeInteger(n) || n > 1000000000) throw new Error('금액은 0원부터 10억원까지 입력한다.');
        payload[key] = n;
      });
      if (all.every(function (k) { return payload[k] == null; })) throw new Error('금액을 한 항목 이상 입력한다.');
      payload.gas_month = payload.gas == null ? null : (form.elements.gas_month.value || selected) + '-01';
      payload.memo = form.elements.memo.value.trim() || null;
      saving = true; seq = ++request;
      root.querySelector('#cost-save').disabled = true; showMessage('서버에 저장하는 중이다…');
      var saved = await ctx.api.saveHousing(payload, before ? before.updated_at : null);
      if (!active || seq !== request) return;
      rows = rows.filter(function (v) { return v.month !== saved.month; }); rows.push(saved); rows.sort(function (a, b) { return b.month.localeCompare(a.month); });
      ctx.write('housing', {rows: rows}); dirty = false; failed = false; loaded = true;
      saving = false; render(); showMessage('서버에 저장하였다. 다른 기기에서도 확인할 수 있다.');
    } catch (err) {
      if (!active || seq !== request) return;
      saving = false;
      root.querySelector('#cost-save').disabled = !ctx.verified();
      showMessage(err.code === 'conflict' ? '다른 기기에서 먼저 저장하였다. 입력 내용은 유지된다. 입력 취소 후 최신 내역을 확인하고 다시 수정한다.' : '저장하지 못하였다. ' + (err.message || '연결을 확인한다.'));
      ctx.error(err, '주거비를 저장하지 못했다');
    }
  }
  window.CoupleHousing = {
    init: function (node, options) {
      root = node; ctx = options; selected = options.month; active = true; rows = []; dirty = saving = loaded = failed = false; ++request;
      readCache(); render();
      root.oninput = function (e) {
        if (e.target.id === 'cost-month') return;
        if (!dirty) { var form = root.querySelector('form'); form._original = row() ? Object.assign({}, row()) : null; }
        dirty = true; showMessage('저장 전 변경 사항이 있다.');
      };
      root.onchange = function (e) {
        if (e.target.id !== 'cost-month') return;
        var month = e.target.value;
        if (!/^(20\d\d|2100)-(0[1-9]|1[0-2])$/.test(month)) { e.target.value = selected; return; }
        if (saving || (dirty && !confirm('저장하지 않은 입력을 취소하고 다른 달을 열까요?'))) { e.target.value = selected; return; }
        setSelected(month);
      };
      root.onclick = function (e) {
        if (e.target.closest('#cost-reset')) { if (!saving) { dirty = false; render(); refresh(); } return; }
        var b = e.target.closest('[data-cost-month]');
        if (b && !saving && (!dirty || confirm('저장하지 않은 입력을 취소하고 다른 달을 열까요?'))) setSelected(b.dataset.costMonth);
      };
      root.onsubmit = save;
      refresh();
    },
    refresh: refresh,
    month: function (month) {
      if (saving || (dirty && !confirm('저장하지 않은 입력을 취소하고 다른 달을 열까요?'))) return false;
      selected = month; dirty = false; render(); return true;
    },
    isDirty: function () { return dirty || saving; },
    verified: function () { var b = root && root.querySelector('#cost-save'); if (b) b.disabled = saving || !ctx.verified(); },
    stop: function () { active = false; ++request; rows = []; dirty = false; if (root) root.innerHTML = ''; }
  };
})();
