// 앱 파일만 저장한다. Supabase 인증·일정·주거비 응답은 가로채지 않는다.
var CACHE = 'unfade-plan-shell-20261028-housing-v4';
var FILES = [
  '/plan/', '/plan/index.html', '/plan/seasons.css', '/plan/app.css?v=20261028-housing',
  '/plan/vendor/supabase-js-2.117.2.min.js', '/plan/config.js', '/plan/holidays.js',
  '/plan/housing.js?v=20261028-housing', '/plan/app.js?v=20261028-housing',
  '/plan/manifest.webmanifest', '/plan/icon-192.png', '/plan/icon-512.png', '/plan/icon-maskable.png'
];
self.addEventListener('install', function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) { return cache.addAll(FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (key) { return key.indexOf('unfade-plan-shell-') === 0 && key !== CACHE; }).map(function (key) { return caches.delete(key); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (event) {
  var url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return;
  // 기존 모바일 설치 주소도 캐시된 Plan 본 화면으로 연다.
  var navigation = event.request.mode === 'navigate' && /^\/plan\/(?:index\.html|m\/(?:index\.html)?)?$/.test(url.pathname);
  var allowed = FILES.some(function (path) { return new URL(path, self.location.origin).pathname === url.pathname; });
  if (!navigation && !allowed) return;
  var key = navigation ? '/plan/' : event.request;
  event.respondWith(caches.open(CACHE).then(async function (cache) {
    var cached = await cache.match(key);
    if (cached) return cached;
    var response = await fetch(event.request);
    if (response.ok && response.type === 'basic') await cache.put(key, response.clone());
    return response;
  }));
});
