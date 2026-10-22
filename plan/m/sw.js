// 이 파일은 구 모바일 조회 화면의 서비스워커를 해제한다.
// 설치된 휴대폰에서 예전 화면과 데이터 캐시를 지우고 새 부부 일정표(/plan/)로 이동시킨다.
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) { return Promise.all(keys.map(function (k) { return caches.delete(k); })); })
      .then(function () { return self.registration.unregister(); })
      .then(function () { return self.clients.matchAll({ type: "window" }); })
      .then(function (clients) { clients.forEach(function (c) { c.navigate("/plan/"); }); })
  );
});
