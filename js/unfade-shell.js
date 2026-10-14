(() => {
  const script = document.currentScript || document.querySelector('script[data-unfade-root]');
  const root = script?.dataset.unfadeRoot || '/';
  const tool = location.pathname.split('/').filter(Boolean)[0];
  const themedTools = new Set(['house', 'cukoo', 'tv', 'lk1800']);
  const links = [
    ['홈', ''], ['신혼 내집 가이드', 'house/'], ['쿠쿠 해독기', 'cukoo/'],
    ['TV 해독기', 'tv/'], ['매트리스 비교', 'lk1800/'],
  ];
  const nav = links.map(([label, path]) => `<a href="${root}${path}">${label}</a>`).join('');
  let chrome = document.getElementById('unfade-site-chrome');
  if (!chrome) {
    chrome = document.createElement('div');
    chrome.id = 'unfade-site-chrome';
    chrome.innerHTML = `<header class="site-header"><div class="sitebar"><button class="menu-toggle" type="button" aria-label="프로젝트 메뉴 열기" aria-expanded="false"><span class="menu-icon" aria-hidden="true"></span><span>MENU</span></button><a class="wordmark" href="${root}">unfade</a><div class="header-meta">TOOLS <strong>LIGHT MODE</strong></div></div></header><div class="menu-scrim" aria-hidden="true"></div><aside class="side-menu" aria-label="프로젝트 메뉴"><div class="side-menu__top"><a class="wordmark" href="${root}">unfade</a><button class="side-menu__close" type="button" aria-label="메뉴 닫기">×</button></div><nav>${nav}</nav></aside>`;
    document.body.insertAdjacentElement('afterbegin', chrome);
    document.body.classList.add('unfade-site-page');
  }
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
  const open = () => { document.body.classList.add('unfade-menu-open'); chrome.querySelector('.menu-toggle')?.setAttribute('aria-expanded', 'true'); };
  const close = () => { document.body.classList.remove('unfade-menu-open'); chrome.querySelector('.menu-toggle')?.setAttribute('aria-expanded', 'false'); };
  chrome.querySelector('.menu-toggle')?.addEventListener('click', open);
  chrome.querySelector('.side-menu__close')?.addEventListener('click', close);
  chrome.querySelector('.menu-scrim')?.addEventListener('click', close);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') close(); });
})();
