#!/usr/bin/env python3
"""Pulse UP-DR-01..10 deep research upgrade wave — open/done counts."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PLAN = ROOT / "data" / "sourcea-deep-research-10-upgrade-plan-v1.json"
RECEIPT = SINA / "sourcea-deep-research-10-pulse-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def pulse(*, write: bool = True) -> dict[str, Any]:
    doc = _read(PLAN)
    plans = doc.get("upgrade_plans") or []
    done = sum(1 for p in plans if p.get("status") == "done")
    open_n = sum(1 for p in plans if p.get("status") not in ("done",))
    total = len(plans)
    row = {
        "schema": "sourcea-deep-research-10-pulse-v1",
        "ok": total == 10,
        "at": _now(),
        "total": total,
        "done": done,
        "open": open_n,
        "pct": round(100 * done / total) if total else 0,
        "gate_plan": doc.get("gate_plan"),
        "critical_path": doc.get("critical_path"),
        "plans": [
            {"id": p.get("id"), "tier": p.get("tier"), "status": p.get("status"), "title": p.get("title")}
            for p in plans
        ],
    }
    if write:
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = pulse(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"UP-DR pulse {row['done']}/{row['total']} done ({row['pct']}%)")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
