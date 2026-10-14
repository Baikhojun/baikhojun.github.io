"""data.json → 발행 폴더의 index.html (대시보드 + A4 가로 고정 인쇄 페이지) · report.css · report.js

사용법
  python _system/scripts/build.py --issue 2026-10-w2_20261014

동작
  1. reports/{발행 ID}/data.json 을 읽는다 (HTML·PDF·PPTX 의 단일 데이터 원본)
  2. 대시보드(탭 패널)와 인쇄 흐름 블록을 템플릿으로 만든다
  3. 헤드리스 Chromium 으로 각 블록 높이를 실제 글꼴로 재서 A4 가로 페이지에 나누어 담는다
     (긴 표는 행 단위로 나누고 다음 페이지에 머리글 반복, 카드 묶음은 줄 단위로 나눈다)
  4. design_tokens.json 의 토큰을 붙인 report.css, report.js 사본을 발행 폴더에 쓴다
"""
import argparse
import functools
import html as _html
import http.server
import json
import math
import re
import shutil
import sys
import threading
from collections import OrderedDict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parents[2]          # ai-trend/
SYS = ROOT / "_system"
TPL = SYS / "templates"
TOKENS = json.loads((SYS / "config" / "design_tokens.json").read_text(encoding="utf-8"))
SITE = "https://unfade.is-a.dev/ai-trend/"
MM = 96 / 25.4                                       # CSS px per mm

TABS = OrderedDict([
    ("changes", "핵심 변화"),
    ("services", "AI 서비스"),
    ("capabilities", "가능해진 일"),
    ("civil", "토목설계 AI 특집"),
    ("global", "글로벌 사례"),
    ("archive", "아카이브"),
    ("sources", "출처"),
])
SECTION_NO = {"changes": "01", "services": "02", "capabilities": "03", "civil": "04", "global": "05", "sources": "06"}
SECTION_NAME = {"changes": "핵심 변화", "services": "AI 서비스", "capabilities": "가능해진 일",
                "civil": "토목설계 AI 특집", "global": "글로벌 사례", "sources": "출처·방법론"}

# ───────────────────────── 아이콘 (직접 제작한 24×24 선 아이콘) ─────────────────────────
ICONS = {
    "sparkle": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "arrow-up": '<path d="M12 19V5"/><path d="M5.5 11.5L12 5l6.5 6.5"/>',
    "coin": '<circle cx="12" cy="12" r="9"/><path d="M7.5 8.5l2 7 2.5-5.5 2.5 5.5 2-7"/><path d="M6.5 11.5h11"/>',
    "scale": '<path d="M12 4v16"/><path d="M7 20h10"/><path d="M5 7h14"/><path d="M5 7l-3 6a3 3 0 006 0z"/><path d="M19 7l-3 6a3 3 0 006 0z"/>',
    "alert": '<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5"/><path d="M12 17.6v.4"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "stop": '<rect x="5.5" y="5.5" width="13" height="13" rx="2"/>',
    "pencil": '<path d="M4 20l4.2-1.1L19.5 7.6a2 2 0 000-2.8l-.3-.3a2 2 0 00-2.8 0L5.1 15.8z"/><path d="M14.5 6.5l3 3"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6.2L4.8 18a2 2 0 001.7 3h11a2 2 0 001.7-3L14 9.2V3"/><path d="M7.4 15h9.2"/>',
    "question": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.4a2.5 2.5 0 014.9.6c0 1.8-2.5 2.2-2.5 4"/><path d="M12 17.2v.4"/>',
    "dot": '<circle cx="12" cy="12" r="3.2" fill="currentColor"/>',
    "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 12h6"/><path d="M9 16h6"/>',
    "table": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9.5h18"/><path d="M3 14.8h18"/><path d="M9 4v16"/>',
    "code": '<path d="M8 7l-5 5 5 5"/><path d="M16 7l5 5-5 5"/><path d="M13.5 4.5l-3 15"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9.5" r="1.6"/><path d="M21 15.5l-5-5L6.5 20"/>',
    "video": '<rect x="2.5" y="6" width="13.5" height="12" rx="2"/><path d="M16 10.2l5.5-3.2v10l-5.5-3.2"/>',
    "music": '<path d="M9 18V6l11-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0013 0"/><path d="M12 17.5V21"/>',
    "cad": '<path d="M4 20L20 4"/><path d="M4 20V9"/><path d="M4 20h11"/><path d="M8.5 15.5h3.5V12"/><circle cx="4" cy="20" r="1.2" fill="currentColor"/>',
    "layers": '<path d="M12 3.5l9 4.8-9 4.8-9-4.8z"/><path d="M3 12.6l9 4.8 9-4.8"/><path d="M3 16.6l9 4.8 9-4.8"/>',
    "bolt": '<path d="M13 2.5L4.5 13.5h6.5l-1 8 8.5-11h-6.5z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 010 18"/><path d="M12 3a14 14 0 000 18"/>',
    "building": '<path d="M4 21V5.5L12 3v18"/><path d="M12 9l8 2.5V21"/><path d="M2 21h20"/><path d="M7 8h2"/><path d="M7 12h2"/><path d="M7 16h2"/><path d="M15 14h2"/><path d="M15 17.5h2"/>',
    "bridge": '<path d="M2 18h20"/><path d="M4 18v-4.5"/><path d="M20 18v-4.5"/><path d="M2 13.5c4.5-5.5 15.5-5.5 20 0"/><path d="M8.5 18v-5.3"/><path d="M12 18v-6"/><path d="M15.5 18v-5.3"/>',
    "map": '<path d="M9 4L3 6.2v13.8l6-2.2 6 2.2 6-2.2V4l-6 2.2z"/><path d="M9 4v13.8"/><path d="M15 6.2V20"/>',
    "drone": '<circle cx="12" cy="12" r="2.5"/><path d="M9.8 10.2L6.5 7.5"/><path d="M14.2 10.2l3.3-2.7"/><path d="M9.8 13.8l-3.3 2.7"/><path d="M14.2 13.8l3.3 2.7"/><circle cx="5.5" cy="6.5" r="2.2"/><circle cx="18.5" cy="6.5" r="2.2"/><circle cx="5.5" cy="17.5" r="2.2"/><circle cx="18.5" cy="17.5" r="2.2"/>',
    "chart": '<path d="M4 4v16h16"/><path d="M8.5 16v-5"/><path d="M12.5 16V8"/><path d="M16.5 16v-3"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0"/><path d="M16 4.6a3.5 3.5 0 010 6.8"/><path d="M18.5 20a6 6 0 00-3-5.2"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.8 12l2.2 2.2 4.3-4.4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20.5 20.5l-4.5-4.5"/>',
    "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1"/>',
    "print": '<path d="M7 9V3h10v6"/><path d="M7 17H4v-8h16v8h-3"/><path d="M7 14h10v7H7z"/>',
    "download": '<path d="M12 4v11"/><path d="M7 10.5l5 5 5-5"/><path d="M4 20h16"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18"/><path d="M8 3v4"/><path d="M16 3v4"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9.5 9.5h5v5h-5z"/><path d="M9 2.5V6"/><path d="M15 2.5V6"/><path d="M9 18v3.5"/><path d="M15 18v3.5"/><path d="M2.5 9H6"/><path d="M2.5 15H6"/><path d="M18 9h3.5"/><path d="M18 15h3.5"/>',
    "agent": '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 4.5V8"/><circle cx="12" cy="3.5" r="1.2"/><circle cx="9" cy="13.5" r="1.4" fill="currentColor"/><circle cx="15" cy="13.5" r="1.4" fill="currentColor"/><path d="M9.5 17h5"/>',
    "chat": '<path d="M4 5h16v11H9.5L4 20z"/><path d="M8 9.5h8"/><path d="M8 12.5h5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "book": '<path d="M4 5.5A2.5 2.5 0 016.5 3H20v15H6.5A2.5 2.5 0 004 20.5z"/><path d="M4 20.5A2.5 2.5 0 006.5 23H20v-5"/>',
    "money": '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/><path d="M6 9.5v5"/><path d="M18 9.5v5"/>',
    "factory": '<path d="M3 21V10l5 3V10l5 3V10l5 3V4h3v17z"/><path d="M7 17h2"/><path d="M12 17h2"/>',
    "road": '<path d="M8 3L4 21"/><path d="M16 3l4 18"/><path d="M12 4v3"/><path d="M12 10.5v3"/><path d="M12 17v3"/>',
    "box": '<path d="M12 3l8.5 4.5v9L12 21l-8.5-4.5v-9z"/><path d="M3.5 7.5L12 12l8.5-4.5"/><path d="M12 12v9"/>',
    "tool": '<path d="M14.5 6.5a4 4 0 015 5L9 22l-3-3L16.5 8.5"/><path d="M14.5 6.5L12 4"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2"/><path d="M8 10.5V7.5a4 4 0 018 0v3"/>',
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.8z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><path d="M12 7.6v.4"/>',
    "heart": '<path d="M12 20s-7.5-4.6-9-9.3C1.9 7.1 4.1 4.5 7 4.5c2 0 3.6 1.2 5 3 1.4-1.8 3-3 5-3 2.9 0 5.1 2.6 4 6.2-1.5 4.7-9 9.3-9 9.3z"/>',
}


def icon(name, cls="ico", label=None):
    body = ICONS.get(name, ICONS["dot"])
    aria = f'role="img" aria-label="{escape(label)}"' if label else 'aria-hidden="true" focusable="false"'
    return Markup(f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                  f'stroke-linecap="round" stroke-linejoin="round" {aria}>{body}</svg>')


# ───────────────────────── 작은 표식 (색 + 아이콘 + 글자) ─────────────────────────
def _pill(cls, label, screen, printc, ico=None, sym=None, title=None):
    inner = ""
    if ico:
        inner += str(icon(ico))
    if sym:
        inner += f'<span class="sym" aria-hidden="true">{escape(sym)}</span>'
    t = f' title="{escape(title)}"' if title else ""
    return Markup(f'<span class="{cls}" style="--c:{screen};--cp:{printc}"{t}>{inner}{escape(label)}</span>')


def tag(name):
    t = TOKENS["tags"].get(name)
    if not t:
        return Markup("")
    return _pill("tag", name, t["screen"], t["print"], ico=t["icon"])


def lvl(sym, show_label=True):
    t = TOKENS["levels"].get(sym, TOKENS["levels"]["?"])
    return _pill("lvl", t["label"] if show_label else "", t["screen"], t["print"], sym=sym if sym in TOKENS["levels"] else "?",
                 title=f'{sym} {t["label"]}')


def mat(name):
    t = TOKENS["maturity"].get(name)
    if not t:
        return Markup("")
    return _pill("mat", name, t["screen"], t["print"], ico=t["icon"])


def grade(g):
    t = TOKENS["grades"].get(g)
    if not t:
        return Markup("")
    return _pill("grade", g, t["screen"], t["print"], title=t["label"])


WTYPE = {"공식 예고": ("#0A7369", "#0A7369", "check"), "보도": ("#1D5FB8", "#1D5FB8", "doc"), "루머": ("#7A5E00", "#7A5E00", "question")}


def wtype(name):
    s, p, ico = WTYPE.get(name, ("#4F5D73", "#4F5D73", "dot"))
    return _pill("wtype", name, s, p, ico=ico)


SENTI = {"긍정": ("#0A7369", "#0A7369", "arrow-up"), "혼재": ("#7A5E00", "#7A5E00", "scale"), "부정": ("#B42323", "#B42323", "alert")}


def senti(name):
    s, p, ico = SENTI.get(name, ("#4F5D73", "#4F5D73", "dot"))
    return _pill("tag", "반응 " + name, s, p, ico=ico)


IMP_LABEL = {1: "최상", 2: "높음", 3: "참고"}


def imp(n):
    n = int(n or 3)
    bars = "".join(f'<i class="{"on" if k < 4 - n else ""}"></i>' for k in range(3))
    return Markup(f'<span class="imp" title="중요도 {n}">{bars}<span>{IMP_LABEL.get(n, "참고")}</span></span>')


def short_url(u, n=46):
    try:
        p = urlparse(u)
        s = p.netloc.replace("www.", "") + p.path
    except Exception:
        s = u
    s = s.rstrip("/")
    return s if len(s) <= n else s[: n - 1] + "…"


def src_links(sources, limit=3, dates=True, short=False):
    if not sources:
        return Markup("")
    out = ['<span class="src-links">']
    for s in sources[:limit]:
        d = s.get("published_at") or ""
        if short and len(d) == 10:
            d = d[5:].replace("-", ".")
        dd = f'<span class="s-d">{escape(d)}</span>' if (dates and d) else ""
        out.append(f'<a href="{escape(s["url"])}" target="_blank" rel="noopener">{grade(s.get("grade", ""))}'
                   f'<span class="s-t">{escape(s.get("publisher") or short_url(s["url"], 28))}</span>{dd}</a>')
    if len(sources) > limit:
        out.append(f'<span class="s-d">외 {len(sources) - limit}건</span>')
    out.append("</span>")
    return Markup("".join(out))


def nl2br(s):
    return Markup("<br>".join(escape(x) for x in str(s).split("\n")))


def fmt_num(v, digits=0):
    if v is None or v == "":
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return f"{f:,.{digits}f}"


def fmt_score(v):
    """점수: 원래 소수 자릿수는 그대로 두고 천 단위 쉼표만 붙인다 (1525.4 → 1,525.4, 1158 → 1,158, 95.0 → 95.0)."""
    if v is None or v == "":
        return "—"
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, int):
        return f"{v:,}"
    s = repr(v)
    nd = len(s.split(".")[1]) if "." in s and "e" not in s else 0
    return f"{v:,.{nd}f}"


def krw(usd, rate):
    """달러 → 원화 환산 (100원 단위 반올림, 0.5 는 올림)."""
    from decimal import Decimal, ROUND_HALF_UP
    if usd in (None, "") or not rate:
        return "—"
    if float(usd) == 0:
        return "0원"
    v = (Decimal(str(usd)) * Decimal(str(rate)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100
    return f"약 {int(v):,}원"


def vat_label(v):
    return "포함" if v is True else ("별도" if v is False else "미확인")


# ───────────────────────── 차트 (인라인 SVG, 데이터 → 그림) ─────────────────────────
THEME = {
    # 화면도 밝은 지면(흰 카드 위) — 밝은 뉴스 디자인 시스템. 이름표 테두리(bg)는 흰색
    "screen": {"ink": "#111214", "muted": "#626871", "line": "#DFE2E7", "grid": "#ECEEF1", "bg": "#FFFFFF",
               "teal": "#0E8F84", "violet": "#5B4BD6", "orange": "#C76A12", "fs": 14, "fs_s": 13},
    "print": {"ink": "#0E1A2E", "muted": "#55657D", "line": "#D9E0EA", "grid": "#E8EDF3", "bg": "#FFFFFF",
              "teal": "#0E8F84", "violet": "#5B4BD6", "orange": "#C76A12", "fs": 13, "fs_s": 12.5},
}


def vendor_color(v):
    return TOKENS["vendors"].get(v, TOKENS["vendors"]["_other"])


def text_w(s, fs):
    """한글·영문 혼합 글자 폭 대략 계산 (라벨 배치용)."""
    w = 0.0
    for ch in str(s):
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F or 0x4E00 <= o <= 0x9FFF:
            w += 0.98
        elif ch in "MW@%":
            w += 0.82
        elif ch.isupper() or ch.isdigit():
            w += 0.62
        elif ch in " .,·:;'|!il()[]-":
            w += 0.3
        else:
            w += 0.52
    return w * fs


def svg_open(w, h, label):
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(label)}" '
            f'xmlns="http://www.w3.org/2000/svg" style="font-family:inherit">')


def svg_timeline(events, start, end, theme="screen", width=1200):
    """가로 타임라인: 날짜 축 + 사건 점 + 겹치지 않게 줄을 나눈 이름표."""
    T = THEME[theme]
    fs = T["fs"]
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    span = max((d1 - d0).days, 1)
    left, right = 18, width - 18
    def x_of(d):
        return left + (right - left) * ((date.fromisoformat(d) - d0).days / span)
    evs = sorted([e for e in events if start <= e["date"] <= end], key=lambda e: (e["date"], e.get("importance", 3)))
    lanes = []                      # 각 줄의 마지막 이름표 끝 x
    placed = []
    for e in evs:
        x = x_of(e["date"])
        label = e["title"]
        w = text_w(label, fs) + 26
        if x + w > right:           # 오른쪽 끝을 넘으면 점 왼쪽으로 이름표
            lx0, lx1, anchor = x - w, x, "end"
        else:
            lx0, lx1, anchor = x, x + w, "start"
        lane = None
        for i, last in enumerate(lanes):
            if lx0 > last + 8:
                lane = i
                break
        if lane is None:
            lanes.append(-1e9)
            lane = len(lanes) - 1
        lanes[lane] = lx1
        placed.append((e, x, lane, anchor))
    lane_h = fs + (13 if theme == "print" else 16)   # 인쇄는 줄 간격을 조금 좁혀 한 쪽에 같이 담기 쉽게
    axis_y = 30
    top = axis_y + 26
    h = top + max(len(lanes), 1) * lane_h + 8
    out = [svg_open(width, h, "비교 기간 주요 사건 타임라인")]
    out.append(f'<line x1="{left}" y1="{axis_y}" x2="{right}" y2="{axis_y}" stroke="{T["muted"]}" stroke-width="1.5"/>')
    # 눈금: 매주 월요일 + 시작·끝
    ticks = {d0, d1}
    d = d0
    while d <= d1:
        if d.weekday() == 0:
            ticks.add(d)
        d = date.fromordinal(d.toordinal() + 1)
    for t in sorted(ticks):
        x = x_of(t.isoformat())
        out.append(f'<line x1="{x:.1f}" y1="{axis_y - 5}" x2="{x:.1f}" y2="{h - 6}" stroke="{T["grid"]}" stroke-width="1"/>')
        anchor = "start" if t == d0 else ("end" if t == d1 else "middle")
        out.append(f'<text x="{x:.1f}" y="{axis_y - 11}" font-size="{T["fs_s"]}" fill="{T["muted"]}" text-anchor="{anchor}">'
                   f'{t.month}.{t.day}</text>')
    lines, dots, labels = [], [], []
    for e, x, lane, anchor in placed:
        tg = TOKENS["tags"].get(e.get("tag"), TOKENS["tags"]["관찰"])
        col = tg[theme]
        y = top + lane * lane_h + lane_h / 2
        lines.append(f'<line x1="{x:.1f}" y1="{axis_y}" x2="{x:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="1" opacity=".45"/>')
        dots.append(f'<circle cx="{x:.1f}" cy="{axis_y}" r="4.5" fill="{col}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}"/>')
        tx = x + 9 if anchor == "start" else x - 9
        weight = 700 if e.get("importance", 3) == 1 else 500
        labels.append(f'<text x="{tx:.1f}" y="{y + fs * 0.36:.1f}" font-size="{fs}" font-weight="{weight}" fill="{T["ink"]}" '
                      f'text-anchor="{anchor}" stroke="{T["bg"]}" stroke-width="4" stroke-linejoin="round" paint-order="stroke">'
                      f'{escape(e["title"])}</text>')
    out.extend(lines + dots + labels)
    out.append("</svg>")
    return Markup("".join(out))


def svg_dotplot(rows, theme="screen", width=640, title="점수"):
    """점수 + 오차 범위(±) 점 그림. 막대가 아니므로 축을 0에서 시작하지 않는다(눈금 표기)."""
    T = THEME[theme]
    fs = T["fs"]
    rows = [r for r in rows if r.get("score") not in (None, "")]
    if not rows:
        return Markup("")
    lo = min(float(r["score"]) - float(r.get("ci_minus") or 0) for r in rows)
    hi = max(float(r["score"]) + float(r.get("ci_plus") or 0) for r in rows)
    pad = max((hi - lo) * 0.12, 2)
    lo, hi = math.floor((lo - pad) / 5) * 5, math.ceil((hi + pad) / 5) * 5
    label_w = max(text_w(f'{r["rank"]}. {r["model"]}', fs) for r in rows) + 16
    label_w = min(label_w, width * 0.48)
    x0, x1 = label_w, width - 64
    row_h = fs + 14
    top = 26
    h = top + len(rows) * row_h + 8
    def X(v):
        return x0 + (x1 - x0) * (float(v) - lo) / (hi - lo)
    out = [svg_open(width, h, title)]
    # 눈금 간격: 숫자 이름표가 겹치지 않을 만큼만 (그림 폭에 들어가는 개수 기준)
    max_ticks = max(2, int((x1 - x0) // (text_w(f"{hi:,.0f}", T["fs_s"]) + 14)))
    step = next((s_ for s_ in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000) if (hi - lo) / s_ + 1 <= max_ticks), 1000)
    v = math.ceil(lo / step) * step
    while v <= hi:
        out.append(f'<line x1="{X(v):.1f}" y1="{top - 6}" x2="{X(v):.1f}" y2="{h - 4}" stroke="{T["grid"]}"/>')
        out.append(f'<text x="{X(v):.1f}" y="{top - 11}" font-size="{T["fs_s"]}" fill="{T["muted"]}" text-anchor="middle">{v:,.0f}</text>')
        v += step
    for i, r in enumerate(rows):
        y = top + i * row_h + row_h / 2
        col = vendor_color(r.get("vendor"))
        s = float(r["score"])
        cm, cp = float(r.get("ci_minus") or 0), float(r.get("ci_plus") or 0)
        out.append(f'<text x="{x0 - 12}" y="{y + fs * .36:.1f}" font-size="{fs}" fill="{T["ink"]}" text-anchor="end">'
                   f'{escape(str(r["rank"]))}. {escape(r["model"])}</text>')
        if cm or cp:
            out.append(f'<line x1="{X(s - cm):.1f}" y1="{y:.1f}" x2="{X(s + cp):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="3" opacity=".55" stroke-linecap="round"/>')
        out.append(f'<circle cx="{X(s):.1f}" cy="{y:.1f}" r="6" fill="{col}" stroke="{T["bg"]}" stroke-width="1.5"/>')
        ci = f' ±{cp:g}' if cp and cp == cm else (f' +{cp:g}/−{cm:g}' if (cp or cm) else "")
        out.append(f'<text x="{x1 + 8}" y="{y + fs * .36:.1f}" font-size="{T["fs_s"]}" fill="{T["muted"]}">{s:,.0f}{escape(ci)}</text>')
    out.append("</svg>")
    return Markup("".join(out))


def svg_bars(rows, theme="screen", width=640, unit="", title="막대", max_value=None, value_fmt="{:,.0f}"):
    """가로 막대(축 0에서 시작) + 막대 끝 직접 이름표."""
    T = THEME[theme]
    fs = T["fs"]
    rows = [r for r in rows if r.get("value") not in (None, "")]
    if not rows:
        return Markup("")
    vmax = max_value or max(float(r["value"]) for r in rows) * 1.08
    label_w = min(max(text_w(r["label"], fs) for r in rows) + 16, width * 0.46)
    x0, x1 = label_w, width - 90
    row_h = fs + 14
    top = 24
    h = top + len(rows) * row_h + 6
    out = [svg_open(width, h, title)]
    out.append(f'<line x1="{x0}" y1="{top - 6}" x2="{x0}" y2="{h - 2}" stroke="{T["muted"]}"/>')
    out.append(f'<text x="{x0}" y="{top - 10}" font-size="{T["fs_s"]}" fill="{T["muted"]}" text-anchor="middle">0</text>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        v = float(r["value"])
        w = (x1 - x0) * v / vmax
        col = r.get("color") or vendor_color(r.get("vendor"))
        out.append(f'<text x="{x0 - 10}" y="{y + row_h / 2 + fs * .36:.1f}" font-size="{fs}" fill="{T["ink"]}" text-anchor="end">{escape(r["label"])}</text>')
        out.append(f'<rect x="{x0}" y="{y + 5}" width="{max(w, 1.5):.1f}" height="{row_h - 10}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{x0 + w + 8:.1f}" y="{y + row_h / 2 + fs * .36:.1f}" font-size="{T["fs_s"]}" fill="{T["ink"]}" font-weight="650">'
                   f'{escape(value_fmt.format(v))}{escape(unit)}</text>')
    out.append("</svg>")
    return Markup("".join(out))


TILE_LAYOUT = {   # 단순화한 지역 타일 지도 (열, 행) — 8열
    "캐나다": (0, 0), "영국": (3, 0), "북유럽": (4, 0),
    "미국": (0, 1), "유럽": (3, 1), "중동": (4, 1), "중국": (5, 1), "대한민국": (6, 1), "일본": (7, 1),
    "중남미": (0, 2), "아프리카": (3, 2), "인도": (4, 2), "동남아": (5, 2), "싱가포르": (6, 2), "호주": (7, 2),
    "글로벌": (1, 3),
}
TILE_SHORT = {"대한민국": "한국", "싱가포르": "싱가포르", "아프리카": "아프리카"}


def svg_tilemap(counts, theme="screen", width=560, accent="teal"):
    T = THEME[theme]
    cols, rows_n = 8, 4
    gap = 6
    tw = (width - gap * (cols - 1)) / cols
    th = tw * 0.82
    h = rows_n * (th + gap)
    mx = max(counts.values()) if counts else 1
    out = [svg_open(width, int(h), "사례 국가 분포 타일 지도")]
    for name, (c, r) in TILE_LAYOUT.items():
        n = counts.get(name, 0)
        x, y = c * (tw + gap), r * (th + gap)
        base = T[accent]
        op = 0.12 + 0.78 * (n / mx) if n else 0.05
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{tw:.1f}" height="{th:.1f}" rx="6" fill="{base}" fill-opacity="{op:.2f}" '
                   f'stroke="{T["line"]}"/>')
        label = name if text_w(name, T["fs_s"]) < tw - 8 else TILE_SHORT.get(name, name)
        fsz = T["fs_s"]
        txt_col = "#FFFFFF" if (n and op >= 0.55) else T["ink"]     # 화면·인쇄 모두 밝은 지면: 진한 칸만 흰 글자
        out.append(f'<text x="{x + tw / 2:.1f}" y="{y + th / 2 - 3:.1f}" font-size="{fsz}" fill="{txt_col}" text-anchor="middle">{escape(label)}</text>')
        out.append(f'<text x="{x + tw / 2:.1f}" y="{y + th / 2 + fsz + 1:.1f}" font-size="{fsz + 1}" font-weight="800" fill="{txt_col}" '
                   f'text-anchor="middle">{n if n else "·"}</text>')
    out.append("</svg>")
    return Markup("".join(out))


def svg_lifecycle(stages, theme="screen", width=1200, accent="violet"):
    """프로젝트 생애주기: 단계 화살표 + 단계별 사례 이름표."""
    T = THEME[theme]
    fs = T["fs"]
    n = len(stages)
    gap = 10
    sw = (width - gap * (n - 1)) / n
    head_h = 40
    max_items = max((len(s.get("items", [])) for s in stages), default=0)
    line_h = fs * 1.45
    body_h = 12 + max(max_items, 1) * (line_h * 2 + 8)
    h = head_h + body_h + 4
    out = [svg_open(width, int(h), "프로젝트 생애주기별 AI 적용 사례")]
    for i, s in enumerate(stages):
        x = i * (sw + gap)
        tip = 14 if i < n - 1 else 0
        notch = 14 if i > 0 else 0
        pts = f"{x},{0} {x + sw - tip},{0} {x + sw},{head_h / 2} {x + sw - tip},{head_h} {x},{head_h} {x + notch},{head_h / 2}"
        out.append(f'<polygon points="{pts}" fill="{T[accent]}" fill-opacity="{0.25 + 0.12 * i:.2f}" stroke="{T[accent]}"/>')
        out.append(f'<text x="{x + sw / 2:.1f}" y="{head_h / 2 + fs * .38:.1f}" font-size="{fs + 1}" font-weight="800" fill="{T["ink"]}" '
                   f'text-anchor="middle">{escape(s["stage"])}</text>')
        y = head_h + 12
        for it in s.get("items", []):
            # 두 줄까지 줄바꿈
            words = str(it).split(" ")
            lines, cur = [], ""
            for wd in words:
                trial = (cur + " " + wd).strip()
                if text_w(trial, fs) > sw - 20 and cur:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = trial
            lines.append(cur)
            lines = lines[:2]
            out.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{sw - 4:.1f}" height="{line_h * len(lines) + 8:.1f}" rx="6" fill="none" stroke="{T["line"]}"/>')
            for k, ln in enumerate(lines):
                out.append(f'<text x="{x + 10:.1f}" y="{y + 4 + line_h * (k + 0.75):.1f}" font-size="{fs}" fill="{T["ink"]}">{escape(ln)}</text>')
            y += line_h * len(lines) + 16
    out.append("</svg>")
    return Markup("".join(out))


# ───────────────────────── 데이터 준비 ─────────────────────────
def all_sources(d):
    """data.json 전체에서 출처를 모아 URL 기준으로 중복 제거."""
    seen = OrderedDict()

    def walk(o):
        if isinstance(o, dict):
            if "url" in o and "grade" in o and isinstance(o.get("url"), str) and o["url"].startswith("http"):
                u = o["url"]
                if u not in seen:
                    seen[u] = o
                else:   # 더 이른 게시일·더 구체적인 정보를 유지
                    for k, v in o.items():
                        if not seen[u].get(k) and v:
                            seen[u] = {**seen[u], k: v}
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk({k: v for k, v in d.items() if k not in ("previous_report",)})
    order = {"A": 0, "B": 1, "C": 2}
    return sorted(seen.values(), key=lambda s: (order.get(s.get("grade"), 3), (s.get("publisher") or "").lower(), s.get("published_at") or ""))


def counts_by_status(items):
    c = {"new": 0, "changed": 0, "corrected": 0, "ended": 0, "unchanged": 0, "watch": 0}
    for it in items:
        c[it.get("status", "unchanged")] = c.get(it.get("status", "unchanged"), 0) + 1
    return c


def prepare(d):
    items = d.get("items", [])
    by_id = {it["id"]: it for it in items}
    for it in items:
        it.setdefault("date", it.get("first_announced_at"))
    srcs = all_sources(d)
    grade_counts = {"A": 0, "B": 0, "C": 0}
    for s in srcs:
        if s.get("grade") in grade_counts:
            grade_counts[s["grade"]] += 1
    st = counts_by_status(items)
    period_start, period_end = d["period"].split("~")
    timeline = [{"date": it["date"], "title": it.get("timeline_label") or it.get("title_ko") or it["summary_ko"],
                 "tag": it.get("tag"), "importance": it.get("importance", 3)}
                for it in items
                if it.get("date") and it.get("status") in ("new", "changed", "ended", "corrected")
                and period_start <= it["date"] <= period_end and it.get("on_timeline", True)]
    ctx = {
        "d": d, "by_id": by_id, "sources": srcs, "grade_counts": grade_counts, "status_counts": st,
        "period_start": period_start, "period_end": period_end, "timeline": timeline,
        "core": [by_id[i] for i in d.get("core_ids", []) if i in by_id] or
                sorted([it for it in items if it.get("section") == "core"], key=lambda x: (x.get("importance", 3), x.get("date") or "")),
        "top": [by_id[i] for i in d["headline"].get("top_change_ids", []) if i in by_id],
        "watch": [it for it in items if it.get("section") == "watch"],
        "civil_items": [it for it in items if it.get("section") == "civil"],
        "fx": d.get("basis", {}).get("fx", {}),
    }
    ctx["source_count"] = len(srcs)

    # 가능 수준 매트릭스: "시나리오|서비스" → 판정
    ctx["matrix"] = {f'{r["scenario"]}|{r["service"]}': r for r in d.get("metrics", {}).get("capabilities", [])}

    # 리더보드 막대 그림용 행
    for lb in d.get("metrics", {}).get("leaderboards", []):
        lb["bar_rows"] = [{"label": r["model"], "value": r["score"], "vendor": r.get("vendor")} for r in lb.get("rows", [])
                          if isinstance(r.get("score"), (int, float))]

    # 토목 특집: 하위 주제별 사례
    ctx["civil_sub_key"] = CIVIL_SUB_KEY
    by_sub = {k: [] for k in CIVIL_SUB_KEY}
    for it in ctx["civil_items"]:
        by_sub.setdefault(it.get("sub", "업계 신기술"), []).append(it)
    for k in by_sub:
        by_sub[k].sort(key=lambda x: (x.get("importance", 3), x.get("date") or ""))
    ctx["civil_by_sub"] = by_sub

    # 지역 타일 지도
    civil_regions = {}
    for it in ctx["civil_items"]:
        r = region_tile(it.get("country") or it.get("region"))
        civil_regions[r] = civil_regions.get(r, 0) + 1
    ctx["civil_regions"] = civil_regions
    all_regions = {}
    for it in items:
        if it.get("section") == "watch":
            continue
        r = region_tile(it.get("country") or it.get("region"))
        all_regions[r] = all_regions.get(r, 0) + 1
    for k in d.get("cases", []):
        r = region_tile(k.get("country"))
        all_regions[r] = all_regions.get(r, 0) + 1
    ctx["all_regions"] = all_regions

    # 트렌드 레이더 4구역
    ctx["radar_zones"] = [dict(z, items=d.get("radar", {}).get(z["name"], [])) for z in RADAR_ZONES]

    # 링크 미리보기 문구
    lead = d["headline"]["lead"]
    ctx["og_description"] = d.get("og_description") or (lead if len(lead) <= 150 else lead[:148] + "…")
    ctx["og_headline"] = d.get("og_headline") or "이번 기준일의 AI 변화"
    return ctx


CIVIL_SUB_KEY = OrderedDict([
    ("CAD·도면", "civil_cad_news"),
    ("BIM·IFC·디지털트윈", "civil_bim_news"),
    ("GIS·측량", "civil_gis"),
    ("인프라·안전·유지관리", "civil_infra"),
    ("설계·시공 생산성", "civil_prod_news"),
    ("업계 신기술", "civil_news"),
])

RADAR_ZONES = [
    {"name": "확산 중", "icon": "trend", "color": "#0A7369", "color_p": "#0A7369", "desc": "이미 많은 사람·기업이 쓰기 시작한 흐름"},
    {"name": "주목할 만함", "icon": "star", "color": "#1D5FB8", "color_p": "#1D5FB8", "desc": "아직 초기지만 방향을 바꿀 수 있는 흐름"},
    {"name": "논쟁 중", "icon": "scale", "color": "#A52A78", "color_p": "#A52A78", "desc": "찬반·법적 다툼이 이어지는 흐름"},
    {"name": "위험 증가", "icon": "alert", "color": "#B42323", "color_p": "#B42323", "desc": "피해·사고가 늘어 주의가 필요한 흐름"},
]

REGION_ALIAS = {
    "EU": "유럽", "유럽연합": "유럽", "독일": "유럽", "프랑스": "유럽", "네덜란드": "유럽", "스페인": "유럽", "이탈리아": "유럽",
    "스위스": "유럽", "벨기에": "유럽", "오스트리아": "유럽", "폴란드": "유럽", "아일랜드": "유럽",
    "스웨덴": "북유럽", "노르웨이": "북유럽", "핀란드": "북유럽", "덴마크": "북유럽",
    "한국": "대한민국", "국내": "대한민국", "영국·유럽": "영국",
    "베트남": "동남아", "태국": "동남아", "인도네시아": "동남아", "말레이시아": "동남아", "필리핀": "동남아",
    "사우디아라비아": "중동", "사우디": "중동", "UAE": "중동", "아랍에미리트": "중동", "카타르": "중동", "이스라엘": "중동",
    "브라질": "중남미", "멕시코": "중남미", "칠레": "중남미", "뉴질랜드": "호주", "홍콩": "중국", "대만": "중국",
    "기타": "글로벌", "다국적": "글로벌", "": "글로벌", None: "글로벌",
}


def region_tile(name):
    if name in TILE_LAYOUT:
        return name
    if isinstance(name, str) and name.split("·")[0].strip() in TILE_LAYOUT:
        return name.split("·")[0].strip()
    return REGION_ALIAS.get(name, "글로벌")


def archive_entries(d):
    """reports.json 목록 + 이번 호 항목. 이번 호가 이미 올라가 있으면 지금 data.json 기준 항목으로 바꿔 끼운다
    (reports.json 갱신은 빌드 다음 단계라, 다시 빌드할 때 옛 호수·요약이 남지 않게)."""
    p = ROOT / "reports.json"
    reports = []
    if p.exists():
        reports = json.loads(p.read_text(encoding="utf-8")).get("reports", [])
    old = next((r for r in reports if r.get("issue_id") == d["issue_id"]), None)
    cur = archive_entry_for(d, status=old.get("status", "published") if old else "published")
    reports = [cur] + [r for r in reports if r.get("issue_id") != d["issue_id"]]
    reports.sort(key=lambda r: (r["published_at_kst"], r.get("issue_no", 0), r["issue_id"]), reverse=True)
    return reports


def archive_entry_for(d, status="published"):
    iid = d["issue_id"]
    return {
        "issue_no": d["issue_no"], "issue_id": iid, "status": status,
        "published_at_kst": d["report_date_kst"], "week_label": d["week_label"], "period": d["period"],
        "title": d.get("title", "AI 트렌드 브리핑"),
        "headline": d.get("og_headline", ""),
        "summary": d.get("archive_summary") or d["headline"]["three_min_summary"][:3],
        "report_url": f"reports/{iid}/", "pdf_url": f"reports/{iid}/report.pdf",
        "pptx_url": f"reports/{iid}/report.pptx", "data_url": f"reports/{iid}/data.json",
        "download_name": d["download_prefix"],
    }


# ───────────────────────── 템플릿 환경 ─────────────────────────
def make_env():
    env = Environment(loader=FileSystemLoader(str(TPL)), autoescape=True, trim_blocks=True, lstrip_blocks=True,
                      undefined=StrictUndefined)
    env.globals.update(icon=icon, tag=tag, lvl=lvl, mat=mat, grade=grade, imp=imp, wtype=wtype, senti=senti,
                       src_links=src_links, short_url=short_url, fmt_num=fmt_num, fmt_score=fmt_score, krw=krw, vat_label=vat_label, TOKENS=TOKENS,
                       svg_timeline=svg_timeline, svg_dotplot=svg_dotplot, svg_bars=svg_bars, svg_tilemap=svg_tilemap,
                       svg_lifecycle=svg_lifecycle, vendor_color=vendor_color, TABS=TABS, SECTION_NO=SECTION_NO,
                       SECTION_NAME=SECTION_NAME, IMP_LABEL=IMP_LABEL)
    env.filters["nl2br"] = nl2br
    return env


def tokens_css():
    lines = [":root {"]
    for k, v in TOKENS["screen"].items():
        lines.append(f"  {k}: {v};")
    for k, v in TOKENS["print"].items():
        lines.append(f"  {k}: {v};")
    lines.append(f'  --font: {TOKENS["font"]["family"]};')
    lines.append(f'  --font-en: {TOKENS["font"].get("family_en", TOKENS["font"]["family"])};')
    lines.append("}")
    return "\n".join(lines) + "\n"


# ───────────────────────── 인쇄 흐름 블록 → 페이지 ─────────────────────────
class PItem:
    """인쇄 흐름 블록. split='table'|'grid'|None"""

    def __init__(self, section, html, split=None, keep_with_next=False, break_before=False, small_gap=False,
                 sources=None, chunk=None, civil=False):
        self.section = section
        self.html = str(html)
        self.split = split
        self.keep_with_next = keep_with_next
        self.break_before = break_before
        self.small_gap = small_gap
        self.sources = sources or []
        self.chunk = chunk          # 분할 렌더링 함수: chunk(start, end, first, last) -> html
        self.civil = civil


def serve_root():
    """ai-trend/ 를 로컬 HTTP 로 제공 (글꼴·상대 경로·fetch 를 실제 웹과 같게)."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()
    handler = functools.partial(Quiet, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/"


def launch_browser(p):
    """Playwright 전용 Chromium → 설치된 Chrome → Edge 순서로 시도한다."""
    errors = []
    for kw in ({}, {"channel": "chrome"}, {"channel": "msedge"}):
        try:
            return p.chromium.launch(**kw)
        except Exception as e:      # 브라우저가 없거나 버전이 맞지 않으면 다음 후보
            errors.append(f"{kw or 'bundled'}: {str(e).splitlines()[0]}")
    raise RuntimeError("헤드리스 브라우저를 열 수 없음 — " + " / ".join(errors))


def block_external(page):
    def handler(route):
        u = route.request.url
        if u.startswith("http://127.0.0.1") or u.startswith("data:") or u.startswith("about:"):
            return route.continue_()
        return route.abort()
    page.route("**/*", handler)


MEASURE_JS = r"""
() => {
  const out = [];
  document.querySelectorAll('.measure-root > .pi').forEach(el => {
    const r = el.getBoundingClientRect();
    const o = { i: +el.dataset.i, h: r.height };
    const tbl = el.querySelector('table.split');
    if (tbl) {
      const tr = tbl.getBoundingClientRect();
      o.title_h = tr.top - r.top;
      o.head_h = tbl.tHead ? tbl.tHead.getBoundingClientRect().height : 0;
      o.rows = Array.from(tbl.tBodies[0].rows).map(x => x.getBoundingClientRect().height);
      o.tail_h = r.bottom - tr.bottom;
    }
    const grid = el.querySelector('.split-grid');
    if (grid) {
      const gr = grid.getBoundingClientRect();
      o.title_h = gr.top - r.top;
      const tops = {};
      Array.from(grid.children).forEach(c => {
        const cr = c.getBoundingClientRect();
        const k = Math.round(cr.top - gr.top);
        tops[k] = Math.max(tops[k] || 0, cr.height);
      });
      o.grid_rows = Object.keys(tops).map(Number).sort((a, b) => a - b).map(k => tops[k]);
      o.grid_gap = parseFloat(getComputedStyle(grid).rowGap) || 0;
      o.grid_cols = getComputedStyle(grid).gridTemplateColumns.split(' ').length;
      o.tail_h = r.bottom - gr.bottom;
    }
    out.push(o);
  });
  return out;
}
"""


def page_geometry():
    pg = TOKENS["page"]
    body_h_mm = pg["height_mm"] - pg["head_mm"] - pg["foot_mm"] - pg["body_pad_top_mm"] - pg["body_pad_bottom_mm"]
    return body_h_mm * MM


def measure(items, issue_dir, base_url, issue_id, browser):
    shell = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><link rel="stylesheet" href="report.css">',
             '</head><body style="background:#fff;margin:0"><div class="page measure-root">']
    for i, it in enumerate(items):
        shell.append(f'<div class="pi{" gap-s" if it.small_gap else ""}" data-i="{i}">{it.html}</div>')
    shell.append("</div></body></html>")
    mp = issue_dir / "_measure.html"
    mp.write_text("".join(shell), encoding="utf-8")
    try:
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        block_external(page)
        page.goto(base_url + f"reports/{issue_id}/_measure.html", wait_until="load")
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_timeout(150)
        res = page.evaluate(MEASURE_JS)
        page.close()
    finally:
        mp.unlink(missing_ok=True)
    res.sort(key=lambda o: o["i"])
    return res


def paginate(items, meas, avail):
    GAP, GAP_S, SAFE = 4 * MM, 2.5 * MM, 3.0
    pages = []
    cur = {"blocks": [], "used": 0.0, "section": None, "sources": [], "civil": False, "last": None}
    warnings = []

    def new_page(section=None, civil=False):
        nonlocal cur
        if cur["blocks"]:
            pages.append(cur)
        cur = {"blocks": [], "used": 0.0, "section": section, "sources": [], "civil": civil, "last": None}

    def gap_before():
        if not cur["blocks"]:
            return 0.0
        return GAP_S if (cur["last"] is not None and cur["last"].small_gap) else GAP

    def place(it, html, h, srcs=None):
        if not cur["blocks"]:
            cur["section"] = it.section
            cur["civil"] = it.civil
        cur["used"] += gap_before() + h
        cur["blocks"].append(f'<div class="pi{" gap-s" if it.small_gap else ""}">{html}</div>')
        cur["sources"].extend(it.sources if srcs is None else srcs)
        cur["last"] = it

    def chunk_sources(it, s, e):
        rs = getattr(it, "row_sources", None)
        if rs is None:
            return None
        return [x for r in rs[s:e] for x in r]

    def first_chunk_h(it, m):
        if it.split == "table" and m.get("rows"):
            return m["title_h"] + m["head_h"] + m["rows"][0] + (m["tail_h"] if len(m["rows"]) == 1 else 0)
        if it.split == "grid" and m.get("grid_rows"):
            return m["title_h"] + m["grid_rows"][0] + (m["tail_h"] if len(m["grid_rows"]) == 1 else 0)
        return m["h"]

    for idx, it in enumerate(items):
        m = meas[idx]
        if it.break_before and cur["blocks"]:
            new_page(it.section, it.civil)
        if it.keep_with_next and idx + 1 < len(items):
            nxt, nm = items[idx + 1], meas[idx + 1]
            need = m["h"] + GAP_S + first_chunk_h(nxt, nm)
            if cur["blocks"] and cur["used"] + gap_before() + need > avail - SAFE:
                new_page(it.section, it.civil)
        if cur["used"] + gap_before() + m["h"] <= avail - SAFE:
            place(it, it.html, m["h"])
            continue
        if it.split == "table" and m.get("rows"):
            rows = m["rows"]
            i, first = 0, True
            while i < len(rows):
                g = gap_before()
                room = avail - SAFE - cur["used"] - g - m["title_h"] - m["head_h"]
                take, acc = 0, 0.0
                while i + take < len(rows):
                    is_last = (i + take == len(rows) - 1)
                    need = rows[i + take] + (m["tail_h"] if is_last else 0)
                    if acc + need <= room:
                        acc += rows[i + take]
                        take += 1
                    else:
                        break
                if take == 0 or (take == 1 and len(rows) - i > 1 and cur["blocks"] and room < avail * 0.18):
                    if cur["blocks"]:
                        new_page(it.section, it.civil)
                        continue
                    take = 1
                    acc = rows[i]
                    warnings.append(f"블록 {idx}: 한 행이 페이지보다 큼")
                last = (i + take == len(rows))
                html = it.chunk(i, i + take, first, last)
                place(it, html, m["title_h"] + m["head_h"] + acc + (m["tail_h"] if last else 0), chunk_sources(it, i, i + take))
                i += take
                first = False
                if i < len(rows):
                    new_page(it.section, it.civil)
            continue
        if it.split == "grid" and m.get("grid_rows"):
            grows = m["grid_rows"]
            i, first = 0, True
            while i < len(grows):
                g = gap_before()
                room = avail - SAFE - cur["used"] - g - m["title_h"]
                take, acc = 0, 0.0
                while i + take < len(grows):
                    is_last = (i + take == len(grows) - 1)
                    add = grows[i + take] + (m["grid_gap"] if take else 0) + (m["tail_h"] if is_last else 0)
                    if acc + add <= room:
                        acc += grows[i + take] + (m["grid_gap"] if take else 0)
                        take += 1
                    else:
                        break
                if take == 0:
                    if cur["blocks"]:
                        new_page(it.section, it.civil)
                        continue
                    take = 1
                    acc = grows[i]
                    warnings.append(f"블록 {idx}: 카드 한 줄이 페이지보다 큼")
                last = (i + take == len(grows))
                c0, c1 = i * m["grid_cols"], (i + take) * m["grid_cols"]
                html = it.chunk(c0, c1, first, last)
                place(it, html, m["title_h"] + acc + (m["tail_h"] if last else 0), chunk_sources(it, c0, c1))
                i += take
                first = False
                if i < len(grows):
                    new_page(it.section, it.civil)
            continue
        # 나눌 수 없는 블록: 새 페이지로
        if cur["blocks"]:
            new_page(it.section, it.civil)
        if m["h"] > avail - SAFE:
            warnings.append(f"블록 {idx}({it.section}): 높이 {m['h']:.0f}px > 페이지 {avail:.0f}px — 넘침")
        place(it, it.html, m["h"])
    if cur["blocks"]:
        pages.append(cur)
    return pages, warnings


def page_sources_line(srcs):
    pubs = []
    for s in srcs:
        p = s.get("publisher") or short_url(s.get("url", ""), 24)
        if p and p not in pubs:
            pubs.append(p)
    if not pubs:
        return "출처: 이번 호 조사 기록(조사근거 파일) · 전체 출처는 마지막 장"
    head = ", ".join(pubs[:4])
    more = f" 외 {len(pubs) - 4}곳" if len(pubs) > 4 else ""
    return f"출처: {head}{more} · 전체 출처는 마지막 장"


def assemble_pages(d, cover_html, pages):
    total = len(pages) + 1
    out = [f'<section class="page cover" aria-label="표지">{cover_html}</section>']
    for n, pg in enumerate(pages, start=2):
        sec = pg["section"] or "changes"
        civil = " civil" if sec == "civil" else ""
        out.append(
            f'<section class="page" aria-label="{n}쪽">'
            f'<header class="pg-head{civil}"><span class="ph-l">AI 트렌드 브리핑<span>{escape(d["week_label"])} · {escape(d["report_date_kst"])} 기준</span>'
            f'<span class="ph-sec">{SECTION_NO.get(sec, "")} {escape(SECTION_NAME.get(sec, ""))}</span></span>'
            f'<span class="ph-r">Unfade</span></header>'
            f'<div class="pg-body">{"".join(pg["blocks"])}</div>'
            f'<footer class="pg-foot"><span class="pf-src">{escape(page_sources_line(pg["sources"]))}</span>'
            f'<span class="pf-no">{n} / {total}</span></footer></section>')
    return Markup("".join(out)), total


# ───────────────────────── 빌드 ─────────────────────────
def build(issue_id, measure_pages=True):
    issue_dir = ROOT / "reports" / issue_id
    d = json.loads((issue_dir / "data.json").read_text(encoding="utf-8"))
    ctx = prepare(d)
    env = make_env()
    archive = archive_entries(d)

    # 1) 스타일·스크립트 사본 (해당 호 전용)
    (issue_dir / "report.css").write_text("/* 이 파일은 build.py 가 생성한 이 호 전용 사본이다 */\n" + tokens_css() +
                                          (TPL / "report.css").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copyfile(TPL / "report.js", issue_dir / "report.js")

    # 2) 인쇄 흐름 블록
    pitems = build_print_items(env, ctx)
    cover_html = env.get_template("_print.j2").module.cover(ctx)

    # 3) 측정 → 페이지 나누기
    warnings = []
    if measure_pages:
        from playwright.sync_api import sync_playwright
        httpd, base = serve_root()
        try:
            with sync_playwright() as p:
                browser = launch_browser(p)
                meas = measure(pitems, issue_dir, base, issue_id, browser)
                browser.close()
        finally:
            httpd.shutdown()
        pages, warnings = paginate(pitems, meas, page_geometry())
    else:
        pages = [{"blocks": [it.html], "section": it.section, "sources": it.sources, "civil": it.civil} for it in pitems]
    pages_html, total = assemble_pages(d, cover_html, pages)

    # 4) 최종 HTML
    html = env.get_template("report.html.j2").render(
        c=ctx, pages_html=pages_html, page_total=total, archive=archive,
        archive_json=json.dumps({"reports": archive}, ensure_ascii=False),
        config_json=json.dumps({"tabs": list(TABS.keys()), "canonical": d["canonical_url"], "issue_id": issue_id,
                                "archive_json": "../../reports.json", "archive_root": "../../"}, ensure_ascii=False),
    )
    (issue_dir / "index.html").write_text(html, encoding="utf-8")
    return {"pages": total, "warnings": warnings, "print_blocks": len(pitems)}


def build_print_items(env, ctx):
    """_print.j2 매크로로 인쇄 흐름 블록 목록을 만든다 (순서 = 인쇄 페이지 순서)."""
    m = env.get_template("_print.j2").module
    d = ctx["d"]
    P = []

    def srcs_of(rows):
        out = []
        for r in rows:
            out.extend(r.get("sources", []) if isinstance(r, dict) else [])
            if isinstance(r, dict) and r.get("source_url"):
                out.append({"url": r["source_url"], "publisher": r.get("publisher") or short_url(r["source_url"], 24)})
        return out

    def blk(section, macro, arg=None, sources=None, **kw):
        P.append(PItem(section, getattr(m, macro)(ctx, arg), sources=sources, civil=(section == "civil"), **kw))

    def split(kind, section, macro, rows, arg=None, **kw):
        if not rows:
            return
        f = getattr(m, macro)

        def chunk(s, e, first, last):
            return str(f(ctx, arg, s, e, first, last))
        it = PItem(section, chunk(0, 10 ** 6, True, True), split=kind, chunk=chunk, sources=srcs_of(rows),
                   civil=(section == "civil"), **kw)
        it.row_sources = [srcs_of([r]) for r in rows]
        P.append(it)

    def head(key):
        blk(key, "sec_head", key, keep_with_next=True, small_gap=True, break_before=True)

    lbs = d["metrics"].get("leaderboards", [])
    # 01 핵심 변화
    head("changes")
    blk("changes", "summary_stats")
    split("grid", "changes", "top_list", ctx["top"])
    split("table", "changes", "core_table", ctx["core"])
    blk("changes", "timeline", sources=srcs_of(ctx["core"]))
    blk("changes", "unchanged")
    split("table", "changes", "watch_table", ctx["watch"])
    # 02 AI 서비스
    head("services")
    split("table", "services", "services_table", d.get("services", []))
    split("table", "services", "media_table", d.get("media_services", []))
    split("grid", "services", "guide_cards", d.get("selection_guide", []))
    if any(lb.get("print_chart") for lb in lbs):
        blk("services", "perf_figs", sources=[{"url": lb["source_url"], "publisher": lb.get("publisher")} for lb in lbs if lb.get("print_chart")])
    split("table", "services", "bench_table", lbs)
    split("table", "services", "candidates_table", d.get("candidates", []))
    split("table", "services", "usertype_table", d.get("user_types", []))
    split("table", "services", "price_table", d["metrics"].get("prices", []))
    split("table", "services", "api_table", d["metrics"].get("api_prices", []))
    # 03 가능해진 일
    head("capabilities")
    split("grid", "capabilities", "areas", d.get("capability_areas", []))
    split("table", "capabilities", "matrix_table", d.get("matrix_order", {}).get("scenarios", []))
    split("table", "capabilities", "files_table", d["metrics"].get("file_support", []))
    blk("capabilities", "reality")
    split("grid", "capabilities", "daily_scenes", d.get("daily", {}).get("scenes", []))
    blk("capabilities", "daily_split")
    blk("capabilities", "case_card", sources=d.get("daily", {}).get("case_card", {}).get("sources", []))
    # 04 토목설계 AI 특집
    cv = d.get("civil", {})
    head("civil")
    blk("civil", "civil_banner")
    blk("civil", "civil_flow", keep_with_next=True, small_gap=True)
    split("table", "civil", "ladder_table", cv.get("ladder", {}).get("steps", []))
    split("grid", "civil", "civil_cards", ctx["civil_by_sub"].get("CAD·도면", []), arg="CAD·도면")
    split("table", "civil", "platform_files", cv.get("platform_files", []))
    if cv.get("lifecycle"):
        blk("civil", "lifecycle")
    split("grid", "civil", "civil_cards", ctx["civil_by_sub"].get("BIM·IFC·디지털트윈", []), arg="BIM·IFC·디지털트윈")
    split("grid", "civil", "civil_cards", ctx["civil_by_sub"].get("GIS·측량", []), arg="GIS·측량")
    if cv.get("infra_matrix"):
        blk("civil", "infra_matrix")
    split("grid", "civil", "civil_cards", ctx["civil_by_sub"].get("인프라·안전·유지관리", []), arg="인프라·안전·유지관리")
    split("grid", "civil", "vs_cards", cv.get("compare", []))
    split("grid", "civil", "civil_cards", ctx["civil_by_sub"].get("설계·시공 생산성", []), arg="설계·시공 생산성")
    split("grid", "civil", "civil_cards", ctx["civil_by_sub"].get("업계 신기술", []), arg="업계 신기술")
    blk("civil", "civil_tilemap")
    # 05 글로벌 사례
    head("global")
    split("grid", "global", "radar", ctx["radar_zones"])
    split("table", "global", "cases_table", d.get("cases", []))
    split("grid", "global", "community_cards", d.get("community", []))
    # 06 출처·방법론
    head("sources")
    blk("sources", "methodology")
    split("grid", "sources", "glossary", d.get("glossary", []))
    split("grid", "sources", "sources_table", ctx["sources"])
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, help="발행 ID (예: 2026-10-w2_20261014)")
    ap.add_argument("--no-measure", action="store_true", help="측정 없이 블록마다 한 페이지 (디버그용)")
    a = ap.parse_args()
    r = build(a.issue, measure_pages=not a.no_measure)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 1 if r["warnings"] else 0


if __name__ == "__main__":
    sys.exit(main())
