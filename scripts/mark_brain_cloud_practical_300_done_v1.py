#!/usr/bin/env python3
"""Mark brain-cloud-practical-300 plan rows done with cloud_proof counter."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "brain-cloud-practical-300-plan-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_range(*, start_id: str, end_id: str, cloud_proof: bool = True) -> dict:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    plans = plan.get("plans") or []
    start_seq = int(start_id.split("-")[1])
    end_seq = int(end_id.split("-")[1])
    touched = 0
    for row in plans:
        seq = int(row.get("seq") or 0)
        if start_seq <= seq <= end_seq:
            if row.get("status") != "done":
                row["status"] = "done"
                row["done_at"] = _now()
                if cloud_proof:
                    row["cloud_proof"] = True
                touched += 1
    done = sum(1 for p in plans if p.get("status") == "done")
    cloud_proven = sum(1 for p in plans if p.get("cloud_proof"))
    plan["saved_at"] = _now()
    plan["progress"] = {
        "total": len(plans),
        "done": done,
        "planned": len(plans) - done,
        "cloud_proven": cloud_proven,
    }
    PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    head = next((p for p in plans if p.get("status") != "done"), {})
    return {
        "ok": True,
        "touched": touched,
        "done": done,
        "cloud_proven": cloud_proven,
        "head_id": head.get("id"),
        "range": f"{start_id}..{end_id}",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="from_id", default="C300-001")
    ap.add_argument("--to", dest="to_id", default="C300-050")
    ap.add_argument("--no-cloud-proof", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = mark_range(start_id=args.from_id, end_id=args.to_id, cloud_proof=not args.no_cloud_proof)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: {row['range']} touched={row['touched']} done={row['done']}/{row['done']+row.get('planned',0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
