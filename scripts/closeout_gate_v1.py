#!/usr/bin/env python3
"""Gate REGISTRY closeout — receipt or broker VERIFY only. No batch stamp.

Law: REGISTRY_DRAIN_RAIL · GOAL_EXECUTION_ACTIVE §closeout
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"
ROUND_REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"
LOGS = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"
OVERRIDE_FLAG = Path.home() / ".sina" / "closeout-founder-override-v1.flag"

HONEST_RECEIPT = frozenset({"DONE", "PASS", "VERIFIED", "CHECK_PASSED"})

# Bulk-stamp evidence — one proof pasted across many sa (audit Jun 2026)
BATCH_EVIDENCE_RE = re.compile(
    r"(pack\d+\s+.*verify-only|"
    r"validate-phase-s\d+.*machine proof|"
    r"wire\+dispatch\+hub PASS|"
    r"wire\+runreceipt\+dispatch PASS|"
    r"validators\+batch PASS|"
    r"spine\+event-bus\+batch PASS|"
    r"commercial\+pre-llm verify-only)",
    re.I,
)


def _load_receipt(sa_id: str) -> dict | None:
    p = RECEIPTS / f"{sa_id}-receipt.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _worker_report() -> dict:
    if not ROUND_REPORT.is_file():
        return {}
    try:
        return json.loads(ROUND_REPORT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _evidence_used_for_other_sa(*, sa_id: str, evidence: str) -> bool:
    """Block same evidence string already used for a different sa."""
    needle = (evidence or "").strip()[:120]
    if len(needle) < 12:
        return False
    count = 0
    for p in LOGS.glob("*plan-with-no-asf*.yaml"):
        if sa_id in p.name:
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if needle in t:
            count += 1
            if count >= 1:
                return True
    return False


def check_closeout_allowed(
    *,
    task_id: str,
    evidence: str,
    authorized_source: str = "",
    round_type: str = "",
    critical_bugs: int = 0,
) -> dict:
    """Return {ok: True} or {ok: False, error, hint}."""
    if not task_id.startswith("sa-"):
        return {"ok": False, "error": "INVALID_SA_ID", "hint": "task_id must be sa-XXXX"}

    if OVERRIDE_FLAG.is_file():
        return {"ok": True, "mode": "founder_override_flag", "warning": "OVERRIDE_ACTIVE"}

    ev = (evidence or "").strip()
    if not ev or len(ev) < 12:
        return {"ok": False, "error": "EVIDENCE_TOO_SHORT", "hint": "Per-sa validator output required"}

    if BATCH_EVIDENCE_RE.search(ev):
        return {
            "ok": False,
            "error": "BATCH_EVIDENCE_BLOCKED",
            "hint": "Bulk pack evidence forbidden — one sa one proof",
            "law": "CLOSEOUT_GATE_LOCKED_v1",
        }

    rec = _load_receipt(task_id)
    if rec and str(rec.get("status") or "").upper() in HONEST_RECEIPT:
        # Permanent: receipt alone is insufficient — broker cycle must be PASS (INCIDENT-007)
        sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
        from monitor_honesty_lib_v1 import broker_column, load_broker_cycles, worker_column  # noqa: WPS433

        cycle = load_broker_cycles().get(task_id)
        worker = worker_column(rec=rec, reg_st="done", in_queue=False)
        broker = broker_column(
            sa=task_id,
            cycle=cycle,
            in_queue=False,
            worker=worker,
            reg_st="done",
            has_receipt=True,
        )
        if worker != "PASS" or broker != "PASS":
            return {
                "ok": False,
                "error": "BROKER_RECEIPT_GATE",
                "worker": worker,
                "broker": broker,
                "hint": "goal1_lane_broker worker-submit VERIFY before closeout_sa_task",
                "law": "WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md",
            }
        return {"ok": True, "mode": "receipt", "receipt_status": rec.get("status"), "broker": broker}

    from yaml_quarantine_lib_v1 import evidence_is_quarantined_only  # noqa: WPS433

    if evidence_is_quarantined_only(sa_id=task_id, evidence=ev):
        return {
            "ok": False,
            "error": "QUARANTINED_YAML_ONLY",
            "hint": "Closeout YAML quarantined — cannot restore from batch proof",
            "law": "CLOSEOUT_GATE_LOCKED_v1",
        }

    if _evidence_used_for_other_sa(sa_id=task_id, evidence=ev):
        return {
            "ok": False,
            "error": "DUPLICATE_EVIDENCE_BLOCKED",
            "hint": "Evidence string already used for another sa",
        }

    src = (authorized_source or "").strip()
    if src == "goal1_lane_broker":
        report = _worker_report()
        if str(report.get("sa_focus") or "") != task_id:
            return {"ok": False, "error": "REPORT_SA_MISMATCH", "hint": "WORKER_ROUND_REPORT sa_focus must match"}
        if str(report.get("round_type") or "").lower() != "verify":
            return {"ok": False, "error": "NOT_VERIFY_TURN", "hint": "REGISTRY done only on VERIFY turn"}
        if int(report.get("critical_bugs") or critical_bugs or 0) != 0:
            return {"ok": False, "error": "CRITICAL_BUGS", "hint": "critical_bugs must be 0"}
        if not rec:
            return {
                "ok": False,
                "error": "RECEIPT_REQUIRED",
                "hint": "Write receipts/<sa>-receipt.json before closeout (worker_receipt_v1)",
            }
        return {"ok": True, "mode": "broker_verify", "receipt_status": rec.get("status")}

    return {
        "ok": False,
        "error": "CLOSEOUT_UNAUTHORIZED",
        "hint": "Use goal1_lane_broker worker-submit VERIFY + receipt, or registry_updater from DONE receipt",
        "law": "CLOSEOUT_GATE_LOCKED_v1",
    }
