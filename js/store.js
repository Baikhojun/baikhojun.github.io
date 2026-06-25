// 이 파일의 역할: 내부 DB(localStorage) 저장소 - 스키마(v2)/기본값/CRUD/내보내기·가져오기/실행취소/지난달복사
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});

  // ----- 상수 -----
  WS.STORAGE_KEY = 'ws.schedule.v1';     // 데이터 저장 키(스키마는 내부 version 필드로 관리)
  WS.SYNC_TOKEN_KEY = 'ws.sync.token';   // GitHub 토큰(데이터와 분리 저장 → 내보내기에 미포함)
  WS.SCHEMA_VERSION = 2;

  // 공정 번호별 기본 색상(border / background) — 7번째 이후 순환. 공정별 커스텀 색상이 있으면 그것을 우선.
  WS.PALETTE = [
    { bd: '#7c3aed', bg: '#f3e8ff' }, { bd: '#2563eb', bg: '#dbeafe' },
    { bd: '#f59e0b', bg: '#fef3c7' }, { bd: '#059669', bg: '#d1fae5' },
    { bd: '#db2777', bg: '#fce7f3' }, { bd: '#0891b2', bg: '#cffafe' },
    { bd: '#e11d48', bg: '#ffe4e6' }, { bd: '#475569', bg: '#f1f5f9' }
  ];

  // 휴가 / 근무형태 유형
  WS.LEAVE_TYPES = [
    { key: '연차', color: '#0d9488', full: true },
    { key: '오전반차', color: '#0d9488', full: false },
    { key: '오후반차', color: '#0d9488', full: false },
    { key: '출장', color: '#7c3aed', full: false },
    { key: '재택', color: '#1d4ed8', full: false },
    { key: '외근', color: '#ea580c', full: false }
  ];
  WS.leaveType = function (key) {
    return WS.LEAVE_TYPES.filter(function (t) { return t.key === key; })[0] || null;
  };

  // 교대근무 유형(하루 1개) - 약자/색상
  WS.SHIFT_TYPES = [
    { key: 'Day', abbr: 'D', color: '#0284c7' },
    { key: 'Evening', abbr: 'E', color: '#ea580c' },
    { key: 'Night', abbr: 'N', color: '#4f46e5' },
    { key: 'Off', abbr: 'Of', color: '#64748b' }
  ];
  WS.shiftType = function (key) { return WS.SHIFT_TYPES.filter(function (t) { return t.key === key; })[0] || null; };

  // 개인 일정: 공정과 구분되게 '글자색'만 입힘. 빠른 선택용 색상 + 기본색.
  WS.PERSONAL_COLORS = ['#db2777', '#0d9488', '#4f46e5', '#b45309', '#e11d48', '#475569'];
  WS.PERSONAL_DEFAULT = '#db2777';

  WS.circled = function (i) { return i >= 0 && i < 20 ? String.fromCharCode(0x2460 + i) : '(' + (i + 1) + ')'; };
  WS.color = function (idx) { return WS.PALETTE[((idx % WS.PALETTE.length) + WS.PALETTE.length) % WS.PALETTE.length]; };
  // 공정 색상: 커스텀(cat.color) 우선, 배경은 같은 색 13% 틴트(8자리 hex)
  WS.catColor = function (cat, idx) {
    if (cat && cat.color) return { bd: cat.color, bg: cat.color + '22' };
    return WS.color(idx);
  };

  var _seq = 0;
  WS.uid = function (prefix) { _seq += 1; return (prefix || 'id') + '_' + Date.now().toString(36) + '_' + _seq.toString(36); };
  WS.monthKey = function (year, month) { return year + '-' + String(month).padStart(2, '0'); };

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
        { date: '2026-05-05', name: '어린이날' }, { date: '2026-05-24', name: '부처님오신날' }, { date: '2026-05-25', name: '대체 휴일' }
      ],
      leaves: [],
      shifts: [],
      personal: [],
      inactiveCats: [],
      events: events,
      progressOverride: {
        c1: [0, 100, 100, 100, 100], c2: [0, 0, 80, 100, 100], c3: [0, 0, 100, 100, 100],
        c4: [0, 0, 40, 80, 100], c5: [0, 0, 0, 50, 100], c6: [0, 0, 36, 71, 100]
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
      ui: { lastMonth: '2026-05' },
      sync: { owner: '', repo: '', path: 'data/schedule-data.json', branch: 'main' }
    };
  };

  WS.emptyMonth = function () {
    return { holidays: [], leaves: [], shifts: [], personal: [], events: [], progressOverride: {}, summaryOverride: null, footerNote: '', inactiveCats: [] };
  };

  // ----- 저장소 -----
  WS.Store = {
    data: null,
    _history: [],   // 실행취소용 직전 상태 스냅샷
    _last: null,
    onSave: null,   // 저장 후 후크(자동 동기화 연결용)

    load: function () {
      try {
        var raw = root.localStorage ? root.localStorage.getItem(WS.STORAGE_KEY) : null;
        if (raw) { this.data = JSON.parse(raw); this._migrate(); }
        else { this.data = WS.seed(); this._writeLS(); }
      } catch (e) {
        console.error('[Store.load] 로드 실패, 기본값 사용: %s', e && e.message);
        this.data = WS.seed();
      }
      this._last = JSON.stringify(this.data);
      this._history = [];
      return this.data;
    },

    _writeLS: function () {
      if (root.localStorage) root.localStorage.setItem(WS.STORAGE_KEY, JSON.stringify(this.data));
    },

    save: function (skipHistory) {
      try {
        if (!skipHistory && this._last != null) {
          this._history.push(this._last);
          if (this._history.length > 30) this._history.shift();
        }
        this._writeLS();
        this._last = JSON.stringify(this.data);
        if (typeof this.onSave === 'function') { try { this.onSave(); } catch (e) {} }
        return true;
      } catch (e) { console.error('[Store.save] 저장 실패: %s', e && e.message); return false; }
    },

    canUndo: function () { return this._history.length > 0; },
    undo: function () {
      if (!this._history.length) return false;
      var prev = this._history.pop();
      try { this.data = JSON.parse(prev); if (root.localStorage) root.localStorage.setItem(WS.STORAGE_KEY, prev); }
      catch (e) { console.error('[Store.undo] 실패: %s', e && e.message); return false; }
      this._last = prev;
      return true;
    },

    _migrate: function () {
      if (!this.data || typeof this.data !== 'object') { this.data = WS.seed(); return; }
      if (!this.data.meta) this.data.meta = { dept: '', author: '' };
      if (!Array.isArray(this.data.categories) || !this.data.categories.length) this.data.categories = WS.DEFAULT_CATEGORIES();
      if (!this.data.months || typeof this.data.months !== 'object') this.data.months = {};
      // 월 구조 보정(휴가 배열 등)
      var months = this.data.months;
      Object.keys(months).forEach(function (k) {
        var m = months[k] || {};
        if (!Array.isArray(m.holidays)) m.holidays = [];
        if (!Array.isArray(m.leaves)) m.leaves = [];
        if (!Array.isArray(m.shifts)) m.shifts = [];
        if (!Array.isArray(m.personal)) m.personal = [];
        if (!Array.isArray(m.inactiveCats)) m.inactiveCats = [];
        if (!Array.isArray(m.events)) m.events = [];
        if (!m.progressOverride || typeof m.progressOverride !== 'object') m.progressOverride = {};
        if (m.summaryOverride === undefined) m.summaryOverride = null;
        if (typeof m.footerNote !== 'string') m.footerNote = '';
        months[k] = m;
      });
      if (!this.data.ui) this.data.ui = { lastMonth: null };
      if (!this.data.sync) this.data.sync = { owner: '', repo: '', path: 'data/schedule-data.json', branch: 'main' };
      this.data.version = WS.SCHEMA_VERSION;
    },

    getMonth: function (key, createIfMissing) {
      if (!this.data.months[key] && createIfMissing) this.data.months[key] = WS.emptyMonth();
      return this.data.months[key] || WS.emptyMonth();
    },
    savedMonthKeys: function () { return Object.keys(this.data.months).sort(); },
    findCategory: function (id) { return this.data.categories.filter(function (c) { return c.id === id; })[0] || null; },
    eventsOn: function (key, date) { return this.getMonth(key).events.filter(function (e) { return e.date === date; }); },
    leaveOn: function (key, date) { return this.getMonth(key).leaves.filter(function (l) { return l.date === date; })[0] || null; },

    // 지난 달(또는 임의 달) 일정·휴가를 대상 달로 복제(요일 아닌 날짜 기준, 말일 초과는 말일로 클램프)
    copyMonth: function (srcKey, dstKey) {
      var src = this.data.months[srcKey];
      if (!src) return false;
      var dp = dstKey.split('-').map(Number);
      var dim = new Date(dp[0], dp[1], 0).getDate();
      function remap(dateStr) {
        var d = Number(dateStr.split('-')[2]); if (d > dim) d = dim;
        return dstKey + '-' + String(d).padStart(2, '0');
      }
      var dst = WS.emptyMonth();
      dst.events = src.events.map(function (e) { return { id: WS.uid('e'), date: remap(e.date), catId: e.catId, text: e.text, time: e.time, major: e.major }; });
      dst.leaves = (src.leaves || []).map(function (l) { return { id: WS.uid('l'), date: remap(l.date), type: l.type }; });
      dst.shifts = (src.shifts || []).map(function (s) { return { date: remap(s.date), type: s.type }; });
      dst.personal = (src.personal || []).map(function (p) { return { id: WS.uid('p'), date: remap(p.date), text: p.text, color: p.color }; });
      dst.inactiveCats = (src.inactiveCats || []).slice();
      dst.footerNote = src.footerNote || '';
      this.data.months[dstKey] = dst;
      return true;
    },

    // 토큰(데이터와 분리)
    getToken: function () { try { return (root.localStorage && root.localStorage.getItem(WS.SYNC_TOKEN_KEY)) || ''; } catch (e) { return ''; } },
    setToken: function (t) { try { if (root.localStorage) { if (t) root.localStorage.setItem(WS.SYNC_TOKEN_KEY, t); else root.localStorage.removeItem(WS.SYNC_TOKEN_KEY); } } catch (e) {} },

    exportJSON: function () { return JSON.stringify(this.data, null, 2); },
    importJSON: function (str) {
      var parsed = JSON.parse(str);
      if (!parsed || typeof parsed !== 'object' || !parsed.months) throw new Error('올바른 일정표 데이터 파일이 아닙니다.');
      this.data = parsed; this._migrate(); this.save(true);
      return this.data;
    },
    resetAll: function () { this.data = WS.seed(); this.save(true); return this.data; }
  };
})(typeof window !== 'undefined' ? window : globalThis);
