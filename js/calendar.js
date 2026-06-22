// 이 파일의 역할: 상태(state)를 받아 A4 일정표 시트(헤더/달력/우측패널/푸터) HTML 렌더링
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});

  WS.esc = function (s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  function catIndexMap(cats) {
    var m = {};
    cats.forEach(function (c, i) { m[c.id] = i; });
    return m;
  }

  function pad(n) { return String(n).padStart(2, '0'); }

  function renderHeader(data, y, m) {
    var last = WS.daysInMonth(y, m);
    return '' +
      '<div class="header">' +
        '<div class="left">' +
          '<div class="dept">' + WS.esc(data.meta.dept) + '</div>' +
          '<div class="title">' + WS.esc(data.meta.author) + ' · ' + m + '월 업무 일정표</div>' +
        '</div>' +
        '<div class="right">' +
          '<div class="month">' + y + '년 ' + m + '월</div>' +
          '<div>' + y + '. ' + pad(m) + '. 01 ~ ' + pad(m) + '. ' + pad(last) + '</div>' +
        '</div>' +
      '</div>';
  }

  function renderCalendar(data, month, y, m) {
    var idx = catIndexMap(data.categories);
    var catById = {};
    data.categories.forEach(function (c) { catById[c.id] = c; });
    var holidayBy = {};
    (month.holidays || []).forEach(function (h) { holidayBy[h.date] = h.name; });
    var evBy = {};
    (month.events || []).forEach(function (e) {
      (evBy[e.date] = evBy[e.date] || []).push(e);
    });
    var leaveBy = {};
    (month.leaves || []).forEach(function (l) { leaveBy[l.date] = l; });
    var shiftBy = {};
    (month.shifts || []).forEach(function (s) { shiftBy[s.date] = s; });

    var firstDow = new Date(y, m - 1, 1).getDay();
    var days = WS.daysInMonth(y, m);
    var rows = Math.ceil((firstDow + days) / 7);
    var cells = rows * 7;

    var html = '<div class="calendar">' +
      '<div class="cal-dow"><div class="sun">일</div><div>월</div><div>화</div><div>수</div><div>목</div><div>금</div><div class="sat">토</div></div>' +
      '<div class="cal-grid">';

    for (var i = 0; i < cells; i++) {
      var d = i - firstDow + 1;
      var col = i % 7;
      var lastRow = i >= (rows - 1) * 7 ? ' last-row' : '';
      if (d < 1 || d > days) { html += '<div class="cell empty' + lastRow + '"></div>'; continue; }
      var dateStr = y + '-' + pad(m) + '-' + pad(d);
      var cls = 'cell' + lastRow;
      if (col === 0) cls += ' sun';
      if (col === 6) cls += ' sat';
      var hname = holidayBy[dateStr];
      if (hname) cls += ' holiday';
      var lv = leaveBy[dateStr];
      var lt = lv ? WS.leaveType(lv.type) : null;
      if (lt && lt.full) cls += ' leave-full';
      html += '<div class="' + cls + '" data-date="' + dateStr + '">';
      html += '<div class="date">' + d + '</div>';
      if (hname) html += '<div class="holiday-tag">' + WS.esc(hname) + '</div>';
      if (lv) {
        var lc = lt ? lt.color : '#0d9488';
        html += '<div class="leave-tag" style="color:' + lc + ';border-color:' + lc + ';background:' + lc + '18;">' + WS.esc(lv.type) + '</div>';
      }
      (evBy[dateStr] || []).forEach(function (e) {
        var c = WS.catColor(catById[e.catId], idx[e.catId] || 0);
        var timeTag = e.time ? ' <span class="key">(' + WS.esc(e.time) + ')</span>' : '';
        html += '<div class="ev' + (e.major ? ' major' : '') + '" data-ev="' + e.id + '" ' +
          'style="border-color:' + c.bd + ';background:' + c.bg + ';">' + WS.esc(e.text) + timeTag + '</div>';
      });
      var sh = shiftBy[dateStr];
      if (sh) {
        var stt = WS.shiftType(sh.type) || { abbr: '?', color: '#64748b' };
        html += '<div class="shift-badge" title="' + WS.esc(sh.type) + '" style="background:' + stt.color + ';">' + WS.esc(stt.abbr) + '</div>';
      }
      html += '<div class="cell-hint">＋</div>';
      html += '</div>';
    }
    html += '</div></div>';
    return html;
  }

  function renderLegend(data, month) {
    var items = data.categories.map(function (c, i) {
      var col = WS.catColor(c, i);
      return '<div class="legend-item"><div class="legend-swatch" style="background:' + col.bd + ';"></div>' +
        WS.circled(i) + ' ' + WS.esc(c.name) + '</div>';
    }).join('');
    items += '<div class="legend-item"><div class="legend-swatch" style="background:#dc2626;"></div>공휴일 / 대체 휴일</div>';
    var used = {};
    (month.leaves || []).forEach(function (l) { used[l.type] = true; });
    WS.LEAVE_TYPES.forEach(function (t) {
      if (used[t.key]) items += '<div class="legend-item"><div class="legend-swatch" style="background:' + t.color + ';"></div>' + WS.esc(t.key) + '</div>';
    });
    var usedSh = {};
    (month.shifts || []).forEach(function (s) { usedSh[s.type] = true; });
    WS.SHIFT_TYPES.forEach(function (t) {
      if (usedSh[t.key]) items += '<div class="legend-item"><div class="legend-swatch" style="background:' + t.color + ';"></div>' + t.abbr + ' · ' + t.key + '</div>';
    });
    return '<div class="panel"><div class="panel-title">공정 분류 / 휴무 / 교대</div><div class="legend">' + items + '</div></div>';
  }

  function renderProgress(data, month, y, m) {
    var ep = WS.effectiveProgress(month, data.categories, y, m);
    var ths = '';
    for (var w = 0; w < ep.weeks; w++) ths += '<th>' + (w + 1) + '주차</th>';
    var body = data.categories.map(function (c, i) {
      var col = WS.catColor(c, i);
      var tds = ep.rows[c.id].map(function (v, w) {
        var bold = v === 100 ? '<b>100%</b>' : (v + '%');
        return '<td class="prog-cell" data-cat="' + c.id + '" data-week="' + w + '" contenteditable="true">' + bold + '</td>';
      }).join('');
      return '<tr><td class="cat-name" style="border-left:3px solid ' + col.bd + ';">' +
        WS.circled(i) + ' ' + WS.esc(c.short || c.name) + '</td>' + tds + '</tr>';
    }).join('');
    var avg = ep.average.map(function (v) { return '<td>' + v + '%</td>'; }).join('');
    body += '<tr class="total-row"><td class="cat-name">전체 평균</td>' + avg + '</tr>';
    return '<div class="panel"><div class="panel-title">주차별 누적 진행률 <span class="hint-text">(셀 클릭 후 직접 수정)</span></div>' +
      '<div class="prog-table"><table><thead><tr><th style="width:30%;">공정 분류</th>' + ths + '</tr></thead><tbody>' +
      body + '</tbody></table></div></div>';
  }

  function renderSummary(data, month, y, m) {
    var lines = (month.summaryOverride && month.summaryOverride.length)
      ? month.summaryOverride
      : WS.autoSummary(month, data.categories, y, m);
    var li = lines.map(function (s) { return '<li>' + WS.esc(s) + '</li>'; }).join('');
    if (!li) li = '<li style="color:#94a3b8;">등록된 일정이 없습니다. 달력의 날짜를 클릭해 추가하세요.</li>';
    return '<div class="panel"><div class="panel-title">주요 일정 요약</div><div class="notes"><ul>' + li + '</ul></div></div>';
  }

  function renderFooter(data, month, y, m) {
    var note = month.footerNote || '';
    return '<div class="footer"><div>' + WS.esc(note) + '</div>' +
      '<div>작성: ' + WS.esc(data.meta.dept) + ' ' + WS.esc(data.meta.author) + ' &nbsp;|&nbsp; ' + y + '.' + pad(m) + '</div></div>';
  }

  // 전체 시트 렌더링
  WS.renderSheet = function (el, state) {
    var data = state.data, y = state.year, m = state.month, key = state.key;
    var month = data.months[key] || WS.emptyMonth();
    el.innerHTML =
      renderHeader(data, y, m) +
      '<div class="body">' +
        renderCalendar(data, month, y, m) +
        '<div class="right-panel">' +
          renderLegend(data, month) +
          renderProgress(data, month, y, m) +
          renderSummary(data, month, y, m) +
        '</div>' +
      '</div>' +
      renderFooter(data, month, y, m);
  };
})(typeof window !== 'undefined' ? window : globalThis);
