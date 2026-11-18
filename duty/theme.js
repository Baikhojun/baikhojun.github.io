// 이 파일은 화면 모드(일반·다크)를 정한다. 첫 그리기 전에 실행하여 깜빡임을 막는다.
// 기본은 기기 설정을 따르고, 사용자가 고르면 localStorage(duty_theme)에 기억한다.
(function () {
  'use strict';
  var KEY = 'duty_theme';
  var COLORS = { light: '#F4F5F7', dark: '#0E0F12' };
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  var listeners = [];
  var current = 'system';       // 'system' | 'light' | 'dark'

  try {
    var saved = window.localStorage.getItem(KEY);
    if (saved === 'light' || saved === 'dark') current = saved;
  } catch (e) { /* 저장소를 못 쓰면 기기 설정을 따른다. */ }

  function effective() {
    if (current !== 'system') return current;
    return mq && mq.matches ? 'dark' : 'light';
  }

  function apply() {
    var mode = effective();
    document.documentElement.setAttribute('data-theme', mode);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', COLORS[mode]);
    for (var i = 0; i < listeners.length; i++) listeners[i](mode, current);
  }

  function set(value) {
    current = value === 'light' || value === 'dark' ? value : 'system';
    try {
      if (current === 'system') window.localStorage.removeItem(KEY);
      else window.localStorage.setItem(KEY, current);
    } catch (e) { /* 저장하지 못해도 이번 화면에는 적용한다. */ }
    apply();
  }

  if (mq) {
    if (mq.addEventListener) mq.addEventListener('change', apply);
    else if (mq.addListener) mq.addListener(apply);
  }
  apply();

  window.DutyTheme = {
    pref: function () { return current; },
    effective: effective,
    set: set,
    onChange: function (fn) { listeners.push(fn); }
  };
})();
