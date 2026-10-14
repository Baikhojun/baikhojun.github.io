"""발행 폴더 index.html → report.pdf (A4 가로) + og.png (1200×630) + 넘침·쪽수 검사 + 페이지 이미지

사용법
  python _system/scripts/make_pdf.py --issue 2026-10-w2_20261014 [--pages-png 출력폴더]

검사
  - 각 .page 안의 요소가 페이지 경계를 넘는지 (scrollHeight > clientHeight, 요소 경계 비교)
  - PDF 쪽수 = 인쇄 페이지(.page) 수
  - 9pt(12px) 미만 글자가 인쇄 페이지에 있는지
  - PDF 문서 속성: 제목 'AI 트렌드 브리핑 | 주차', 작성자 'Unfade'
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ROOT, serve_root, block_external, launch_browser  # noqa: E402

OVERFLOW_JS = r"""
() => {
  const res = [];
  const pages = Array.from(document.querySelectorAll('.print-view .page'));
  pages.forEach((pg, idx) => {
    const body = pg.querySelector('.pg-body') || pg;
    const pr = pg.getBoundingClientRect();
    const br = body.getBoundingClientRect();
    const problems = [];
    if (body.scrollHeight > body.clientHeight + 1) problems.push(`본문 세로 넘침 ${body.scrollHeight - body.clientHeight}px`);
    if (body.scrollWidth > body.clientWidth + 1) problems.push(`본문 가로 넘침 ${body.scrollWidth - body.clientWidth}px`);
    // 잘라 내는 상자(overflow hidden/clip) 안에 있고 그 상자가 페이지 안에 있으면 실제로는 보이지 않으므로 넘침이 아니다
    // (표지의 장식 도형, 말줄임 처리한 출처 줄 등)
    const clippedInside = (el) => {
      for (let a = el.parentElement; a && a !== body; a = a.parentElement) {
        const ov = getComputedStyle(a).overflow;
        if (ov.includes('hidden') || ov.includes('clip')) {
          const ar = a.getBoundingClientRect();
          if (ar.right <= br.right + 1.5 && ar.bottom <= br.bottom + 1.5) return true;
        }
      }
      return false;
    };
    body.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      if ((r.bottom > br.bottom + 1.5 || r.right > br.right + 1.5) && !clippedInside(el)) {
        problems.push(`요소 경계 초과: <${el.tagName.toLowerCase()} class="${el.className && el.className.baseVal === undefined ? el.className : ''}"> (${Math.round(r.bottom - br.bottom)}px)`);
      }
    });
    // 셀 안 글자 가로 넘침
    body.querySelectorAll('td, th, .p-card').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 2) problems.push(`칸 가로 넘침: ${el.textContent.trim().slice(0, 24)}…`);
    });
    // 최소 글자 크기 9pt = 12px
    const small = [];
    body.querySelectorAll('*').forEach(el => {
      if (!el.childNodes.length) return;
      const hasText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
      if (!hasText) return;
      const fs = parseFloat(getComputedStyle(el).fontSize);
      if (fs < 11.9) small.push(`${fs.toFixed(1)}px: ${el.textContent.trim().slice(0, 20)}`);
    });
    if (small.length) problems.push(`9pt 미만 글자 ${small.length}곳 (예: ${small[0]})`);
    if (problems.length) res.push({ page: idx + 1, problems: problems.slice(0, 6) });
  });
  return { pages: pages.length, issues: res };
}
"""

SVG_TEXT_JS = r"""
() => {
  // 인쇄 페이지 SVG 안 글자의 실제 화면 크기 (viewBox 축소로 9pt 미만이 되는지)
  const out = [];
  document.querySelectorAll('.print-view .page svg').forEach((svg, i) => {
    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width) return;
    const scale = svg.getBoundingClientRect().width / vb.width;
    let minFs = 99;
    svg.querySelectorAll('text').forEach(t => { const f = parseFloat(t.getAttribute('font-size') || '12'); minFs = Math.min(minFs, f * scale); });
    if (minFs < 11.9) out.push({ svg: i, min_px: +minFs.toFixed(2), scale: +scale.toFixed(3) });
  });
  return out;
}
"""


def make(issue_id, pages_png=None, og=True):
    issue_dir = ROOT / "reports" / issue_id
    d = json.loads((issue_dir / "data.json").read_text(encoding="utf-8"))
    pdf_path = issue_dir / "report.pdf"
    title = f"AI 트렌드 브리핑 | {d['week_label']}"
    from playwright.sync_api import sync_playwright
    httpd, base = serve_root()
    url = base + f"reports/{issue_id}/index.html"
    report = {"issue": issue_id}
    try:
        with sync_playwright() as p:
            browser = launch_browser(p)
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            block_external(page)
            page.goto(url + "#print", wait_until="load")
            page.emulate_media(media="print")
            page.evaluate("document.fonts.ready.then(() => true)")
            page.wait_for_timeout(300)
            chk = page.evaluate(OVERFLOW_JS)
            report["print_pages"] = chk["pages"]
            report["overflow"] = chk["issues"]
            report["svg_small_text"] = page.evaluate(SVG_TEXT_JS)
            page.pdf(path=str(pdf_path), format="A4", landscape=True, print_background=True, prefer_css_page_size=True)
            page.close()

            if og:
                pg = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
                block_external(pg)
                pg.goto(url + "#og", wait_until="load")
                pg.evaluate("document.fonts.ready.then(() => true)")
                pg.wait_for_timeout(200)
                pg.locator(".og-card").screenshot(path=str(issue_dir / "og.png"))
                pg.close()
            browser.close()
    finally:
        httpd.shutdown()

    # PDF 문서 속성 · 쪽수 · 페이지 이미지
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf_path))
    doc.set_metadata({"title": title, "author": "Unfade", "subject": d.get("subtitle", ""),
                      "keywords": "AI 트렌드, 생성형 AI, 토목설계 AI", "creator": "AI 트렌드 브리핑 build", "producer": "Unfade"})
    report["pdf_pages"] = doc.page_count
    report["page_count_match"] = (doc.page_count == report["print_pages"])
    fonts = set()
    for i in range(min(doc.page_count, 3)):
        for f in doc.get_page_fonts(i):
            fonts.add(f[3])
    report["pdf_fonts"] = sorted(fonts)
    tmp = pdf_path.with_suffix(".tmp.pdf")
    doc.save(str(tmp), garbage=3, deflate=True)
    doc.close()
    tmp.replace(pdf_path)
    report["pdf_bytes"] = pdf_path.stat().st_size
    if pages_png:
        out = Path(pages_png)
        out.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(str(pdf_path))
        for i, pg in enumerate(doc, start=1):
            pg.get_pixmap(dpi=110).save(str(out / f"page_{i:02d}.png"))
        doc.close()
        report["pages_png"] = str(out)
    return report


TABS_JS = "() => Array.from(document.querySelectorAll('.tab')).map(t => t.dataset.tab)"


def screens(issue_id, out_dir, width=1440, height=900, full=True, tabs=None):
    """대시보드 탭별 화면 캡처 (검수·시안용). 첫 화면(뷰포트)과 전체 페이지를 저장."""
    from playwright.sync_api import sync_playwright
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    httpd, base = serve_root()
    url = base + f"reports/{issue_id}/index.html"
    saved = []
    try:
        with sync_playwright() as p:
            browser = launch_browser(p)
            page = browser.new_page(viewport={"width": width, "height": height})
            block_external(page)
            page.goto(url, wait_until="load")
            page.evaluate("document.fonts.ready.then(() => true)")
            for tab in tabs or page.evaluate(TABS_JS):
                page.evaluate(f"location.hash = '{tab}'")
                page.wait_for_timeout(250)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(100)
                f1 = out / f"screen_{tab}_top.png"
                page.screenshot(path=str(f1))
                saved.append(str(f1))
                if full:
                    f2 = out / f"screen_{tab}_full.png"
                    page.screenshot(path=str(f2), full_page=True)
                    saved.append(str(f2))
            # 좁은 화면(한 열) 확인
            mob = browser.new_page(viewport={"width": 390, "height": 844})
            block_external(mob)
            mob.goto(url, wait_until="load")
            mob.evaluate("document.fonts.ready.then(() => true)")
            f3 = out / "screen_narrow_top.png"
            mob.screenshot(path=str(f3))
            saved.append(str(f3))
            sw = mob.evaluate("document.documentElement.scrollWidth")
            browser.close()
    finally:
        httpd.shutdown()
    return {"screens": saved, "narrow_scroll_width": sw}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--pages-png", help="PDF 각 쪽을 PNG 로 렌더링할 폴더 (검수용)")
    ap.add_argument("--screens", help="대시보드 탭별 화면 캡처 폴더 (검수용)")
    ap.add_argument("--no-og", action="store_true")
    ap.add_argument("--screens-only", action="store_true")
    a = ap.parse_args()
    if a.screens_only:
        print(json.dumps(screens(a.issue, a.screens), ensure_ascii=False, indent=2))
        return 0
    r = make(a.issue, a.pages_png, og=not a.no_og)
    if a.screens:
        r.update(screens(a.issue, a.screens))
    print(json.dumps(r, ensure_ascii=False, indent=2))
    bad = r["overflow"] or not r["page_count_match"] or r["svg_small_text"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
