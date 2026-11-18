// 이 파일은 근무표 화면의 서버 호출을 맡는다.
// 실제 서버: POST {url}/rest/v1/rpc/<함수명> (Supabase 함수 duty_*).
// 시험 모드: localhost에서 주소에 ?mock을 붙이면 서버 없이 mock-data.js의 가짜 자료로 같은 모양의 응답을 돌려준다.
//   ?mock          구성원 화면      ?mock=admin   관리자 화면
//   ?mock=pending  공개 전 화면     ?mock=error   근무표를 받지 못하는 화면
(function () {
  'use strict';

  var cfg = window.DUTY_CONFIG || {};
  var params = new URLSearchParams(window.location.search);
  var isLocal = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(window.location.hostname);
  var mockMode = isLocal && params.has('mock') ? (params.get('mock') || 'staff') : null;
  var TIMEOUT_MS = 15000;

  function fail(kind) {
    var err = new Error(kind);
    err.kind = kind;            // 'network' 연결 실패, 'http' 서버 응답 이상
    return err;
  }

  // ---- 실제 서버 ----
  function rpc(name, args) {
    var ctrl = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = ctrl ? window.setTimeout(function () { ctrl.abort(); }, TIMEOUT_MS) : null;
    return window.fetch(cfg.url + '/rest/v1/rpc/' + name, {
      method: 'POST',
      headers: {
        apikey: cfg.key,
        Authorization: 'Bearer ' + cfg.key,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(args),
      cache: 'no-store',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      signal: ctrl ? ctrl.signal : undefined
    }).then(function (res) {
      if (!res.ok) throw fail('http');
      return res.json().catch(function () { throw fail('http'); });
    }, function () {
      throw fail('network');
    }).then(function (body) {
      if (!body || typeof body !== 'object') throw fail('http');
      return body;
    }).finally(function () {
      if (timer) window.clearTimeout(timer);
    });
  }

  var real = {
    login: function (code) { return rpc('duty_login', { p_code: code }); },
    me: function (token) { return rpc('duty_me', { p_token: token }); },
    roster: function (token, ym) { return rpc('duty_roster', { p_token: token, p_ym: ym }); },
    publish: function (token, ym, candidate) {
      return rpc('duty_publish', { p_token: token, p_ym: ym, p_candidate: candidate });
    },
    logout: function (token) { return rpc('duty_logout', { p_token: token }); }
  };

  // ---- 시험 모드 ----
  var MOCK_STAFF_TOKEN = 'mock.staff';
  var MOCK_ADMIN_TOKEN = 'mock.admin';
  var PUBLISHED_KEY = 'duty_mock_published';
  var mockLoading = null;

  function loadMock() {
    if (!mockLoading) {
      mockLoading = new Promise(function (resolve, reject) {
        if (window.DUTY_MOCK) { resolve(window.DUTY_MOCK); return; }
        var s = document.createElement('script');
        s.src = 'mock-data.js';
        s.onload = function () { resolve(window.DUTY_MOCK); };
        s.onerror = function () { reject(fail('network')); };
        document.head.appendChild(s);
      });
    }
    return mockLoading;
  }

  function later(make) {
    return loadMock().then(function (db) {
      return new Promise(function (resolve, reject) {
        window.setTimeout(function () {
          try { resolve(make(db)); } catch (e) { reject(e); }
        }, 320);
      });
    });
  }

  function clone(v) { return JSON.parse(JSON.stringify(v)); }

  function mockPublished(db) {
    var v = null;
    try { v = window.sessionStorage.getItem(PUBLISHED_KEY); } catch (e) { /* 무시 */ }
    if (v === 'none') return null;
    if (v && db.candidates.some(function (c) { return c.id === v; })) return v;
    return db.candidates[0].id;
  }

  function setMockPublished(id) {
    try { window.sessionStorage.setItem(PUBLISHED_KEY, id || 'none'); } catch (e) { /* 무시 */ }
  }

  function mockRole(token) {
    if (token !== MOCK_STAFF_TOKEN && token !== MOCK_ADMIN_TOKEN) return null;
    // 시험 모드에서는 주소의 ?mock 값이 역할을 정한다.
    return mockMode === 'admin' ? 'admin' : 'staff';
  }

  function mockMe(db) {
    var s = db.staff.filter(function (p) { return p.id === db.meId; })[0];
    return { id: s.id, name: s.name };
  }

  var mock = {
    login: function (code) {
      return later(function (db) {
        var c = String(code == null ? '' : code).trim();
        if (c === '8888') throw fail('network');
        if (c === '9999') return { ok: false, reason: 'locked', retry_after_sec: 600 };
        if (!/^\d{3,}$/.test(c) || c === '0000') return { ok: false, reason: 'invalid' };
        if (mockMode === 'admin') return { ok: true, role: 'admin', token: MOCK_ADMIN_TOKEN, me: null };
        return { ok: true, role: 'staff', token: MOCK_STAFF_TOKEN, me: mockMe(db) };
      });
    },
    me: function (token) {
      return later(function (db) {
        var role = mockRole(token);
        if (!role) return { ok: false, reason: 'expired' };
        return { ok: true, role: role, me: role === 'admin' ? null : mockMe(db) };
      });
    },
    roster: function (token, ym) {
      return later(function (db) {
        if (mockMode === 'error') throw fail('network');
        var role = mockRole(token);
        if (!role) return { ok: false, reason: 'expired' };
        if (ym !== db.ym) return { ok: false, reason: 'no_month' };
        var pubId = mockPublished(db);
        if (mockMode === 'pending' && role === 'staff') pubId = null;
        var pub = db.candidates.filter(function (c) { return c.id === pubId; })[0] || null;
        var out = {
          ok: true,
          role: role,
          ym: db.ym,
          status: pub ? 'published' : 'pending',
          me: role === 'admin' ? null : mockMe(db),
          days: clone(db.days),
          prevDays: clone(db.prevDays),
          staff: clone(db.staff),
          roster: pub ? {
            id: pub.id,
            cells: clone(pub.cells),
            prev: clone(pub.prev),
            marks: clone(pub.marks),
            stats: clone(pub.stats),
            publishedAt: db.publishedAt
          } : null
        };
        if (role === 'admin') {
          out.publishedId = pub ? pub.id : null;
          out.search = clone(db.search);
          out.candidates = clone(db.candidates);
        }
        return out;
      });
    },
    publish: function (token, ym, candidate) {
      return later(function (db) {
        if (mockRole(token) !== 'admin') return { ok: false, reason: 'forbidden' };
        if (ym !== db.ym) return { ok: false, reason: 'no_month' };
        if (candidate != null && !db.candidates.some(function (c) { return c.id === candidate; })) {
          return { ok: false, reason: 'not_found' };
        }
        setMockPublished(candidate || null);
        return { ok: true, published: candidate || null };
      });
    },
    logout: function () {
      return later(function () { return { ok: true }; });
    }
  };

  var impl = mockMode ? mock : real;

  window.DutyApi = {
    mock: mockMode,
    login: impl.login,
    me: impl.me,
    roster: impl.roster,
    publish: impl.publish,
    logout: impl.logout
  };
})();
