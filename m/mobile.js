// 이 파일의 역할: 모바일 조회 로직 - 동기화 데이터 fetch → 월별 세로 리스트 렌더(조회 전용)
;(function () {
  'use strict';
  var WS = window.WS;
  var DOW = ['일', '월', '화', '수', '목', '금', '토'];
  var data = null, cur = null;

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function pad(n) { return String(n).padStart(2, '0'); }
  function el(id) { return document.getElementById(id); }
  function daysInMonth(y, m) { return new Date(y, m, 0).getDate(); }
  function ymNow() { var d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1); }
  function hhmm() { var d = new Date(); return pad(d.getHours()) + ':' + pad(d.getMinutes()); }

  function normalize(j) {
    j = j || {}; j.meta = j.meta || {}; j.categories = j.categories || []; j.months = j.months || {}; j.ui = j.ui || {};
    Object.keys(j.months).forEach(function (k) {
      var m = j.months[k] || {};
      ['holidays', 'leaves', 'shifts', 'personal', 'events', 'inactiveCats'].forEach(function (f) { if (!Array.isArray(m[f])) m[f] = []; });
      j.months[k] = m;
    });
    return j;
  }

  function load() {
    el('m-app').innerHTML = '<div class="mloading">불러오는 중…</div>';
    fetch('../data/schedule-data.json?t=' + Date.now(), { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('no-data'); return r.json(); })
      .then(function (j) { data = normalize(j); var keys = Object.keys(data.months).sort(); cur = (data.ui && data.ui.lastMonth) || keys[keys.length - 1] || ymNow(); render(); })
      .catch(function (e) { console.error('[mobile.load] %s', e && e.message); showNoData(); });
  }

  function catIndex() { var m = {}; data.categories.forEach(function (c, i) { m[c.id] = i; }); return m; }
  function findCat(id) { return data.categories.filter(function (c) { return c.id === id; })[0]; }

  function render() {
    var p = cur.split('-').map(Number), y = p[0], mo = p[1];
    el('m-month').textContent = y + '년 ' + mo + '월';
    var month = data.months[cur] || { holidays: [], leaves: [], shifts: [], personal: [], events: [] };
    var idx = catIndex();
    var holBy = {}, leaveBy = {}, shiftBy = {}, evBy = {}, persBy = {};
    (month.holidays || []).forEach(function (h) { holBy[h.date] = h.name; });
    (month.leaves || []).forEach(function (l) { leaveBy[l.date] = l; });
    (month.shifts || []).forEach(function (s) { shiftBy[s.date] = s; });
    (month.events || []).forEach(function (e) { (evBy[e.date] = evBy[e.date] || []).push(e); });
    (month.personal || []).forEach(function (pp) { (persBy[pp.date] = persBy[pp.date] || []).push(pp); });

    var days = daysInMonth(y, mo);
    var html = '<div class="mtitle">' + esc((data.meta.dept || '') + ' ' + (data.meta.author || '')) + ' · ' + mo + '월 업무 일정표</div>';
    for (var d = 1; d <= days; d++) {
      var date = y + '-' + pad(mo) + '-' + pad(d);
      var dow = new Date(y, mo - 1, d).getDay();
      var hol = holBy[date], sh = shiftBy[date], lv = leaveBy[date], evs = evBy[date] || [], pers = persBy[date] || [];
      var stt = sh ? WS.shiftType(sh.type) : null, lt = lv ? WS.leaveType(lv.type) : null;
      var empty = !hol && !sh && !lv && !evs.length && !pers.length;
      var datecls = 'mdate' + ((dow === 0 || hol) ? ' sun' : '') + (dow === 6 ? ' sat' : '');
      html += '<div class="mday' + (empty ? ' empty' : '') + '">';
      html += '<div class="' + datecls + '"><b>' + d + '</b><span>' + DOW[dow] + '</span></div><div class="mcontent">';
      if (hol) html += '<div class="mhol">' + esc(hol) + '</div>';
      if (stt) html += '<span class="mshift" style="background:' + stt.color + '">' + esc(stt.abbr) + ' · ' + esc(stt.key) + '</span>';
      if (lt) html += '<span class="mleave" style="color:' + lt.color + ';border-color:' + lt.color + '">' + esc(lv.type) + '</span>';
      evs.forEach(function (e) {
        var c = WS.catColor(findCat(e.catId), idx[e.catId] || 0);
        html += '<div class="mev" style="border-color:' + c.bd + ';background:' + c.bg + '">' + (e.major ? '★ ' : '') + esc(e.text) + (e.time ? ' (' + esc(e.time) + ')' : '') + '</div>';
      });
      pers.forEach(function (pp) { html += '<div class="mpers" style="color:' + (pp.color || '#db2777') + '">▪ ' + esc(pp.text) + '</div>'; });
      if (empty) html += '<div class="mempty">—</div>';
      html += '</div></div>';
    }
    el('m-app').innerHTML = html;
    el('m-foot').textContent = '조회 전용 · 불러온 시각 ' + hhmm() + ' · 수정은 PC에서 (동기화 업로드 후 반영)';
  }

  function showNoData() {
    el('m-app').innerHTML = '<div class="mnodata"><h2>표시할 데이터가 없습니다</h2>' +
      '<p>PC에서 <b>설정 → GitHub 동기화 → ⬆ GitHub에 저장</b>을 한 번 하면 이 화면에서 조회할 수 있어요.</p>' +
      '<p class="sm">동기화 후 1~2분 뒤 🔄 새로고침 하세요.</p></div>';
    el('m-month').textContent = '업무 일정표';
    el('m-foot').textContent = '조회 전용';
  }

  function move(delta) {
    var p = cur.split('-').map(Number), y = p[0], m = p[1] + delta;
    if (m < 1) { m = 12; y--; } if (m > 12) { m = 1; y++; }
    cur = y + '-' + pad(m); render();
  }

  document.addEventListener('DOMContentLoaded', function () {
    el('m-prev').addEventListener('click', function () { if (data) move(-1); });
    el('m-next').addEventListener('click', function () { if (data) move(1); });
    el('m-today').addEventListener('click', function () { if (data) { cur = ymNow(); render(); } });
    el('m-reload').addEventListener('click', load);
    load();
  });
})();
