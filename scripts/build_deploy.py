#!/usr/bin/env python3
"""Rebuild the published UNFADE tool pages from their in-repo source projects.

Usage: python scripts/build_deploy.py
The script does not crawl the web. It only uses checked-in source/data files.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HOUSE = ROOT / "projects" / "house-guide"
CUCKOO = ROOT / "projects" / "cuckoo-decoder"


def run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def main() -> None:
    # The source generator writes the current PC/mobile single-file artifacts.
    run(sys.executable, "build_all.py", cwd=CUCKOO)
    shutil.copy2(CUCKOO / "cuckoo-decoder.html", ROOT / "cukoo" / "index.html")
    shutil.copy2(CUCKOO / "cuckoo-decoder-mobile.html", ROOT / "cukoo" / "m" / "index.html")

    # These source-owned scripts add the correct mobile redirect and analytics.
    run(sys.executable, "deploy_house.py", str(ROOT), cwd=HOUSE)
    run(sys.executable, "deploy_tv.py", str(ROOT), cwd=CUCKOO / "TV")
    run(sys.executable, "inject_site_shell.py", cwd=ROOT / "scripts")


if __name__ == "__main__":
    main()
