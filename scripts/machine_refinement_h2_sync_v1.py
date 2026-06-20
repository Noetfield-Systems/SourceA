#!/usr/bin/env python3
"""Merge machine upgrade UP-* rows into H2 pending registry maintainer_ship bucket."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SINA = Path.home() / ".sina"
REG = SINA / "h2-pending-registry-v1.json"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from machine_three_pipelines_lib_v1 import UPGRADE_BOARD, now_iso  # noqa: E402


def sync(*, dry_run: bool = False) -> dict:
    reg = {}
    if REG.is_file():
        reg = json.loads(REG.read_text(encoding="utf-8"))
    bucket = list(reg.get("maintainer_ship") or [])
    existing_ids = {r.get("id") for r in bucket if isinstance(r, dict)}
    added = []
    for row in UPGRADE_BOARD:
        uid = row["id"]
        if uid in existing_ids:
            continue
        entry = {
            "id": uid,
            "title": row["goal"],
            "win": row["win"],
            "cadence": row["cadence"],
            "form_pick": row["form_pick"],
            "baseline": "~/.sina/machine-upgrade-baseline-v1.json",
            "owner": "worker",
            "source": "machine_refinement_h2_sync_v1.py",
        }
        bucket.append(entry)
        added.append(uid)
    reg["maintainer_ship"] = bucket
    reg["updated_at"] = now_iso()
    reg["machine_refinement_sync"] = {"added": added, "at": now_iso()}
    if not dry_run:
        REG.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "added": added, "maintainer_ship_count": len(bucket)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sync(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"H2 sync added={row['added']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
