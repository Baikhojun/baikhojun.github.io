// 이 파일은 부부 일정표(은붕이·호붕이)의 동작을 정의한다.
// - 데이터는 Supabase(couple_shifts, couple_events)에 저장한다. 접근은 로그인한 두 계정만 가능하다(DB의 RLS 정책).
// - 로그인 세션은 기기에 저장되어 다음부터 자동으로 열린다.
// - localhost 에서 ?mock 을 붙이면 서버 없이 화면을 시험하는 모의 모드로 동작한다.
(function () {
  'use strict';

  var CFG = window.COUPLE_CONFIG || {};
  var PEOPLE = {
    eun: { name: '은붕이', email: 'eunbung@couple.unfade.invalid', color: 'var(--p-eun)', emoji: '🐰' },
    ho: { name: '호붕이', email: 'hobung@couple.unfade.invalid', color: 'var(--p-ho)', emoji: '🐻' },
    both: { name: '함께', color: 'var(--p-both)', emoji: '💕' }
  };
  var SHIFTS = {
    D: { label: '데이', color: 'var(--shift-D)' },
    E: { label: '이브닝', color: 'var(--shift-E)' },
    N: { label: '나이트', color: 'var(--shift-N)' },
    M: { label: '09:00–17:00', color: 'var(--shift-M)' },
    OF: { label: '오프', color: 'var(--shift-OF)' }
  };
  var SHIFT_ORDER = ['D', 'E', 'N', 'OF'];
  var WEEK = ['일', '월', '화', '수', '목', '금', '토'];
  var LS_PERSON = 'unfade-couple-person';

  // ---------- 날짜 도구 ----------
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function addDays(s, n) { var d = parse(s); d.setDate(d.getDate() + n); return ymd(d); }
  function todayStr() { return ymd(new Date()); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function fmtStamp(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    return (d.getMonth() + 1) + '/' + d.getDate() + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }
  function pname(k) { return PEOPLE[k] ? PEOPLE[k].name : ''; }
  // "9:00"과 "19:00"이 올바른 순서가 되도록 시각을 두 자리로 맞춘 정렬 키를 만든다. 시각이 아닌 글은 시각 뒤에 둔다.
  function timeKey(t) { var m = /^(\d{1,2})[:시]\s*(\d{2})?/.exec(t || ''); return m ? pad(+m[1]) + ':' + (m[2] || '00') : '~' + (t || ''); }
  function isNetworkError(err) { return (err && err.name === 'AuthRetryableFetchError') || /Failed to fetch|fetch failed|NetworkError|Load failed|network|timeout|timed out/i.test((err && (err.message || String(err))) || ''); }
  function defaultPerson() {
    try { var saved = localStorage.getItem(LS_PERSON); if (saved === 'eun' || saved === 'ho') return saved; } catch (e) {}
    var ua = navigator.userAgent || '';
    var iOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    return iOS ? 'eun' : 'ho';
  }

  // ---------- 데이터 계층 ----------
  function supabaseBackend() {
    var sb = window.supabase.createClient(CFG.url, CFG.key, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false, storageKey: 'unfade-couple-auth' }
    });
    function check(r) { if (r.error) throw r.error; return r.data; }
    return {
      session: async function () { var r = await sb.auth.getSession(); if (r.error) throw r.error; return r.data.session; },
      savedSession: function () {
        try { return JSON.parse(localStorage.getItem('unfade-couple-auth')); } catch (e) { return null; }
      },
      signIn: async function (person, password) {
        var r = await sb.auth.signInWithPassword({ email: PEOPLE[person].email, password: password });
        if (r.error) throw r.error;
      },
      // 이 기기의 세션만 끝낸다(같은 계정의 다른 기기는 유지). 서버 응답이 실패해도 기기의 세션은 지운다.
      signOut: async function () { try { await sb.auth.signOut({ scope: 'local' }); } catch (e) { /* 무시 */ } try { localStorage.removeItem('unfade-couple-auth'); } catch (e) {} },
      whoami: async function () { return check(await sb.rpc('couple_person')); },
      load: async function (from, to) {
        var res = await Promise.all([
          sb.from('couple_shifts').select('day,code,updated_by,updated_at').gte('day', from).lte('day', to),
          sb.from('couple_events').select('id,day,owner,title,time_text,memo,created_by,created_at,updated_by,updated_at')
            .gte('day', from).lte('day', to).order('day').order('created_at')
        ]);
        return { shifts: check(res[0]), events: check(res[1]) };
      },
      setShift: async function (day, code) {
        return check(await sb.from('couple_shifts').upsert({ day: day, code: code }, { onConflict: 'day' }).select().single());
      },
      clearShift: async function (day) { check(await sb.from('couple_shifts').delete().eq('day', day)); },
      saveEvent: async function (ev) {
        var row = { day: ev.day, owner: ev.owner, title: ev.title, time_text: ev.time_text || null, memo: ev.memo || null };
        if (ev.id) return check(await sb.from('couple_events').update(row).eq('id', ev.id).select().single());
        return check(await sb.from('couple_events').insert(row).select().single());
      },
      deleteEvent: async function (id) { check(await sb.from('couple_events').delete().eq('id', id)); },
      loadHousing: async function () { return check(await sb.from('couple_housing_costs').select('*').order('month', { ascending: false })); },
      saveHousing: async function (row, version) {
        var r = version
          ? await sb.from('couple_housing_costs').update(row).eq('month', row.month).eq('updated_at', version).select().maybeSingle()
          : await sb.from('couple_housing_costs').insert(row).select().single();
        if ((r.error && r.error.code === '23505') || (!r.error && !r.data)) throw { code: 'conflict', message: '다른 기기에서 먼저 변경한 기록이다.' };
        return check(r);
      }
    };
  }

  // 모의 모드: localhost 에서만 동작하며 서버에 접속하지 않는다.
  function mockBackend() {
    var me = null, shifts = {}, events = [], costs = [], seq = 1;
    var t = todayStr();
    var pattern = ['D', 'D', 'E', 'E', 'N', 'N', 'OF', 'OF', 'OF'];
    for (var i = -40; i < 50; i++) shifts[addDays(t, i)] = { day: addDays(t, i), code: pattern[(i + 90) % pattern.length], updated_by: 'eun', updated_at: new Date().toISOString() };
    function mk(day, owner, title, time, memo, by) { events.push({ id: 'm' + (seq++), day: day, owner: owner, title: title, time_text: time || null, memo: memo || null, created_by: by, created_at: new Date().toISOString(), updated_by: by, updated_at: new Date().toISOString() }); }
    mk(t, 'both', '저녁 데이트', '19:00', '집 앞 파스타집 예약', 'ho');
    mk(t, 'eun', '병원 회식', '', '', 'eun');
    mk(addDays(t, 2), 'ho', '팀 워크숍', '10:00', '', 'ho');
    mk(addDays(t, 5), 'both', '양가 방문', '', '선물 챙기기', 'eun');
    mk(addDays(t, 9), 'eun', '친구 결혼식', '12:30', '', 'eun');
    function wait(v) { return new Promise(function (r) { setTimeout(function () { r(v); }, 120); }); }
    function now() { return new Date().toISOString(); }
    return {
      session: function () { return wait(me ? { mock: true } : null); },
      savedSession: function () { return null; },
      signIn: function (person) { me = person; return wait(); },
      signOut: function () { me = null; return wait(); },
      whoami: function () { return wait(me); },
      load: function (from, to) {
        return wait({
          shifts: Object.keys(shifts).filter(function (d) { return d >= from && d <= to; }).map(function (d) { return shifts[d]; }),
          events: events.filter(function (e) { return e.day >= from && e.day <= to; }).map(function (e) { return Object.assign({}, e); })
        });
      },
      setShift: function (day, code) { shifts[day] = { day: day, code: code, updated_by: me, updated_at: now() }; return wait(shifts[day]); },
      clearShift: function (day) { delete shifts[day]; return wait(); },
      saveEvent: function (ev) {
        if (ev.id) {
          var cur = events.filter(function (e) { return e.id === ev.id; })[0];
          Object.assign(cur, { day: ev.day, owner: ev.owner, title: ev.title, time_text: ev.time_text || null, memo: ev.memo || null, updated_by: me, updated_at: now() });
          return wait(Object.assign({}, cur));
        }
        var row = { id: 'm' + (seq++), day: ev.day, owner: ev.owner, title: ev.title, time_text: ev.time_text || null, memo: ev.memo || null, created_by: me, created_at: now(), updated_by: me, updated_at: now() };
        events.push(row);
        return wait(Object.assign({}, row));
      },
      deleteEvent: function (id) { events = events.filter(function (e) { return e.id !== id; }); return wait(); },
      loadHousing: function () { return wait(costs.map(function (r) { return Object.assign({}, r); })); },
      saveHousing: function (row, version) {
        var previous = costs.find(function (r) { return r.month === row.month; });
        if ((previous && previous.updated_at !== version) || (!previous && version)) return Promise.reject({ code: 'conflict' });
        var saved = Object.assign({}, row, { updated_at: now(), updated_by: me });
        costs = costs.filter(function (r) { return r.month !== row.month; }); costs.push(saved);
        return wait(Object.assign({}, saved));
      }
    };
  }

  var isMock = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && /[?&]mock\b/.test(location.search);
  var api = null;   // start()에서 만든다(라이브러리 로드 실패 시 빈 화면 대신 안내를 보이기 위해서이다)

  // ---------- 상태 ----------
  var t0 = todayStr();
  var state = {
    me: null,
    userId: null,
    verified: false,
    view: 'calendar',
    year: +t0.slice(0, 4), month: +t0.slice(5, 7),
    selected: t0,
    shifts: {},          // day -> row
    events: {},          // day -> [rows]
    range: null,
    shiftMode: false,
    brush: 'D',
    loading: false,
    seqBusy: false,
    pendingShifts: {},   // 저장 중인 교대(day -> row 또는 null=삭제). 늦게 도착한 조회 결과가 덮어쓰지 않게 한다.
    lastToday: t0
  };

  var $ = function (id) { return document.getElementById(id); };
  var els = {};

  // 캐시는 서버에서 구성원으로 확인된 계정별로 나눈다. 인증 API 응답은 캐시하지 않는다.
  var CACHE_PREFIX = 'unfade-plan-v1:', cacheEpoch = 0;
  var CACHE_TTL = 7 * 24 * 60 * 60 * 1000;
  function cacheKey(name) { return CACHE_PREFIX + (isMock ? 'mock:' : '') + state.userId + ':' + name; }
  function readCache(name) {
    if (!state.userId) return null;
    try {
      var value = JSON.parse(localStorage.getItem(cacheKey(name)));
      return value && value.at <= Date.now() && Date.now() - value.at < CACHE_TTL ? value.data : null;
    } catch (e) { return null; }
  }
  function writeCache(name, data) {
    if (!state.userId || !state.me) return;
    try {
      localStorage.setItem(cacheKey(name), JSON.stringify({ at: Date.now(), data: data }));
      var prefix = cacheKey('calendar:');
      var keys = Object.keys(localStorage).filter(function (k) { return k.indexOf(prefix) === 0; });
      keys.sort(function (a, b) {
        try { return JSON.parse(localStorage.getItem(b)).at - JSON.parse(localStorage.getItem(a)).at; } catch (e) { return 0; }
      });
      keys.slice(18).forEach(function (k) { localStorage.removeItem(k); });
    } catch (e) { /* 저장 공간이 부족해도 서버 조회와 저장을 계속한다. */ }
  }
  function clearPrivateCache() {
    ++cacheEpoch; ++loadSeq; state.verified = false;
    try { Object.keys(localStorage).filter(function (k) { return k.indexOf(CACHE_PREFIX) === 0; }).forEach(function (k) { localStorage.removeItem(k); }); } catch (e) {}
    state.shifts = {}; state.events = {}; state.pendingShifts = {}; state.range = null;
    if (window.CoupleHousing) CoupleHousing.stop();
  }
  function syncStatus(message) { els.sync.textContent = message; }
  function calendarKey() { return 'calendar:' + state.year + '-' + pad(state.month); }
  function applyData(data) {
    state.shifts = {}; state.events = {};
    data.shifts.forEach(function (s) { if (SHIFTS[s.code]) state.shifts[s.day] = s; });
    data.events.forEach(function (e) { if (PEOPLE[e.owner]) (state.events[e.day] = state.events[e.day] || []).push(e); });
    Object.keys(state.pendingShifts).forEach(function (d) { var p = state.pendingShifts[d]; if (p) state.shifts[d] = p; else delete state.shifts[d]; });
    Object.keys(state.events).forEach(function (d) { state.events[d].sort(sortEvents); });
  }
  function setView(view) {
    state.view = view;
    if (view === 'housing') state.shiftMode = false;
    $('calendar-view').classList.toggle('hidden', view !== 'calendar');
    $('housing-view').classList.toggle('hidden', view !== 'housing');
    $('calendar-tab').setAttribute('aria-pressed', String(view === 'calendar'));
    $('housing-tab').setAttribute('aria-pressed', String(view === 'housing'));
    els.shiftBtn.classList.toggle('hidden', view !== 'calendar');
    renderShiftBar();
    try { localStorage.setItem('unfade-plan-view', view); } catch (e) {}
  }
  function initHousing() {
    var epoch = cacheEpoch;
    CoupleHousing.init($('housing-view'), {
      api: api, month: state.year + '-' + pad(state.month), read: readCache,
      write: function (k, v) { if (epoch === cacheEpoch) writeCache(k, v); },
      error: handleError, verified: function () { return state.verified; },
      onMonth: function (m) { state.year = +m.slice(0, 4); state.month = +m.slice(5, 7); state.selected = m + '-01'; render(); load(); }
    });
  }

  // ---------- 화면 ----------
  function monthGrid(y, m) {
    var first = new Date(y, m - 1, 1);
    var start = addDays(ymd(first), -first.getDay());
    var days = new Date(y, m, 0).getDate();
    var weeks = Math.ceil((first.getDay() + days) / 7);
    var list = [];
    for (var i = 0; i < weeks * 7; i++) list.push(addDays(start, i));
    return list;
  }

  function applySeason() { document.documentElement.setAttribute('data-month', String(state.month)); }

  function renderHeader() {
    els.title.textContent = state.year + '년 ' + state.month + '월';
    if (state.me) {
      var p = PEOPLE[state.me];
      els.me.innerHTML = '<span class="dot" style="--c:' + p.color + '"></span>' + esc(p.name);
    }
    els.shiftBtn.classList.toggle('on', state.shiftMode);
    els.shiftBtn.textContent = state.shiftMode ? '교대 입력 중' : '교대';
  }

  function renderGrid() {
    var days = monthGrid(state.year, state.month);
    var mKey = state.year + '-' + pad(state.month);
    var t = todayStr();
    var html = '';
    days.forEach(function (d) {
      var dt = parse(d), w = dt.getDay();
      var hol = window.CoupleHolidays ? CoupleHolidays.name(d) : null;
      var sh = state.shifts[d];
      var evs = state.events[d] || [];
      var cls = ['cell'];
      if (d.slice(0, 7) !== mKey) cls.push('out');
      if (w === 0) cls.push('sun');
      if (w === 6) cls.push('sat');
      if (hol) cls.push('hol');
      if (d === t) cls.push('today');
      if (d === state.selected) cls.push('sel');
      var label = (dt.getMonth() + 1) + '월 ' + dt.getDate() + '일 ' + WEEK[w] + '요일' + (hol ? ', ' + hol : '') +
        (sh ? ', 은붕이 ' + SHIFTS[sh.code].label : '') + (evs.length ? ', 일정 ' + evs.length + '개' : '');
      var dots = evs.slice(0, 4).map(function (e) { return '<i style="--c:' + PEOPLE[e.owner].color + '"></i>'; }).join('');
      var titles = evs.slice(0, 3).map(function (e) {
        return '<span style="--c:' + PEOPLE[e.owner].color + '">' + esc((e.time_text ? e.time_text + ' ' : '') + e.title) + '</span>';
      }).join('') + (evs.length > 3 ? '<span class="more">+' + (evs.length - 3) + '</span>' : '');
      html += '<button type="button" class="' + cls.join(' ') + '" data-day="' + d + '" aria-label="' + esc(label) + '">' +
        '<span class="head"><span class="num">' + dt.getDate() + '</span><span class="dots">' + dots + '</span></span>' +
        '<span class="hname">' + esc(hol || '') + '</span>' +
        '<span class="titles">' + titles + '</span>' +
        (sh ? '<span class="shift" style="--c:' + SHIFTS[sh.code].color + '">' + sh.code + '</span>' : '<span class="shift none"></span>') +
        '</button>';
    });
    els.grid.innerHTML = html;
    els.cal.classList.toggle('loading', state.loading);
    els.cal.classList.toggle('shift-mode', state.shiftMode);
  }

  function renderDay() {
    var d = state.selected, dt = parse(d);
    var hol = window.CoupleHolidays ? CoupleHolidays.name(d) : null;
    var sh = state.shifts[d];
    var evs = state.events[d] || [];
    var html = '<div class="day-head"><h2>' + (dt.getMonth() + 1) + '월 ' + dt.getDate() + '일 ' + WEEK[dt.getDay()] + '요일</h2>' +
      (d === todayStr() ? '<span class="by">오늘</span>' : '') + (hol ? '<span class="hol">' + esc(hol) + '</span>' : '') + '</div>';
    html += '<div class="day-shift">🐰 은붕이 근무 ' + (sh
      ? '<span class="shift-chip" style="--c:' + SHIFTS[sh.code].color + '">' + sh.code + ' · ' + SHIFTS[sh.code].label + '</span>' +
        (pname(sh.updated_by) ? '<span class="by">입력 ' + esc(pname(sh.updated_by)) + '</span>' : '')
      : '<span class="by">입력 없음</span>') + '</div>';
    if (!evs.length) {
      html += '<div class="empty">등록된 일정이 없다. 함께 채워 보자 💌</div>';
    } else {
      html += '<ul class="ev-list">' + evs.map(function (e) {
        var p = PEOPLE[e.owner];
        var by = pname(e.created_by) ? '입력 ' + pname(e.created_by) : '';
        if (pname(e.updated_by) && e.updated_by !== e.created_by) by += (by ? ' · ' : '') + '수정 ' + pname(e.updated_by);
        return '<li><button type="button" class="ev" data-id="' + esc(e.id) + '" style="--c:' + p.color + '">' +
          '<span class="bar"></span><span class="who">' + p.emoji + ' ' + esc(p.name) + '</span>' +
          '<span class="ttl">' + (e.time_text ? '<span class="time">' + esc(e.time_text) + '</span>' : '') + esc(e.title) + '</span>' +
          (e.memo ? '<p class="memo">' + esc(e.memo) + '</p>' : '') +
          (by ? '<span class="by">' + esc(by) + '</span>' : '') + '</button></li>';
      }).join('') + '</ul>';
    }
    html += '<button type="button" class="add-btn" id="add-ev">＋ 일정 추가</button>';
    els.day.innerHTML = html;
  }

  function renderShiftBar() {
    els.shiftBar.classList.toggle('hidden', !state.shiftMode);
    document.body.classList.toggle('shift-mode-on', state.shiftMode);
    if (!state.shiftMode) return;
    Array.prototype.forEach.call(els.shiftBar.querySelectorAll('.brush[data-code]'), function (b) {
      b.classList.toggle('on', b.getAttribute('data-code') === state.brush);
    });
  }

  function render() { applySeason(); renderHeader(); renderGrid(); renderDay(); renderShiftBar(); }

  var toastTimer;
  function toast(msg) {
    els.toast.textContent = msg;
    els.toast.classList.remove('hidden');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { els.toast.classList.add('hidden'); }, 2200);
  }

  // ---------- 데이터 적재 ----------
  var loadSeq = 0;
  async function load() {
    if (!state.me) return;
    var days = monthGrid(state.year, state.month);
    var from = days[0], to = days[days.length - 1];
    var my = ++loadSeq;
    var epoch = cacheEpoch, key = calendarKey();
    var cached = readCache(key);
    if (cached && Array.isArray(cached.shifts) && Array.isArray(cached.events)) {
      applyData(cached); state.range = [from, to]; render();
      syncStatus('기기 저장본 · 최신 일정 확인 중');
    } else {
      if (!state.range || state.range[0] !== from) { state.shifts = {}; state.events = {}; render(); }
      syncStatus('최신 일정 확인 중…');
    }
    state.loading = true; renderGrid();
    try {
      var data = await api.load(from, to);
      if (my !== loadSeq || epoch !== cacheEpoch) return;
      writeCache(key, data);
      applyData(data);
      state.range = [from, to];
      syncStatus('최신 일정 · ' + fmtStamp(new Date().toISOString()));
    } catch (err) {
      if (my !== loadSeq) return;
      syncStatus(cached ? '기기 저장본 · 갱신 실패, 연결 후 다시 불러온다' : '일정을 불러오지 못하였다 · 연결을 확인한다');
      handleError(err, '불러오지 못했다');
    } finally {
      if (my === loadSeq) { state.loading = false; render(); }
    }
  }
  function sortEvents(a, b) {
    var ta = a.time_text ? timeKey(a.time_text) : '', tb = b.time_text ? timeKey(b.time_text) : '';
    if (ta !== tb) return ta === '' ? -1 : tb === '' ? 1 : ta < tb ? -1 : 1;
    return (a.created_at || '') < (b.created_at || '') ? -1 : 1;
  }
  function handleError(err, what) {
    var msg = (err && (err.message || err.error_description)) || '';
    if (isNetworkError(err)) { toast('인터넷 연결을 확인한다'); return; }
    if (/JWT/i.test(msg) || (err && (err.status === 401 || err.code === 'PGRST301' || err.code === '42501'))) {
      toast('다시 로그인이 필요하다');
      clearPrivateCache(); state.me = null; state.userId = null;
      showLogin();
      return;
    }
    toast(what + (msg ? ': ' + msg : ''));
  }

  function goMonth(delta) {
    var d = new Date(state.year, state.month - 1 + delta, 1);
    if (!CoupleHousing.month(d.getFullYear() + '-' + pad(d.getMonth() + 1))) return;
    state.year = d.getFullYear(); state.month = d.getMonth() + 1;
    var sel = parse(state.selected);
    var keepDay = Math.min(sel.getDate(), new Date(state.year, state.month, 0).getDate());
    state.selected = ymd(new Date(state.year, state.month - 1, keepDay));
    render(); load();
  }
  function goToday() {
    var t = todayStr();
    if (!CoupleHousing.month(t.slice(0, 7))) return;
    state.lastToday = t;
    state.year = +t.slice(0, 4); state.month = +t.slice(5, 7); state.selected = t;
    render(); load();
  }

  // ---------- 교대 입력 ----------
  // 교대 한 칸을 저장한다. code 가 'X' 이면 지운다. 성공하면 true 를 돌려준다.
  async function paintShift(day, code) {
    if (!state.verified) { toast('연결과 계정 확인 후 저장할 수 있다'); return false; }
    ++loadSeq;
    var prev = state.shifts[day];
    if (code === 'X' && !prev) return true;
    if (code !== 'X' && prev && prev.code === code) return true;
    var next = code === 'X' ? null : { day: day, code: code, updated_by: state.me, updated_at: new Date().toISOString() };
    state.pendingShifts[day] = next;
    if (next) state.shifts[day] = next; else delete state.shifts[day];
    renderGrid(); renderDay();
    try {
      if (next) state.shifts[day] = await api.setShift(day, code); else await api.clearShift(day);
      return true;
    } catch (err) {
      if (prev) state.shifts[day] = prev; else delete state.shifts[day];
      render(); handleError(err, code === 'X' ? '지우지 못했다' : '저장하지 못했다');
      return false;
    } finally {
      if (state.pendingShifts[day] === next) delete state.pendingShifts[day];
      if (state.me && !Object.keys(state.pendingShifts).length) {
        writeCache(calendarKey(), { shifts: Object.values(state.shifts), events: Object.values(state.events).flat() });
      }
    }
  }

  function parseSeq(text) {
    var tokens = [];
    var s = String(text || '').toUpperCase().replace(/[^A-Z\-]/g, ' ');
    var re = /OF|O|D|E|N|M|-/g, m;
    while ((m = re.exec(s))) tokens.push(m[0] === 'O' ? 'OF' : m[0]);
    return tokens;
  }
  async function applySeq() {
    if (state.seqBusy) return;
    var tokens = parseSeq(els.seqInput.value);
    if (!tokens.length) { toast('예: D D E E N N OF OF 처럼 입력한다'); return; }
    state.seqBusy = true;
    var btn = $('seq-apply'); btn.disabled = true;
    var start = state.selected, day = start, ok = 0, failed = false;
    try {
      for (var i = 0; i < tokens.length; i++) {
        if (tokens[i] !== '-') {
          if (await paintShift(day, tokens[i])) ok++; else { failed = true; break; }
        }
        day = addDays(day, 1);
      }
    } finally {
      state.seqBusy = false; btn.disabled = false;
    }
    if (!failed) {
      els.seqInput.value = '';
      toast(parse(start).getDate() + '일부터 ' + ok + '일 입력하였다');
    }
  }

  // ---------- 일정 입력 시트 ----------
  var editing = null;
  function openSheet(ev) {
    if (!state.verified) { toast('연결과 계정 확인 후 수정할 수 있다'); return; }
    editing = ev ? Object.assign({}, ev) : { day: state.selected, owner: state.me || 'ho', title: '', time_text: '', memo: '' };
    var e = editing;
    var meta = '';
    if (e.id) {
      if (pname(e.created_by)) meta += '입력 ' + pname(e.created_by) + ' · ' + fmtStamp(e.created_at);
      if (pname(e.updated_by) && e.updated_at !== e.created_at) meta += (meta ? ' / ' : '') + '수정 ' + pname(e.updated_by) + ' · ' + fmtStamp(e.updated_at);
    }
    els.sheet.innerHTML =
      '<h3>' + (e.id ? '일정 수정' : '새 일정') + '</h3>' + (meta ? '<p class="meta">' + esc(meta) + '</p>' : '') +
      '<div class="field"><span>누구의 일정</span><div class="seg" id="f-owner">' +
      ['eun', 'ho', 'both'].map(function (k) {
        return '<button type="button" data-owner="' + k + '" style="--c:' + PEOPLE[k].color + '" class="' + (e.owner === k ? 'on' : '') + '">' + PEOPLE[k].emoji + ' ' + PEOPLE[k].name + '</button>';
      }).join('') + '</div></div>' +
      '<div class="row2"><label class="field"><span>날짜</span><input type="date" id="f-day" value="' + esc(e.day) + '" required></label>' +
      '<label class="field"><span>시간 (선택)</span><input type="text" id="f-time" maxlength="20" placeholder="예: 19:00, 저녁" value="' + esc(e.time_text || '') + '"></label></div>' +
      '<label class="field"><span>제목</span><input type="text" id="f-title" maxlength="100" required placeholder="무엇을 하나요?" value="' + esc(e.title) + '"></label>' +
      '<label class="field"><span>메모 (선택)</span><textarea id="f-memo" maxlength="500">' + esc(e.memo || '') + '</textarea></label>' +
      '<div class="sheet-actions">' + (e.id ? '<button type="button" class="del" id="f-del">삭제</button>' : '') +
      '<button type="button" id="f-cancel">취소</button><button type="button" class="save" id="f-save">저장</button></div>';
    els.overlay.classList.remove('hidden');
    setTimeout(function () { if (!e.id) $('f-title').focus(); }, 50);
  }
  function closeSheet() { els.overlay.classList.add('hidden'); editing = null; }

  async function saveSheet() {
    var ev = {
      id: editing.id, owner: editing.owner,
      day: $('f-day').value, title: $('f-title').value.trim(),
      time_text: $('f-time').value.trim(), memo: $('f-memo').value.trim()
    };
    if (!/^\d{4}-\d{2}-\d{2}$/.test(ev.day)) { toast('날짜를 확인한다'); return; }
    if (!ev.title) { toast('제목을 입력한다'); $('f-title').focus(); return; }
    var btn = $('f-save'); btn.disabled = true; btn.textContent = '저장 중…';
    try {
      await api.saveEvent(ev);
      closeSheet();
      state.selected = ev.day;
      var d = parse(ev.day);
      if (d.getFullYear() !== state.year || d.getMonth() + 1 !== state.month) { state.year = d.getFullYear(); state.month = d.getMonth() + 1; }
      toast(ev.id ? '수정하였다' : '저장하였다 💕');
      await load();
    } catch (err) {
      btn.disabled = false; btn.textContent = '저장';
      handleError(err, '저장하지 못했다');
    }
  }
  async function deleteFromSheet() {
    if (!editing || !editing.id) return;
    if (!confirm('이 일정을 삭제할까요?')) return;
    try { await api.deleteEvent(editing.id); closeSheet(); toast('삭제하였다'); await load(); }
    catch (err) { handleError(err, '삭제하지 못했다'); }
  }

  // ---------- 로그인 ----------
  var loginPerson = defaultPerson();
  function showLogin() {
    $('boot-status').classList.add('hidden');
    els.app.classList.add('hidden');
    els.login.classList.remove('hidden');
    state.shiftMode = false; renderShiftBar();
    renderLoginPick();
  }
  function renderLoginPick() {
    Array.prototype.forEach.call(els.login.querySelectorAll('[data-person]'), function (b) {
      var k = b.getAttribute('data-person');
      b.style.setProperty('--c', PEOPLE[k].color);
      b.classList.toggle('on', k === loginPerson);
    });
    els.loginUser.value = PEOPLE[loginPerson].email;
  }
  async function doLogin(e) {
    if (e) e.preventDefault();
    var pw = els.loginPw.value;
    if (!pw) {
      // 인터넷 문제로 들어가지 못한 경우: 저장된 세션으로 다시 시도한다
      try { if (await api.session()) { els.loginErr.textContent = ''; await enter(); return; } } catch (x) {}
      els.loginErr.textContent = '비밀번호를 입력한다'; return;
    }
    els.loginGo.disabled = true; els.loginErr.textContent = '';
    try {
      await api.signIn(loginPerson, pw);
      try { localStorage.setItem(LS_PERSON, loginPerson); } catch (x) {}
      els.loginPw.value = '';
      await enter();
    } catch (err) {
      els.loginErr.textContent = isNetworkError(err) ? '인터넷 연결을 확인한다'
        : /invalid/i.test((err && err.message) || '') ? '비밀번호가 맞지 않는다' : '로그인하지 못하였다. 잠시 후 다시 시도한다';
    } finally { els.loginGo.disabled = false; }
  }
  async function enter(session) {
    var epoch = cacheEpoch;
    var me;
    try { me = await api.whoami(); }
    catch (err) {
      if (isNetworkError(err)) {
        if (state.me) { syncStatus('기기 저장본 · 오프라인, 계정 확인 후 수정할 수 있다'); return; }
        // 로그인은 유지한 채 연결 문제만 안내한다
        els.loginErr.textContent = '인터넷에 연결되지 않았다. 연결 후 "들어가기"를 누르면 다시 연다(로그인은 유지되어 있다).';
        showLogin();
        return;
      }
      throw err;
    }
    if (me !== 'eun' && me !== 'ho') {
      clearPrivateCache(); state.me = null; state.userId = null;
      await api.signOut();
      els.loginErr.textContent = '등록되지 않은 계정이다';
      showLogin();
      return;
    }
    if (epoch !== cacheEpoch) return;
    session = session || await api.session();
    if (epoch !== cacheEpoch) return;
    if (!session) { clearPrivateCache(); state.me = null; state.userId = null; showLogin(); return; }
    var nextId = session.user ? session.user.id : 'mock-' + me;
    if (state.userId && state.userId !== nextId) clearPrivateCache();
    var alreadyOpen = !!state.me && state.userId === nextId;
    state.me = me;
    state.userId = nextId;
    state.verified = true;
    writeCache('member', {person: me});
    els.loginErr.textContent = '';
    els.login.classList.add('hidden');
    els.app.classList.remove('hidden');
    $('boot-status').classList.add('hidden');
    if (!alreadyOpen) { render(); load(); initHousing(); }
    CoupleHousing.verified();
    try { setView(localStorage.getItem('unfade-plan-view') === 'housing' ? 'housing' : 'calendar'); } catch (e) { setView('calendar'); }
  }
  async function logout() {
    closeMenu();
    if (!confirm('이 기기에서 로그아웃할까요? 다시 들어오려면 비밀번호가 필요하다.')) return;
    clearPrivateCache(); closeSheet();
    state.me = null;
    state.userId = null;
    showLogin();
    await api.signOut();
  }

  function toggleMenu() { els.menu.classList.toggle('hidden'); }
  function closeMenu() { els.menu.classList.add('hidden'); }

  // ---------- 이벤트 연결 ----------
  function bind() {
    els = {
      app: $('app'), login: $('login'), title: $('m-title'), me: $('me'), shiftBtn: $('shift-btn'),
      cal: $('cal'), grid: $('grid'), day: $('day'), shiftBar: $('shift-bar'), seqInput: $('seq-input'),
      overlay: $('overlay'), sheet: $('sheet'), toast: $('toast'), menu: $('menu'),
      loginPw: $('login-pw'), loginUser: $('login-user'), loginGo: $('login-go'), loginErr: $('login-err')
    };
    els.sync = $('sync-status');
    $('calendar-tab').addEventListener('click', function () { setView('calendar'); });
    $('housing-tab').addEventListener('click', function () { setView('housing'); });
    $('prev').addEventListener('click', function () { goMonth(-1); });
    $('next').addEventListener('click', function () { goMonth(1); });
    $('today-btn').addEventListener('click', goToday);
    els.shiftBtn.addEventListener('click', function () { state.shiftMode = !state.shiftMode; render(); if (state.shiftMode) toast('근무를 고르고 날짜를 누른다'); });
    $('shift-done').addEventListener('click', function () { state.shiftMode = false; render(); });
    $('seq-apply').addEventListener('click', applySeq);
    els.seqInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') applySeq(); });
    els.shiftBar.addEventListener('click', function (e) {
      var b = e.target.closest('.brush[data-code]'); if (!b) return;
      state.brush = b.getAttribute('data-code'); renderShiftBar();
    });
    els.grid.addEventListener('click', function (e) {
      var c = e.target.closest('.cell'); if (!c) return;
      var d = c.getAttribute('data-day');
      if (state.shiftMode) { if (state.seqBusy) return; state.selected = d; paintShift(d, state.brush); return; }
      var dd = parse(d);
      if (dd.getMonth() + 1 !== state.month && !CoupleHousing.month(dd.getFullYear() + '-' + pad(dd.getMonth() + 1))) return;
      state.selected = d;
      if (dd.getMonth() + 1 !== state.month) { state.year = dd.getFullYear(); state.month = dd.getMonth() + 1; render(); load(); return; }
      renderGrid(); renderDay();
      if (window.matchMedia('(max-width: 899px)').matches) els.day.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
    els.day.addEventListener('click', function (e) {
      if (e.target.closest('#add-ev')) { openSheet(null); return; }
      var b = e.target.closest('.ev'); if (!b) return;
      var id = b.getAttribute('data-id');
      var ev = (state.events[state.selected] || []).filter(function (x) { return String(x.id) === id; })[0];
      if (ev) openSheet(ev);
    });
    els.overlay.addEventListener('click', function (e) {
      if (e.target === els.overlay) { closeSheet(); return; }
      var ob = e.target.closest('[data-owner]');
      if (ob) { editing.owner = ob.getAttribute('data-owner'); Array.prototype.forEach.call(els.sheet.querySelectorAll('[data-owner]'), function (x) { x.classList.toggle('on', x === ob); }); return; }
      if (e.target.closest('#f-cancel')) closeSheet();
      else if (e.target.closest('#f-save')) saveSheet();
      else if (e.target.closest('#f-del')) deleteFromSheet();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeSheet(); closeMenu(); }
    });
    els.me.addEventListener('click', function (e) { e.stopPropagation(); toggleMenu(); });
    document.addEventListener('click', function (e) { if (!e.target.closest('#menu')) closeMenu(); });
    $('logout').addEventListener('click', logout);
    $('refresh').addEventListener('click', function () { closeMenu(); load(); CoupleHousing.refresh(); verifyAccess(); });

    els.login.addEventListener('click', function (e) {
      var b = e.target.closest('[data-person]'); if (!b) return;
      loginPerson = b.getAttribute('data-person'); renderLoginPick(); els.loginPw.focus();
    });
    $('login-form').addEventListener('submit', doLogin);

    // 좌우로 밀어 달 이동
    var sx = 0, sy = 0, st = 0;
    els.cal.addEventListener('touchstart', function (e) { var t = e.touches[0]; sx = t.clientX; sy = t.clientY; st = Date.now(); }, { passive: true });
    els.cal.addEventListener('touchend', function (e) {
      if (state.shiftMode) return;
      var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
      if (Date.now() - st < 600 && Math.abs(dx) > 60 && Math.abs(dy) < 45) goMonth(dx < 0 ? 1 : -1);
    }, { passive: true });

    // 다시 열었을 때 최신 내용으로 갱신(상대가 입력한 내용 반영). 그사이 날짜가 바뀌었으면 오늘로 이동한다.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden || !state.me) return;
      var t = todayStr();
      if (t !== state.lastToday && !CoupleHousing.isDirty()) { state.lastToday = t; goToday(); } else if (els.overlay.classList.contains('hidden')) load();
      CoupleHousing.refresh();
      verifyAccess();
    });
    window.addEventListener('online', function () {
      if (state.me) { verifyAccess(); load(); CoupleHousing.refresh(); }
    });
    window.addEventListener('storage', function (e) {
      if (e.key !== 'unfade-couple-auth' || !state.me) return;
      var saved; try { saved = JSON.parse(e.newValue); } catch (x) {}
      if (!saved || !saved.user || saved.user.id !== state.userId) {
        clearPrivateCache(); state.me = null; state.userId = null; closeSheet(); showLogin();
      }
    });
    window.addEventListener('beforeunload', function (e) { if (CoupleHousing.isDirty()) { e.preventDefault(); e.returnValue = ''; } });
  }

  async function verifyAccess() {
    var epoch = cacheEpoch;
    try {
      var session = await api.session();
      if (epoch !== cacheEpoch) return;
      if (session) await enter(session);
      else { clearPrivateCache(); state.me = null; state.userId = null; closeSheet(); showLogin(); }
    } catch (err) { if (epoch === cacheEpoch) handleError(err, '계정을 확인하지 못했다'); }
  }

  async function start() {
    bind();
    applySeason();
    if (isMock) document.title = '[모의] ' + document.title;
    // 구 업무 일정표가 같은 주소에 남긴 데이터와 GitHub 토큰을 이 기기에서 지운다.
    try { localStorage.removeItem('ws.sync.token'); localStorage.removeItem('ws.schedule.v1'); } catch (e) {}
    try {
      if (!isMock && !(CFG.url && CFG.key && window.supabase)) throw new Error('config');
      api = isMock ? mockBackend() : supabaseBackend();
    } catch (err) {
      els.loginErr.textContent = '화면을 불러오지 못하였다. 인터넷 연결을 확인한 뒤 새로고침한다.';
      showLogin();
      return;
    }
    try {
      // 갱신 토큰의 네트워크 응답을 기다리기 전에, 같은 계정의 확인된 저장본만 표시한다.
      var saved = api.savedSession();
      if (saved && saved.user && saved.refresh_token) {
        state.userId = saved.user.id;
        var member = readCache('member');
        if (member && PEOPLE[member.person] && member.person !== 'both') {
          state.me = member.person;
          els.app.classList.remove('hidden'); $('boot-status').classList.add('hidden');
          render(); load(); initHousing();
          try { setView(localStorage.getItem('unfade-plan-view') === 'housing' ? 'housing' : 'calendar'); } catch (e) {}
        }
      }
      var s = await api.session();
      if (s) { await enter(s); return; }
      clearPrivateCache(); state.me = null; state.userId = null;
    } catch (err) {
      if (state.me && isNetworkError(err)) { syncStatus('기기 저장본 · 연결 후 최신 내역을 확인한다'); return; }
      clearPrivateCache(); state.me = null; state.userId = null;
    }
    showLogin();
  }

  if ('serviceWorker' in navigator && !isMock) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/plan/sw.js', { scope: '/plan/', updateViaCache: 'none' }).catch(function () { /* 캐시 불가 환경에서도 앱을 사용할 수 있다. */ });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
