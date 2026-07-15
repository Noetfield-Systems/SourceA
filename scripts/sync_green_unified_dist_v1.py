#!/usr/bin/env python3
"""Mirror green-unified source into dist/ deploy tree (sourcea + unify + root entry pages)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "sites" / "SourceA-landing" / "green-unified"
DIST = GREEN / "dist"
SOURCEA_DIST = DIST / "sourcea"

SKIP_NAMES = {"dist", "scripts", ".DS_Store"}
ROOT_MIRROR = ("index.html", "eval.html", "cookies.html", "privacy.html")


def _copy_tree(src: Path, dst: Path) -> int:
    n = 0
    if not src.is_dir():
        return n
    for item in src.iterdir():
        if item.name in SKIP_NAMES:
            continue
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
            n += 1
        elif item.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            n += 1
    return n


def main() -> int:
    if not GREEN.is_dir():
        print(f"FAIL: missing {GREEN}", file=sys.stderr)
        return 1

    SOURCEA_DIST.mkdir(parents=True, exist_ok=True)
    copied = _copy_tree(GREEN, SOURCEA_DIST)

    for name in ROOT_MIRROR:
        src = GREEN / name
        if src.is_file():
            shutil.copy2(src, DIST / name)

    for sub in ("unify", "unify-demo"):
        src = GREEN / sub
        if src.is_dir():
            dst = DIST / sub
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            sdst = SOURCEA_DIST / sub
            if sdst.exists():
                shutil.rmtree(sdst)
            shutil.copytree(src, sdst)

    print(f"sync_green_unified_dist_v1 OK — mirrored green-unified → dist/sourcea ({copied} top-level entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
