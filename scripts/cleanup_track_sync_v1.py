#!/usr/bin/env python3
"""Sync cleanup track progress receipt from manifest + inventory (read-only scan)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infra/cleanup/cleanup-manifest.md"
INVENTORY = ROOT / "infra/cleanup/inventory-root.tsv"
OUT = ROOT / "data/cleanup-track-progress-v1.json"


def _inventory_count() -> int:
    if not INVENTORY.is_file():
        return 0
    lines = INVENTORY.read_text(encoding="utf-8").strip().splitlines()
    return max(0, len(lines) - 1)


def _batch4_sources() -> list[str]:
    rows: list[str] = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if "| 4 |" not in line:
            continue
        m = re.match(r"\|\s*`(\./[^`]+)`", line)
        if m:
            rows.append(m.group(1).lstrip("./"))
    return rows


def _preflight_batch4() -> dict:
    sources = _batch4_sources()
    present = sum(1 for s in sources if (ROOT / s).is_file())
    collisions = 0
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if "| 4 |" not in line or not line.strip().startswith("| `./"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8:
            continue
        src = parts[1].strip("`").lstrip("./")
        dest = parts[4].strip("`").rstrip("/")
        action = parts[6]
        if action == "archive":
            target = ROOT / dest / Path(src).name
        else:
            target = ROOT / dest / Path(src).name
        if target.is_file() and (ROOT / src).is_file() and action == "move":
            collisions += 1
    return {
        "sources_present": present,
        "sources_total": len(sources),
        "dest_collisions": collisions,
    }


def sync(*, write: bool = True) -> dict:
    existing = {}
    if OUT.is_file():
        existing = json.loads(OUT.read_text(encoding="utf-8"))

    count = _inventory_count()
    pre = _preflight_batch4()
    row = existing.copy()
    row.update(
        {
            "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "inventory_path": str(INVENTORY.relative_to(ROOT)),
            "root_files": {
                **(existing.get("root_files") or {}),
                "current": count,
                "after_batch_4_expected": count - pre["sources_total"],
            },
        }
    )
    batches = row.get("batches") or []
    for b in batches:
        if b.get("id") == "4":
            b["preflight"] = {
                **(b.get("preflight") or {}),
                **pre,
                "all_sources_present": pre["sources_present"] == pre["sources_total"],
            }
    row["batches"] = batches

    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return row


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Sync cleanup track progress receipt")
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    row = sync(write=not args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
