#!/usr/bin/env python3
"""Write DONE receipt for one sa — truth layer before REGISTRY closeout."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"

ALLOWED_RECEIPT_SOURCES = frozenset(
    {
        "goal1_lane_broker",
        "restore-broker-proven-v1",
        "api",
        "maintainer_executor",
        "worker_inbox",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_receipt(
    *,
    sa_id: str,
    round_type: str = "verify",
    critical_bugs: int = 0,
    evidence: str = "",
    engine: str = "WORKER",
    source: str = "goal1_lane_broker",
) -> dict:
    if not sa_id.startswith("sa-"):
        return {"ok": False, "error": "INVALID_SA_ID"}
    if round_type.lower() != "verify":
        return {"ok": False, "error": "RECEIPT_VERIFY_ONLY", "hint": "Receipts only on VERIFY turns"}
    if int(critical_bugs) != 0:
        return {"ok": False, "error": "CRITICAL_BUGS", "hint": "critical_bugs must be 0"}
    src = (source or "").strip()
    if not src or src not in ALLOWED_RECEIPT_SOURCES:
        return {
            "ok": False,
            "error": "INVALID_RECEIPT_SOURCE",
            "hint": f"source must be one of: {sorted(ALLOWED_RECEIPT_SOURCES)}",
            "got": source,
        }

    RECEIPTS.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS / f"{sa_id}-receipt.json"
    payload = {
        "schema": "sourcea-sa-receipt-v1",
        "sa_id": sa_id,
        "status": "DONE",
        "round_type": round_type,
        "critical_bugs": 0,
        "engine": engine,
        "source": src,
        "evidence": (evidence or "")[:500],
        "at": _now(),
        "workspace": str(ROOT),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(path), "sa_id": sa_id, "status": "DONE"}
