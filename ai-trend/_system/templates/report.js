/* AI 트렌드 브리핑 — 화면 동작 (마스터. build.py 가 발행 폴더에 report.js 로 복사)
   탭 전환·해시 열기, 대시보드/인쇄 미리보기 전환, 링크 복사, 인쇄·PDF 저장, 과거 발행본 선택, 방문 집계 */
(function () {
  "use strict";
  var doc = document;
  var body = doc.body;
  var cfg = JSON.parse(doc.getElementById("report-config").textContent);
  var TABS = cfg.tabs;
  var VIEW_KEY = "aitrend.view";

  function $(sel, root) { return (root || doc).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); }

  /* PC 에서 직접 연 경우(file://): 폴더 주소로 된 내부 링크는 열리지 않으므로 index.html 을 붙인다 */
  if (location.protocol === "file:") {
    $all('a[href$="/"]').forEach(function (a) {
      var h = a.getAttribute("href");
      if (!/^[a-z][a-z0-9+.-]*:/i.test(h) && h.charAt(0) !== "/") a.setAttribute("href", h + "index.html");
    });
  }

  var toastTimer = null;
  function toast(msg) {
    var t = $("#toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove("show"); }, 2600);
  }

  /* ── 보기 전환 ── */
  function storeView(v) { try { localStorage.setItem(VIEW_KEY, v); } catch (e) { /* 저장소 차단 시 무시 */ } }
  function loadView() { try { return localStorage.getItem(VIEW_KEY); } catch (e) { return null; } }
  function setView(v, remember) {
    var isPrint = v === "print";
    body.classList.toggle("view-print", isPrint);
    $all("[data-view]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === v)); });
    if (remember) storeView(v);
  }

  /* ── 탭 ── */
  var currentTab = TABS[0];
  // 탭 줄이 가로로 넘어갈 때(좁은 화면) 선택한 탭이 보이게 탭 줄만 옆으로 민다(페이지 세로 위치는 그대로)
  function revealTab(t) {
    var row = t.closest(".tabs");
    if (!row || row.scrollWidth <= row.clientWidth) return;
    var rr = row.getBoundingClientRect(), tr = t.getBoundingClientRect();
    if (tr.left < rr.left) row.scrollLeft -= rr.left - tr.left + 16;
    else if (tr.right > rr.right) row.scrollLeft += tr.right - rr.right + 16;
  }
  function activateTab(id, opts) {
    opts = opts || {};
    if (TABS.indexOf(id) < 0) id = TABS[0];
    currentTab = id;
    $all(".panel").forEach(function (p) { p.classList.toggle("active", p.id === "panel-" + id); });
    $all(".tab").forEach(function (t) {
      var on = t.getAttribute("data-tab") === id;
      t.setAttribute("aria-selected", String(on));
      if (on) revealTab(t);
    });
    if (opts.push) {
      try { history.replaceState(null, "", "#" + id); } catch (e) { location.hash = id; }
    }
    if (!opts.keepScroll) window.scrollTo({ top: 0 });
  }

  function routeFromHash() {
    var h = (location.hash || "").replace(/^#/, "");
    if (h === "og") { body.classList.add("og-mode"); return; }
    if (h === "print") { setView("print", false); return; }
    if (!h) { activateTab(TABS[0], { keepScroll: true }); return; }
    if (TABS.indexOf(h) >= 0) { setView("dashboard", false); activateTab(h, { keepScroll: true }); return; }
    var target = doc.getElementById(h);
    if (target) {
      var panel = target.closest(".panel");
      if (panel) {
        setView("dashboard", false);
        activateTab(panel.id.replace("panel-", ""), { keepScroll: true });
        setTimeout(function () { target.scrollIntoView({ behavior: "auto", block: "start" }); }, 0);
      }
    }
  }

  $all(".tab").forEach(function (t) {
    t.addEventListener("click", function () {
      setView("dashboard", true);
      activateTab(t.getAttribute("data-tab"), { push: true });
    });
  });
  $all("[data-view]").forEach(function (b) {
    b.addEventListener("click", function () {
      var v = b.getAttribute("data-view");
      setView(v, true);
      try { history.replaceState(null, "", v === "print" ? "#print" : "#" + currentTab); } catch (e) { /* 무시 */ }
      window.scrollTo({ top: 0 });
    });
  });
  $all("[data-goto]").forEach(function (a) {
    a.addEventListener("click", function (ev) {
      ev.preventDefault();
      setView("dashboard", true);
      activateTab(a.getAttribute("data-goto"), { push: true });
    });
  });
  window.addEventListener("hashchange", routeFromHash);

  /* ── 링크 복사 ── (앱 안 브라우저 등에서 Clipboard API 쓰기 권한이 거부되면 예전 방식으로 다시 시도) */
  function legacyCopy(text) {
    return new Promise(function (resolve, reject) {
      var ta = doc.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      body.appendChild(ta); ta.select();
      try { doc.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); }
      body.removeChild(ta);
    });
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { return legacyCopy(text); });
    }
    return legacyCopy(text);
  }
  var copyBtn = $("#btn-copy");
  if (copyBtn) copyBtn.addEventListener("click", function () {
    var hash = body.classList.contains("view-print") ? "" : "#" + currentTab;
    copyText(cfg.canonical + hash).then(function () { toast("링크를 복사했습니다"); },
      function () { toast("복사하지 못했습니다. 주소창의 주소를 직접 복사하십시오"); });
  });

  /* ── 인쇄 ── */
  function doPrint() {
    var ready = doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve();
    ready.then(function () { window.print(); });
  }
  var printBtn = $("#btn-print");
  if (printBtn) printBtn.addEventListener("click", doPrint);

  /* ── PDF로 저장하기: report.pdf 를 한글 파일명으로 내려받기, 파일이 없을 때만 인쇄 대화상자 ── */
  var pdfBtn = $("#btn-pdf");
  if (pdfBtn) pdfBtn.addEventListener("click", function (ev) {
    if (location.protocol !== "http:" && location.protocol !== "https:") return; /* PC 에서 연 경우 링크 그대로 */
    ev.preventDefault();
    fetch(pdfBtn.getAttribute("href"), { method: "HEAD", cache: "no-store" }).then(function (r) {
      if (r.ok) {
        var a = doc.createElement("a");
        a.href = pdfBtn.getAttribute("href"); a.download = pdfBtn.getAttribute("download");
        body.appendChild(a); a.click(); body.removeChild(a);
      } else { throw new Error("missing"); }
    }).catch(function () {
      toast("대상에서 'PDF로 저장'을 선택하십시오(Chrome·Edge 권장)");
      setTimeout(doPrint, 600);
    });
  });

  /* ── 과거 AI 신문 보기 (reports.json → 실패 시 빌드 시점 목록) ── */
  function fillArchive(list) {
    var sel = $("#past-select");
    if (!sel || !list || !list.length) return;
    sel.innerHTML = "";
    var ph = doc.createElement("option");
    ph.value = ""; ph.textContent = "발행본을 선택하십시오";
    sel.appendChild(ph);
    list.forEach(function (r) {
      var o = doc.createElement("option");
      o.value = r.report_url;
      o.textContent = r.week_label + " · " + r.published_at_kst + (r.status === "superseded" ? " (정정 전)" : "") + (r.issue_id === cfg.issue_id ? " — 지금 보는 호" : "");
      sel.appendChild(o);
    });
  }
  var embedded = [];
  try { embedded = JSON.parse(doc.getElementById("archive-data").textContent).reports || []; } catch (e) { embedded = []; }
  fillArchive(embedded);
  if (location.protocol === "http:" || location.protocol === "https:") {
    fetch(cfg.archive_json, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && j.reports && j.reports.length) fillArchive(j.reports); })
      .catch(function () { /* 내장 목록 유지 */ });
  }
  var pastSel = $("#past-select");
  if (pastSel) pastSel.addEventListener("change", function () {
    if (!pastSel.value) return;
    var url = cfg.archive_root + pastSel.value;
    if (location.protocol === "file:" && /\/$/.test(url)) url += "index.html"; /* PC 에서 직접 연 경우 폴더 주소는 열리지 않으므로 */
    location.href = url;
  });

  /* ── 맨 위로 ── */
  var topBtn = $("#to-top");
  if (topBtn) {
    topBtn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
    window.addEventListener("scroll", function () { topBtn.classList.toggle("show", window.scrollY > 600); }, { passive: true });
  }

  /* ── 시작 ── */
  var saved = loadView();
  setView(saved === "print" ? "print" : "dashboard", false);
  routeFromHash();

  /* ── 방문 집계: 웹으로 접속했을 때만 (file:// 에서는 아무 요청 없음) ── */
  (function () {
    if (location.protocol !== "http:" && location.protocol !== "https:") return;
    if (/^(localhost|127\.|\[::1\]|0\.0\.0\.0)/.test(location.hostname)) return; /* 로컬 빌드·검수 시 제외 */
    var gc = doc.createElement("script");
    gc.setAttribute("data-goatcounter", "https://unfade.goatcounter.com/count");
    gc.async = true; gc.src = "https://gc.zgo.at/count.js";
    doc.head.appendChild(gc);
  })();
})();
