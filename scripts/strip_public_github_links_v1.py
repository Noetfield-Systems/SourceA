#!/usr/bin/env python3
"""Rewrite legacy personal GitHub repo links to Noetfield-Systems public repos."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
if str(ROOT / "scripts") not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT / "scripts"))
from sourcea_public_github_ssot_v1 import boot_repo_url  # noqa: E402

GITHUB_RE = re.compile(r"https://github\.com/kazemnezhadsina144-dot/sourcea-boot[^\"'\\s]*", re.I)
GITHUB_REPO_RE = re.compile(r"kazemnezhadsina144-dot/sourcea-boot", re.I)
CANONICAL_BOOT = boot_repo_url()


def strip_text(text: str) -> str:
    text = GITHUB_RE.sub(CANONICAL_BOOT, text)
    text = GITHUB_REPO_RE.sub("Noetfield-Systems/sourcea-boot", text)
    return text


def run(*, root: Path | None = None) -> dict:
    base = root or GREEN
    changed: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or "dist" in path.parts:
            continue
        if path.suffix.lower() not in {".html", ".js", ".json", ".md"}:
            continue
        raw = path.read_text(encoding="utf-8")
        if "kazemnezhadsina144" not in raw and "github.com/kazemnezhadsina144" not in raw:
            continue
        new = strip_text(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return {"ok": True, "changed": changed, "count": len(changed)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK strip_public_github_links changed={row['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
