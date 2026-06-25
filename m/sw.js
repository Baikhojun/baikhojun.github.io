// 이 파일의 역할: PWA 서비스워커 - 앱 셸 캐시(오프라인) + 데이터는 네트워크 우선
var CACHE = 'ws-m-v2';
var SHELL = ['./', './index.html', './mobile.css', './mobile.js', '../js/store.js', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.map(function (k) { return k === CACHE ? null : caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  var url = new URL(e.request.url);
  // 데이터: 네트워크 우선(최신), 실패 시 캐시
  if (url.pathname.indexOf('schedule-data.json') >= 0) {
    e.respondWith(
      fetch(e.request).then(function (r) {
        var cp = r.clone(); caches.open(CACHE).then(function (c) { c.put('/data/schedule-data.json', cp); }); return r;
      }).catch(function () { return caches.match('/data/schedule-data.json'); })
    );
    return;
  }
  // 앱 셸: 캐시 우선(쿼리 무시), 없으면 네트워크
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(function (c) {
      return c || fetch(e.request).then(function (r) {
        if (r && r.ok && url.origin === location.origin) { var cp = r.clone(); caches.open(CACHE).then(function (cc) { cc.put(e.request, cp); }); }
        return r;
      });
    })
  );
});
