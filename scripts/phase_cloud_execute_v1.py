#!/usr/bin/env python3
"""Fix 3 machine — live cloud execute + brain cloud_proof rows.

Separate from desired/observed reconciler. Never writes assignment.active.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
CLOUD_SEC_RECEIPT = ROOT / "receipts" / "cloud-sec-001-receipt-v1.json"

sys.path.insert(0, str(SCRIPTS))
from phase_desired_read_v1 import desired_cloud_forge_run_head, read_desired_active  # noqa: E402
from phase_transition_probe_v1 import probe_railway  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def execute_cloud_forge_run(*, plan_id: str | None = None, dry_run: bool = False) -> dict:
    plan_id = plan_id or desired_cloud_forge_run_head() or "CLOUD-SEC-001"
    railway = probe_railway()
    if not railway.get("ok") and not dry_run:
        return {
            "schema": "phase-cloud-execute-receipt-v1",
            "ok": False,
            "error": "railway_fbe_health_down",
            "railway": railway,
            "at": _now(),
        }

    from cloud_worker_dispatch_v1 import dispatch  # noqa: WPS433

    row = dispatch(plan_id=plan_id, dry_run=dry_run)
    ok = bool(row.get("ok"))
    receipt_path = ROOT / "receipts" / "cloud-dispatch" / f"{plan_id}.json"
    if ok and not dry_run:
        src = row.get("receipt_path")
        if src:
            try:
                import shutil

                canonical = ROOT / "receipts" / "cloud-dispatch" / f"{plan_id}.json"
                p = Path(str(src))
                if p.is_file() and p != canonical:
                    shutil.copy2(p, canonical)
            except OSError:
                pass
        summary = {
            "schema": "cloud-sec-001-receipt-v1",
            "id": plan_id,
            "ok": True,
            "dry_run": False,
            "status": row.get("status"),
            "live_dispatch": row,
            "desired_read": read_desired_active(),
            "at": _now(),
        }
        _write(CLOUD_SEC_RECEIPT, summary)

    return {
        "schema": "phase-cloud-execute-receipt-v1",
        "ok": ok or dry_run,
        "plan_id": plan_id,
        "dry_run": dry_run,
        "dispatch": row,
        "receipt_path": str(receipt_path) if receipt_path.is_file() else row.get("receipt_path"),
        "at": _now(),
    }


def mark_brain_cloud_proof(*, upgrade_ids: list[str], evidence: str) -> dict:
    from mark_brain_reasoning_done_v1 import mark_done  # noqa: WPS433

    touched: list[dict] = []
    for uid in upgrade_ids:
        row = mark_done(uid, evidence=evidence)
        touched.append(row)
    ok = all(r.get("ok") for r in touched)
    return {"ok": ok, "touched": touched, "at": _now()}


def run_fix3(*, dry_run: bool = False, brain_ids: list[str] | None = None) -> dict:
    brain_ids = brain_ids or ["B0001", "B0002", "B0003"]
    cloud = execute_cloud_forge_run(dry_run=dry_run)
    brain: dict | None = None
    if cloud.get("ok") and not dry_run:
        evidence = (
            f"{desired_cloud_forge_run_head()} live PASS · "
            f"{cloud.get('receipt_path')} · dry_run=false"
        )
        brain = mark_brain_cloud_proof(upgrade_ids=brain_ids, evidence=evidence)
    try:
        from brain_cloud_reasoning_plan_pulse_v1 import run_pulse  # noqa: WPS433

        pulse = run_pulse(write=True)
    except Exception as exc:
        pulse = {"ok": False, "error": str(exc)[:120]}

    ok = bool(cloud.get("ok")) and (dry_run or (brain or {}).get("ok", False))
    receipt = {
        "schema": "phase-cloud-execute-receipt-v1",
        "ok": ok,
        "fix": 3,
        "cloud": cloud,
        "brain": brain,
        "pulse": {"cloud_proven": (pulse.get("progress") or {}).get("cloud_proven"), "done": (pulse.get("progress") or {}).get("done")},
        "at": _now(),
        "line": f"Fix3 · {desired_cloud_forge_run_head()} {'dry-run' if dry_run else 'live'} · brain={brain_ids}",
    }
    _write(SINA / "phase-cloud-execute-receipt-v1.json", receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Fix 3 — live cloud execute + brain cloud_proof")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--brain-ids", default="B0001,B0002,B0003")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.plan_id:
        row = execute_cloud_forge_run(plan_id=args.plan_id, dry_run=args.dry_run)
    else:
        ids = [x.strip() for x in args.brain_ids.split(",") if x.strip()]
        row = run_fix3(dry_run=args.dry_run, brain_ids=ids)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or json.dumps({"ok": row.get("ok")}))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
