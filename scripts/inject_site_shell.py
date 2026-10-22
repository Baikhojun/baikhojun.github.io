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
    Path("lk1800/index.html"),
    # plan/ (private couple calendar) and its redirect pages must not receive the public site shell.
)
THEMED_PAGES = {
    Path("house/index.html"), Path("house/m/index.html"),
    Path("cukoo/index.html"), Path("cukoo/m/index.html"),
    Path("tv/index.html"), Path("tv/m/index.html"), Path("lk1800/index.html"),
}
START = "<!-- UNFADE-SHELL:START -->"
END = "<!-- UNFADE-SHELL:END -->"


def shell_block(page: Path) -> str:
    relative_root = "../" * len(page.parent.parts)
    tool_theme = (
        f'<link rel="stylesheet" href="{relative_root}css/unfade-tool-theme.css">\n'
        if page in THEMED_PAGES else ""
    )
    if page.parts[0] in {"cukoo", "tv", "lk1800"}:
        tool_theme += f'<link rel="stylesheet" href="{relative_root}css/unfade-premium.css">\n'
    return f'''{START}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css">
<link rel="stylesheet" href="{relative_root}css/unfade-shell.css">
{tool_theme}<script defer src="{relative_root}js/unfade-shell.js" data-unfade-root="{relative_root}"></script>
{END}'''


def inject(page: Path) -> None:
    destination = ROOT / page
    html = destination.read_text(encoding="utf-8")
    if page.parts[0] in {"cukoo", "tv", "lk1800"}:
        # Apply the palette before the first paint, including stored dark preferences.
        html = html.replace(
            "<body>",
            f'<body class="unfade-tool-theme unfade-premium" data-unfade-tool="{page.parts[0]}">',
            1,
        )
    elif page.parts[0] == "house" and 'data-unfade-tool="house"' not in html:
        # The house layout offsets (fixed credit bar and sidebar) must apply before the first paint.
        html = re.sub(r"<body(?=[\s>])", '<body class="unfade-tool-theme" data-unfade-tool="house"', html, count=1)
    html = re.sub(r"\n?<!-- UNFADE-SHELL:START -->.*?<!-- UNFADE-SHELL:END -->", "", html, flags=re.DOTALL)
    if "</head>" not in html:
        raise ValueError(f"Missing </head>: {destination}")
    html = html.replace("</head>", f"{shell_block(page)}\n</head>", 1)
    destination.write_text(html, encoding="utf-8", newline="\n")
    print(f"updated {page.as_posix()}")


if __name__ == "__main__":
    for page in PAGES:
        inject(page)
