// 방문 집계: 사이트의 다른 페이지(house·cukoo·tv·ai-trend)와 같은 GoatCounter 계정에 /polo/ 방문 1건을 보낸다.
// 휴대폰은 mobile.js가 곧바로 보관함으로 이동하므로 외부 스크립트(count.js)를 기다리지 않고 sendBeacon으로 먼저 보낸다.
// 쿠키를 쓰지 않으며, 웹으로 접속했을 때만 동작한다(로컬 파일·로컬 검수 주소 제외).
(function () {
  if (!/^https?:$/.test(location.protocol) || /^(localhost|127\.|\[::1\])/.test(location.hostname)) return;
  var q = "p=" + encodeURIComponent(location.pathname) + "&t=" + encodeURIComponent(document.title || "Polo") +
    "&r=" + encodeURIComponent(document.referrer || "") + "&s=" + screen.width + "&b=" + (navigator.webdriver ? 150 : 0) +
    "&rnd=" + Math.random().toString(36).slice(2);
  var url = "https://unfade.goatcounter.com/count?" + q;
  try { if (navigator.sendBeacon && navigator.sendBeacon(url)) return; } catch (e) {}
  try { fetch(url, { method: "POST", mode: "no-cors", keepalive: true }); } catch (e) {}
})();
