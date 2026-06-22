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

  // html2canvas 지연 로드(필요할 때만, CDN)
  function loadH2C() {
    if (root.html2canvas) return Promise.resolve(root.html2canvas);
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
      s.onload = function () { root.html2canvas ? resolve(root.html2canvas) : reject(new Error('html2canvas 로드 실패')); };
      s.onerror = function () { reject(new Error('이미지 라이브러리 로드 실패(오프라인일 수 있음). 인쇄·PDF를 이용하세요.')); };
      document.head.appendChild(s);
    });
  }

  // 시트를 PNG로 저장(배율 영향 제거 후 캡처)
  WS.Print.png = function (filename) {
    return loadH2C().then(function (h2c) {
      var e = els();
      var pT = e.sheet.style.transform, pW = e.stage.style.width, pH = e.stage.style.height;
      e.sheet.style.transform = 'none'; e.stage.style.width = 'auto'; e.stage.style.height = 'auto';
      function restore() { e.sheet.style.transform = pT; e.stage.style.width = pW; e.stage.style.height = pH; }
      return h2c(e.sheet, { backgroundColor: '#ffffff', scale: 2 }).then(function (canvas) {
        restore();
        var a = document.createElement('a');
        a.href = canvas.toDataURL('image/png');
        a.download = filename || '업무일정표.png';
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        return true;
      }, function (err) { restore(); throw err; });
    });
  };
})(typeof window !== 'undefined' ? window : globalThis);
