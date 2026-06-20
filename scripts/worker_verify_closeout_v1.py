#!/usr/bin/env python3
"""Canonical Worker VERIFY closeout — receipt + broker PASS before REGISTRY done.

Law: WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md · closeout_gate_v1.py
Forbidden: direct REGISTRY.json / sa-XXXX.md status edits without this path.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RECEIPTS = ROOT / "receipts"


def _broker_pass(sa_id: str) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from monitor_honesty_lib_v1 import broker_column, load_broker_cycles, worker_column  # noqa: WPS433

    rec_path = RECEIPTS / f"{sa_id}-receipt.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.is_file() else None
    if not rec:
        return {"ok": False, "error": "MISSING_RECEIPT", "path": str(rec_path)}
    cycle = load_broker_cycles().get(sa_id)
    worker = worker_column(rec=rec, reg_st="done", in_queue=False)
    broker = broker_column(
        sa=sa_id,
        cycle=cycle,
        in_queue=False,
        worker=worker,
        reg_st="done",
        has_receipt=True,
    )
    roles = sorted(cycle.roles) if cycle else []
    ok = worker == "PASS" and broker == "PASS"
    return {
        "ok": ok,
        "worker": worker,
        "broker": broker,
        "roles": roles,
        "receipt": str(rec_path),
        "hint": (
            "Run goal1_lane_broker.py worker-submit with WORKER_ROUND_REPORT first; "
            "then repair-broker-gaps only for audit backfill"
        ),
    }


def verify_closeout(
    *,
    sa_id: str,
    evidence: str,
    task_validator: str = "",
    source: str = "goal1_lane_broker",
    critical_bugs: int = 0,
    dry_run: bool = False,
) -> dict:
    if not sa_id.startswith("sa-"):
        return {"ok": False, "error": "INVALID_SA_ID"}

    if task_validator:
        proc = subprocess.run(
            ["bash", task_validator],
            cwd=str(SCRIPTS),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return {
                "ok": False,
                "error": "TASK_VALIDATOR_FAIL",
                "validator": task_validator,
                "stderr": (proc.stderr or proc.stdout)[-500:],
            }

    bp = _broker_pass(sa_id)
    if not bp.get("ok") and bp.get("broker") == "PEND":
        repair = subprocess.run(
            [sys.executable, str(SCRIPTS / "repair-broker-gaps-from-receipt-v1.py"), "--sa", sa_id],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if repair.returncode == 0:
            bp = _broker_pass(sa_id)
            bp["auto_repaired"] = True
    if not bp.get("ok"):
        return {"ok": False, "error": "BROKER_RECEIPT_GATE", **bp}

    if dry_run:
        return {"ok": True, "dry_run": True, "sa_id": sa_id, "broker_proof": bp}

    sys.path.insert(0, str(SCRIPTS))
    from closeout_sa_task import closeout  # noqa: WPS433

    out = closeout(
        task_id=sa_id,
        evidence=evidence,
        authorized_source=source,
        round_type="verify",
        critical_bugs=critical_bugs,
    )
    return {"ok": bool(out.get("ok")), "sa_id": sa_id, "closeout": out, "broker_proof": bp}


def main() -> int:
    ap = argparse.ArgumentParser(description="Worker VERIFY closeout (receipt + broker gate)")
    ap.add_argument("--sa", required=True, help="sa-XXXX")
    ap.add_argument("--evidence", required=True, help="Per-sa validator proof string")
    ap.add_argument("--task-validator", default="", help="Optional bash validator path under scripts/")
    ap.add_argument("--source", default="goal1_lane_broker")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    tv = args.task_validator
    if tv and not tv.startswith("/"):
        tv = str(SCRIPTS / tv)

    out = verify_closeout(
        sa_id=args.sa,
        evidence=args.evidence,
        task_validator=tv,
        source=args.source,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
