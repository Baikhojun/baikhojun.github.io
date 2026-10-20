(() => {
  const script = document.currentScript || document.querySelector('script[data-unfade-root]');
  const root = script?.dataset.unfadeRoot || '/';
  const tool = location.pathname.split('/').filter(Boolean)[0];
  const themedTools = new Set(['house', 'cukoo', 'tv', 'lk1800']);
  const links = [
    ['홈', ''], ['신혼 내집 가이드', 'house/'], ['쿠쿠 해독기', 'cukoo/'],
    ['TV 해독기', 'tv/'], ['매트리스 비교', 'lk1800/'], ['여성 러닝화 비교', 'running/'],
  ];
  const nav = links.map(([label, path]) => `<a href="${root}${path}">${label}</a>`).join('');
  let chrome = document.getElementById('unfade-site-chrome');
  if (!chrome) {
    chrome = document.createElement('div');
    chrome.id = 'unfade-site-chrome';
    chrome.innerHTML = `<header class="site-header"><div class="sitebar"><button class="menu-toggle" type="button" aria-label="프로젝트 메뉴 열기" aria-expanded="false"><span class="menu-icon" aria-hidden="true"></span><span>MENU</span></button><a class="wordmark" href="${root}">unfade</a><div class="header-meta">TOOLS <strong>LIGHT MODE</strong></div></div></header><div class="menu-scrim" aria-hidden="true"></div><aside class="side-menu" aria-label="프로젝트 메뉴"><div class="side-menu__top"><a class="wordmark" href="${root}">unfade</a><button class="side-menu__close" type="button" aria-label="메뉴 닫기">×</button></div><nav>${nav}</nav></aside>`;
    document.body.insertAdjacentElement('afterbegin', chrome);
  }
  // 생성된 셸과 HTML에 미리 들어 있는 셸 모두 같은 프로젝트 목록을 쓴다.
  const projectNav = chrome.querySelector('.side-menu nav');
  if (projectNav) projectNav.innerHTML = nav;
  document.body.classList.add('unfade-site-page');
  if (themedTools.has(tool)) {
    document.body.classList.add('unfade-tool-theme');
    document.body.dataset.unfadeTool = tool;
  }
  if (['cukoo', 'tv', 'lk1800'].includes(tool)) {
    document.body.classList.add('unfade-premium');
  }
  // Publish how much of the header is still on screen so fixed/sticky tool bars never leave a gap.
  const header = chrome.querySelector('.site-header');
  const rootStyle = document.documentElement.style;
  let queued = false;
  const syncOffset = () => {
    queued = false;
    const visible = header ? Math.max(0, Math.round(header.getBoundingClientRect().bottom)) : 0;
    rootStyle.setProperty('--unfade-shell-offset', `${visible}px`);
  };
  const queueSync = () => { if (!queued) { queued = true; requestAnimationFrame(syncOffset); } };
  addEventListener('scroll', queueSync, { passive: true });
  addEventListener('resize', queueSync);
  syncOffset();
  // 지금 있는 구역을 서랍 메뉴에 표시한다(홈은 '/'와 정확히 같을 때만)
  const section = (path) => path.split('/').filter(Boolean)[0] || '';
  chrome.querySelectorAll('nav a').forEach((a) => {
    const target = section(a.pathname);   // a.pathname 사용: 일부 도구가 전역 URL 이름을 덮어써서 new URL() 을 못 씀
    if (target === (tool || '')) a.setAttribute('aria-current', 'page');
  });
  // 오른쪽 머리 정보: 모바일판이 있는 도구는 PC↔모바일 전환 링크, 그 밖에는 비운다
  const meta = chrome.querySelector('.header-meta');
  if (meta) {
    if (['house', 'cukoo', 'tv'].includes(tool)) {
      const onMobile = /\/m\/?(index\.html)?$/.test(location.pathname);
      meta.innerHTML = onMobile ? `<a href="${root}${tool}/?pc">PC 버전</a>` : `<a href="${root}${tool}/m/">모바일 버전</a>`;
      meta.classList.add('has-switch');
    } else {
      meta.textContent = 'TOOLS';
    }
  }
  // '맨 위로' 버튼이 없는 긴 화면에 하나 넣는다
  if (!document.querySelector('#back-top, #totop, .totop, #to-top, .to-top, .back-top')) {
    const top = document.createElement('button');
    top.type = 'button'; top.className = 'unfade-to-top'; top.setAttribute('aria-label', '맨 위로'); top.textContent = '↑';
    top.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));
    document.body.appendChild(top);
    const toggleTop = () => top.classList.toggle('is-on', scrollY > 600);
    addEventListener('scroll', toggleTop, { passive: true }); toggleTop();
  }
  const toggleBtn = chrome.querySelector('.menu-toggle'), closeBtn = chrome.querySelector('.side-menu__close');
  const open = () => { document.body.classList.add('unfade-menu-open'); toggleBtn?.setAttribute('aria-expanded', 'true'); setTimeout(() => closeBtn?.focus(), 30); };
  const close = () => {
    if (!document.body.classList.contains('unfade-menu-open')) return;
    document.body.classList.remove('unfade-menu-open'); toggleBtn?.setAttribute('aria-expanded', 'false'); toggleBtn?.focus();
  };
  chrome.querySelector('.menu-toggle')?.addEventListener('click', open);
  chrome.querySelector('.side-menu__close')?.addEventListener('click', close);
  chrome.querySelector('.menu-scrim')?.addEventListener('click', close);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') close();
    // 서랍이 열려 있으면 Tab 이 서랍 안에서만 돈다
    if (event.key === 'Tab' && document.body.classList.contains('unfade-menu-open')) {
      const items = [...chrome.querySelectorAll('.side-menu a, .side-menu button')];
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      else if (!items.includes(document.activeElement)) { event.preventDefault(); first.focus(); }
    }
  });
})();
