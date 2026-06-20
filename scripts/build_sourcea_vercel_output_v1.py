#!/usr/bin/env python3
"""Build static output for SourceA Vercel deploy (source-a project).

Assembles green-unified under /sourcea/ plus vendored /assets/ for Gate K.
Law: SourceA-landing/green-unified · vercel-static/assets
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
DIST = GREEN / "dist"
VENDORED_ASSETS = ROOT / "SourceA-landing" / "vercel-static" / "assets"
DESKTOP_ASSETS = Path.home() / "Desktop" / "agentrun-app" / "assets"

ALLOW_SUFFIX = {".html", ".css", ".js", ".svg", ".json", ".mp4", ".webp", ".png", ".jpg"}


def _copy_tree(src: Path, dest: Path) -> int:
    n = 0
    skip_dirs = {"dist", ".vercel", "__pycache__", "node_modules"}
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        if f.name == "vercel.json":
            continue
        if any(part in skip_dirs for part in f.relative_to(src).parts):
            continue
        if f.suffix.lower() not in ALLOW_SUFFIX and f.name not in ("favicon.svg",):
            continue
        rel = f.relative_to(src)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        n += 1
    return n


def _sync_assets(dest_assets: Path) -> None:
    dest_assets.mkdir(parents=True, exist_ok=True)
    src = VENDORED_ASSETS if VENDORED_ASSETS.is_dir() else DESKTOP_ASSETS
    if not src.is_dir():
        raise SystemExit(f"FAIL: no assets source — need {VENDORED_ASSETS} or {DESKTOP_ASSETS}")
    for name in ("agentrun.css", "agentrun.js", "favicon.svg"):
        f = src / name
        if not f.is_file():
            raise SystemExit(f"FAIL: missing asset {f}")
        shutil.copy2(f, dest_assets / name)


def build(*, clean: bool = True) -> dict:
    if not GREEN.is_dir():
        raise SystemExit(f"FAIL: green-unified missing: {GREEN}")
    if clean and DIST.is_dir():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    sourcea_dir = DIST / "sourcea"
    page_count = _copy_tree(GREEN, sourcea_dir)
    _sync_assets(DIST / "assets")

    root_index = DIST / "index.html"
    root_index.write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="0;url=/sourcea/" />
  <link rel="canonical" href="/sourcea/" />
  <title>SourceA</title>
</head>
<body>
  <p><a href="/sourcea/">SourceA — Execution Proof Infrastructure</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )

    return {
        "ok": True,
        "dist": str(DIST.relative_to(ROOT)),
        "page_count": page_count,
        "urls": {
            "root": "/",
            "home": "/sourcea/",
            "trust": "/sourcea/trust/",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Build SourceA Vercel static dist")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = build()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: {row['dist']} pages={row['page_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
