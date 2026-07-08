#!/usr/bin/env python3
"""Fail if legacy personal GitHub slugs remain in public sourcea-boot surfaces."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_public_github_ssot_v1 import load_ssot  # noqa: E402

SCAN_ROOTS = [
    ROOT / "packages" / "sourcea-boot",
    ROOT / "packages" / "sourcea-sdk",
    ROOT / "sites" / "SourceA-landing" / "green-unified",
    ROOT / "data" / "sourcea-products-catalog-v1.json",
]

SKIP_PARTS = {".git", "dist", "node_modules", "__pycache__"}
SKIP_FILES = {
    "data/sourcea-public-github-v1.json",
    "scripts/strip_public_github_links_v1.py",
    "scripts/inject_landing_buyer_trust_v1.py",
}


def iter_files() -> list[Path]:
    out: list[Path] = []
    for item in SCAN_ROOTS:
        if item.is_file():
            out.append(item)
            continue
        for path in item.rglob("*"):
            if not path.is_file():
                continue
            if SKIP_PARTS.intersection(path.parts):
                continue
            if path.suffix.lower() not in {".md", ".html", ".json", ".toml", ".py", ".js", ".yml", ".yaml"}:
                continue
            out.append(path)
    return out


def run() -> dict:
    forbidden = load_ssot().get("legacy_forbidden_public_slugs") or []
    findings: list[dict] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for slug in forbidden:
            if slug in text:
                rel = str(path.relative_to(ROOT))
                if rel in SKIP_FILES:
                    continue
                findings.append({"path": rel, "slug": slug})
    return {"ok": not findings, "forbidden": forbidden, "findings": findings}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run()
    if args.json:
        print(json.dumps(row, indent=2))
    elif row["ok"]:
        print("OK validate_sourcea_public_github_ssot_v1")
    else:
        for f in row["findings"]:
            print(f"FAIL {f['path']} contains {f['slug']}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
