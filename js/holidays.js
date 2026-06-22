// 이 파일의 역할: 한국 공휴일 자동 생성(양력 고정 + 음력 표 기반) + 대체공휴일 규칙
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});

  // 음력 기반 공휴일(설날/추석 3일, 부처님오신날) — 연도별 양력 환산표
  var LUNAR = {
    2025: { seollal: ['2025-01-28', '2025-01-29', '2025-01-30'], buddha: '2025-05-05', chuseok: ['2025-10-05', '2025-10-06', '2025-10-07'] },
    2026: { seollal: ['2026-02-16', '2026-02-17', '2026-02-18'], buddha: '2026-05-24', chuseok: ['2026-09-24', '2026-09-25', '2026-09-26'] },
    2027: { seollal: ['2027-02-06', '2027-02-07', '2027-02-08'], buddha: '2027-05-13', chuseok: ['2027-09-14', '2027-09-15', '2027-09-16'] }
  };

  function pad(n) { return String(n).padStart(2, '0'); }
  function ymd(y, m, d) { return y + '-' + pad(m) + '-' + pad(d); }
  function dowOf(dateStr) {
    var p = dateStr.split('-').map(Number);
    return new Date(p[0], p[1] - 1, p[2]).getDay(); // 0=일 .. 6=토
  }
  function addDays(dateStr, n) {
    var p = dateStr.split('-').map(Number);
    var d = new Date(p[0], p[1] - 1, p[2] + n);
    return ymd(d.getFullYear(), d.getMonth() + 1, d.getDate());
  }

  // 해당 연도 전체 공휴일 목록 생성
  WS.holidaysForYear = function (year) {
    var list = [];
    function push(date, name) { list.push({ date: date, name: name }); }

    // 양력 고정 공휴일
    push(ymd(year, 1, 1), '신정');
    push(ymd(year, 3, 1), '삼일절');
    push(ymd(year, 5, 5), '어린이날');
    push(ymd(year, 6, 6), '현충일');
    push(ymd(year, 8, 15), '광복절');
    push(ymd(year, 10, 3), '개천절');
    push(ymd(year, 10, 9), '한글날');
    push(ymd(year, 12, 25), '성탄절');

    // 음력 공휴일
    var lu = LUNAR[year];
    if (lu) {
      push(lu.seollal[0], '설날 연휴'); push(lu.seollal[1], '설날'); push(lu.seollal[2], '설날 연휴');
      push(lu.buddha, '부처님오신날');
      push(lu.chuseok[0], '추석 연휴'); push(lu.chuseok[1], '추석'); push(lu.chuseok[2], '추석 연휴');
    }

    // 대체공휴일 규칙
    //  - 설날·추석·어린이날: 토(6)/일(0)과 겹치면 대체
    //  - 삼일절·광복절·개천절·한글날·부처님오신날·성탄절: 일(0)만 겹치면 대체
    //  - 신정·현충일: 대체 없음
    var taken = {};
    list.forEach(function (h) { taken[h.date] = true; });

    function nextOpenDay(fromDate) {
      var d = addDays(fromDate, 1);
      while (taken[d] || dowOf(d) === 0 || dowOf(d) === 6) d = addDays(d, 1);
      return d;
    }

    var subs = [];
    // 어린이날(토·일 모두)
    var kid = ymd(year, 5, 5);
    if (dowOf(kid) === 0 || dowOf(kid) === 6) subs.push([nextOpenDay(kid), '어린이날 대체휴일']);
    // 일요일만 대체 대상
    [[ymd(year, 3, 1), '삼일절'], [ymd(year, 8, 15), '광복절'], [ymd(year, 10, 3), '개천절'], [ymd(year, 10, 9), '한글날'], [ymd(year, 12, 25), '성탄절']]
      .forEach(function (p) { if (dowOf(p[0]) === 0) subs.push([nextOpenDay(p[0]), p[1] + ' 대체휴일']); });
    if (lu) {
      if (dowOf(lu.buddha) === 0) subs.push([nextOpenDay(lu.buddha), '부처님오신날 대체휴일']);
      // 설날/추석: 연휴 중 토·일 겹치면 연휴 끝 다음 평일 1일 대체
      [lu.seollal, lu.chuseok].forEach(function (block, idx) {
        var weekendOverlap = block.some(function (d) { return dowOf(d) === 0 || dowOf(d) === 6; });
        if (weekendOverlap) subs.push([nextOpenDay(block[block.length - 1]), (idx === 0 ? '설날' : '추석') + ' 대체휴일']);
      });
    }
    subs.forEach(function (s) { if (!taken[s[0]]) { taken[s[0]] = true; list.push({ date: s[0], name: s[1] }); } });

    list.sort(function (a, b) { return a.date < b.date ? -1 : 1; });
    return list;
  };

  // 특정 연·월 공휴일만 추출
  WS.holidaysForMonth = function (year, month) {
    var prefix = year + '-' + pad(month);
    return WS.holidaysForYear(year).filter(function (h) { return h.date.indexOf(prefix) === 0; });
  };
})(typeof window !== 'undefined' ? window : globalThis);
