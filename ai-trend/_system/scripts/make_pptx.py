"""data.json → report.pptx (16:9, 13.333×7.5in, 맑은 고딕, 본문 18pt 이상) + 미리보기 렌더링·넘침 검사

사용법
  python _system/scripts/make_pptx.py --issue 2026-10-w2_20261014 [--preview 출력폴더]

원칙 (지시서 8.6)
  - 표지 → 핵심 요약 → 변화 → 서비스 비교 → 가능해진 일 → 토목설계 AI 특집 → 글로벌 사례 → 성능/가격 → 트렌드 → 출처
  - 한 슬라이드에 메시지 하나, 제목은 결론 문장, 본문 18pt 이상 (머리띠·바닥 출처·쪽번호·출처 목록은 예외)
  - 글자는 편집 가능한 텍스트, 차트는 편집 가능한 PowerPoint 차트, 흐름도·타임라인은 고해상도 이미지
  - 파일 속성 작성자 Unfade
검수
  - LibreOffice 가 없는 환경을 위해 PPTX 를 다시 읽어 HTML 로 재구성 → 헤드리스 Chromium 으로 슬라이드 이미지를 만들고
    글상자 넘침(scrollHeight > clientHeight)·슬라이드 밖으로 나간 도형을 검사한다 (맑은 고딕 실제 글꼴 사용)
"""
import argparse
import base64
import html as _html
import json
import sys
from pathlib import Path

from PIL import ImageFont
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import (ROOT, TOKENS, block_external, fmt_num, launch_browser, prepare, serve_root,  # noqa: E402
                   svg_lifecycle, svg_timeline, vendor_color)

FONT = TOKENS["font"]["pptx"]
SW, SH = 13.333, 7.5
MX = 0.6
BODY_TOP, BODY_BOTTOM = 2.08, 6.86
NAVY, INK, MUTED, LINE, SOFT = "17334B", "111214", "55657D", "D9E0EA", "F3F6FA"
# 밝은 뉴스 디자인 시스템(_system/AI_Trend_Light_Design_System.md)
WASH, HEAD = "F3F4F6", "EEF1F5"
CORAL, CORAL_WASH, LIME_WASH, BLUE_WASH, MINT = "FF8C86", "FFE4E1", "E9F8DF", "E2EFFF", "99F0DC"
TEAL, TEAL_T, TEAL_SOFT = "0E8F84", "0A7369", "E6F4F2"
VIOLET, VIOLET_SOFT = "5B4BD6", "EFEDFC"
ORANGE, ORANGE_T = "C76A12", "A0520C"
WHITE = "FFFFFF"
SPACING = 1.3            # 줄 간격 = 글자 크기 × 1.3 (고정값으로 넣어 미리보기와 일치)
MIN_BODY = 18

FONT_FILES = {False: "C:/Windows/Fonts/malgun.ttf", True: "C:/Windows/Fonts/malgunbd.ttf"}
_FC = {}


def _pil(size, bold):
    k = (size, bold)
    if k not in _FC:
        try:
            _FC[k] = ImageFont.truetype(FONT_FILES[bold], int(size * 10))
        except OSError:
            _FC[k] = None
    return _FC[k]


def tw(text, size, bold=False):
    """글자 폭(인치)."""
    f = _pil(size, bold)
    if f is None:
        return len(str(text)) * size * 0.9 / 72
    return f.getlength(str(text)) / 10 / 72


def wrap(text, size, width, bold=False):
    width -= 0.12            # 글상자 좌우 여백
    out = []
    for para in str(text).split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            trial = f"{cur} {w}" if cur else w
            if tw(trial, size, bold) <= width:
                cur = trial
                continue
            if cur:
                out.append(cur)
            if tw(w, size, bold) > width:
                buf = ""
                for ch in w:
                    if tw(buf + ch, size, bold) > width:
                        out.append(buf)
                        buf = ch
                    else:
                        buf += ch
                cur = buf
            else:
                cur = w
        out.append(cur)
    return out


def th(text, size, width, bold=False):
    """글자 높이(인치, 여백 포함)."""
    return len(wrap(text, size, width, bold)) * size * SPACING / 72 + 0.1


def rgb(h):
    return RGBColor.from_string(h)


def set_font(run, size, bold=False, color=INK):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = rgb(color)
    f.name = FONT
    rPr = run._r.get_or_add_rPr()
    rPr.set("lang", "ko-KR")
    rPr.set("altLang", "en-US")
    for t in ("a:ea", "a:cs"):
        el = rPr.find(qn(t))
        if el is None:
            el = rPr.makeelement(qn(t), {})
            rPr.append(el)
        el.set("typeface", FONT)


def no_word_split(p):
    """한글 단어 중간에서 줄이 바뀌지 않게 한다(띄어쓰기 단위 줄바꿈 — wrap()·미리보기의 keep-all 과 같은 규칙)."""
    p._p.get_or_add_pPr().set("eaLnBrk", "0")


def add_text(s, x, y, w, h, paras, size=MIN_BODY, color=INK, bold=False, align="l", anchor="t", frame=None):
    shp = frame if frame is not None else s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shp.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    first = True
    for item in paras:
        if isinstance(item, str):
            item = {"text": item}
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        sz = item.get("size", size)
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[item.get("align", align)]
        p.line_spacing = Pt(round(sz * SPACING, 1))
        no_word_split(p)
        if item.get("before"):
            p.space_before = Pt(item["before"])
        for text, st in item.get("runs") or [(item.get("text", ""), {})]:
            r = p.add_run()
            r.text = str(text)
            set_font(r, st.get("size", sz), st.get("bold", item.get("bold", bold)), st.get("color", item.get("color", color)))
    return shp


def add_rect(s, x, y, w, h, fill=None, line=None, radius=None, line_w=1.0):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                             Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        shp.adjustments[0] = radius
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


TAGC = {k: (v["print"].lstrip("#")) for k, v in TOKENS["tags"].items()}
MATC = {k: (v["print"].lstrip("#")) for k, v in TOKENS["maturity"].items()}
LVLC = {k: (v["print"].lstrip("#")) for k, v in TOKENS["levels"].items()}
SYM_LABEL = {k: v["label"] for k, v in TOKENS["levels"].items()}


def chip(s, x, y, label, color, size=MIN_BODY, fill_soft=True):
    w = tw(label, size, True) + 0.34
    h = size * SPACING / 72 + 0.12
    shp = add_rect(s, x, y, w, h, fill=("FFFFFF" if not fill_soft else _soft(color)), line=color, radius=0.5, line_w=1.0)
    add_text(s, 0, 0, 0, 0, [{"text": label, "align": "c"}], size=size, bold=True, color=color, anchor="m", frame=shp)
    shp.text_frame.margin_left = shp.text_frame.margin_right = Inches(0.04)
    shp.text_frame.margin_top = shp.text_frame.margin_bottom = Inches(0.0)
    return w, h


def _soft(hexc):
    r, g, b = int(hexc[0:2], 16), int(hexc[2:4], 16), int(hexc[4:6], 16)
    mix = lambda c: int(c * 0.1 + 255 * 0.9)
    return f"{mix(r):02X}{mix(g):02X}{mix(b):02X}"


class Deck:
    def __init__(self, d, ctx, issue_dir):
        self.d, self.c, self.dir = d, ctx, issue_dir
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(SW), Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.page_boxes = []
        self.notes = []

    # ── 공통 틀 ──
    def slide(self, kicker, title, sources_line, accent=NAVY, title_size=26):
        s = self.prs.slides.add_slide(self.blank)
        d = self.d
        # 머리띠: 흰 바탕 + 아래 선 (밝은 톤) — 작은 사각 표식 + 보고서명 · 오른쪽 Unfade
        add_rect(s, MX, 0.17, 0.11, 0.11, fill=NAVY)
        add_text(s, MX + 0.18, 0.05, 9.0, 0.34, [f"AI 트렌드 브리핑 · {d['week_label']} · {d['report_date_kst']} 기준"], size=12, color=INK)
        add_text(s, SW - MX - 2.5, 0.05, 2.5, 0.34, [{"text": "Unfade", "align": "r"}], size=12, color=INK, bold=True)
        add_rect(s, MX, 0.44, SW - 2 * MX, 0.014, fill=INK)
        add_text(s, MX, 0.6, 11.0, 0.4, [kicker], size=16, color=accent, bold=True)
        # 제목: 두 줄 안에 들어가도록 크기 조정 (최소 22pt)
        size = title_size
        while size > 22 and len(wrap(title, size, SW - 2 * MX, True)) > 2:
            size -= 1
        add_text(s, MX, 0.98, SW - 2 * MX, 1.02, [title], size=size, bold=True, color=INK)
        add_rect(s, MX, 6.97, SW - 2 * MX, 0.012, fill=LINE)
        add_text(s, MX, 7.0, 10.6, 0.36, [sources_line], size=11, color=MUTED)
        pb = add_text(s, SW - MX - 1.6, 7.0, 1.6, 0.36, [{"text": "", "align": "r"}], size=11, color=INK, bold=True)
        self.page_boxes.append(pb)
        return s

    def finish(self, path):
        total = len(self.prs.slides)
        # 쪽 번호: 표지 제외 슬라이드 순서대로
        idx = 2
        for pb in self.page_boxes:
            r = pb.text_frame.paragraphs[0].add_run()
            r.text = f"{idx} / {total}"
            set_font(r, 11, True, INK)
            idx += 1
        cp = self.prs.core_properties
        cp.author = "Unfade"
        cp.last_modified_by = "Unfade"
        cp.title = f"AI 트렌드 브리핑 | {self.d['week_label']}"
        cp.subject = self.d.get("subtitle", "")
        cp.keywords = "AI 트렌드, 생성형 AI, 토목설계 AI"
        cp.comments = f"{self.d['report_date_kst']} 기준 · 비교 기간 {self.d['period']}"
        self.prs.save(str(path))
        return total


def srcline(pubs, extra=""):
    pubs = [p for i, p in enumerate(pubs) if p and p not in pubs[:i]]
    head = ", ".join(pubs[:4]) + (f" 외 {len(pubs) - 4}곳" if len(pubs) > 4 else "")
    t = f"출처: {head}" if head else "출처: 이번 호 조사 기록"
    line = t + (f" · {extra}" if extra else "") + " · 전체 출처는 마지막 장"
    while tw(line, 11) > 10.3 and len(line) > 20:
        line = line[:-2]
    return line if line.endswith("장") else line.rstrip(" ·,") + "…"


def pubs_of(rows):
    out = []
    for r in rows:
        for s in (r.get("sources") or []):
            out.append(s.get("publisher"))
        if r.get("publisher"):
            out.append(r["publisher"])
    return out


def short(text, n):
    t = str(text or "").strip()
    if len(t) <= n:
        return t
    cut = t[:n]
    # 문장 끝(마침표+공백)에서 자를 수 있으면 말줄임 없이 문장 단위로 끝낸다 ("…23건…" 같은 중간 끊김 방지)
    end = cut.rfind(". ")
    if end >= n * 0.55:
        return cut[:end + 1]
    if " " in cut[n // 2:]:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(",·;: ") + "…"


def P(rec, key, fallback_key, n):
    """PPTX 전용 짧은 문구(rec['pptx'][key]) 우선, 없으면 원문을 줄임."""
    pp = rec.get("pptx") or {}
    return pp.get(key) or short(rec.get(fallback_key, ""), n)


# ───────────────────────── 이미지 (SVG → PNG) ─────────────────────────
def render_svgs(issue_dir, svgs):
    """[(파일명, svg마크업, 너비px)] → images/*.png (2배 해상도)."""
    from playwright.sync_api import sync_playwright
    img_dir = issue_dir / "images"
    img_dir.mkdir(exist_ok=True)
    httpd, base = serve_root()
    try:
        with sync_playwright() as p:
            br = launch_browser(p)
            for name, svg, width in svgs:
                page = br.new_page(viewport={"width": width + 40, "height": 800}, device_scale_factor=2.5)
                block_external(page)
                tmp = issue_dir / f"_svg_{name}.html"
                tmp.write_text('<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="report.css"></head>'
                               f'<body style="margin:0;background:#fff;font-family:var(--font)"><div id="w" style="width:{width}px;padding:8px;background:#fff">{svg}</div></body></html>',
                               encoding="utf-8")
                page.goto(base + f"reports/{issue_dir.name}/{tmp.name}", wait_until="load")
                page.evaluate("document.fonts.ready.then(() => true)")
                page.locator("#w").screenshot(path=str(img_dir / f"{name}.png"))
                page.close()
                tmp.unlink(missing_ok=True)
            br.close()
    finally:
        httpd.shutdown()
    return img_dir


# ───────────────────────── 슬라이드 구성 ─────────────────────────
def build_deck(issue_id):
    issue_dir = ROOT / "reports" / issue_id
    d = json.loads((issue_dir / "data.json").read_text(encoding="utf-8"))
    c = prepare(d)
    dk = Deck(d, c, issue_dir)
    secs = d["sections"]

    # 그림 준비
    img_dir = render_svgs(issue_dir, [
        ("timeline", str(svg_timeline(c["timeline"], c["period_start"], c["period_end"], "print", 1180)), 1180),
        ("lifecycle", str(svg_lifecycle(d["civil"]["lifecycle"], "print", 1180)), 1180),
    ])

    # 1. 표지 (제목·주차·기준일·Unfade 만) — A형 매거진 표지: 흰 지면 + 오른쪽 산호색 기하 도형
    s = dk.prs.slides.add_slide(dk.blank)
    ax = 7.45                                           # 도형 영역 시작 x (오른쪽 약 44%)
    add_rect(s, ax, 0, SW - ax, SH, fill=CORAL_WASH)
    for gx in [ax + 1.0 * k for k in range(1, 6)]:      # 옅은 격자선
        add_rect(s, gx, 0, 0.03, SH, fill="FFF6F5")
    for gy in [1.0 * k for k in range(1, 8)]:
        add_rect(s, ax, gy, SW - ax, 0.03, fill="FFF6F5")
    # 남색 원판(슬라이드 안쪽, 오른쪽 끝에 맞춤) + 왼쪽으로 조금 비켜 놓은 산호색 고리 — 웹 표지와 같은 배치
    dd_, rd_ = 4.6, 3.25
    dx_, dy_ = SW - dd_, 0.75
    disc = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(dx_), Inches(dy_), Inches(dd_), Inches(dd_))
    disc.fill.solid()
    disc.fill.fore_color.rgb = rgb(NAVY)
    disc.line.fill.background()
    disc.shadow.inherit = False
    ring = s.shapes.add_shape(MSO_SHAPE.DONUT, Inches(dx_ + (dd_ - rd_) / 2 - 0.5), Inches(dy_ + (dd_ - rd_) / 2), Inches(rd_), Inches(rd_))
    ring.adjustments[0] = 0.2
    ring.fill.solid()
    ring.fill.fore_color.rgb = rgb(CORAL)
    ring.line.fill.background()
    ring.shadow.inherit = False
    add_text(s, ax + 0.45, 4.85, 4.0, 1.95, ["AI", "TREND"], size=48, bold=True, color=NAVY)
    add_rect(s, MX + 0.2, 1.42, 0.13, 0.13, fill=CORAL)
    add_text(s, MX + 0.42, 1.27, 6.2, 0.44, [f"제{d['issue_no']}호 · {'신규 기준선' if d['is_baseline'] else '직전 발행일 ' + str(d['previous_report']['report_date_kst']) + ' 대비'}"],
             size=16, bold=True, color=INK)
    add_text(s, MX + 0.2, 2.05, 6.7, 1.1, ["AI 트렌드 브리핑"], size=48, bold=True, color=INK)
    add_text(s, MX + 0.2, 3.1, 6.7, 0.9, [d["week_label"]], size=36, bold=True, color=NAVY)
    add_text(s, MX + 0.2, 4.1, 6.7, 0.6, [f"{d['report_date_kst']} 기준"], size=22, color=MUTED)
    add_rect(s, MX + 0.2, 6.18, 6.4, 0.014, fill=INK)
    add_text(s, MX + 0.2, 6.3, 5.0, 0.6, ["Unfade"], size=24, bold=True, color=INK)

    # 2. 핵심 요약
    st = c["status_counts"]
    s = dk.slide("01 핵심 요약 · 3분 요약", d["headline"]["lead"], srcline(pubs_of(c["top"])))
    y = BODY_TOP + 0.05
    colw = 7.6
    for i, t in enumerate(d["headline"].get("pptx_summary") or d["headline"]["three_min_summary"]):
        h = max(th(t, 20, colw - 0.75), 0.62)
        circ = add_rect(s, MX, y + 0.04, 0.5, 0.5, fill=LIME_WASH)
        add_text(s, 0, 0, 0, 0, [{"text": str(i + 1), "align": "c"}], size=18, bold=True, color=INK, anchor="m", frame=circ)
        add_text(s, MX + 0.68, y, colw - 0.68, h, [t], size=20, color=INK)
        y += h + 0.18
    tiles = [(st["new"], "신규", "새로 나온 것"), (st["changed"], "개선", "기능·가격·정책 변경"),
             (st["ended"], "종료", "서비스·모델 종료"), (st["watch"], "관찰", "다음 호까지 추적")]
    x0 = MX + colw + 0.35
    w0, h0, g0 = SW - MX - x0, 1.06, 0.16
    for i, (v, tg, lb) in enumerate(tiles):
        yy = BODY_TOP + 0.05 + i * (h0 + g0)
        add_rect(s, x0, yy, w0, h0, fill=WHITE, line=LINE, radius=0.1)
        add_text(s, x0 + 0.12, yy + 0.12, 1.1, 0.8, [{"text": str(v), "align": "c"}], size=36, bold=True, color=INK, anchor="m")
        chip(s, x0 + 1.32, yy + 0.1, tg, TAGC[tg])
        add_text(s, x0 + 1.27, yy + 0.55, w0 - 1.4, 0.46, [lb], size=18, color=MUTED)

    # 3. 가장 중요한 변화 (넘치면 여러 장)
    rows = c["top"]
    page_rows, cur, used = [], [], 0.0
    for it in rows:
        h = max(th(it["title_ko"], 20, 8.7, True) + th(P(it, "summary", "summary_ko", 70), 18, 8.7), 0.95) + 0.2
        if cur and used + h > BODY_BOTTOM - BODY_TOP:
            page_rows.append(cur)
            cur, used = [], 0.0
        cur.append((it, h))
        used += h
    if cur:
        page_rows.append(cur)
    n0 = 1
    for pi, chunk in enumerate(page_rows):
        s = dk.slide("02 변화 · 이번 기준일 가장 중요한 변화" + (" (계속)" if pi else ""), secs["top"]["title"],
                     srcline(pubs_of([r for r, _ in chunk])))
        y = BODY_TOP
        for it, h in chunk:
            add_rect(s, MX, y - 0.06, SW - 2 * MX, 0.012, fill=LINE)
            add_text(s, MX, y + 0.02, 1.0, 0.7, [f"{n0:02d}"], size=30, bold=True, color=ORANGE)
            th1 = th(it["title_ko"], 20, 8.7, True)
            add_text(s, MX + 1.05, y, 8.7, th1, [it["title_ko"]], size=20, bold=True)
            add_text(s, MX + 1.05, y + th1 - 0.04, 8.7, th(P(it, "summary", "summary_ko", 70), 18, 8.7),
                     [P(it, "summary", "summary_ko", 70)], size=18, color=MUTED)
            cw = tw(it["tag"], 18, True) + 0.34
            chip(s, SW - MX - cw, y + 0.04, it["tag"], TAGC[it["tag"]])
            y += h
            n0 += 1

    # 4. 타임라인 (이미지)
    s = dk.slide("02 변화 · 비교 기간 타임라인", secs["timeline"]["title"], srcline(pubs_of(c["core"])))
    pic = s.shapes.add_picture(str(img_dir / "timeline.png"), Inches(MX), Inches(BODY_TOP))
    scale = (SW - 2 * MX) / (pic.width / 914400)
    pic.width = Inches(SW - 2 * MX)
    pic.height = int(pic.height * scale)
    if pic.height / 914400 > 4.1:
        k = 4.1 / (pic.height / 914400)
        pic.height = Inches(4.1)
        pic.width = int(pic.width * k)
    cap_y = BODY_TOP + pic.height / 914400 + 0.12
    add_text(s, MX, cap_y, SW - 2 * MX, BODY_BOTTOM - cap_y,
             [{"runs": [("이 그림으로 알 수 있는 것  ", {"bold": True, "color": TEAL_T}),
                        (secs["timeline"].get("caption", ""), {})]}], size=18)

    # 5. 서비스 비교 (카드 6장)
    svcs = d["services"][:6]
    s = dk.slide("03 서비스 비교 · 범용 대화형 AI", secs["svc_table"]["title"], srcline(pubs_of(svcs), "요금·기능 확인 " + d["report_date_kst"]))
    cols, gap = 3, 0.25
    cw = (SW - 2 * MX - gap * (cols - 1)) / cols
    chh = (BODY_BOTTOM - BODY_TOP - gap) / 2
    for i, r in enumerate(svcs):
        x = MX + (i % cols) * (cw + gap)
        y = BODY_TOP + (i // cols) * (chh + gap)
        add_rect(s, x, y, cw, chh, fill=WHITE, line=LINE, radius=0.06)
        add_rect(s, x, y, 0.09, chh, fill=vendor_color(r.get("vendor")).lstrip("#"))
        yy = y + 0.1
        head = [{"runs": [(r["service"], {"size": 20, "bold": True}), ("  " + P(r, "model", "flagship", 22), {"size": 18, "color": MUTED})]}]
        hh = th(r["service"] + "  " + P(r, "model", "flagship", 22), 19, cw - 0.3, True)
        add_text(s, x + 0.2, yy, cw - 0.3, hh, head, size=18)
        yy += hh
        best = "강점 · " + P(r, "best", "best_at", 34)
        hb = th(best, 18, cw - 0.3)
        add_text(s, x + 0.2, yy, cw - 0.3, hb, [best], size=18, color=INK)
        yy += hb
        lim = "한계 · " + P(r, "limit", "limits", 34)
        add_text(s, x + 0.2, yy, cw - 0.3, max(y + chh - yy - 0.05, 0.3), [lim], size=18, color=ORANGE_T)

    # 6. 이미지·영상·음성 (3열)
    media = d.get("media_services", [])
    s = dk.slide("03 서비스 비교 · 이미지·영상·음성", secs["media"]["title"], srcline(pubs_of(media)))
    groups = ["이미지", "영상", "음성·음악"]
    cw = (SW - 2 * MX - 0.3 * 2) / 3
    for gi, g in enumerate(groups):
        x = MX + gi * (cw + 0.3)
        add_rect(s, x, BODY_TOP, cw, 0.5, fill=HEAD)
        add_rect(s, x, BODY_TOP + 0.48, cw, 0.02, fill=INK)
        add_text(s, x, BODY_TOP, cw, 0.5, [{"text": g, "align": "c"}], size=20, bold=True, color=INK, anchor="m")
        y = BODY_TOP + 0.62
        for r in [m for m in media if m["group"] == g][:4]:
            line1 = f'{r["service"]} · {P(r, "model", "latest", 22)}'
            line2 = P(r, "note", "strength", 30)
            h1, h2 = th(line1, 18, cw, True), th(line2, 18, cw)
            if y + h1 + h2 > BODY_BOTTOM:
                break
            add_text(s, x, y, cw, h1, [line1], size=18, bold=True, color=(MUTED if r.get("status") == "종료" else INK))
            add_text(s, x, y + h1 - 0.06, cw, h2, [("[종료] " if r.get("status") == "종료" else "") + line2], size=18, color=MUTED)
            y += h1 + h2 + 0.12

    # 7. 가능해진 일 — 8개 영역
    areas = d.get("capability_areas", [])[:8]
    s = dk.slide("04 가능해진 일 · 8개 영역", secs["cap_flow"]["title"], srcline([], "각 사 공식 도움말 기준"))
    cols, gap = 4, 0.22
    cw = (SW - 2 * MX - gap * (cols - 1)) / cols
    chh = (BODY_BOTTOM - BODY_TOP - gap) / 2
    for i, a in enumerate(areas):
        x = MX + (i % cols) * (cw + gap)
        y = BODY_TOP + (i // cols) * (chh + gap)
        add_rect(s, x, y, cw, chh, fill=SOFT, radius=0.06)
        add_text(s, x + 0.12, y + 0.1, cw - 0.24, 0.45, [a["area"]], size=20, bold=True, color=TEAL_T)
        body = P(a, "title", "title", 40)
        add_text(s, x + 0.12, y + 0.55, cw - 0.24, chh - 0.65, [body], size=18)

    # 8. 가능 수준 매트릭스 (표)
    mo = d["matrix_order"]
    s = dk.slide("04 가능해진 일 · 서비스별 가능 수준", secs["matrix"]["title"],
                 srcline([], "● 가능 ◐ 제한적 ○ 불가 ? 미확인 · 공식 문서 기준"))
    nrow, ncol = len(mo["scenarios"]) + 1, len(mo["services"]) + 1
    tw0 = SW - 2 * MX
    tbl_h = min(BODY_BOTTOM - BODY_TOP, 0.43 * nrow)
    gf = s.shapes.add_table(nrow, ncol, Inches(MX), Inches(BODY_TOP), Inches(tw0), Inches(tbl_h))
    tb = gf.table
    tb.columns[0].width = Inches(3.6)
    for j in range(1, ncol):
        tb.columns[j].width = Inches((tw0 - 3.6) / (ncol - 1))
    for i in range(nrow):
        tb.rows[i].height = Inches(tbl_h / nrow)
    _cell(tb.cell(0, 0), "시나리오", 18, True, INK, HEAD)
    for j, sv in enumerate(mo["services"], 1):
        _cell(tb.cell(0, j), short(sv.replace("Microsoft ", ""), 10), 18, True, INK, HEAD, "c")
    for i, sc in enumerate(mo["scenarios"], 1):
        _cell(tb.cell(i, 0), short(sc, 14), 18, True, INK, WHITE if i % 2 else "F8FAFC")
        for j, sv in enumerate(mo["services"], 1):
            cell = c["matrix"].get(f"{sc}|{sv}")
            sym = cell["level"] if cell else "?"
            _cell(tb.cell(i, j), f"{sym} {SYM_LABEL.get(sym, '')}", 18, True, LVLC.get(sym, MUTED), WHITE if i % 2 else "F8FAFC", "c")

    # 9. 토목 특집 — 요약
    cv = d["civil"]
    s = dk.slide("05 토목설계 AI 특집", cv["banner"]["title"], srcline(pubs_of(c["civil_items"])), accent=VIOLET)
    lead = P(cv["banner"], "lead", "lead", 120)
    hl = th(lead, 18, 7.6)
    add_rect(s, MX, BODY_TOP, 7.8, hl + 0.3, fill=VIOLET_SOFT, radius=0.06)
    add_text(s, MX + 0.12, BODY_TOP + 0.15, 7.6, hl, [lead], size=18)
    ks = cv.get("key_stats", [])[:4]
    kx, kw = MX + 8.1, (SW - 2 * MX - 8.1 - 0.2) / 2
    for i, k in enumerate(ks):
        x = kx + (i % 2) * (kw + 0.2)
        y = BODY_TOP + (i // 2) * 1.12
        add_rect(s, x, y, kw, 1.0, fill=WHITE, line="C9C2F2", radius=0.08)
        add_text(s, x + 0.12, y + 0.04, kw - 0.24, 0.55, [str(k["v"])], size=26, bold=True, color=VIOLET)
        add_text(s, x + 0.12, y + 0.56, kw - 0.24, 0.42, [k.get("pptx_label", k["label"])], size=18, color=MUTED)
    f = cv["cad_flow"]
    fy = BODY_TOP + max(hl + 0.3, 2.24) + 0.3
    steps = [("① 파일 입력", f["input"], SOFT, MUTED), ("② AI 처리", f["ai"], VIOLET_SOFT, VIOLET),
             ("③ 설계자 검토", f["human"], "FBF1E7", ORANGE_T), ("④ 산출물", f["output"], SOFT, MUTED)]
    fw = (SW - 2 * MX - 0.3 * 3) / 4
    fh = BODY_BOTTOM - fy
    for i, (k, v, bg, kc) in enumerate(steps):
        x = MX + i * (fw + 0.3)
        add_rect(s, x, fy, fw, fh, fill=bg, radius=0.08)
        add_text(s, x + 0.1, fy + 0.08, fw - 0.2, 0.45, [k], size=18, bold=True, color=kc)
        add_text(s, x + 0.1, fy + 0.52, fw - 0.2, fh - 0.6, [P({"t": v}, "x", "t", 46)], size=18)
        if i < 3:
            add_text(s, x + fw - 0.02, fy + fh / 2 - 0.25, 0.34, 0.5, [{"text": "›", "align": "c"}], size=24, bold=True, color=MUTED)

    # 10. 토목 특집 — CAD·BIM 6단계 판정 (표)
    L = cv["ladder"]
    s = dk.slide("05 토목설계 AI 특집 · CAD·BIM 6단계", L["title"], srcline([], L.get("source_note", "공식 문서 기준")), accent=VIOLET)
    nrow, ncol = len(L["steps"]) + 1, len(L["columns"]) + 2
    tbl_h = min(BODY_BOTTOM - BODY_TOP, 0.62 * nrow)
    gf = s.shapes.add_table(nrow, ncol, Inches(MX), Inches(BODY_TOP), Inches(SW - 2 * MX), Inches(tbl_h))
    tb = gf.table
    tb.columns[0].width = Inches(0.8)
    tb.columns[1].width = Inches(5.0)
    for j in range(2, ncol):
        tb.columns[j].width = Inches((SW - 2 * MX - 5.8) / (ncol - 2))
    for i in range(nrow):
        tb.rows[i].height = Inches(tbl_h / nrow)
    _cell(tb.cell(0, 0), "단계", 18, True, VIOLET, VIOLET_SOFT, "c")
    _cell(tb.cell(0, 1), "확인 내용", 18, True, VIOLET, VIOLET_SOFT)
    for j, col in enumerate(L["columns"], 2):
        _cell(tb.cell(0, j), col, 18, True, VIOLET, VIOLET_SOFT, "c")
    for i, stp in enumerate(L["steps"], 1):
        bg = WHITE if i % 2 else "F8FAFC"
        _cell(tb.cell(i, 0), str(stp["no"]), 20, True, VIOLET, bg, "c")
        _cell(tb.cell(i, 1), P(stp, "q", "q", 24), 18, True, INK, bg)
        for j, cell in enumerate(stp["cells"], 2):
            _cell(tb.cell(i, j), f'{cell["lv"]} {SYM_LABEL.get(cell["lv"], "")}', 18, True, LVLC.get(cell["lv"], MUTED), bg, "c")

    # 11. 토목 특집 — 주요 사례 4건
    top_civil = sorted(c["civil_items"], key=lambda x: (x.get("importance", 3), x.get("date") or ""))[:4]
    s = dk.slide("05 토목설계 AI 특집 · 주요 사례", secs["civil_news"]["title"], srcline(pubs_of(top_civil)), accent=VIOLET)
    cw = (SW - 2 * MX - 0.25) / 2
    chh = (BODY_BOTTOM - BODY_TOP - 0.25) / 2
    for i, it in enumerate(top_civil):
        x = MX + (i % 2) * (cw + 0.25)
        y = BODY_TOP + (i // 2) * (chh + 0.25)
        add_rect(s, x, y, cw, chh, fill=WHITE, line="C9C2F2", radius=0.05)
        wch, hch = chip(s, x + 0.15, y + 0.12, it["maturity"], MATC.get(it["maturity"], MUTED))
        add_text(s, x + 0.15 + wch + 0.12, y + 0.1, cw - wch - 0.45, 0.45, [f'{it.get("country", "")} · {short(it.get("org", ""), 18)}'],
                 size=18, color=MUTED)
        t1 = P(it, "title", "title_ko", 44)
        h1 = th(t1, 20, cw - 0.3, True)
        add_text(s, x + 0.15, y + 0.62, cw - 0.3, h1, [t1], size=20, bold=True)
        eff = "효과 · " + P(it, "effect", "effect", 52) if it.get("effect") else P(it, "summary", "summary_ko", 60)
        add_text(s, x + 0.15, y + 0.62 + h1, cw - 0.3, max(chh - 0.7 - h1, 0.4), [eff], size=18, color=INK)

    # 12. 글로벌 — 트렌드 레이더
    s = dk.slide("06 글로벌 사례 · 트렌드 레이더", secs["radar"]["title"],
                 srcline([x.get("publisher") for z in c["radar_zones"] for r in z["items"] for x in r.get("sources", [])]))
    cw = (SW - 2 * MX - 0.25) / 2
    chh = (BODY_BOTTOM - BODY_TOP - 0.25) / 2
    for i, z in enumerate(c["radar_zones"]):
        x = MX + (i % 2) * (cw + 0.25)
        y = BODY_TOP + (i // 2) * (chh + 0.25)
        col = z["color_p"].lstrip("#")
        add_rect(s, x, y, cw, chh, fill=WHITE, line=LINE, radius=0.05)
        add_rect(s, x, y, cw, 0.08, fill=col)
        add_text(s, x + 0.15, y + 0.14, cw - 0.3, 0.45, [z["name"]], size=20, bold=True, color=col)
        yy = y + 0.6
        for r in z["items"][:2]:
            t = "· " + P(r, "title", "title", 40)
            h = th(t, 18, cw - 0.3)
            if yy + h > y + chh - 0.05:
                break
            add_text(s, x + 0.15, yy, cw - 0.3, h, [t], size=18)
            yy += h + 0.04

    # 13. 글로벌 — 기업 도입 사례 (글로벌 / 국내)
    cases = d.get("cases", [])
    s = dk.slide("06 글로벌 사례 · 기업 도입", secs["cases"]["title"], srcline(pubs_of(cases)))
    cw = (SW - 2 * MX - 0.35) / 2
    for gi, scope in enumerate(["글로벌", "국내"]):
        x = MX + gi * (cw + 0.35)
        add_rect(s, x, BODY_TOP, cw, 0.48, fill=HEAD)
        add_rect(s, x, BODY_TOP + 0.46, cw, 0.02, fill=INK)
        add_text(s, x, BODY_TOP, cw, 0.48, [{"text": f"{scope} 기업", "align": "c"}], size=20, bold=True, color=INK, anchor="m")
        y = BODY_TOP + 0.6
        for k in [k for k in cases if k["scope"] == scope][:4]:
            t = f'{k["company"]} — {P(k, "effect", "effect", 40)}'
            h = th(t, 18, cw)
            if y + h > BODY_BOTTOM:
                break
            add_text(s, x, y, cw, h, [{"runs": [(k["company"], {"bold": True}), (" — " + P(k, "effect", "effect", 40), {})]}], size=18)
            y += h + 0.1

    # 14. 성능 — 편집 가능한 차트 + Arena 상위
    lbs = d["metrics"]["leaderboards"]
    aa = next((lb for lb in lbs if lb.get("chart") == "bar" and lb.get("print_chart")), None)
    ar = next((lb for lb in lbs if lb.get("chart") == "dot"), None)
    s = dk.slide("07 성능과 가격 · 성능 지표", secs["perf"]["title"],
                 srcline([lb.get("publisher") for lb in (aa, ar) if lb], " · ".join(f'{lb["name"]} {lb["version"]} 측정 {lb["checked_at"]}' for lb in (aa, ar) if lb)))
    if aa:
        rows = [r for r in aa["rows"] if isinstance(r.get("score"), (int, float))][:7]
        cd = CategoryChartData()
        cd.categories = [r["model"] for r in reversed(rows)]
        cd.add_series(aa["name"], [r["score"] for r in reversed(rows)])
        gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(MX), Inches(BODY_TOP + 0.45), Inches(7.4), Inches(4.3), cd)
        ch = gf.chart
        ch.has_legend = False
        ch.font.name = FONT
        ch.font.size = Pt(18)
        plot = ch.plots[0]
        plot.gap_width = 55
        plot.has_data_labels = True
        plot.data_labels.font.size = Pt(18)
        plot.data_labels.font.bold = True
        plot.data_labels.number_format = "0"
        plot.data_labels.number_format_is_linked = False
        va = ch.value_axis
        va.minimum_scale = 0
        va.has_major_gridlines = False
        va.tick_labels.font.size = Pt(14)
        va.visible = False
        ca = ch.category_axis
        ca.tick_labels.font.size = Pt(18)
        ca.format.line.color.rgb = rgb(MUTED)
        ser = plot.series[0]
        for i, r in enumerate(reversed(rows)):
            pt = ser.points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(vendor_color(r.get("vendor")).lstrip("#"))
        cap = f'{aa["name"]} ({aa["version"]}) · 막대 = 점수(0부터)'
        add_text(s, MX, BODY_TOP - 0.1, 7.4, th(cap, 18, 7.4, True), [cap], size=18, bold=True)
    if ar:
        x = MX + 7.8
        w = SW - MX - x
        cap2 = f'{ar["name"]} 상위 5 (± = 오차 범위)'
        h2 = th(cap2, 18, w, True)
        add_text(s, x, BODY_TOP - 0.1, w, h2, [cap2], size=18, bold=True)
        y = BODY_TOP - 0.1 + h2 + 0.1
        for r in ar["rows"][:5]:
            # HTML 점 그림(build.svg_dotplot)과 같은 표기: 점수는 천 단위 쉼표, 오차 범위는 원값 그대로
            cp, cm = float(r.get("ci_plus") or 0), float(r.get("ci_minus") or 0)
            ci = f' ±{cp:g}' if cp and cp == cm else (f' +{cp:g}/−{cm:g}' if (cp or cm) else "")
            nm = r["model"].split(" (")[0]
            t = f'{r["rank"]}. {short(nm, 17)}  {float(r["score"]):,.0f}{ci}'
            add_rect(s, x, y + 0.12, 0.14, 0.32, fill=vendor_color(r.get("vendor")).lstrip("#"))
            add_text(s, x + 0.24, y, w - 0.24, 0.56, [t], size=18)
            y += 0.6
        note = ar.get("easy", "")
        room = BODY_BOTTOM - y - 0.1
        if note and th(note, 18, w) > room:
            note = "± 오차 범위가 겹치면 사실상 동률이다."
        if note and th(note, 18, w) <= room:
            add_text(s, x, y + 0.1, w, room, [note], size=18, color=MUTED)

    # 15. 가격 — 대표 구독료 (표)
    prices = [r for r in d["metrics"]["prices"] if r.get("pptx_show", True)][:8]
    fx = c["fx"]
    s = dk.slide("07 성능과 가격 · 개인 구독료", secs["prices"]["title"],
                 srcline([], f'환율 1달러 = {fmt_num(fx.get("usd_krw"), 1)}원 ({fx.get("date")}, {fx.get("source")}) · 확인 {d["report_date_kst"]}'))
    nrow = len(prices) + 1
    tbl_h = min(BODY_BOTTOM - BODY_TOP, 0.5 * nrow)
    gf = s.shapes.add_table(nrow, 4, Inches(MX), Inches(BODY_TOP), Inches(SW - 2 * MX), Inches(tbl_h))
    tb = gf.table
    for j, wdt in enumerate([3.2, 4.3, 2.2, 2.43]):
        tb.columns[j].width = Inches(wdt)
    for i in range(nrow):
        tb.rows[i].height = Inches(tbl_h / nrow)
    for j, h in enumerate(["서비스", "요금제", "월 요금(정가)", "원화 환산"]):
        _cell(tb.cell(0, j), h, 18, True, INK, HEAD, "l" if j < 2 else "r")
    from build import krw
    for i, r in enumerate(prices, 1):
        bg = WHITE if i % 2 else "F8FAFC"
        price = r.get("price_label") or (("$" + fmt_num(r["price"], 2 if float(r["price"]) % 1 else 0)) if r.get("price") is not None else "미확인")
        _cell(tb.cell(i, 0), r["service"], 18, True, INK, bg)
        _cell(tb.cell(i, 1), short(r["plan"], 20), 18, False, INK, bg)
        _cell(tb.cell(i, 2), price, 18, False, INK, bg, "r")
        kl = (r.get("krw_label") or krw(r["price"], fx.get("usd_krw"))).split("(")[0].strip()
        _cell(tb.cell(i, 3), kl, 18, False, INK, bg, "r")

    # 16. 트렌드 — 커뮤니티 반응
    com = d.get("community", [])[:5]
    s = dk.slide("08 트렌드 · 커뮤니티 반응 (등급 C, 사실과 구분)", secs["community"]["title"], srcline(pubs_of(com), "이용자 반응 요약"))
    y = BODY_TOP
    for k in com:
        col = {"긍정": TAGC["신규"], "혼재": TAGC["관찰"], "부정": TAGC["주의"]}.get(k["sentiment"], MUTED)
        wch, _ = chip(s, MX, y + 0.02, "반응 " + k["sentiment"], col)
        t = f'{k["topic"]} — {P(k, "summary", "summary", 46)}'
        h = th(t, 18, SW - 2 * MX - wch - 0.2)
        if y + h > BODY_BOTTOM:
            break
        add_text(s, MX + wch + 0.15, y, SW - 2 * MX - wch - 0.15, h,
                 [{"runs": [(k["topic"], {"bold": True}), (" — " + P(k, "summary", "summary", 46), {})]}], size=18)
        y += max(h, 0.5) + 0.16

    # 17~. 트렌드 — 다음 호까지 추적할 항목 (전부 싣고, 넘치면 다음 장으로)
    wcol = {"공식 예고": TAGC["신규"], "보도": TAGC["개선"], "루머": TAGC["관찰"]}
    tw_w = SW - 2 * MX - 1.7
    groups, cur, y = [], [], BODY_TOP
    for it in c["watch"]:
        t, sig = it["title_ko"], "신호 · " + P(it, "signal", "signal", 50)
        h1, h2 = th(t, 18, tw_w, True), th(sig, 18, tw_w)
        if cur and y + h1 + h2 > BODY_BOTTOM:
            groups.append(cur)
            cur, y = [], BODY_TOP
        cur.append((it, t, sig, h1, h2))
        y += h1 + h2 + 0.08
    if cur:
        groups.append(cur)
    # 필요한 장 수는 그대로 두고 장마다 항목 수를 고르게 (예: 5·5·2 → 4·4·4), 각 장이 넘치지 않을 때만
    flat = [x for g in groups for x in g]
    per = -(-len(flat) // max(len(groups), 1))
    even = [flat[i:i + per] for i in range(0, len(flat), per)]
    if len(even) == len(groups) and all(sum(h1 + h2 + 0.08 for _, _, _, h1, h2 in g) - 0.08 <= BODY_BOTTOM - BODY_TOP for g in even):
        groups = even
    for gi, g in enumerate(groups):
        s = dk.slide("08 트렌드 · 다음 보고서까지 추적할 항목" + (" (계속)" if gi else ""), secs["watch"]["title"],
                     srcline(pubs_of([x[0] for x in g])))
        y = BODY_TOP
        # 남는 높이는 항목 사이에 고르게 나눈다 (최대 0.4in) — 위쪽에만 몰려 보이지 않게
        used = sum(h1 + h2 for _, _, _, h1, h2 in g)
        gap = 0.08 if len(g) < 2 else min(0.4, max(0.08, (BODY_BOTTOM - BODY_TOP - used) / (len(g) - 1)))
        for it, t, sig, h1, h2 in g:
            wt = it.get("watch_type", "보도")
            chip(s, MX, y + 0.02, wt, wcol.get(wt, MUTED))
            add_text(s, MX + 1.6, y, SW - 2 * MX - 1.6, h1, [t], size=18, bold=True)
            add_text(s, MX + 1.6, y + h1 - 0.05, SW - 2 * MX - 1.6, h2, [sig], size=18, color=MUTED)
            y += h1 + h2 + gap

    # 18~. 출처 (전체 목록, 2열 — 참고 목록이라 14pt, 칸 높이에 맞춰 채운다)
    srcs = c["sources"]
    SRC_SZ, cols = 14, 2
    cw = (SW - 2 * MX - 0.3) / 2
    room = BODY_BOTTOM - BODY_TOP - 0.12

    def src_runs(no, x):
        # 날짜는 발행처 바로 뒤(첫 줄 앞쪽)에 둔다 — 줄 끝에 두면 PowerPoint 가 하이픈에서 끊는다. HTML 출처 목록과 같은 순서
        return [(f"{no}. [{x.get('grade', '')}] ", {"bold": True, "color": TEAL_T}),
                (short(x.get("publisher") or "", 18), {"bold": True}),
                ((f" · {x.get('published_at')}" if x.get("published_at") else "") + " — ", {"color": MUTED}),
                (short(x.get("title") or "", 34), {})]

    pages, page, used = [], [[]], 0.0
    for i, x in enumerate(srcs):
        runs = src_runs(i + 1, x)
        h = len(wrap("".join(r[0] for r in runs), SRC_SZ, cw, True)) * SRC_SZ * SPACING / 72   # 굵은 글씨 폭으로 넉넉히
        if page[-1] and used + h > room:
            if len(page) == cols:
                pages.append(page)
                page = [[]]
            else:
                page.append([])
            used = 0.0
        page[-1].append(runs)
        used += h
    if page[-1]:
        pages.append(page)
    # 마지막 장은 두 열을 고르게 (한쪽 열에 1~2건만 남지 않게) — 한 열에 들어가던 분량이라 반으로 나눠도 넘치지 않는다
    if pages and len(pages[-1]) == cols:
        flat = [r for col in pages[-1] for r in col]
        half = -(-len(flat) // cols)
        pages[-1] = [flat[:half], flat[half:]]
    for pi, pcols in enumerate(pages):
        s = dk.slide("출처 · 전체 목록" + (f" ({pi + 1}/{len(pages)})" if len(pages) > 1 else ""),
                     f"이번 호는 검색 {fmt_num(d['search_count'])}회, 출처 {len(srcs)}개를 근거로 했다 (A {c['grade_counts']['A']} · B {c['grade_counts']['B']} · C {c['grade_counts']['C']})",
                     "확인일 " + d["report_date_kst"] + " · 전체 주소는 조사근거(research.md)와 HTML 출처 탭")
        for ci, part in enumerate(pcols):
            if part:
                add_text(s, MX + ci * (cw + 0.3), BODY_TOP, cw, BODY_BOTTOM - BODY_TOP, [{"runs": r} for r in part],
                         size=SRC_SZ, color=INK)

    out = issue_dir / "report.pptx"
    total = dk.finish(out)
    return out, total


def _cell(cell, text, size, bold, color, fill, align="l"):
    cell.fill.solid()
    cell.fill.fore_color.rgb = rgb(fill)
    cell.margin_left = cell.margin_right = Inches(0.08)
    cell.margin_top = cell.margin_bottom = Inches(0.03)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
    p.line_spacing = Pt(round(size * SPACING, 1))
    no_word_split(p)
    r = p.add_run()
    r.text = str(text)
    set_font(r, size, bold, color)


# ───────────────────────── 미리보기 렌더링·넘침 검사 ─────────────────────────
EMU_PX = 96 / 914400


def _px(v):
    return round((v or 0) * EMU_PX, 2)


def _runs_html(tf, scale=1.0):
    out = []
    for p in tf.paragraphs:
        al = {PP_ALIGN.CENTER: "center", PP_ALIGN.RIGHT: "right"}.get(p.alignment, "left")
        lh = p.line_spacing.pt * 96 / 72 if hasattr(p.line_spacing, "pt") and p.line_spacing is not None else None
        sb = p.space_before.pt * 96 / 72 if p.space_before is not None else 0
        spans = []
        max_sz = 0
        for r in p.runs:
            f = r.font
            sz = f.size.pt if f.size else 18
            max_sz = max(max_sz, sz)
            col = "#" + str(f.color.rgb) if f.color and f.color.type is not None else "#000"
            spans.append(f'<span style="font-size:{sz * 96 / 72:.2f}px;font-weight:{700 if f.bold else 400};color:{col}">'
                         f'{_html.escape(r.text)}</span>')
        lh_css = f"{lh:.2f}px" if lh else f"{max_sz * 96 / 72 * 1.2:.2f}px"
        fs_css = f"{(max_sz or 18) * 96 / 72:.2f}px"
        out.append(f'<p style="margin:{sb:.1f}px 0 0;text-align:{al};line-height:{lh_css};font-size:{fs_css}">{"".join(spans) or "&nbsp;"}</p>')
    return "".join(out)


def preview(pptx_path, out_dir):
    prs = Presentation(str(pptx_path))
    W, H = _px(prs.slide_width), _px(prs.slide_height)
    slides_html = []
    for si, slide in enumerate(prs.slides, 1):
        parts = []
        for k, shp in enumerate(slide.shapes):
            x, y, w, h = _px(shp.left), _px(shp.top), _px(shp.width), _px(shp.height)
            base = f"left:{x}px;top:{y}px;width:{w}px;height:{h}px"
            if shp.shape_type == MSO_SHAPE_TYPE.PICTURE:
                b64 = base64.b64encode(shp.image.blob).decode()
                parts.append(f'<img class="shp" data-k="{k}" style="{base}" src="data:{shp.image.content_type};base64,{b64}">')
                continue
            if shp.has_chart:
                ch = shp.chart
                cats = list(ch.plots[0].categories)
                vals = list(ch.plots[0].series[0].values)
                mx = max(vals) if vals else 1
                bars = "".join(f'<div style="display:flex;align-items:center;gap:8px;height:{(h - 10) / max(len(vals), 1):.1f}px">'
                               f'<span style="width:38%;text-align:right;font-size:24px">{_html.escape(str(cname))}</span>'
                               f'<span style="background:#7FB3A0;height:60%;width:{50 * v / mx:.1f}%"></span><b style="font-size:24px">{v:g}</b></div>'
                               for cname, v in reversed(list(zip(cats, vals))))
                parts.append(f'<div class="shp chart" data-k="{k}" style="{base}">{bars}</div>')
                continue
            if shp.has_table:
                rows = []
                for r in shp.table.rows:
                    tds = []
                    for cidx, cell in enumerate(r.cells):
                        fill = "#" + str(cell.fill.fore_color.rgb) if cell.fill.type is not None else "transparent"
                        tds.append(f'<td style="background:{fill};width:{_px(shp.table.columns[cidx].width)}px;padding:3px 8px;vertical-align:middle">'
                                   f'{_runs_html(cell.text_frame)}</td>')
                    rows.append(f'<tr style="height:{_px(r.height)}px">{"".join(tds)}</tr>')
                parts.append(f'<table class="shp tbl" data-k="{k}" style="left:{x}px;top:{y}px;width:{w}px">{"".join(rows)}</table>')
                continue
            style = base
            if shp.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                try:
                    if shp.fill.type is not None and shp.fill.type == 1:
                        style += f";background:#{shp.fill.fore_color.rgb}"
                except Exception:
                    pass
                try:
                    if shp.line.fill.type == 1:
                        style += f";border:{max(shp.line.width.pt * 96 / 72, 1):.1f}px solid #{shp.line.color.rgb}"
                except Exception:
                    pass
                if shp.auto_shape_type == MSO_SHAPE.ROUNDED_RECTANGLE:
                    try:
                        rad = shp.adjustments[0] * min(w, h)
                    except Exception:
                        rad = 8
                    style += f";border-radius:{rad:.1f}px"
            inner = ""
            if shp.has_text_frame and shp.text_frame.text.strip():
                tf = shp.text_frame
                pad = (f"padding:{_px(tf.margin_top)}px {_px(tf.margin_right)}px {_px(tf.margin_bottom)}px {_px(tf.margin_left)}px")
                va = {MSO_ANCHOR.MIDDLE: "center", MSO_ANCHOR.BOTTOM: "flex-end"}.get(tf.vertical_anchor, "flex-start")
                inner = f'<div class="tf" style="{pad};justify-content:{va}">{_runs_html(tf)}</div>'
            parts.append(f'<div class="shp" data-k="{k}" style="{style}">{inner}</div>')
        slides_html.append(f'<section class="slide" data-n="{si}" style="width:{W}px;height:{H}px">{"".join(parts)}</section>')
    doc = ('<!doctype html><html><head><meta charset="utf-8"><style>'
           'body{margin:0;background:#888;font-family:"Malgun Gothic",sans-serif}'
           '.slide{position:relative;overflow:hidden;background:#fff;margin:0 0 20px}'
           '.shp{position:absolute;box-sizing:border-box}'
           '.tf{position:absolute;inset:0;display:flex;flex-direction:column;overflow:hidden;box-sizing:border-box;word-break:keep-all;overflow-wrap:anywhere}'
           '.tbl{border-collapse:collapse;table-layout:fixed;word-break:keep-all}.tbl td{box-sizing:border-box}'
           '.tbl p{margin:0}'
           '</style></head><body>' + "".join(slides_html) + "</body></html>")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "_pptx_preview.html").write_text(doc, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    issues = []
    with sync_playwright() as p:
        br = launch_browser(p)
        page = br.new_page(viewport={"width": int(W), "height": int(H)})
        page.goto((out / "_pptx_preview.html").resolve().as_uri(), wait_until="load")
        page.wait_for_timeout(200)
        res = page.evaluate("""() => {
          const out = [];
          document.querySelectorAll('.slide').forEach(sl => {
            const n = +sl.dataset.n; const sr = sl.getBoundingClientRect(); const probs = [];
            sl.querySelectorAll('.tf').forEach(tf => {
              if (tf.scrollHeight > tf.clientHeight + 2) probs.push('글상자 넘침 ' + (tf.scrollHeight - tf.clientHeight) + 'px: ' + tf.textContent.trim().slice(0, 30));
              if (tf.scrollWidth > tf.clientWidth + 2) probs.push('가로 넘침: ' + tf.textContent.trim().slice(0, 30));
            });
            sl.querySelectorAll('.shp').forEach(s => {
              const r = s.getBoundingClientRect();
              if (r.right > sr.right + 1 || r.bottom > sr.bottom + 1) probs.push('슬라이드 밖: ' + (s.textContent || s.tagName).trim().slice(0, 30));
            });
            sl.querySelectorAll('table.tbl').forEach(t => {
              const r = t.getBoundingClientRect();
              if (r.bottom > sr.top + 6.92 * 96) probs.push('표가 바닥글을 침범: ' + Math.round(r.bottom - sr.top - 6.92 * 96) + 'px');
            });
            if (probs.length) out.push({ slide: n, problems: probs.slice(0, 6) });
          });
          return out;
        }""")
        issues = res
        for i, sec in enumerate(page.locator("section.slide").all(), 1):
            sec.screenshot(path=str(out / f"slide_{i:02d}.png"))
        br.close()
    (out / "_pptx_preview.html").unlink(missing_ok=True)
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--preview", help="슬라이드 미리보기 PNG 폴더 (넘침 검사 포함)")
    a = ap.parse_args()
    out, total = build_deck(a.issue)
    r = {"pptx": str(out), "slides": total, "bytes": out.stat().st_size}
    if a.preview:
        r["overflow"] = preview(out, a.preview)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 1 if r.get("overflow") else 0


if __name__ == "__main__":
    sys.exit(main())
