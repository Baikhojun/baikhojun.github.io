// 휴대폰에서는 보관함을 iframe이 아닌 전체 화면으로 연다.
// 휴대폰 브라우저는 다른 도메인 iframe의 로그인 쿠키를 막을 수 있고, 쇼핑몰 앱 링크도 전체 화면에서 가장 확실하게 동작한다.
(function () {
  var app = "https://polo.13.124.246.27.sslip.io/";
  var phone = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || window.matchMedia("(max-width: 820px)").matches;
  if (phone && !/[?&]frame=1/.test(location.search)) location.replace(app);
})();
