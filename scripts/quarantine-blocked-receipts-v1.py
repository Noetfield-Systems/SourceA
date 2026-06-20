#!/usr/bin/env python3
"""Move non-DONE receipts out of receipts/ so honest gate stays clean."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"
QUARANTINE = RECEIPTS / "quarantine"

HONEST = frozenset({"DONE", "PASS", "VERIFIED", "CHECK_PASSED"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []
    for p in sorted(RECEIPTS.glob("sa-*-receipt.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        st = str(d.get("status") or "").upper()
        if st in HONEST:
            continue
        dest = QUARANTINE / p.name
        if dest.exists():
            dest = QUARANTINE / f"{p.stem}_{_now().replace(':', '')}.json"
        shutil.move(str(p), str(dest))
        moved.append(p.name)
    print(json.dumps({"ok": True, "moved": moved, "count": len(moved)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
