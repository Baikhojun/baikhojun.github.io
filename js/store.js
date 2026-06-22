// 이 파일의 역할: 내부 DB(localStorage) 저장소 - 데이터 스키마/기본값/CRUD/내보내기·가져오기
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});

  // ----- 상수 -----
  WS.STORAGE_KEY = 'ws.schedule.v1';
  WS.SCHEMA_VERSION = 1;

  // 공정 번호별 고정 색상 (border / background) — 7번째 이후는 순환
  WS.PALETTE = [
    { bd: '#7c3aed', bg: '#f3e8ff' }, // ① 보라
    { bd: '#2563eb', bg: '#dbeafe' }, // ② 파랑
    { bd: '#f59e0b', bg: '#fef3c7' }, // ③ 주황
    { bd: '#059669', bg: '#d1fae5' }, // ④ 초록
    { bd: '#db2777', bg: '#fce7f3' }, // ⑤ 분홍
    { bd: '#0891b2', bg: '#cffafe' }, // ⑥ 청록
    { bd: '#e11d48', bg: '#ffe4e6' }, // ⑦ 적색
    { bd: '#475569', bg: '#f1f5f9' }  // ⑧ 회색
  ];

  // 원문자 ①②③… (인덱스 0부터)
  WS.circled = function (i) {
    return i >= 0 && i < 20 ? String.fromCharCode(0x2460 + i) : '(' + (i + 1) + ')';
  };
  WS.color = function (idx) {
    return WS.PALETTE[((idx % WS.PALETTE.length) + WS.PALETTE.length) % WS.PALETTE.length];
  };

  // 고유 id 생성
  var _seq = 0;
  WS.uid = function (prefix) {
    _seq += 1;
    return (prefix || 'id') + '_' + Date.now().toString(36) + '_' + _seq.toString(36);
  };

  // YYYY-MM 키
  WS.monthKey = function (year, month) {
    return year + '-' + String(month).padStart(2, '0');
  };

  WS.DEFAULT_CATEGORIES = function () {
    return [
      { id: 'c1', name: '계약관리 업무교육', short: '계약교육' },
      { id: 'c2', name: 'AI 결과보고서', short: 'AI보고서' },
      { id: 'c3', name: 'EPC 전체회의', short: 'EPC회의' },
      { id: 'c4', name: '관리부서 AI교육', short: 'AI교육' },
      { id: 'c5', name: 'EPC 외주계약 개발', short: 'EPC외주개발' },
      { id: 'c6', name: '계약관리 소스코드 분석', short: '소스 분석' }
    ];
  };

  // 첫 실행 시 보여줄 2026년 5월 예시 데이터(기존 템플릿 재현)
  function seedMay2026() {
    function ev(date, catId, text, opts) {
      opts = opts || {};
      return { id: WS.uid('e'), date: date, catId: catId, text: text, time: opts.time || '', major: !!opts.major };
    }
    var events = [
      ev('2026-05-08', 'c1', '계약관리 업무교육', { time: '오후', major: true }),
      ev('2026-05-11', 'c2', 'AI보고서 작성'), ev('2026-05-11', 'c4', 'AI교육 PPT'), ev('2026-05-11', 'c6', '소스 분석'),
      ev('2026-05-12', 'c2', 'AI보고서 작성'), ev('2026-05-12', 'c4', 'AI교육 PPT'), ev('2026-05-12', 'c6', '소스 분석'),
      ev('2026-05-13', 'c2', 'AI보고서 작성'), ev('2026-05-13', 'c4', 'AI교육 PPT'), ev('2026-05-13', 'c6', '소스 분석'),
      ev('2026-05-14', 'c3', 'EPC 전체회의(예상)', { major: true }), ev('2026-05-14', 'c6', '소스 분석'),
      ev('2026-05-15', 'c2', 'AI보고서 작성 완료', { major: true }), ev('2026-05-15', 'c4', 'PPT 완료'), ev('2026-05-15', 'c6', '소스 분석'),
      ev('2026-05-18', 'c2', 'AI보고서 보고', { major: true }), ev('2026-05-18', 'c5', 'EPC 외주개발'), ev('2026-05-18', 'c6', '소스 분석'),
      ev('2026-05-19', 'c4', 'AI교육 예비교육 1차', { major: true }), ev('2026-05-19', 'c5', 'EPC 외주개발'), ev('2026-05-19', 'c6', '소스 분석'),
      ev('2026-05-20', 'c5', 'EPC 외주개발'), ev('2026-05-20', 'c6', '소스 분석'),
      ev('2026-05-21', 'c4', 'AI교육 예비교육 2차', { major: true }), ev('2026-05-21', 'c5', 'EPC 외주개발'), ev('2026-05-21', 'c6', '소스 분석'),
      ev('2026-05-22', 'c5', 'EPC 외주개발'), ev('2026-05-22', 'c6', '소스 분석'),
      ev('2026-05-26', 'c4', '관리부서 AI교육 실시', { major: true }), ev('2026-05-26', 'c6', '소스 분석'),
      ev('2026-05-27', 'c5', 'EPC 외주개발'), ev('2026-05-27', 'c6', '소스 분석'),
      ev('2026-05-28', 'c5', 'EPC 외주개발'), ev('2026-05-28', 'c6', '소스 분석'),
      ev('2026-05-29', 'c5', 'EPC 외주개발 마무리', { major: true }), ev('2026-05-29', 'c6', '소스 분석 완료', { major: true })
    ];
    return {
      holidays: [
        { date: '2026-05-05', name: '어린이날' },
        { date: '2026-05-24', name: '부처님오신날' },
        { date: '2026-05-25', name: '대체 휴일' }
      ],
      events: events,
      // 기존 템플릿의 손계산 진행률을 그대로 재현(주차별 누적 %)
      progressOverride: {
        c1: [0, 100, 100, 100, 100],
        c2: [0, 0, 80, 100, 100],
        c3: [0, 0, 100, 100, 100],
        c4: [0, 0, 40, 80, 100],
        c5: [0, 0, 0, 50, 100],
        c6: [0, 0, 36, 71, 100]
      },
      summaryOverride: [
        '5/8 (금) 오후 — 계약관리 업무교육',
        '5/11 (월) ~ 5/29 (금) — 계약관리 소스코드 분석 (매일 진행)',
        '5/14 (목) — EPC 전체회의 (예상, 협의 후 확정)',
        '5/15 (금) — AI 결과보고서 작성 완료 / AI교육 PPT 완료',
        '5/18 (월) — AI 결과보고서 보고 / EPC 외주계약 개발 착수',
        '5/19 (화), 5/21 (목) — 관리부서 AI교육 예비교육 1·2차',
        '5/24 (일) 부처님오신날 / 5/25 (월) 대체 휴일',
        '5/26 (화) — 관리부서 AI교육 1회 실시',
        '5/29 (금) — EPC 외주계약 개발 / 소스코드 분석 마무리'
      ],
      footerNote: '※ EPC 전체회의 일자(5/14) 및 AI교육 예비교육 일자(5/19, 5/21)는 협의 후 조정 가능'
    };
  }

  WS.seed = function () {
    return {
      version: WS.SCHEMA_VERSION,
      meta: { dept: '정보실', author: '백호준 과장' },
      categories: WS.DEFAULT_CATEGORIES(),
      months: { '2026-05': seedMay2026() },
      ui: { lastMonth: '2026-05' }
    };
  };

  // 빈 달 구조
  WS.emptyMonth = function () {
    return { holidays: [], events: [], progressOverride: {}, summaryOverride: null, footerNote: '' };
  };

  // ----- 저장소 -----
  WS.Store = {
    data: null,

    load: function () {
      try {
        var raw = root.localStorage ? root.localStorage.getItem(WS.STORAGE_KEY) : null;
        if (raw) {
          this.data = JSON.parse(raw);
          this._migrate();
        } else {
          this.data = WS.seed();
          this.save();
        }
      } catch (e) {
        console.error('[Store.load] 데이터 로드 실패, 기본값 사용: %s', e && e.message);
        this.data = WS.seed();
      }
      return this.data;
    },

    save: function () {
      try {
        if (root.localStorage) {
          root.localStorage.setItem(WS.STORAGE_KEY, JSON.stringify(this.data));
        }
        return true;
      } catch (e) {
        console.error('[Store.save] 저장 실패: %s', e && e.message);
        return false;
      }
    },

    _migrate: function () {
      if (!this.data || typeof this.data !== 'object') { this.data = WS.seed(); return; }
      if (!this.data.meta) this.data.meta = { dept: '', author: '' };
      if (!Array.isArray(this.data.categories) || !this.data.categories.length) {
        this.data.categories = WS.DEFAULT_CATEGORIES();
      }
      if (!this.data.months || typeof this.data.months !== 'object') this.data.months = {};
      if (!this.data.ui) this.data.ui = { lastMonth: null };
      this.data.version = WS.SCHEMA_VERSION;
    },

    // 달 데이터 반환(없으면 생성 옵션)
    getMonth: function (key, createIfMissing) {
      if (!this.data.months[key] && createIfMissing) {
        this.data.months[key] = WS.emptyMonth();
      }
      return this.data.months[key] || WS.emptyMonth();
    },

    savedMonthKeys: function () {
      return Object.keys(this.data.months).sort();
    },

    findCategory: function (id) {
      return this.data.categories.filter(function (c) { return c.id === id; })[0] || null;
    },

    eventsOn: function (key, date) {
      var m = this.getMonth(key);
      return m.events.filter(function (e) { return e.date === date; });
    },

    // 내보내기 / 가져오기
    exportJSON: function () {
      return JSON.stringify(this.data, null, 2);
    },

    importJSON: function (str) {
      var parsed = JSON.parse(str); // 호출부에서 try/catch
      if (!parsed || typeof parsed !== 'object' || !parsed.months) {
        throw new Error('올바른 일정표 데이터 파일이 아닙니다.');
      }
      this.data = parsed;
      this._migrate();
      this.save();
      return this.data;
    },

    resetAll: function () {
      this.data = WS.seed();
      this.save();
      return this.data;
    }
  };
})(typeof window !== 'undefined' ? window : globalThis);
