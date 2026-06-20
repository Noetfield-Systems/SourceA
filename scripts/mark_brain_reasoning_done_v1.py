#!/usr/bin/env python3
"""Mark brain cloud reasoning upgrade done with brain_proof receipt logged."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_done(upgrade_id: str, *, evidence: str = "") -> dict:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    wo = _read_json(SINA / "brain-outbound-work-order-active-v1.json")
    work_order_id = str(wo.get("work_order_id") or "wo-brain-unified-plans-upgrade")

    receipt = {
        "schema": "brain-reasoning-receipt-v1",
        "upgrade_id": upgrade_id,
        "at": _now(),
        "brain_proof": True,
        "cloud_proof": True,
        "work_order_id": work_order_id,
        "evidence": evidence or f"{upgrade_id} brain reasoning acceptance",
        "founder_line": f"Brain · {upgrade_id} · disk-first reasoning receipt",
    }
    path = SINA / f"brain-reasoning-receipt-{upgrade_id.lower()}.json"
    SINA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    matched = False
    for u in plan.get("upgrades") or []:
        if u.get("id") != upgrade_id:
            continue
        u["status"] = "done"
        u["brain_proof"] = True
        u["cloud_proof"] = True
        u["work_order_id"] = work_order_id
        u["local_worker_deprecated"] = True
        u["brain_receipt_path"] = str(path)
        matched = True
        break
    if not matched:
        return {"ok": False, "error": f"{upgrade_id} not found"}

    upgrades = plan.get("upgrades") or []
    done = sum(1 for u in upgrades if u.get("status") == "done")
    plan["progress"] = {
        **(plan.get("progress") or {}),
        "done": done,
        "planned": sum(1 for u in upgrades if u.get("status") != "done"),
        "pct": round(100 * done / max(len(upgrades), 1), 2),
        "mac_proven": sum(1 for u in upgrades if u.get("mac_proof")),
    }
    plan["saved_at"] = _now()
    PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "upgrade_id": upgrade_id, "receipt_path": str(path), "done": done}


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("upgrade_id")
    ap.add_argument("--evidence", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = mark_done(args.upgrade_id, evidence=args.evidence)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
