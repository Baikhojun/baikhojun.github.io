// 이 파일은 한국 공휴일과 대체공휴일을 계산한다(표시 전용).
// 규칙(2026년 기준)
//  - 설날·추석 연휴: 일요일 또는 다른 공휴일과 겹치면 연휴 다음 첫 평일을 대체공휴일로 한다(토요일은 해당하지 않는다).
//  - 어린이날·노동절·국경일(삼일절·제헌절·광복절·개천절·한글날)·부처님오신날·성탄절: 토요일 또는 일요일과 겹치면 다음 첫 평일을 대체한다.
//  - 신정·현충일: 대체하지 않는다.
//  - 제헌절(7/17)과 노동절(5/1)은 2026년부터 공휴일이다.
// 음력 공휴일과 선거일은 연도별 표로 관리한다. 표에 없는 연도는 양력 공휴일만 표시한다.
;(function (root) {
  'use strict';

  var LUNAR = {
    2025: { seollal: ['2025-01-28', '2025-01-29', '2025-01-30'], buddha: '2025-05-05', chuseok: ['2025-10-05', '2025-10-06', '2025-10-07'] },
    2026: { seollal: ['2026-02-16', '2026-02-17', '2026-02-18'], buddha: '2026-05-24', chuseok: ['2026-09-24', '2026-09-25', '2026-09-26'] },
    2027: { seollal: ['2027-02-06', '2027-02-07', '2027-02-08'], buddha: '2027-05-13', chuseok: ['2027-09-14', '2027-09-15', '2027-09-16'] },
    2028: { seollal: ['2028-01-25', '2028-01-26', '2028-01-27'], buddha: '2028-05-02', chuseok: ['2028-10-02', '2028-10-03', '2028-10-04'] },
    // 2029·2030년은 한국천문연구원 월력요항 발표 후 다시 확인한다.
    2029: { seollal: ['2029-02-12', '2029-02-13', '2029-02-14'], buddha: '2029-05-20', chuseok: ['2029-09-21', '2029-09-22', '2029-09-23'] },
    2030: { seollal: ['2030-02-02', '2030-02-03', '2030-02-04'], buddha: '2030-05-09', chuseok: ['2030-09-11', '2030-09-12', '2030-09-13'] }
  };
  var EXTRA = {
    2026: [['2026-06-03', '지방선거']],
    2028: [['2028-04-12', '국회의원선거']]
  };

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(y, m, d) { return y + '-' + pad(m) + '-' + pad(d); }
  function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function dow(s) { return parse(s).getDay(); }
  function addDays(s, n) { var d = parse(s); d.setDate(d.getDate() + n); return ymd(d.getFullYear(), d.getMonth() + 1, d.getDate()); }

  var cache = {};

  function forYear(year) {
    if (cache[year]) return cache[year];
    var names = {};   // 날짜 → 공휴일 이름 배열
    function add(date, name) { (names[date] = names[date] || []).push(name); }

    // 대체 규칙 구분: 'none'(대체 없음), 'weekend'(토·일 대체)
    var fixed = [[1, 1, '신정', 'none'], [3, 1, '삼일절', 'weekend'], [5, 5, '어린이날', 'weekend'], [6, 6, '현충일', 'none'],
      [8, 15, '광복절', 'weekend'], [10, 3, '개천절', 'weekend'], [10, 9, '한글날', 'weekend'], [12, 25, '성탄절', 'weekend']];
    if (year >= 2026) fixed.push([5, 1, '노동절', 'weekend'], [7, 17, '제헌절', 'weekend']);
    var weekendRule = [];
    fixed.forEach(function (f) { var d = ymd(year, f[0], f[1]); add(d, f[2]); if (f[3] === 'weekend') weekendRule.push(d); });

    var lu = LUNAR[year];
    var blocks = [];
    var inBlock = {};
    if (lu) {
      lu.seollal.forEach(function (d, i) { inBlock[d] = true; add(d, i === 1 ? '설날' : '설날 연휴'); });
      lu.chuseok.forEach(function (d, i) { inBlock[d] = true; add(d, i === 1 ? '추석' : '추석 연휴'); });
      blocks.push([lu.seollal, '설날'], [lu.chuseok, '추석']);
      add(lu.buddha, '부처님오신날');
      weekendRule.push(lu.buddha);
    }
    (EXTRA[year] || []).forEach(function (e) { add(e[0], e[1]); });

    var taken = {};
    Object.keys(names).forEach(function (d) { taken[d] = true; });
    function nextWeekday(from) {
      var d = addDays(from, 1);
      while (taken[d] || dow(d) === 0 || dow(d) === 6) d = addDays(d, 1);
      return d;
    }
    function substitute(from, label) { var d = nextWeekday(from); taken[d] = true; add(d, label + ' 대체공휴일'); }

    // 토·일 대체 대상: 주말과 겹치거나, 다른 공휴일과 같은 날이면 한 번 대체한다. 설·추석 연휴 안의 날짜는 연휴 규칙에서 처리한다.
    var done = {};
    weekendRule.forEach(function (d) {
      if (done[d] || inBlock[d]) return;
      done[d] = true;
      var w = dow(d);
      if (w === 0 || w === 6) substitute(d, names[d][0]);
      else if (names[d].length > 1) substitute(d, names[d][names[d].length - 1]);
    });
    // 설·추석 연휴: 일요일 또는 다른 공휴일과 겹치면 연휴 다음 첫 평일 하루를 대체한다.
    blocks.forEach(function (b) {
      var hit = b[0].some(function (d) { return dow(d) === 0 || names[d].length > 1; });
      if (hit) substitute(b[0][b[0].length - 1], b[1]);
    });

    var map = {};
    Object.keys(names).forEach(function (d) { map[d] = names[d].join(' · '); });
    cache[year] = map;
    return map;
  }

  // 날짜 문자열(YYYY-MM-DD) → 공휴일 이름 또는 null
  root.CoupleHolidays = {
    name: function (date) { return forYear(+date.slice(0, 4))[date] || null; }
  };
})(typeof window !== 'undefined' ? window : globalThis);
