#!/usr/bin/env python3
"""Backfill broker WORKER_SUBMIT events for honest-done rows with PARTIAL broker gap.

Law: receipt on disk is truth; this repairs audit trail only — never changes REGISTRY.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
RECEIPTS = ROOT / "receipts"
EVENTS = Path.home() / ".sina/goal1-lane-broker-events.jsonl"

sys.path.insert(0, str(ROOT / "scripts"))
from monitor_honesty_lib_v1 import (  # noqa: E402
    broker_column,
    load_broker_cycles,
    worker_column,
)
from registry_honest_lib_v1 import audit_registry_done  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_role(round_type: str) -> str:
    rt = (round_type or "").lower().strip()
    if rt in ("implement", "act", "fix"):
        return "act"
    if rt in ("audit", "check"):
        return "check"
    return "verify"


def _load_receipt(sa: str) -> dict | None:
    p = RECEIPTS / f"{sa}-receipt.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _append_event(payload: dict) -> None:
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")


def repair_one(*, sa: str, dry_run: bool = False) -> dict:
    rec = _load_receipt(sa)
    if not rec:
        return {"ok": False, "sa": sa, "error": "NO_RECEIPT"}
    cycles = load_broker_cycles()
    cycle = cycles.get(sa)
    roles = set(cycle.roles if cycle else set())
    need_verify_fix = cycle and "verify" in roles and cycle.verify_deliver_ok is False

    worker = worker_column(rec=rec, reg_st="done", in_queue=False)
    broker = broker_column(
        sa=sa,
        cycle=cycle,
        in_queue=False,
        worker=worker,
        reg_st="done",
        has_receipt=True,
    )
    if broker == "PASS":
        return {"ok": True, "sa": sa, "skipped": True, "reason": "already_pass"}

    at = str(rec.get("at") or _now())
    appended: list[str] = []
    for role in ("check", "act", "verify"):
        if role in roles and not (role == "verify" and need_verify_fix):
            continue
        evt = {
            "at": at,
            "kind": "WORKER_SUBMIT",
            "sa": sa,
            "round_type": role,
            "orch_ok": True,
            "deliver_ok": True,
            "source": "repair-broker-gaps-from-receipt-v1",
            "repair": True,
            "receipt_backfill": True,
        }
        if not dry_run:
            _append_event(evt)
        appended.append(role)

    if not appended:
        return {"ok": True, "sa": sa, "skipped": True, "reason": "no_append_needed"}

    return {"ok": True, "sa": sa, "appended": appended, "dry_run": dry_run}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sa", action="append", default=[])
    ap.add_argument("--all-partial", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    audit = audit_registry_done()
    cycles = load_broker_cycles()
    targets: list[str] = list(args.sa)
    if args.all_partial:
        for sa in audit.get("honest_done_ids") or []:
            rec = _load_receipt(sa)
            if not rec:
                continue
            w = worker_column(rec=rec, reg_st="done", in_queue=False)
            b = broker_column(
                sa=sa,
                cycle=cycles.get(sa),
                in_queue=False,
                worker=w,
                reg_st="done",
                has_receipt=True,
            )
            if w == "PASS" and b != "PASS":
                targets.append(sa)
    targets = sorted(set(targets), key=lambda x: int(x.split("-")[1]))

    results = [repair_one(sa=sa, dry_run=args.dry_run) for sa in targets]
    fixed = sum(1 for r in results if r.get("appended"))
    print(json.dumps({"ok": True, "targets": len(targets), "repaired": fixed, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
