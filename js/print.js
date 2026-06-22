// 이 파일의 역할: 시트 화면 확대/축소(화면맞춤) + 인쇄/PDF 출력
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});
  WS.Print = {};

  var zoom = 1;
  var fitMode = true;

  function els() { return { sheet: document.getElementById('sheet'), stage: document.getElementById('stage'), canvas: document.getElementById('canvas') }; }

  function base() {
    var e = els();
    var prev = e.sheet.style.transform;
    e.sheet.style.transform = 'none';
    e.stage.style.width = 'auto'; e.stage.style.height = 'auto';
    var w = e.sheet.offsetWidth, h = e.sheet.offsetHeight;
    e.sheet.style.transform = prev;
    return { w: w, h: h };
  }

  function apply() {
    var e = els();
    var b = base();
    e.sheet.style.transformOrigin = 'top left';
    e.sheet.style.transform = 'scale(' + zoom + ')';
    e.stage.style.width = (b.w * zoom) + 'px';
    e.stage.style.height = (b.h * zoom) + 'px';
    var lbl = document.getElementById('zoom-label');
    if (lbl) lbl.textContent = Math.round(zoom * 100) + '%';
  }

  WS.Print.fit = function () {
    var e = els();
    var b = base();
    var cw = e.canvas.clientWidth || 0;
    if (cw < 200) cw = (root.innerWidth || 1200) - 60; // 레이아웃 미완료 시 폴백
    var avail = cw - 40;
    zoom = Math.max(0.3, Math.min(1.5, Math.round((avail / b.w) * 100) / 100));
    fitMode = true;
    apply();
  };
  WS.Print.setZoom = function (z) { zoom = Math.max(0.2, Math.min(2, z)); fitMode = false; apply(); };
  WS.Print.zoomIn = function () { WS.Print.setZoom(Math.round((zoom + 0.1) * 100) / 100); };
  WS.Print.zoomOut = function () { WS.Print.setZoom(Math.round((zoom - 0.1) * 100) / 100); };
  WS.Print.reapply = function () { if (fitMode) WS.Print.fit(); else apply(); };

  WS.Print.print = function () {
    try { root.print(); } catch (e) { console.error('[Print] 인쇄 실패: %s', e && e.message); }
  };
})(typeof window !== 'undefined' ? window : globalThis);
