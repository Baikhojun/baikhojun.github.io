#!/usr/bin/env python3
"""Adds the shared UNFADE light-mode shell to published tool pages.

Run after updating a generated tool page. The markers make it safe to run again.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    Path("house/index.html"), Path("house/m/index.html"),
    Path("cukoo/index.html"), Path("cukoo/m/index.html"),
    Path("tv/index.html"), Path("tv/m/index.html"),
    Path("lk1800/index.html"), Path("plan/index.html"), Path("plan/m/index.html"),
    Path("schedule/index.html"), Path("m/index.html"),
)
START = "<!-- UNFADE-SHELL:START -->"
END = "<!-- UNFADE-SHELL:END -->"


def shell_block(page: Path) -> str:
    relative_root = "../" * len(page.parent.parts)
    return f'''{START}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css">
<link rel="stylesheet" href="{relative_root}css/unfade-shell.css">
<script defer src="{relative_root}js/unfade-shell.js" data-unfade-root="{relative_root}"></script>
{END}'''


def inject(page: Path) -> None:
    destination = ROOT / page
    html = destination.read_text(encoding="utf-8")
    html = re.sub(r"\n?<!-- UNFADE-SHELL:START -->.*?<!-- UNFADE-SHELL:END -->", "", html, flags=re.DOTALL)
    if "</head>" not in html:
        raise ValueError(f"Missing </head>: {destination}")
    html = html.replace("</head>", f"{shell_block(page)}\n</head>", 1)
    destination.write_text(html, encoding="utf-8", newline="\n")
    print(f"updated {page.as_posix()}")


if __name__ == "__main__":
    for page in PAGES:
        inject(page)
