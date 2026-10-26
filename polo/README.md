# Polo 개인 보관함

2026-10-23 사용자 요청에 따라 `https://unfade.is-a.dev/polo/`를 진입 주소로 사용한다.

기존 GitHub Pages는 그대로 유지한다. 이 정적 페이지는 Lightsail의 인증된 보관함을 iframe으로 표시한다. DB·상품 데이터·비밀번호·API 토큰은 이 공개 저장소에 넣지 않는다. 사이트 주소창은 `/polo/`에 머물고 내부 상품 상세·필터는 프레임 안에서 이동한다. 개별 상품 주소를 `/polo/product/...`로 직접 제공하는 리버스 프록시는 아니다.

서버는 CSP `frame-ancestors 'self' https://unfade.is-a.dev`로 소유 도메인의 임베드만 허용한다. HTTPS·HTTP-only·SameSite=None·Partitioned 세션을 사용하며 로그인·로그아웃의 Origin 검사는 계속 적용한다. CHIPS를 지원하는 최신 Chrome을 기준으로 확인한다. 브라우저에서 임베드 인증이 지원되지 않으면 상단의 새 창 열기를 사용한다.

앱 원본과 운영 기록은 비공개 `Baikhojun/unfade` 저장소의 `NewProject/Polo-Sale-Launcher/`에서 관리한다. iframe 원점이 바뀌면 index.html의 src·새 창 링크·frame-src를 함께 갱신한다.

## 2026-10-27 아이콘과 방문 집계

- 탭 아이콘·홈 화면 아이콘과 상단 표시에 사용자 제공 폴로 포니 그림(`icon.png`, `apple-touch-icon.png`)을 사용한다. 보관함 앱(`app/icon.png`)과 같은 그림이다.
- `stats.js`가 사이트 공용 GoatCounter(`unfade.goatcounter.com`)에 `/polo/` 방문을 보낸다. 휴대폰은 바로 보관함으로 이동하므로 외부 스크립트 대신 `sendBeacon`을 먼저 보낸다. CSP는 `connect-src https://unfade.goatcounter.com`만 추가하였다.
- 방문 통계(일별 방문 수 등)는 GoatCounter 대시보드 `https://unfade.goatcounter.com`에서 로그인하여 본다.
