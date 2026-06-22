// 이 파일의 역할: 월간 통계 집계(공정별 투입일수/일정수, 휴가 사용현황, 근무일수)
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});
  WS.Stats = {};

  function pad(n) { return String(n).padStart(2, '0'); }

  WS.Stats.compute = function (month, categories, y, m) {
    var perCat = categories.map(function (c) {
      var evs = month.events.filter(function (e) { return e.catId === c.id; });
      var days = {};
      evs.forEach(function (e) { days[e.date] = true; });
      return { id: c.id, name: c.name, short: c.short, events: evs.length, days: Object.keys(days).length };
    });

    var leaveCount = {};
    (month.leaves || []).forEach(function (l) { leaveCount[l.type] = (leaveCount[l.type] || 0) + 1; });
    var leaves = WS.LEAVE_TYPES.map(function (t) { return { type: t.key, count: leaveCount[t.key] || 0 }; })
      .filter(function (x) { return x.count > 0; });

    var leaveDays = 0;
    (month.leaves || []).forEach(function (l) {
      var t = WS.leaveType(l.type);
      leaveDays += (t && t.full) ? 1 : (l.type.indexOf('반차') >= 0 ? 0.5 : 0);
    });

    // 근무일수(평일 - 공휴일)
    var dim = WS.daysInMonth(y, m);
    var holidaySet = {};
    (month.holidays || []).forEach(function (h) { holidaySet[h.date] = true; });
    var workdays = 0;
    for (var d = 1; d <= dim; d++) {
      var wd = new Date(y, m - 1, d).getDay();
      var ds = y + '-' + pad(m) + '-' + pad(d);
      if (wd !== 0 && wd !== 6 && !holidaySet[ds]) workdays++;
    }

    var shiftCount = {};
    (month.shifts || []).forEach(function (s) { shiftCount[s.type] = (shiftCount[s.type] || 0) + 1; });
    var shifts = WS.SHIFT_TYPES.map(function (t) { return { type: t.key, abbr: t.abbr, count: shiftCount[t.key] || 0 }; })
      .filter(function (x) { return x.count > 0; });

    return { totalEvents: month.events.length, perCat: perCat, leaves: leaves, leaveDays: leaveDays, workdays: workdays, holidays: (month.holidays || []).length, shifts: shifts };
  };
})(typeof window !== 'undefined' ? window : globalThis);
