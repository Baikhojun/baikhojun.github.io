// 이 파일의 역할: 주차 계산 + 진행률 자동산출(누적) + 주요일정 요약 자동생성
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});

  var DOW = ['일', '월', '화', '수', '목', '금', '토'];

  function daysInMonth(y, m) { return new Date(y, m, 0).getDate(); }

  // 월요일 시작 기준 주차 인덱스(0-base). 진행률 표의 "주차"에 사용.
  function mondayOffset(y, m) {
    var jsDay = new Date(y, m - 1, 1).getDay(); // 0=일
    return (jsDay + 6) % 7;                     // 월=0 .. 일=6
  }
  WS.weekOfDay = function (y, m, day) {
    return Math.floor((mondayOffset(y, m) + (day - 1)) / 7);
  };
  WS.weekCount = function (y, m) {
    return WS.weekOfDay(y, m, daysInMonth(y, m)) + 1;
  };

  function dayNum(dateStr) { return Number(dateStr.split('-')[2]); }

  // 진행률 자동계산: 카테고리별 누적(해당 주차까지 발생한 일정수 / 전체 일정수)
  WS.autoProgress = function (monthData, categories, y, m) {
    var weeks = WS.weekCount(y, m);
    var result = {};
    categories.forEach(function (cat) {
      var evs = monthData.events.filter(function (e) { return e.catId === cat.id; });
      var total = evs.length;
      var perWeek = new Array(weeks).fill(0);
      evs.forEach(function (e) {
        var w = WS.weekOfDay(y, m, dayNum(e.date));
        if (w >= 0 && w < weeks) perWeek[w] += 1;
      });
      var row = new Array(weeks).fill(0);
      var cum = 0;
      for (var w = 0; w < weeks; w++) {
        cum += perWeek[w];
        row[w] = total ? Math.round((cum / total) * 100) : 0;
      }
      result[cat.id] = row;
    });
    return result;
  };

  // 화면에 쓸 최종 진행률(셀별 override 우선) + 전체 평균 행
  WS.effectiveProgress = function (monthData, categories, y, m) {
    var weeks = WS.weekCount(y, m);
    var auto = WS.autoProgress(monthData, categories, y, m);
    var ov = monthData.progressOverride || {};
    var rows = {};
    categories.forEach(function (cat) {
      var a = auto[cat.id] || new Array(weeks).fill(0);
      var o = ov[cat.id];
      var r = new Array(weeks);
      for (var w = 0; w < weeks; w++) {
        r[w] = (o && o[w] !== undefined && o[w] !== null && o[w] !== '') ? Number(o[w]) : a[w];
      }
      rows[cat.id] = r;
    });
    var avg = new Array(weeks).fill(0);
    for (var w2 = 0; w2 < weeks; w2++) {
      var sum = 0;
      categories.forEach(function (cat) { sum += rows[cat.id][w2] || 0; });
      avg[w2] = categories.length ? Math.round(sum / categories.length) : 0;
    }
    return { weeks: weeks, rows: rows, average: avg };
  };

  // 주요일정 요약 자동생성(override 없을 때)
  WS.autoSummary = function (monthData, categories, y, m) {
    var lines = [];
    function dowStr(dateStr) { return DOW[new Date(y, m - 1, dayNum(dateStr)).getDay()]; }
    function md(dateStr) { return m + '/' + dayNum(dateStr); }
    var catName = {};
    categories.forEach(function (c) { catName[c.id] = c.short || c.name; });

    // 공휴일
    (monthData.holidays || []).forEach(function (h) {
      lines.push({ date: h.date, text: md(h.date) + ' (' + dowStr(h.date) + ') ' + h.name });
    });
    // 마일스톤(major)
    monthData.events.filter(function (e) { return e.major; }).forEach(function (e) {
      var t = e.time ? ' ' + e.time : '';
      lines.push({ date: e.date, text: md(e.date) + ' (' + dowStr(e.date) + ')' + t + ' — ' + e.text });
    });
    // 장기 매일 일정(같은 카테고리가 4일 이상)
    categories.forEach(function (cat) {
      var ds = monthData.events.filter(function (e) { return e.catId === cat.id; })
        .map(function (e) { return e.date; }).sort();
      if (ds.length >= 4) {
        var s = ds[0], en = ds[ds.length - 1];
        lines.push({ date: s, text: md(s) + ' (' + dowStr(s) + ') ~ ' + md(en) + ' (' + dowStr(en) + ') — ' + (cat.short || cat.name) + ' (매일 진행)' });
      }
    });
    lines.sort(function (a, b) { return a.date < b.date ? -1 : (a.date > b.date ? 1 : 0); });
    return lines.map(function (l) { return l.text; }).slice(0, 10);
  };

  WS.DOW = DOW;
  WS.daysInMonth = daysInMonth;
})(typeof window !== 'undefined' ? window : globalThis);
