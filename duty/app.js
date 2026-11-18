// 이 파일은 근무표 보기 화면의 동작이다. 번호 입력, 내 달력, 날짜 상세, 다른 사람, 전체 표, 설정, 관리자 화면을 그린다.
// 서버에서 받은 값은 모두 글자(textContent)로만 넣는다. 사번은 기기에 저장하지 않고 접속 토큰만 저장한다.
// 구성원 토큰은 쿠키와 localStorage에 1년 두고, 관리자 토큰은 sessionStorage에만 두어 창을 닫으면 사라지게 한다.
(function () {
  'use strict';

  var Api = window.DutyApi;
  var Theme = window.DutyTheme;
  var CFG = window.DUTY_CONFIG || {};
  var YM = CFG.ym || '2026-12';
  var MOCK = Api.mock;
  var TOKEN_KEY = MOCK ? 'duty_token_mock' : 'duty_token';
  var ADMIN_KEY = MOCK ? 'duty_admin_token_mock' : 'duty_admin_token';
  var COOKIE_PATH = '/duty/';
  // 화면이 다시 보일 때 마지막 수신 후 이 시간이 지났으면 근무표를 조용히 다시 받는다.
  var REFRESH_MS = 3 * 60 * 1000;
  if (MOCK) {
    // 시험 모드에서는 ?mock&refresh=초 로 줄일 수 있다.
    var refreshParam = new URLSearchParams(window.location.search).get('refresh');
    if (refreshParam !== null && refreshParam !== '' && isFinite(Number(refreshParam)) && Number(refreshParam) >= 0) {
      REFRESH_MS = Number(refreshParam) * 1000;
    }
  }
  var TEXT = {
    network: '연결하지 못했어요. 잠시 후 다시 시도하세요.',
    server: '서버에 문제가 생겼어요. 잠시 뒤 다시 열어 주세요.',
    draw: '화면을 그리지 못했어요. 새로 고쳐 보세요.'
  };
  var DOW = ['일', '월', '화', '수', '목', '금', '토'];

  // 근무 코드의 뜻과 색 묶음. 모르는 코드는 글자 그대로 보인다.
  var CODES = {
    D: { cat: 'd', name: '데이' },
    E: { cat: 'e', name: '이브닝' },
    N: { cat: 'n', name: '나이트' },
    S: { cat: 'off', name: '휴무' },
    OF: { cat: 'off', name: '휴무' },
    HD: { cat: 'off', name: '공휴 휴무' },
    OO: { cat: 'off', name: '슬리핑 휴무' },
    AL: { cat: 'al', name: '연차' },
    HE1: { cat: 'half', name: '반차' },
    CD: { cat: 'lv', name: '생리휴가' },
    BA: { cat: 'lv', name: '환갑 휴가' },
    EL: { cat: 'lv', name: '교육 공가' },
    '-': { cat: 'none', name: '대상 아님' }
  };
  var CODE_GUIDE = ['D', 'E', 'N', 'S', 'OF', 'HD', 'AL', 'HE1', 'CD', 'BA', 'EL', 'OO'];
  // 감점 규칙 번호의 한국어 이름. 관리자에게는 번호 대신 이름을 보인다. 모르는 번호는 번호 그대로 보인다.
  var RULE_NAMES = {
    'S-01': '들어주지 못한 희망',
    'S-02': '나이트 뒤 휴무 부족',
    'S-03': '5일 연속 근무 뒤 휴무 부족',
    'S-04': '나이트 수 초과',
    'S-04b': '나이트 수 부족',
    'S-05': '나이트 간격',
    'S-06': '역방향 복귀',
    'S-07': '같은 근무 연속',
    'S-08': '한 근무 쏠림',
    'S-09a': '나이트 형평',
    'S-09b': '주말·공휴일 근무 형평',
    'S-09c': '데이·이브닝 균형',
    'S-11': '연차 소멸 형평',
    'S-12': '말일 나이트 시작',
    'S-13a': '징검다리 근무',
    'S-13b': '토막 휴무',
    'S-13c': '하루짜리 나이트',
    'S-13d': '5일 연속 근무',
    'S-13e': '함께 쉬는 주말 없음',
    'S-13f': '떨어진 연차',
    'S-13g': '신청 휴가 전날 나이트',
    'S-13h': '주말 반차',
    'S-SHORT': '기본 휴무 부족'
  };
  var MARK_NAMES = { req: '본인 신청', cond: '조건' };

  var state = {
    token: null,
    tokenRole: null,     // 토큰을 둔 곳: 'staff'(쿠키·localStorage) | 'admin'(sessionStorage)
    data: null,
    dataKey: null,       // 받은 응답의 글자열. 다시 받은 내용이 같은지 견준다.
    todayKey: null,      // 마지막으로 그린 날의 날짜. 자정을 넘겼는지 본다.
    loadedAt: 0,         // 마지막으로 근무표를 받은 때
    loadSeq: 0,
    loading: 0,
    notice: null,        // 근무표 대신 안내 화면을 보이는 중이면 그 종류와 때
    tab: 'cal',          // cal | table | settings
    viewId: null,        // 달력에서 보고 있는 사람
    adminCand: null,     // 관리자가 고른 후보안
    lockTimer: null
  };

  // ---------- 작은 도구 ----------
  function append(el, kid) {
    if (kid == null || kid === false) return;
    if (Array.isArray(kid)) { kid.forEach(function (k) { append(el, k); }); return; }
    el.appendChild(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }

  function h(tag, props) {
    var el = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (k) {
        var v = props[k];
        if (v == null || v === false) return;
        if (k === 'class') el.className = v;
        else if (k === 'on') Object.keys(v).forEach(function (ev) { el.addEventListener(ev, v[ev]); });
        else if (k === 'style') Object.keys(v).forEach(function (p) { el.style.setProperty(p, v[p]); });
        else el.setAttribute(k, v === true ? '' : String(v));
      });
    }
    for (var i = 2; i < arguments.length; i++) append(el, arguments[i]);
    return el;
  }

  var ICONS = {
    calendar: ['M8 3v3M16 3v3M4 10h16', 'M6 5h12a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z'],
    table: ['M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z', 'M4 10h16M4 15h16M10 4v16'],
    settings: ['M4 7h9M19 7h1M4 17h1M11 17h9', 'M13 7a3 3 0 1 0 6 0a3 3 0 1 0-6 0z', 'M5 17a3 3 0 1 0 6 0a3 3 0 1 0-6 0z'],
    sun: ['M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8z', 'M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'],
    moon: ['M20 14.5A8 8 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5z'],
    left: ['M15 5l-7 7l7 7'],
    right: ['M9 5l7 7l-7 7'],
    close: ['M6 6l12 12M18 6L6 18'],
    back: ['M9 14l-4-4l4-4', 'M5 10h9a5 5 0 0 1 0 10h-3'],
    logout: ['M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4', 'M15 8l4 4l-4 4', 'M19 12H9'],
    eye: ['M2.5 12S6 5.5 12 5.5S21.5 12 21.5 12S18 18.5 12 18.5S2.5 12 2.5 12z', 'M12 9.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5z'],
    eyeOff: ['M4 4l16 16', 'M9.9 5.8A9.6 9.6 0 0 1 12 5.5c6 0 9.5 6.5 9.5 6.5a17 17 0 0 1-3 3.7M14.5 17.9a9 9 0 0 1-2.5.6C6 18.5 2.5 12 2.5 12a17 17 0 0 1 4-4.6'],
    check: ['M5 12.5l4.5 4.5L19 7.5'],
    refresh: ['M20 12a8 8 0 1 1-2.6-5.9', 'M20 4v5h-5']
  };

  function icon(name) {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('class', 'icon');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    (ICONS[name] || []).forEach(function (d) {
      var p = document.createElementNS(NS, 'path');
      p.setAttribute('d', d);
      svg.appendChild(p);
    });
    return svg;
  }

  function codeInfo(code) {
    return CODES[code] || { cat: 'etc', name: code };
  }

  function tile(code, extraClass) {
    var info = codeInfo(code);
    var text = code === '-' || code == null ? '' : String(code);
    return h('span', {
      class: 'tile cat-' + info.cat + (extraClass ? ' ' + extraClass : ''),
      'data-len': text.length >= 3 ? '3' : null
    }, text);
  }

  function reduceMotion() {
    return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  function ymParts(ym) {
    var m = /^(\d{4})-(\d{2})$/.exec(ym || '') || [];
    return { year: Number(m[1]) || 0, month: Number(m[2]) || 0 };
  }

  function prevMonthOf(ym) {
    var p = ymParts(ym);
    return p.month === 1 ? 12 : p.month - 1;
  }

  function todayParts() {
    var now = new Date();
    if (MOCK) {
      var t = /^(\d{4})-(\d{2})-(\d{2})$/.exec(new URLSearchParams(window.location.search).get('today') || '');
      if (t) return { year: Number(t[1]), month: Number(t[2]), day: Number(t[3]) };
    }
    return { year: now.getFullYear(), month: now.getMonth() + 1, day: now.getDate() };
  }

  function todayIn(ym) {
    var p = ymParts(ym);
    var t = todayParts();
    return t.year === p.year && t.month === p.month ? t.day : null;
  }

  function sortedStaff(d) {
    return (d.staff || []).slice().sort(function (a, b) { return (a.sort || 0) - (b.sort || 0); });
  }

  function nameOf(d, id) {
    var s = (d.staff || []).filter(function (p) { return p.id === id; })[0];
    return s ? s.name : (id || '');
  }

  function num(n) {
    return typeof n === 'number' && isFinite(n) ? n.toLocaleString('ko-KR') : '-';
  }

  // 점수와 감점처럼 소수로 오는 값은 정수로 반올림하여 보인다.
  function int(n) {
    return typeof n === 'number' && isFinite(n) ? Math.round(n).toLocaleString('ko-KR') : '-';
  }

  // ---------- 토큰 저장 (쿠키 + localStorage) ----------
  function readToken() {
    var t = null;
    try { t = window.localStorage.getItem(TOKEN_KEY); } catch (e) { /* 무시 */ }
    if (!t) {
      var m = new RegExp('(?:^|;\\s*)' + TOKEN_KEY + '=([^;]+)').exec(document.cookie || '');
      if (m) { try { t = decodeURIComponent(m[1]); } catch (e) { t = null; } }
    }
    return t || null;
  }

  function writeToken(token) {
    try { window.localStorage.setItem(TOKEN_KEY, token); } catch (e) { /* 무시 */ }
    document.cookie = TOKEN_KEY + '=' + encodeURIComponent(token) +
      '; Max-Age=31536000; Path=' + COOKIE_PATH + '; Secure; SameSite=Lax';
  }

  function clearToken() {
    try { window.localStorage.removeItem(TOKEN_KEY); } catch (e) { /* 무시 */ }
    document.cookie = TOKEN_KEY + '=; Max-Age=0; Path=' + COOKIE_PATH + '; Secure; SameSite=Lax';
  }

  // 관리자 토큰은 이 창에만 둔다(sessionStorage). 쿠키와 localStorage에는 쓰지 않는다.
  function readAdminToken() {
    try { return window.sessionStorage.getItem(ADMIN_KEY) || null; } catch (e) { return null; }
  }

  function writeAdminToken(token) {
    try { window.sessionStorage.setItem(ADMIN_KEY, token); } catch (e) { /* 저장하지 못하면 이번 화면에서만 쓴다. */ }
  }

  function clearAdminToken() {
    try { window.sessionStorage.removeItem(ADMIN_KEY); } catch (e) { /* 무시 */ }
  }

  function useToken(token, role) {
    state.token = token;
    state.tokenRole = role;
  }

  // 지금 쓰는 토큰만 지운다. 관리자로 접속 중이면 구성원 토큰은 그대로 둔다.
  function dropCurrentToken() {
    if (state.tokenRole === 'admin') clearAdminToken();
    else clearToken();
    state.token = null;
    state.tokenRole = null;
    state.data = null;
    state.dataKey = null;
    state.loadSeq++;
  }

  function todayKey() {
    var t = todayParts();
    return t.year + '-' + t.month + '-' + t.day;
  }

  // 누르는 동작에서 난 오류를 통신 오류와 섞지 않고 알린다.
  function guard(fn) {
    return function () {
      try {
        return fn.apply(this, arguments);
      } catch (err) {
        console.error('[duty] 화면을 그리지 못했다.', err);
        toast(TEXT.draw);
      }
    };
  }

  // ---------- 공통 화면 조각 ----------
  var appEl = document.getElementById('app');
  var toastEl = document.getElementById('toast');
  var toastTimer = null;

  function mount(node) {
    stopLockTimer();
    state.notice = null;
    while (appEl.firstChild) appEl.removeChild(appEl.firstChild);
    appEl.appendChild(node);
    appEl.removeAttribute('aria-busy');
  }

  function toast(message) {
    window.clearTimeout(toastTimer);
    toastEl.textContent = message;
    toastEl.classList.add('is-on');
    toastTimer = window.setTimeout(function () { toastEl.classList.remove('is-on'); }, 2600);
  }

  function themeButton() {
    var btn = h('button', { class: 'icon-btn js-theme-toggle', type: 'button', on: {
      click: function () { Theme.set(Theme.effective() === 'dark' ? 'light' : 'dark'); }
    } });
    paintThemeButton(btn);
    return btn;
  }

  function paintThemeButton(btn) {
    var dark = Theme.effective() === 'dark';
    while (btn.firstChild) btn.removeChild(btn.firstChild);
    btn.appendChild(icon(dark ? 'sun' : 'moon'));
    btn.setAttribute('aria-label', dark ? '밝은 화면으로 바꾸기' : '어두운 화면으로 바꾸기');
  }

  Theme.onChange(function () {
    Array.prototype.forEach.call(document.querySelectorAll('.js-theme-toggle'), paintThemeButton);
    Array.prototype.forEach.call(document.querySelectorAll('.js-theme-seg input'), function (input) {
      input.checked = input.value === Theme.pref();
    });
  });

  function openDialog(dlg, onClose) {
    var opener = document.activeElement;
    var done = false;
    document.body.appendChild(dlg);
    document.documentElement.classList.add('modal-open');

    function finish() {
      if (done) return;
      done = true;
      try { if (dlg.open && dlg.close) dlg.close(); } catch (e) { /* 무시 */ }
      if (dlg.parentNode) dlg.parentNode.removeChild(dlg);
      if (!document.querySelector('dialog[open]')) document.documentElement.classList.remove('modal-open');
      if (opener && opener.focus && document.contains(opener)) opener.focus();
      if (onClose) onClose();
    }

    function close() {
      if (done || dlg.classList.contains('is-closing')) return;
      dlg.classList.add('is-closing');
      window.setTimeout(finish, reduceMotion() ? 0 : 170);
    }

    dlg.addEventListener('cancel', function (e) { e.preventDefault(); close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
    if (typeof dlg.showModal === 'function') dlg.showModal();
    else { dlg.setAttribute('open', ''); dlg.classList.add('is-fallback'); }
    return { close: close };
  }

  function confirmDialog(opts) {
    return new Promise(function (resolve) {
      var result = false;
      var ctl;
      var cancel = h('button', { class: 'btn btn-ghost', type: 'button', on: { click: function () { ctl.close(); } } }, '취소');
      var ok = h('button', { class: 'btn ' + (opts.danger ? 'btn-danger' : 'btn-primary'), type: 'button', on: {
        click: function () { result = true; ctl.close(); }
      } }, opts.okLabel);
      var dlg = h('dialog', { class: 'modal', 'aria-labelledby': 'confirm-title' },
        h('div', { class: 'modal-body' },
          h('h2', { id: 'confirm-title', class: 'modal-title' }, opts.title),
          opts.body ? h('p', { class: 'modal-text' }, opts.body) : null,
          h('div', { class: 'modal-actions' }, cancel, ok)));
      ctl = openDialog(dlg, function () { resolve(result); });
      cancel.focus();
    });
  }

  function emptyCard(title, text, action) {
    return h('section', { class: 'empty' },
      h('div', { class: 'empty-art', 'aria-hidden': 'true' }, tile('D'), tile('E'), tile('N')),
      h('h2', { class: 'empty-title' }, title),
      text ? h('p', { class: 'empty-text' }, text) : null,
      action || null);
  }

  // ---------- 번호 입력 ----------
  function stopLockTimer() {
    if (state.lockTimer) { window.clearInterval(state.lockTimer); state.lockTimer = null; }
  }

  function renderLogin(notice) {
    var msg = h('p', { id: 'login-msg', class: 'form-msg', role: 'alert' }, notice || '');
    var timer = h('p', { class: 'lock-timer', 'aria-hidden': 'true', hidden: true });
    var input = h('input', {
      id: 'duty-code', class: 'code-input is-masked', name: 'duty-code', type: 'text',
      inputmode: 'numeric', pattern: '[0-9]*', autocomplete: 'off', autocapitalize: 'off',
      autocorrect: 'off', spellcheck: 'false', enterkeyhint: 'go', maxlength: '32',
      'aria-describedby': 'login-msg'
    });
    var reveal = h('button', { class: 'icon-btn code-reveal', type: 'button', 'aria-label': '번호 보기', 'aria-pressed': 'false', on: {
      click: function () {
        var masked = input.classList.toggle('is-masked');
        reveal.setAttribute('aria-pressed', masked ? 'false' : 'true');
        reveal.setAttribute('aria-label', masked ? '번호 보기' : '번호 숨기기');
        reveal.replaceChild(icon(masked ? 'eye' : 'eyeOff'), reveal.firstChild);
      }
    } }, icon('eye'));
    var submit = h('button', { class: 'btn btn-primary btn-block', type: 'submit' }, '들어가기');
    var busy = false;
    var lockedUntil = 0;

    function setBusy(on) {
      busy = on;
      submit.disabled = on || Date.now() < lockedUntil;
      submit.classList.toggle('is-busy', on);
      submit.textContent = on ? '접속 중…' : '들어가기';
    }

    function showLock(sec) {
      lockedUntil = Date.now() + Math.max(1, Number(sec) || 600) * 1000;
      var minutes = Math.max(1, Math.ceil((Number(sec) || 600) / 60));
      // 전체 잠금에서는 한 번도 틀리지 않은 사람도 이 문구를 본다. 이유를 단정하지 않는다.
      msg.textContent = '잠시 접속이 잠겼어요. ' + minutes + '분 뒤에 다시 넣어 주세요.';
      submit.disabled = true;
      input.disabled = true;
      timer.hidden = false;
      stopLockTimer();
      var tick = function () {
        var left = Math.ceil((lockedUntil - Date.now()) / 1000);
        if (left <= 0) {
          stopLockTimer();
          timer.hidden = true;
          input.disabled = false;
          submit.disabled = false;
          msg.textContent = '다시 입력할 수 있어요.';
          return;
        }
        timer.textContent = '남은 시간 ' + Math.floor(left / 60) + '분 ' + String(left % 60).padStart(2, '0') + '초';
      };
      tick();
      state.lockTimer = window.setInterval(tick, 1000);
    }

    var form = h('form', { class: 'login-form', novalidate: true, on: {
      submit: function (e) {
        e.preventDefault();
        if (busy || Date.now() < lockedUntil) return;
        var code = input.value.trim();
        if (!code) { msg.textContent = '사번을 입력하세요.'; input.focus(); return; }
        msg.textContent = '';
        setBusy(true);
        Api.login(code).then(function (res) {
          if (res && res.ok && res.token) {
            input.value = '';
            if (res.role === 'admin') {
              writeAdminToken(res.token);
              useToken(res.token, 'admin');
            } else {
              writeToken(res.token);
              useToken(res.token, 'staff');
            }
            loadRoster();
            return;
          }
          setBusy(false);
          var reason = res && res.reason;
          if (reason === 'locked') { input.value = ''; showLock(res.retry_after_sec); return; }
          if (reason === 'invalid') {
            msg.textContent = '번호가 맞지 않아요. 다시 입력하세요.';
            input.value = '';
            input.focus();
            return;
          }
          msg.textContent = TEXT.server;      // error 등: 번호 탓이 아니다.
        }).catch(function (err) {
          setBusy(false);
          if (err && err.kind) { msg.textContent = err.kind === 'http' ? TEXT.server : TEXT.network; return; }
          console.error('[duty] 화면을 그리지 못했다.', err);
          msg.textContent = TEXT.draw;
        });
      }
    } },
      h('label', { class: 'login-label', for: 'duty-code' }, '사번을 입력하세요'),
      h('div', { class: 'code-field' }, input, reveal),
      submit, msg, timer);

    var card = h('div', { class: 'login-card' },
      h('div', { class: 'brand', 'aria-hidden': 'true' }, tile('D'), tile('E'), tile('N')),
      h('h1', { class: 'login-title' }, '근무표'),
      form,
      MOCK ? h('p', { class: 'mock-hint' }, '시험 모드예요. 숫자를 3자리 이상 넣으면 ' + (MOCK === 'admin' ? '관리자로 ' : '') +
        '들어가요. 0000은 틀린 번호, 9999는 잠김, 8888은 연결 실패, 7777은 서버 문제예요.') : null);

    mount(h('main', { class: 'login' },
      h('div', { class: 'login-top' }, themeButton()),
      card));
    if (window.matchMedia && window.matchMedia('(hover: hover)').matches) input.focus();
  }

  // ---------- 자료 받기 ----------
  function renderLoading() {
    mount(h('main', { class: 'loading', role: 'status' },
      h('span', { class: 'spinner', 'aria-hidden': 'true' }),
      h('p', null, '근무표를 불러오는 중이에요…')));
  }

  // 근무표 대신 보이는 안내 화면. 종류: network 연결 실패, server 서버 문제, draw 그리기 실패, pending 준비 중.
  function renderNotice(kind) {
    var p = ymParts(YM);
    var copy = {
      network: ['연결하지 못했어요', '인터넷 연결을 확인하고 다시 시도하세요.', '다시 시도'],
      server: ['서버에 문제가 생겼어요', '잠시 뒤 다시 열어 주세요.', '다시 시도'],
      draw: ['화면을 그리지 못했어요', '새로 고쳐 보세요.', '새로 고침'],
      pending: [p.month + '월 근무표를 준비하고 있어요', '공개되면 여기에서 바로 볼 수 있어요.', '새로 고침']
    }[kind];
    mount(h('main', { class: 'login' },
      h('div', { class: 'login-top' }, themeButton()),
      h('div', { class: 'notice', 'data-notice': kind },
        emptyCard(copy[0], copy[1],
          h('div', { class: 'empty-actions' },
            h('button', { class: 'btn btn-primary', type: 'button', on: {
              click: function () { if (kind === 'draw') window.location.reload(); else loadRoster(); }
            } }, copy[2]),
            h('button', { class: 'btn btn-ghost', type: 'button', on: { click: function () { logout(true); } } }, '나가기'))))));
    state.notice = { kind: kind, at: Date.now() };
  }

  // 접속이 만료됐을 때: 지금 쓰던 토큰만 지우고 번호 입력으로 보낸다.
  function expireSession() {
    dropCurrentToken();
    state.tab = 'cal';
    state.viewId = null;
    state.adminCand = null;
    renderLogin('접속 정보가 만료됐어요. 번호를 다시 입력하세요.');
  }

  // 받은 근무표를 그린다. keep이면 스크롤과 표의 가로 위치를 그대로 둔다.
  function draw(keep) {
    var y = window.scrollY;
    var oldTable = document.querySelector('.rt-wrap');
    var x = oldTable ? oldTable.scrollLeft : null;
    state.todayKey = todayKey();
    if (state.data.role === 'admin') renderAdmin();
    else renderStaff();
    if (keep) {
      var table = document.querySelector('.rt-wrap');
      if (table && x !== null) table.scrollLeft = x;
      window.scrollTo(0, y);
    }
  }

  // 근무표를 받는다. silent이면 화면을 비우지 않고, 받은 내용이 같으면 다시 그리지도 않는다.
  // 결과: updated 새로 그림, same 변화 없음, expired 만료, pending 아직 없음, server 서버 문제, network 연결 실패, draw 그리기 실패, stale 그사이 다른 요청이 앞섬
  function loadRoster(opts) {
    var silent = !!(opts && opts.silent);
    var token = state.token;
    var seq = ++state.loadSeq;
    state.loading++;
    if (!silent) renderLoading();
    return Api.roster(token, YM).then(function (data) {
      if (seq !== state.loadSeq || token !== state.token) return 'stale';
      if (!data || !data.ok) {
        var reason = data && data.reason;
        if (reason === 'expired') { expireSession(); return 'expired'; }
        if (reason === 'not_found') { if (!silent) renderNotice('pending'); return 'pending'; }
        if (!silent) renderNotice('server');      // error, invalid 등: 토큰은 지우지 않는다.
        return 'server';
      }
      if (data.role === 'admin') {
        // 관리자 토큰이 쿠키·localStorage에 남아 있었다면(예전 방식) 지우고 이 창에만 둔다.
        if (state.tokenRole !== 'admin') { clearToken(); writeAdminToken(token); state.tokenRole = 'admin'; }
      } else if (state.tokenRole === 'staff') {
        writeToken(token);      // 구성원 쿠키의 기한을 새로 고친다.
      }
      var key = JSON.stringify(data);
      state.loadedAt = Date.now();
      if (silent && state.data && key === state.dataKey && todayKey() === state.todayKey) return 'same';
      state.data = data;
      state.dataKey = key;
      draw(silent);
      return 'updated';
    }).catch(function (err) {
      if (err && err.kind) {
        var kind = err.kind === 'http' ? 'server' : 'network';
        if (!silent && seq === state.loadSeq) renderNotice(kind);
        return kind;
      }
      // 통신은 됐는데 그리다가 난 오류이다.
      console.error('[duty] 화면을 그리지 못했다.', err);
      state.data = null;
      state.dataKey = null;
      renderNotice('draw');
      return 'draw';
    }).then(function (result) {
      state.loading--;
      return result;
    });
  }

  // 화면이 다시 보일 때(다른 앱에서 돌아옴, 뒤로 가기 복원): 오래됐으면 조용히 다시 받는다.
  function onReturn() {
    if (document.visibilityState === 'hidden') return;
    if (!state.token || state.loading) return;
    if (document.querySelector('dialog[open]')) return;      // 확인 창이나 날짜 상세가 열려 있으면 건너뛴다.
    if (!state.data) {
      var n = state.notice;
      if (n && n.kind !== 'draw' && Date.now() - n.at >= REFRESH_MS) loadRoster();
      return;
    }
    if (Date.now() - state.loadedAt >= REFRESH_MS) { loadRoster({ silent: true }); return; }
    if (todayKey() !== state.todayKey) {
      // 자정을 넘겼으면 "오늘" 강조만 다시 맞춘다.
      try { draw(true); } catch (err) { console.error('[duty] 화면을 그리지 못했다.', err); }
    }
  }

  document.addEventListener('visibilitychange', onReturn);
  window.addEventListener('pageshow', onReturn);

  function logout(skipConfirm) {
    var wasAdmin = state.tokenRole === 'admin';
    var go = function () {
      var token = state.token;
      dropCurrentToken();
      state.tab = 'cal';
      state.viewId = null;
      state.adminCand = null;
      if (token) Api.logout(token).catch(function () { /* 서버에 알리지 못해도 기기에서는 지운다. */ });
      // 관리자가 나가면 관리자 토큰만 지운다. 이 기기에 구성원 토큰이 있으면 구성원 화면으로 돌아간다.
      var staffToken = wasAdmin ? readToken() : null;
      if (staffToken) {
        useToken(staffToken, 'staff');
        loadRoster();
        toast('관리자 화면에서 나갔어요.');
        return;
      }
      renderLogin();
      toast('나갔어요.');
    };
    if (skipConfirm) { go(); return; }
    confirmDialog({
      title: '나갈까요?',
      body: wasAdmin ? '관리자 화면에서 나가요. 다시 들어오려면 관리자 번호를 넣어야 해요.' : '다음에 들어올 때 번호를 다시 입력해야 해요.',
      okLabel: '나가기',
      danger: true
    }).then(function (yes) { if (yes) go(); });
  }

  // ---------- 구성원 화면 ----------
  function meId() {
    var d = state.data;
    return d && d.me ? d.me.id : null;
  }

  function renderStaff() {
    var d = state.data;
    var p = ymParts(d.ym || YM);
    if (!state.viewId || !nameOf(d, state.viewId)) state.viewId = meId();

    var view = h('main', { class: 'view', id: 'view' });
    var tabs = [
      { id: 'cal', label: '달력', icon: 'calendar' },
      { id: 'table', label: '전체 표', icon: 'table' },
      { id: 'settings', label: '설정', icon: 'settings' }
    ];
    var nav = h('nav', { class: 'tabbar', 'aria-label': '화면 이동' }, tabs.map(function (t) {
      return h('button', { class: 'tab', type: 'button', 'data-tab': t.id, on: {
        click: guard(function () {
          if (t.id === 'cal' && state.tab === 'cal') state.viewId = meId();
          state.tab = t.id;
          paintStaffView(true);
        })
      } }, icon(t.icon), h('span', null, t.label));
    }));

    mount(h('div', { class: 'shell' },
      h('header', { class: 'topbar' },
        h('div', { class: 'topbar-in' },
          h('h1', { class: 'topbar-title' }, h('span', { class: 'topbar-month' }, p.month + '월'), h('span', { class: 'topbar-year' }, String(p.year))),
          themeButton())),
      view,
      h('div', { class: 'return-wrap', id: 'return-wrap' }),
      nav));
    paintStaffView(false);
  }

  function paintStaffView(scrollTop) {
    var view = document.getElementById('view');
    if (!view) return;
    var keepChips = view.querySelector('.people');
    var chipScroll = keepChips ? keepChips.scrollLeft : 0;
    while (view.firstChild) view.removeChild(view.firstChild);
    view.className = 'view' + (state.tab === 'table' ? ' view--wide' : '');
    if (view.parentNode) view.parentNode.classList.toggle('is-wide', state.tab === 'table');
    Array.prototype.forEach.call(document.querySelectorAll('.tab'), function (b) {
      if (b.getAttribute('data-tab') === state.tab) b.setAttribute('aria-current', 'page');
      else b.removeAttribute('aria-current');
    });

    if (state.tab === 'cal') append(view, calendarView());
    else if (state.tab === 'table') append(view, tableView());
    else append(view, settingsView());

    // 다른 사람의 달력을 볼 때는 내 달력으로 돌아가는 단추를 늘 보인다.
    var wrap = document.getElementById('return-wrap');
    while (wrap.firstChild) wrap.removeChild(wrap.firstChild);
    if (state.tab === 'cal' && state.viewId !== meId()) {
      wrap.appendChild(h('button', { class: 'return-pill', type: 'button', on: {
        click: guard(function () { state.viewId = meId(); paintStaffView(true); })
      } }, icon('back'), h('span', null, '내 달력으로')));
    }

    var chips = view.querySelector('.people');
    if (chips) {
      chips.scrollLeft = chipScroll;
      var on = chips.querySelector('[aria-pressed="true"]');
      if (on && on.scrollIntoView) on.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
    var rt = view.querySelector('.rt-wrap');
    if (rt) { scrollTableToStart(rt); hideHintIfFits(view, rt); }
    if (scrollTop) window.scrollTo(0, 0);
  }

  function pendingCard() {
    var p = ymParts(state.data.ym || YM);
    return emptyCard(p.month + '월 근무표를 준비하고 있어요', '공개되면 여기에서 바로 볼 수 있어요.',
      h('div', { class: 'empty-actions' },
        h('button', { class: 'btn btn-primary', type: 'button', on: { click: function () { loadRoster(); } } }, '새로 고침')));
  }

  function calendarView() {
    var d = state.data;
    if (d.status !== 'published' || !d.roster) return pendingCard();

    var me = meId();
    var pid = state.viewId || me;
    var isMe = pid === me;
    var roster = d.roster;
    var cells = (roster.cells && roster.cells[pid]) || [];
    var prev = (roster.prev && roster.prev[pid]) || [];
    var marks = (roster.marks && roster.marks[pid]) || {};
    var stats = roster.stats && roster.stats[pid];
    var p = ymParts(d.ym || YM);
    var today = todayIn(d.ym || YM);
    var out = [];

    // 사람 고르기
    var people = sortedStaff(d);
    people.sort(function (a, b) { return (a.id === me ? -1 : 0) - (b.id === me ? -1 : 0); });
    out.push(h('div', { class: 'people', role: 'group', 'aria-label': '근무표를 볼 사람' }, people.map(function (s) {
      return h('button', { class: 'chip' + (s.id === me ? ' chip-me' : ''), type: 'button',
        'aria-pressed': s.id === pid ? 'true' : 'false', on: {
          click: guard(function () { state.viewId = s.id; paintStaffView(false); })
        } }, s.id === me ? [h('span', { class: 'chip-badge' }, '나'), s.name] : s.name);
    })));

    var body = h('div', { class: 'cal-body' });
    out.push(body);

    body.appendChild(h('h2', { class: 'section-title' }, isMe ? '내 근무' : [nameOf(d, pid), h('span', { class: 'title-sub' }, ' 님의 근무')]));

    // 오늘과 내일
    if (today && cells[today - 1] != null) {
      var todayBox = h('section', { class: 'today', 'aria-label': '오늘과 내일 근무' });
      [[today, '오늘'], [today + 1, '내일']].forEach(function (pair) {
        var code = cells[pair[0] - 1];
        var day = (d.days || [])[pair[0] - 1];
        if (code == null || !day) return;
        todayBox.appendChild(h('div', { class: 'today-item' },
          tile(code),
          h('div', { class: 'today-text' },
            h('span', { class: 'today-when' }, pair[1] + ' ' + day.d + '일(' + DOW[day.dow] + ')'),
            h('strong', { class: 'today-name' }, codeInfo(code).name))));
      });
      body.appendChild(todayBox);
    }

    // 이번 달 요약
    if (stats) {
      body.appendChild(h('section', { class: 'summary', 'aria-label': '이번 달 요약' },
        h('dl', { class: 'stat-row' },
          ['D', 'E', 'N'].map(function (c) {
            return h('div', { class: 'stat' },
              h('dt', null, tile(c, 'tile-sm'), h('span', { class: 'sr-only' }, codeInfo(c).name)),
              h('dd', null, num(stats[c])));
          }),
          h('div', { class: 'stat' }, h('dt', null, h('span', { class: 'tile tile-sm cat-off', 'data-len': '3' }, '휴무')), h('dd', null, num(stats.off)))),
        h('p', { class: 'al-line' },
          h('span', { class: 'al-tag' }, tile('AL', 'tile-xs'), '연차'),
          h('span', null, h('b', null, num(stats.alUsed)), '일 사용'),
          h('span', { class: 'dot-sep', 'aria-hidden': 'true' }, '·'),
          h('span', null, h('b', null, num(stats.alLeft)), '일 남음'))));
    }

    // 달력
    var grid = h('div', { class: 'cal-grid' });
    var days = d.days || [];
    var prevDays = d.prevDays || [];
    var lead = days.length ? days[0].dow : 0;
    var pm = prevMonthOf(d.ym || YM);
    for (var k = 0; k < lead; k++) {
      var pi = prevDays.length - lead + k;
      if (pi >= 0 && prev[pi] != null) {
        var pd = prevDays[pi];
        grid.appendChild(h('div', { class: 'day day-prev', role: 'img',
          'aria-label': '지난달 ' + pm + '월 ' + pd.d + '일 ' + DOW[pd.dow] + '요일, ' + codeInfo(prev[pi]).name },
          h('span', { class: 'day-num' }, String(pd.d)), tile(prev[pi])));
      } else {
        grid.appendChild(h('div', { class: 'day day-blank', 'aria-hidden': 'true' }));
      }
    }
    days.forEach(function (day, i) {
      var code = cells[i] == null ? '-' : cells[i];
      var mark = marks[String(day.d)];
      var cls = 'day';
      if (day.dow === 0 || day.holiday) cls += ' is-sun';
      else if (day.dow === 6) cls += ' is-sat';
      if (day.d === today) cls += ' is-today';
      var label = p.month + '월 ' + day.d + '일 ' + DOW[day.dow] + '요일, ' + codeInfo(code).name +
        (mark && MARK_NAMES[mark] ? ', ' + MARK_NAMES[mark] : '') +
        (day.holiday ? ', 공휴일' : '') + (day.d === today ? ', 오늘' : '');
      grid.appendChild(h('button', { class: cls, type: 'button', 'aria-label': label, on: {
        click: guard(function () { openDay(day.d); })
      } },
        h('span', { class: 'day-num' }, String(day.d)),
        tile(code),
        mark && MARK_NAMES[mark] ? h('span', { class: 'mark mark-' + mark, 'aria-hidden': 'true' }) : null));
    });
    var tail = (7 - ((lead + days.length) % 7)) % 7;
    for (var t = 0; t < tail; t++) grid.appendChild(h('div', { class: 'day day-blank', 'aria-hidden': 'true' }));

    body.appendChild(h('section', { class: 'cal', 'aria-label': (isMe ? '내' : nameOf(d, pid) + ' 님의') + ' ' + p.month + '월 달력' },
      h('div', { class: 'cal-dow', 'aria-hidden': 'true' }, DOW.map(function (w, i) {
        return h('span', { class: i === 0 ? 'is-sun' : i === 6 ? 'is-sat' : null }, w);
      })),
      grid));

    body.appendChild(legend(false));
    return out;
  }

  function legend(forTable) {
    var items = [
      h('li', null, tile('D', 'tile-xs'), '데이'),
      h('li', null, tile('E', 'tile-xs'), '이브닝'),
      h('li', null, tile('N', 'tile-xs'), '나이트'),
      h('li', null, tile('OF', 'tile-xs'), '휴무'),
      h('li', null, tile('AL', 'tile-xs'), '연차'),
      h('li', null, tile('HE1', 'tile-xs'), '반차'),
      h('li', null, h('span', { class: 'mark-demo' }, h('span', { class: 'mark mark-req' })), '본인 신청'),
      h('li', null, h('span', { class: 'mark-demo' }, h('span', { class: 'mark mark-cond' })), '조건')
    ];
    if (forTable) {
      items.push(h('li', null, h('span', { class: 'line-demo line-week' }), '주 경계'));
      items.push(h('li', null, h('span', { class: 'line-demo line-month' }), '월 경계'));
    }
    return h('ul', { class: 'legend', 'aria-label': '표시 안내' }, items);
  }

  // ---------- 날짜 상세 ----------
  function openDay(dayNo) {
    var d = state.data;
    var roster = d.roster;
    if (!roster) return;
    var p = ymParts(d.ym || YM);
    var me = meId();
    var current = dayNo;
    var ctl;
    var body = h('div', { class: 'sheet-content' });
    var days = d.days || [];
    var cells = roster.cells || {};

    function paint() {
      var day = days[current - 1];
      while (body.firstChild) body.removeChild(body.firstChild);
      if (!day) return;
      var groups = { D: [], E: [], N: [], half: [], rest: [] };
      sortedStaff(d).forEach(function (s) {
        var code = (cells[s.id] || [])[current - 1];
        if (code == null || code === '-') return;
        if (code === 'D' || code === 'E' || code === 'N') groups[code].push({ s: s, code: code });
        else if (codeInfo(code).cat === 'half') groups.half.push({ s: s, code: code });
        else groups.rest.push({ s: s, code: code });
      });
      var rows = [
        ['D', '데이', groups.D, false],
        ['E', '이브닝', groups.E, false],
        ['N', '나이트', groups.N, false],
        ['HE1', '반차', groups.half, false],
        ['OF', '휴무', groups.rest, true]
      ];
      var prevBtn = h('button', { class: 'icon-btn', type: 'button', 'aria-label': '전날 보기', disabled: current <= 1, on: {
        click: guard(function () { if (current > 1) { current--; paint(); } })
      } }, icon('left'));
      var nextBtn = h('button', { class: 'icon-btn', type: 'button', 'aria-label': '다음 날 보기', disabled: current >= days.length, on: {
        click: guard(function () { if (current < days.length) { current++; paint(); } })
      } }, icon('right'));
      var titleCls = 'sheet-title' + (day.dow === 0 || day.holiday ? ' is-sun' : day.dow === 6 ? ' is-sat' : '');
      body.appendChild(h('div', { class: 'sheet-head' },
        prevBtn,
        h('h2', { id: 'sheet-title', class: titleCls, 'aria-live': 'polite' },
          p.month + '월 ' + day.d + '일 ' + DOW[day.dow] + '요일',
          day.holiday ? h('span', { class: 'badge badge-holiday' }, '공휴일') : null),
        nextBtn));
      var list = h('dl', { class: 'who' });
      rows.forEach(function (r) {
        var people = r[2];
        if (r[0] === 'HE1' && !people.length) return;
        list.appendChild(h('div', { class: 'who-row' },
          h('dt', null, r[3] ? h('span', { class: 'tile tile-sm cat-off', 'aria-hidden': 'true' }, '휴') : tile(r[0], 'tile-sm'), h('span', null, r[1]),
            h('span', { class: 'who-count' }, people.length + '명')),
          h('dd', null, people.length ? people.map(function (x) {
            return h('span', { class: 'name-chip' + (x.s.id === me ? ' is-me' : '') },
              x.s.name,
              x.s.id === me ? h('span', { class: 'chip-badge' }, '나') : null,
              r[3] ? h('span', { class: 'name-code cat-' + codeInfo(x.code).cat }, x.code) : null);
          }) : h('span', { class: 'who-none' }, '없어요'))));
      });
      body.appendChild(list);
      if (document.activeElement === document.body && closeBtn) closeBtn.focus();
    }

    var closeBtn = h('button', { class: 'btn btn-ghost btn-block', type: 'button', on: { click: function () { ctl.close(); } } }, '닫기');
    var dlg = h('dialog', { class: 'sheet', 'aria-labelledby': 'sheet-title' },
      h('div', { class: 'sheet-body' },
        h('div', { class: 'sheet-grab', 'aria-hidden': 'true' }),
        body,
        closeBtn));
    paint();
    ctl = openDialog(dlg);
  }

  // ---------- 전체 표 ----------
  function rosterTable(d, sheet, highlightId) {
    var days = d.days || [];
    var prevDays = d.prevDays || [];
    var staff = sortedStaff(d);
    var today = todayIn(d.ym || YM);
    var p = ymParts(d.ym || YM);
    var pm = prevMonthOf(d.ym || YM);
    var cells = sheet.cells || {};
    var prev = sheet.prev || {};
    var marks = sheet.marks || {};

    function colClass(day, isPrev, index) {
      var c = [];
      if (isPrev) c.push('is-prev');
      if (day.dow === 0 || day.dow === 6 || day.holiday) c.push('is-weekend');
      if (day.dow === 0 && !(isPrev && index === 0)) c.push('wk-start');
      if (!isPrev && index === 0) c.push('mo-start');
      if (!isPrev && day.d === today) c.push('is-today');
      return c.join(' ');
    }

    var headRow = h('tr', null, h('th', { class: 'rt-name rt-corner', scope: 'col' }, '이름'));
    prevDays.forEach(function (day, i) {
      headRow.appendChild(h('th', { class: 'rt-date ' + colClass(day, true, i), scope: 'col', 'aria-label': pm + '월 ' + day.d + '일 ' + DOW[day.dow] + '요일' },
        h('span', { class: 'rt-d' }, String(day.d)),
        h('span', { class: 'rt-w' + (day.dow === 0 ? ' is-sun' : day.dow === 6 ? ' is-sat' : '') }, DOW[day.dow])));
    });
    days.forEach(function (day, i) {
      headRow.appendChild(h('th', { class: 'rt-date ' + colClass(day, false, i), scope: 'col', 'data-day': String(day.d),
        'aria-label': p.month + '월 ' + day.d + '일 ' + DOW[day.dow] + '요일' + (day.holiday ? ' 공휴일' : '') },
        h('span', { class: 'rt-d' + (day.dow === 0 || day.holiday ? ' is-sun' : day.dow === 6 ? ' is-sat' : '') }, String(day.d)),
        h('span', { class: 'rt-w' + (day.dow === 0 || day.holiday ? ' is-sun' : day.dow === 6 ? ' is-sat' : '') }, DOW[day.dow])));
    });

    var tbody = h('tbody');
    staff.forEach(function (s) {
      var isMe = s.id === highlightId;
      var tr = h('tr', { class: isMe ? 'is-me' : null },
        h('th', { class: 'rt-name', scope: 'row' }, h('span', { class: 'rt-name-in' }, s.name)));
      prevDays.forEach(function (day, i) {
        var code = (prev[s.id] || [])[i];
        tr.appendChild(h('td', { class: colClass(day, true, i) }, code == null ? null : cellChip(code, null)));
      });
      days.forEach(function (day, i) {
        var code = (cells[s.id] || [])[i];
        var mark = (marks[s.id] || {})[String(day.d)];
        tr.appendChild(h('td', { class: colClass(day, false, i) }, code == null ? null : cellChip(code, mark)));
      });
      tbody.appendChild(tr);
    });

    var tfoot = h('tfoot');
    ['D', 'E', 'N'].forEach(function (shift) {
      var tr = h('tr', null, h('th', { class: 'rt-name', scope: 'row' },
        h('span', { class: 'rt-name-in' }, tile(shift, 'tile-xs'), h('span', { class: 'rt-foot-label' }, '인원'), h('span', { class: 'sr-only' }, codeInfo(shift).name))));
      var count = function (source, i) {
        var n = 0;
        staff.forEach(function (s) { if ((source[s.id] || [])[i] === shift) n++; });
        return n;
      };
      prevDays.forEach(function (day, i) {
        tr.appendChild(h('td', { class: 'rt-count ' + colClass(day, true, i) }, String(count(prev, i))));
      });
      days.forEach(function (day, i) {
        tr.appendChild(h('td', { class: 'rt-count ' + colClass(day, false, i) }, String(count(cells, i))));
      });
      tfoot.appendChild(tr);
    });

    return h('div', { class: 'rt-wrap', tabindex: '0', role: 'region', 'aria-label': '전체 근무표. 옆으로 밀어서 보세요.' },
      h('table', { class: 'rt' },
        h('caption', { class: 'sr-only' }, p.year + '년 ' + p.month + '월 전체 근무표'),
        h('thead', null, headRow), tbody, tfoot));
  }

  function cellChip(code, mark) {
    var info = codeInfo(code);
    var text = code === '-' ? '' : String(code);
    var known = mark && MARK_NAMES[mark];
    return h('span', { class: 'cc cat-' + info.cat, 'data-len': text.length >= 3 ? '3' : null,
      title: info.name + (known ? ' · ' + MARK_NAMES[mark] : '') },
      text,
      known ? h('span', { class: 'mark mark-' + mark, 'aria-hidden': 'true' }) : null,
      known ? h('span', { class: 'sr-only' }, ' ' + MARK_NAMES[mark]) : null);
  }

  // 표를 처음 열면 이번 달 1일(오늘이 이번 달이면 오늘)이 이름 열 바로 옆에 오게 한다.
  function scrollTableToStart(wrap) {
    var today = todayIn(state.data.ym || YM);
    var target = wrap.querySelector('th[data-day="' + (today || 1) + '"]');
    var nameCol = wrap.querySelector('th.rt-corner');
    if (!target || !nameCol) return;
    var left = target.offsetLeft - nameCol.offsetWidth - (today ? target.offsetWidth : 0);
    wrap.scrollLeft = Math.max(0, left);
  }

  // 표가 한 화면에 다 들어오면 "옆으로 밀어서" 안내를 숨긴다.
  function hideHintIfFits(root, wrap) {
    var hint = root.querySelector('.js-scroll-hint');
    if (hint) hint.hidden = wrap.scrollWidth <= wrap.clientWidth + 1;
  }

  function tableView() {
    var d = state.data;
    if (d.status !== 'published' || !d.roster) return pendingCard();
    return [
      h('div', { class: 'view-head' },
        h('h2', { class: 'section-title' }, '전체 표'),
        h('p', { class: 'view-hint js-scroll-hint' }, '옆으로 밀어서 보세요.')),
      rosterTable(d, d.roster, meId()),
      legend(true)
    ];
  }

  // ---------- 설정 ----------
  function themeSegment() {
    var opts = [['system', '기기 설정'], ['light', '밝게'], ['dark', '어둡게']];
    return h('div', { class: 'seg js-theme-seg', role: 'radiogroup', 'aria-label': '화면 모드' }, opts.map(function (o) {
      var input = h('input', { type: 'radio', name: 'duty-theme', value: o[0], id: 'theme-' + o[0], class: 'seg-input', on: {
        change: function () { Theme.set(o[0]); }
      } });
      input.checked = Theme.pref() === o[0];
      return [input, h('label', { class: 'seg-label', for: 'theme-' + o[0] }, o[1])];
    }));
  }

  // 설정의 "새로 고침": 홈 화면에 추가한 앱에는 브라우저의 새로 고침이 없어서 둔다.
  function refreshNow(btn) {
    btn.disabled = true;
    btn.classList.add('is-busy');
    loadRoster({ silent: true }).then(function (result) {
      if (result === 'updated') toast('근무표를 새로 받았어요.');
      else if (result === 'same') toast('이미 최신 근무표예요.');
      else if (result === 'network') toast(TEXT.network);
      else if (result === 'server') toast(TEXT.server);
      else if (result === 'pending') { state.data = null; state.dataKey = null; renderNotice('pending'); }
      if (document.contains(btn)) { btn.disabled = false; btn.classList.remove('is-busy'); }
    });
  }

  function settingsView() {
    var d = state.data;
    var publishedAt = d.status === 'published' && d.roster ? fmtDateTime(d.roster.publishedAt) : '';
    var refreshBtn = h('button', { class: 'btn btn-ghost btn-block', type: 'button', on: {
      click: function () { refreshNow(refreshBtn); }
    } }, icon('refresh'), '새로 고침');
    return [
      h('h2', { class: 'section-title' }, '설정'),
      d.me ? h('section', { class: 'card profile' },
        h('span', { class: 'avatar', 'aria-hidden': 'true' }, String(d.me.name || '').slice(0, 1)),
        h('div', null, h('strong', { class: 'profile-name' }, d.me.name, h('span', { class: 'title-sub' }, ' 님')),
          h('p', { class: 'profile-sub' }, '이 기기에서 접속 중이에요.'))) : null,
      h('section', { class: 'card' },
        h('h3', { class: 'card-title' }, '근무표'),
        h('p', { class: 'pub-line' }, d.status !== 'published' || !d.roster ? '아직 공개 전이에요.'
          : publishedAt ? publishedAt + ' 공개' : '공개된 근무표예요.'),
        refreshBtn),
      h('section', { class: 'card' },
        h('h3', { class: 'card-title' }, '화면 모드'),
        themeSegment()),
      h('section', { class: 'card' },
        h('h3', { class: 'card-title' }, '근무 코드 안내'),
        h('ul', { class: 'code-list' }, CODE_GUIDE.map(function (c) {
          return h('li', null, tile(c, 'tile-sm'), h('span', null, codeInfo(c).name));
        }))),
      h('button', { class: 'btn btn-outline btn-block', type: 'button', on: { click: function () { logout(false); } } }, icon('logout'), '나가기')
    ];
  }

  // ---------- 관리자 화면 ----------
  function candById(id) {
    return ((state.data && state.data.candidates) || []).filter(function (c) { return c.id === id; })[0] || null;
  }

  // 감점을 규칙별로 묶는다. 감점 합계가 큰 순(같으면 건수가 많은 순)으로 둔다.
  function softGroups(cand) {
    var byRule = {};
    var groups = [];
    (cand.soft || []).forEach(function (v) {
      var key = v && v.rule ? String(v.rule) : '기타';
      var g = byRule[key];
      if (!g) {
        g = byRule[key] = { rule: key, name: RULE_NAMES[key] || key, count: 0, penalty: 0, hasPenalty: false, items: [] };
        groups.push(g);
      }
      g.count++;
      g.items.push(v);
      if (typeof v.penalty === 'number' && isFinite(v.penalty)) { g.penalty += v.penalty; g.hasPenalty = true; }
    });
    return groups.sort(function (a, b) { return (b.penalty - a.penalty) || (b.count - a.count); });
  }

  // 토·일·공휴일에 D·E·N으로 일한 날 수. 응답에 없어서 화면이 센다.
  function weekendWork(d, cand, staffId) {
    var row = (cand.cells && cand.cells[staffId]) || [];
    var n = 0;
    (d.days || []).forEach(function (day, i) {
      var off = day.dow === 0 || day.dow === 6 || day.holiday;
      if (off && (row[i] === 'D' || row[i] === 'E' || row[i] === 'N')) n++;
    });
    return n;
  }

  function fmtDateTime(iso) {
    var dt = iso ? new Date(iso) : null;
    if (!dt || isNaN(dt.getTime())) return '';
    try {
      return new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(dt);
    } catch (e) {
      return (dt.getMonth() + 1) + '월 ' + dt.getDate() + '일';
    }
  }

  function renderAdmin() {
    var d = state.data;
    var p = ymParts(d.ym || YM);
    var cands = (d.candidates || []).slice().sort(function (a, b) { return (a.rank || 0) - (b.rank || 0); });
    if (!candById(state.adminCand)) state.adminCand = d.publishedId && candById(d.publishedId) ? d.publishedId : (cands[0] ? cands[0].id : null);
    var published = d.publishedId ? candById(d.publishedId) : null;
    var s = d.search || {};

    var status = h('section', { class: 'pub-status' + (published ? ' is-on' : '') },
      h('div', { class: 'pub-text' },
        h('span', { class: 'pub-dot', 'aria-hidden': 'true' }),
        h('div', null,
          h('strong', null, published ? published.label + ' 공개 중' : '아직 공개하지 않았어요'),
          h('p', null, published
            ? (fmtDateTime(d.roster && d.roster.publishedAt) ? fmtDateTime(d.roster.publishedAt) + '에 공개했어요. ' : '') + '구성원이 이 표를 보고 있어요.'
            : '후보안을 골라 공개하면 구성원이 볼 수 있어요.'))),
      published ? h('button', { class: 'btn btn-outline', type: 'button', on: { click: function () { askUnpublish(published); } } }, '공개 취소') : null);

    var list = h('div', { class: 'cand-list', role: 'radiogroup', 'aria-label': '후보안', 'data-count': String(cands.length) }, cands.map(function (c) {
      var m = c.metrics || {};
      var groups = softGroups(c);
      var softCount = (c.soft || []).length;
      var input = h('input', { type: 'radio', name: 'duty-cand', class: 'cand-input', id: 'cand-' + c.id, value: c.id, on: {
        change: guard(function () { state.adminCand = c.id; paintAdminDetail(true); })
      } });
      input.checked = c.id === state.adminCand;
      return h('div', { class: 'cand' },
        input,
        h('label', { class: 'cand-card', for: 'cand-' + c.id },
          h('span', { class: 'cand-top' },
            h('span', { class: 'cand-label' }, c.label || c.id),
            c.id === d.publishedId ? h('span', { class: 'badge badge-live' }, '공개 중') : null,
            h('span', { class: 'cand-check', 'aria-hidden': 'true' }, icon('check'))),
          h('span', { class: 'cand-score' },
            h('span', { class: 'cand-score-num' }, int(c.score)),
            h('span', { class: 'cand-score-unit' }, '점 · 낮을수록 좋아요')),
          h('span', { class: 'cand-metrics' },
            h('span', { class: 'metric' }, h('span', { class: 'metric-k' }, '신청 반영'), h('span', { class: 'metric-v' }, num(m.wantMet) + '/' + num(m.wantTotal))),
            h('span', { class: 'metric' }, h('span', { class: 'metric-k' }, '나이트'), h('span', { class: 'metric-v' }, m.nightsMin === m.nightsMax ? num(m.nightsMin) + '개' : num(m.nightsMin) + '~' + num(m.nightsMax) + '개')),
            h('span', { class: 'metric' }, h('span', { class: 'metric-k' }, '남는 연차'), h('span', { class: 'metric-v' }, '최대 ' + num(m.alLeftMax) + '일'))),
          // 감점 요약: 가장 큰 항목 3개만 보이고 나머지는 "외 n종"으로 줄인다.
          h('span', { class: 'cand-soft' },
            h('span', { class: 'cand-soft-head' }, softCount ? '감점 ' + num(softCount) + '건' : '감점 없음'),
            groups.slice(0, 3).map(function (g) {
              return h('span', { class: 'cand-soft-row' },
                h('span', { class: 'cand-soft-name' }, g.name),
                h('span', { class: 'cand-soft-n' }, num(g.count) + '건'));
            }),
            groups.length > 3 ? h('span', { class: 'cand-soft-more' }, '외 ' + (groups.length - 3) + '종') : null)));
    }));

    mount(h('div', { class: 'admin' },
      h('header', { class: 'topbar' },
        h('div', { class: 'topbar-in' },
          h('h1', { class: 'topbar-title' }, h('span', { class: 'topbar-month' }, '근무표 관리'), h('span', { class: 'topbar-year' }, p.year + '년 ' + p.month + '월')),
          h('div', { class: 'topbar-actions' },
            themeButton(),
            h('button', { class: 'icon-btn', type: 'button', 'aria-label': '나가기', on: { click: function () { logout(false); } } }, icon('logout'))))),
      h('main', { class: 'admin-main' },
        status,
        h('section', { class: 'admin-block' },
          h('div', { class: 'view-head' },
            h('h2', { class: 'section-title' }, '후보안'),
            typeof s.restarts === 'number' ? h('p', { class: 'view-hint' },
              num(s.restarts) + '번 탐색해서 유효한 표 ' + num(s.feasible) + '개를 찾았어요' +
              (typeof s.distinctFeasible === 'number' ? ' (서로 다른 표 ' + num(s.distinctFeasible) + '개).' : '.')) : null),
          cands.length ? list : emptyCard('후보안이 아직 없어요', '편성 결과를 올리면 여기에서 볼 수 있어요.')),
        h('section', { class: 'admin-detail', id: 'admin-detail', 'aria-label': '고른 후보안' }))));
    paintAdminDetail(false);
  }

  function issueList(d, items, emptyText) {
    if (!items || !items.length) return h('p', { class: 'issue-empty' }, emptyText);
    return h('ul', { class: 'issue-list' }, items.map(function (v) {
      var who = v.staff ? nameOf(d, v.staff) : '';
      var when = v.date != null ? v.date + '일' : '';
      return h('li', null,
        who || when ? h('span', { class: 'issue-meta' },
          who ? h('strong', null, who) : null,
          when ? h('span', { class: 'issue-date' }, when) : null) : null,
        h('span', { class: 'issue-text' }, v.text || ''));
    }));
  }

  // 감점 목록: 규칙별로 묶어 접고 편다. 처음에는 모두 접혀 있다.
  function softGroupList(d, cand) {
    var groups = softGroups(cand);
    if (!groups.length) return h('p', { class: 'issue-empty' }, '감점이 없어요.');
    return h('div', { class: 'grp-list' }, groups.map(function (g) {
      return h('details', { class: 'grp' },
        h('summary', { class: 'grp-sum' },
          h('span', { class: 'grp-text' },
            h('span', { class: 'grp-name' }, g.name),
            h('span', { class: 'grp-meta' }, num(g.count) + '건' + (g.hasPenalty ? ' · 감점 ' + int(g.penalty) + '점' : ''))),
          h('span', { class: 'grp-chev', 'aria-hidden': 'true' }, icon('right'))),
        issueList(d, g.items, ''));
    }));
  }

  function statsTable(d, cand) {
    var stats = cand.stats || {};
    var stat = function (key) { return function (s) { return (stats[s.id] || {})[key]; }; };
    var cols = [
      { label: 'D', get: stat('D') },
      { label: 'E', get: stat('E') },
      { label: 'N', get: stat('N') },
      { label: '근무', get: stat('work') },
      { label: ['주말·', h('wbr'), '공휴'], full: '주말·공휴일 근무', get: function (s) { return weekendWork(d, cand, s.id); } },
      { label: '휴무', get: stat('off') },
      { label: '쓴 연차', get: stat('alUsed') },
      { label: '남는 연차', get: stat('alLeft') }
    ];
    return h('div', { class: 'st-wrap', tabindex: '0', role: 'region', 'aria-label': '개인별 집계' },
      h('table', { class: 'st' },
        h('thead', null, h('tr', null, h('th', { scope: 'col', class: 'st-name' }, '이름'), cols.map(function (c) {
          return h('th', { scope: 'col', 'aria-label': c.full || null, title: c.full || null }, c.label);
        }))),
        h('tbody', null, sortedStaff(d).map(function (s) {
          return h('tr', null, h('th', { scope: 'row', class: 'st-name' }, s.name), cols.map(function (c) {
            return h('td', null, num(c.get(s)));
          }));
        }))));
  }

  function paintAdminDetail(scrollIntoView) {
    var box = document.getElementById('admin-detail');
    if (!box) return;
    var d = state.data;
    while (box.firstChild) box.removeChild(box.firstChild);
    var cand = candById(state.adminCand);
    if (!cand) return;
    var isLive = cand.id === d.publishedId;
    var other = d.publishedId && !isLive ? candById(d.publishedId) : null;

    var table = rosterTable(d, cand, null);
    append(box, [
      h('div', { class: 'view-head' },
        h('h2', { class: 'section-title' }, (cand.label || cand.id) + ' 살펴보기'),
        h('p', { class: 'view-hint js-scroll-hint' }, '표는 옆으로 밀어서 보세요.')),
      table,
      legend(true),
      h('div', { class: 'detail-grid' },
        h('section', { class: 'card' }, h('h3', { class: 'card-title' }, '개인별 집계'), statsTable(d, cand)),
        h('div', { class: 'detail-col' },
          h('section', { class: 'card' },
            h('h3', { class: 'card-title' }, '감점 목록', h('span', { class: 'count-pill' }, String((cand.soft || []).length)),
              h('span', { class: 'card-title-note' }, '눌러서 펼쳐 보세요')),
            softGroupList(d, cand)),
          h('section', { class: 'card' },
            h('h3', { class: 'card-title' }, '들어주지 못한 신청', h('span', { class: 'count-pill' }, String((cand.unmet || []).length))),
            issueList(d, cand.unmet, '모든 신청을 반영했어요.')),
          h('section', { class: 'card' },
            h('h3', { class: 'card-title' }, '인간미 검토 기록'),
            issueList(d, cand.humanNotes, '기록이 없어요.')))),
      h('div', { class: 'publish-bar' },
        h('div', { class: 'publish-in' },
          h('p', { class: 'publish-note' }, isLive ? '지금 구성원에게 공개 중인 안이에요.' : other ? '지금은 ' + other.label + '이 공개 중이에요.' : '아직 공개한 안이 없어요.'),
          isLive
            ? h('button', { class: 'btn btn-outline', type: 'button', on: { click: function () { askUnpublish(cand); } } }, '공개 취소')
            : h('button', { class: 'btn btn-primary', type: 'button', on: { click: function () { askPublish(cand, other); } } }, '이 안을 구성원에게 공개')))
    ]);
    scrollTableToStart(table);
    hideHintIfFits(box, table);
    if (scrollIntoView && box.scrollIntoView && window.matchMedia && window.matchMedia('(max-width: 899px)').matches) {
      box.scrollIntoView({ block: 'start', behavior: reduceMotion() ? 'auto' : 'smooth' });
    }
  }

  function publish(candId, doneText) {
    var token = state.token;
    return Api.publish(token, YM, candId).then(function (res) {
      if (token !== state.token) return;
      if (!res || !res.ok) {
        var reason = res && res.reason;
        if (reason === 'expired') { expireSession(); return; }
        if (reason === 'forbidden') { toast('관리자만 할 수 있어요.'); return; }
        if (reason === 'error' || reason === 'invalid') { toast(TEXT.server); return; }
        toast(candId ? '공개하지 못했어요. 다시 시도하세요.' : '공개를 취소하지 못했어요. 다시 시도하세요.');
        return;
      }
      toast(doneText);
      return loadRoster({ silent: true }).then(function (result) {
        // 다시 받지 못했으면 가진 자료에서 공개 상태만 고쳐 그린다.
        if ((result === 'network' || result === 'server' || result === 'pending') && state.data) {
          state.data.publishedId = res.published || null;
          state.dataKey = null;
          draw(true);
        }
      });
    }).catch(function (err) {
      if (err && err.kind) { toast(err.kind === 'http' ? TEXT.server : TEXT.network); return; }
      console.error('[duty] 화면을 그리지 못했다.', err);
      toast(TEXT.draw);
    });
  }

  function askPublish(cand, other) {
    confirmDialog({
      title: cand.label + '을 공개할까요?',
      body: (other ? '지금 공개 중인 ' + other.label + ' 대신 ' : '') + '구성원 모두가 이 표를 바로 보게 돼요.',
      okLabel: '공개'
    }).then(function (yes) { if (yes) publish(cand.id, cand.label + '을 공개했어요.'); });
  }

  function askUnpublish(cand) {
    confirmDialog({
      title: '공개를 취소할까요?',
      body: '구성원에게는 "준비하고 있어요" 화면이 보여요.',
      okLabel: '공개 취소',
      danger: true
    }).then(function (yes) { if (yes) publish(null, cand.label + ' 공개를 취소했어요.'); });
  }

  // ---------- 시작 ----------
  function framed() {
    try { return window.top !== window.self; } catch (e) { return true; }
  }

  function boot() {
    // 다른 사이트의 틀(프레임) 안에서는 화면을 그리지 않는다.
    if (framed()) {
      mount(h('p', { class: 'boot' }, '새 창에서 열어 주세요.'));
      return;
    }
    // 이 창의 관리자 토큰을 먼저 보고, 없으면 기기에 둔 구성원 토큰을 본다.
    var adminToken = readAdminToken();
    if (adminToken) { useToken(adminToken, 'admin'); loadRoster(); return; }
    // 시험 모드의 ?mock=admin은 관리자 화면을 보려는 것이므로 구성원 토큰으로 들어가지 않는다.
    var staffToken = MOCK === 'admin' ? null : readToken();
    if (staffToken) { useToken(staffToken, 'staff'); loadRoster(); return; }
    renderLogin();
  }

  boot();
})();
