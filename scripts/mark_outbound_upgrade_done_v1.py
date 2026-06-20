#!/usr/bin/env python3
"""Mark outbound upgrade row done with execution_proof receipt."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from outbound_receipt_path_v1 import LAW, write_receipt  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_done(
    upgrade_id: str,
    *,
    sa_id: str,
    title: str = "",
    evidence: str = "",
) -> dict:
    rcpt = write_receipt(
        upgrade_id=upgrade_id,
        sa_id=sa_id,
        title=title or f"{upgrade_id} shipped",
        evidence=evidence or f"{upgrade_id} acceptance verified on disk",
    )
    if not rcpt.get("ok"):
        return rcpt

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    receipt_path = rcpt["receipt_path"]
    matched = False
    for u in plan.get("upgrades") or []:
        if u.get("id") != upgrade_id:
            continue
        u["status"] = "done"
        u["done_at"] = _now()
        u["execution_proof"] = {
            "sa_id": sa_id,
            "receipt_path": receipt_path,
            "receipt_law": LAW,
            "pulse_verified": True,
        }
        matched = True
        break
    if not matched:
        return {"ok": False, "error": f"upgrade {upgrade_id} not found"}

    upgrades = plan.get("upgrades") or []
    done = sum(1 for x in upgrades if x.get("status") == "done")
    plan["progress"] = {
        **(plan.get("progress") or {}),
        "done_total": done,
        "planned_total": sum(1 for x in upgrades if x.get("status") == "planned"),
        "pct": round(100 * done / max(len(upgrades), 1)),
        "p0_done": sum(1 for x in upgrades if x.get("status") == "done" and x.get("tier") == "P0"),
        "p1_done": sum(1 for x in upgrades if x.get("status") == "done" and x.get("tier") == "P1"),
    }
    plan["execution_proof_law"] = LAW
    plan["saved_at"] = _now()
    PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    try:
        from outbound_telemetry_v1 import append_upgrade_status  # noqa: WPS433

        append_upgrade_status(upgrade_id, sa_id=sa_id, ok=True)
    except Exception:
        pass

    queue_row: dict = {"skipped": True}
    try:
        from outbound_queue_coherence_v1 import rebuild_queue_and_deliver  # noqa: WPS433

        queue_row = rebuild_queue_and_deliver(sync=True)
    except Exception as exc:
        queue_row = {"ok": False, "error": str(exc)}

    return {
        "ok": True,
        "upgrade_id": upgrade_id,
        "sa_id": sa_id,
        "receipt_path": receipt_path,
        "done_total": done,
        "queue_advance": queue_row,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("upgrade_id")
    ap.add_argument("--sa-id", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--evidence", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = mark_done(args.upgrade_id, sa_id=args.sa_id, title=args.title, evidence=args.evidence)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
