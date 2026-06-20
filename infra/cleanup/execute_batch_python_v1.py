#!/usr/bin/env python3
"""Execute cleanup-manifest rows — pure Python (no xargs). Mac-safe single batch."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "infra/cleanup/cleanup-manifest.md"


def parse_rows(batch: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if f"| {batch} |" not in line or not line.strip().startswith("| `./"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8:
            continue
        src = parts[1].strip("`").lstrip("./")
        dest = parts[4].strip("`").rstrip("/")
        action = parts[6]
        if action not in ("move", "archive"):
            continue
        rows.append((src, dest, action))
    return rows


def execute(*, batch: str, dry_run: bool) -> int:
    if not MANIFEST.is_file():
        print(f"MISSING manifest: {MANIFEST}", file=sys.stderr)
        return 1
    moved = skipped = 0
    for src, dest, action in parse_rows(batch):
        src_path = ROOT / src
        if action == "archive":
            target_dir = ROOT / "archive" / "root-stubs"
        else:
            target_dir = ROOT / dest
        target = target_dir / src_path.name
        if not src_path.is_file():
            print(f"SKIP missing: {src}")
            skipped += 1
            continue
        if target.is_file():
            print(f"SKIP exists: {target}")
            skipped += 1
            continue
        if dry_run:
            print(f"DRY-RUN {action}: {src_path} -> {target}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(target))
            print(f"OK {action}: {src} -> {target}")
        moved += 1
    print(f"Batch {batch} done: moved/archived={moved} skipped={skipped} dry_run={dry_run}")
    return 0 if moved > 0 or skipped >= 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return execute(batch=args.batch, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
