#!/usr/bin/env python3
"""Move superseded WTM locked docs to archive and verify canonical vN+1 exists."""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = SOURCE_A / "archive" / "superseded" / "wtm"
MANIFEST = ARCHIVE_ROOT / "ARCHIVE_MANIFEST_LOCKED_v1.md"

CANONICAL_WTM = [
    "WORLD_TARGET_MODEL_MAP_LOCKED",
    "WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED",
    "SINA_BIG_PICTURE_ROADMAP_LOCKED",
    "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED",
]


def latest_version(stem: str) -> int | None:
    best = 0
    for p in SOURCE_A.glob(f"{stem}_v*.md"):
        m = re.search(r"_v(\d+)\.md$", p.name)
        if m:
            best = max(best, int(m.group(1)))
    return best or None


def archive_version(stem: str, version: int, *, dry_run: bool) -> dict:
    src = SOURCE_A / f"{stem}_v{version}.md"
    if not src.is_file():
        return {"ok": False, "error": f"missing {src.name}"}
    dest_dir = ARCHIVE_ROOT / f"v{version}"
    dest = dest_dir / src.name
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            return {"ok": False, "error": f"already archived: {dest}"}
        src.rename(dest)
    return {"ok": True, "archived": str(dest.relative_to(SOURCE_A))}


def main() -> int:
    ap = argparse.ArgumentParser(description="Archive superseded WTM locked docs")
    ap.add_argument("--version", type=int, required=True, help="Version to archive (e.g. 1)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    results = []
    for stem in CANONICAL_WTM:
        nxt = args.version + 1
        canon = SOURCE_A / f"{stem}_v{nxt}.md"
        if not canon.is_file():
            print(f"BLOCKED: write {canon.name} before archiving v{args.version}", file=sys.stderr)
            return 2
        results.append(archive_version(stem, args.version, dry_run=args.dry_run))
    failed = [r for r in results if not r.get("ok")]
    if failed:
        for r in failed:
            print(r.get("error"), file=sys.stderr)
        return 1
    print(f"OK: archived v{args.version} → archive/superseded/wtm/v{args.version}/")
    if not args.dry_run:
        print(f"Reminder: append evidence row to {MANIFEST.relative_to(SOURCE_A)}")
        print(f"Reminder: update scripts/system_roadmap.py MAP_DOC / LAW_DOC paths to v{args.version + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
