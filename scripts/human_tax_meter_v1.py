"""Human Tax meter — observe + record (NF-GOVERNED-WORK-PACKET-CONTROL-V1)."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.governed_work_packet_v1 import compute_htu, event_is_tax  # noqa: E402

LEDGER = Path.home() / ".sina" / "human-tax-events-v1.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_owner_message(text: str, *, prior_goal_intent: str = "") -> str:
    t = (text or "").strip().lower()
    prior = (prior_goal_intent or "").strip().lower()
    if prior and prior in t and ("only" in t or "same" in t or "again" in t or "just" in t):
        return "GOAL_RESTATEMENT"
    if "scope" in t and ("only" in t or "don't" in t or "do not" in t):
        return "SCOPE_RESTATEMENT"
    return "OWNER_DECISION"


def record_human_tax_event(
    *,
    task_id: str,
    event_type: str,
    avoidable: bool = True,
    active_human_seconds: float = 0.0,
    evidence_ref: str = "",
    goal_changed: bool = False,
    new_information: bool = False,
) -> dict:
    event = {
        "schema": "noetfield.human_tax_event.v1",
        "event_id": f"he_{uuid.uuid4().hex[:12]}",
        "task_id": task_id,
        "event_type": event_type,
        "new_information": bool(new_information),
        "goal_changed": bool(goal_changed),
        "avoidable": bool(avoidable),
        "active_human_seconds": float(active_human_seconds),
        "root_layer": "OWNER",
        "evidence_ref": evidence_ref or None,
        "at": _now(),
    }
    units = 0.0
    if event_is_tax(event_type, avoidable=avoidable):
        units = compute_htu(
            active_correction_minutes=active_human_seconds / 60.0,
            goal_restatements=1 if event_type == "GOAL_RESTATEMENT" else 0,
            scope_restatements=1 if event_type == "SCOPE_RESTATEMENT" else 0,
            manual_rollbacks=1 if event_type == "MANUAL_ROLLBACK" else 0,
            manual_restarts=1 if event_type == "MANUAL_RESTART" else 0,
            false_done_rejections=1 if event_type == "FALSE_DONE_REJECTION" else 0,
            out_of_scope_repairs=1 if event_type == "OUT_OF_SCOPE_REPAIR" else 0,
        )
    event["htu_delta"] = units
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")
    return event


if __name__ == "__main__":
    e = record_human_tax_event(task_id="task_selftest", event_type="GOAL_RESTATEMENT", active_human_seconds=30)
    print(json.dumps(e, indent=2))
