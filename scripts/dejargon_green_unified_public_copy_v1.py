#!/usr/bin/env python3
"""Apply customer-facing copy normalize — delegates to sourcea_lexicon_normalize_repo_v1 pairs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "sites" / "SourceA-landing" / "green-unified"
SCRUB = ROOT / "scripts" / "sourcea_lexicon_normalize_repo_v1.py"

SKIP_SUBSTRINGS = ("investors.html",)


def _apply():
    spec = importlib.util.spec_from_file_location("thread_scrub", SCRUB)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod._apply


def main() -> int:
    apply_text = _apply()
    changed = 0
    for path in sorted(GREEN.rglob("*")):
        if "dist" in path.parts or path.name.startswith("."):
            continue
        if any(x in str(path) for x in SKIP_SUBSTRINGS):
            continue
        if path.suffix not in (".html", ".js", ".css", ".json") and path.name != "README.md":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        new = apply_text(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"dejargon_green_unified_public_copy_v1 OK — {changed} files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
