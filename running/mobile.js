/* FIRST 3K: shared responsive controls, with one source of filter state. */
(() => {
  'use strict';
  const app = window.FIRST3K;
  if (!app) return;
  const $ = id => document.getElementById(id);
  const media = matchMedia('(max-width: 760px)');
  const fields = ['query', 'brandFilter', 'sizeFilter', 'budgetRange', 'purposeFilter', 'widthFilter', 'coverageFilter', 'minScore', 'pricedOnly'];
  const key = 'first3k-preferences-v4';
  const panel = $('filterPanel');
  const anchor = document.createComment('desktop filter position');
  panel.before(anchor);
  const sheet = $('filterSheet');
  const sortSheet = $('sortSheet');
  let restoring = true;

  function save() {
    if (restoring) return;
    try {
      const values = Object.fromEntries(fields.map(id => [id, $(id).type === 'checkbox' ? $(id).checked : $(id).value]));
      localStorage.setItem(key, JSON.stringify({ values, sort: app.state.sort, direction: app.state.direction, selected: app.state.selected, view: app.state.view }));
    } catch (_) { /* Browsing and comparison still work when storage is unavailable. */ }
  }
  function restore() {
    try {
      const saved = JSON.parse(localStorage.getItem(key) || 'null');
      if (!saved || typeof saved !== 'object') return;
      for (const id of fields) {
        const el = $(id), val = saved.values?.[id];
        if (val == null) continue;
        if (el.type === 'checkbox') el.checked = val === true;
        else if (el.tagName === 'SELECT') {
          if ([...el.options].some(o => o.value === String(val))) el.value = String(val);
        } else if (id === 'budgetRange') el.value = String(Math.max(50000, Math.min(310000, +val || 310000)));
        else el.value = String(val).slice(0, 150);
      }
      if (app.metrics.some(m => m.key === saved.sort)) app.state.sort = saved.sort;
      app.state.direction = saved.direction === -1 ? -1 : 1;
      if (['cards', 'table', 'xy'].includes(saved.view)) app.state.view = saved.view;
      app.state.selected = Array.isArray(saved.selected) ? [...new Set(saved.selected)].filter(id => app.data.models.some(m => m.id === id)).slice(0, 4) : [];
      document.querySelectorAll('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === app.state.view));
      app.render(); app.renderTray(); app.syncChecks();
    } catch (_) { /* Ignore malformed or older saved settings. */ }
  }
  function mount() {
    if (media.matches) {
      panel.classList.remove('collapsed');
      $('filterSheetBody').append(panel);
    } else {
      if (sheet.open) sheet.close();
      if (sortSheet.open) sortSheet.close();
      anchor.after(panel);
    }
    document.documentElement.classList.toggle('first3k-mobile', media.matches);
  }
  function filterCount() {
    return Number(!!$('query').value.trim()) + Number($('brandFilter').value !== 'all') +
      Number($('sizeFilter').value !== 'all') + Number(+$('budgetRange').value < 310000) +
      Number($('purposeFilter').value !== 'daily') + Number($('widthFilter').value !== 'all') +
      Number($('coverageFilter').value !== 'all') + Number(+$('minScore').value > 0) + Number($('pricedOnly').checked);
  }
  function sync() {
    const count = filterCount(), n = app.filtered().length;
    $('mobileFilterCount').textContent = count ? String(count) : '';
    $('mobileFilterCount').hidden = !count;
    $('mobileCompareCount').textContent = `${app.state.selected.length}/4`;
    $('mobileCompare').classList.toggle('has-selection', app.state.selected.length >= 2);
    $('filterApply').textContent = `${n}개 신발 보기`;
    const sz = $('sizeFilter').value;
    $('mobileConditionSummary').textContent = `${sz === 'all' ? '여성 전체 옵션' : '여성 ' + sz + ' 대응 옵션'} · ${+$('budgetRange').value >= 310000 ? '예산 제한 없음' : (+$('budgetRange').value / 10000).toLocaleString('ko-KR') + '만원 이하'}`;
    $('mobile230').classList.toggle('active', sz === '230');
    $('mobile230').setAttribute('aria-pressed', String(sz === '230'));
    $('mobileSortSummary').textContent = $('sortSelect').selectedOptions[0]?.textContent || '가격 낮은 순';
    document.body.classList.toggle('has-compare-selection', app.state.selected.length > 0);
    save();
  }
  function goToResults() {
    $('finder').scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  }
  function openFilters() {
    if (!media.matches) { panel.scrollIntoView({ block: 'center' }); $('query').focus(); return; }
    sync(); sheet.showModal();
    // Keep the keyboard closed until the visitor explicitly taps the search field.
    $('filterSheetClose').focus({ preventScroll: true });
  }
  function openSort() {
    const choices = [...$('sortSelect').options];
    $('mobileSortOptions').replaceChildren(...choices.map(o => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'sort-option';
      b.setAttribute('role', 'radio'); b.setAttribute('aria-checked', String(o.value === app.state.sort));
      const label = document.createElement('span'); label.textContent = o.textContent;
      const tick = document.createElement('span'); tick.className = 'sort-tick'; tick.textContent = o.value === app.state.sort ? '✓' : '';
      b.append(label, tick);
      b.addEventListener('click', () => {
        $('sortSelect').value = o.value;
        $('sortSelect').dispatchEvent(new Event('change', { bubbles: true }));
        sortSheet.close(); goToResults();
      });
      return b;
    }));
    $('mobileReverseLabel').textContent = app.state.direction === 1 ? '현재 낮은 순 · 높은 순으로 바꾸기' : '현재 높은 순 · 낮은 순으로 바꾸기';
    sortSheet.showModal();
    $('sortSheetClose').focus({ preventScroll: true });
  }
  $('mobileFilter').addEventListener('click', openFilters);
  $('inlineMobileFilter').addEventListener('click', openFilters);
  $('mobileSort').addEventListener('click', openSort);
  $('filterApply').addEventListener('click', () => { sheet.close(); goToResults(); });
  $('mobileCompare').addEventListener('click', () => $('openCompare').click());
  $('mobileReverse').addEventListener('click', () => { $('sortDirection').click(); sortSheet.close(); goToResults(); });
  $('mobile230').addEventListener('click', () => {
    $('sizeFilter').value = $('sizeFilter').value === '230' ? 'all' : '230';
    $('sizeFilter').dispatchEvent(new Event('change', { bubbles: true }));
  });
  $('resetFilters').addEventListener('click', sync);
  document.addEventListener('first3k:render', sync);
  document.addEventListener('first3k:selection', sync);
  document.querySelectorAll('dialog').forEach(d => {
    d.addEventListener('close', () => { document.body.classList.toggle('dialog-is-open', !!document.querySelector('dialog[open]')); });
    new MutationObserver(() => { document.body.classList.toggle('dialog-is-open', !!document.querySelector('dialog[open]')); }).observe(d, { attributes: true, attributeFilter: ['open'] });
  });
  media.addEventListener('change', mount);
  restore(); restoring = false; mount(); sync();
})();
