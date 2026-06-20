#!/usr/bin/env python3
"""Validate markdown doc headers include date + exact UTC time.

Law: docs/SOURCEA_DOC_DATETIME_MANDATORY_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAW = "docs/SOURCEA_DOC_DATETIME_MANDATORY_LOCKED_v1.md"

# **Saved:** 2026-06-16T05:47:17Z  OR  saved_at: / **saved_at:**
SAVED_RE = re.compile(
    r"(?:\*\*Saved:\*\*|\*\*saved_at:\*\*|saved_at:)\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)",
    re.I,
)
DATE_ONLY_RE = re.compile(
    r"(?:\*\*Saved:\*\*|\*\*saved_at:\*\*|saved_at:)\s*(\d{4}-\d{2}-\d{2})(?!T)",
    re.I,
)


def check_file(path: Path, *, scan_lines: int = 12) -> dict:
    if not path.is_file():
        return {"ok": False, "path": str(path), "reason": "missing_file"}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return {"ok": False, "path": str(path), "reason": str(e)}
    head = "\n".join(lines[:scan_lines])
    if SAVED_RE.search(head):
        m = SAVED_RE.search(head)
        return {"ok": True, "path": str(path), "saved": m.group(1) if m else None}
    if DATE_ONLY_RE.search(head):
        return {
            "ok": False,
            "path": str(path),
            "reason": "date_only_no_exact_time",
            "law": LAW,
            "fix": "Use **Saved:** YYYY-MM-DDTHH:MM:SSZ",
        }
    return {
        "ok": False,
        "path": str(path),
        "reason": "missing_saved_timestamp",
        "law": LAW,
        "fix": "Add **Saved:** YYYY-MM-DDTHH:MM:SSZ in first 12 lines",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate doc datetime header")
    ap.add_argument("paths", nargs="*", help="Files to check (default: recent LOCKED docs)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    paths = [Path(p) for p in args.paths] if args.paths else [
        ROOT / "docs/SOURCEA_1000_STEP_MASTER_UPGRADE_PLAN15JUNE_LOCKED_v1.md",
        ROOT / "docs/SOURCEA_CRAWL_MIRROR_PIPELINE_LOCKED_v1.md",
        ROOT / "docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md",
        ROOT / "docs/SOURCEA_DOC_DATETIME_MANDATORY_LOCKED_v1.md",
    ]

    rows = [check_file(p) for p in paths]
    ok = all(r.get("ok") for r in rows)
    if args.json:
        import json

        print(json.dumps({"ok": ok, "results": rows}, indent=2))
    else:
        for r in rows:
            status = "PASS" if r.get("ok") else "FAIL"
            print(f"{status}: {r.get('path')} — {r.get('reason') or r.get('saved')}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
