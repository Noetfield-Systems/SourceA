#!/usr/bin/env python3
"""Activate client-proof batch 78 in control plane when batch 77 sink is green."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROL_PLANE = ROOT / "data/cloud-workers-control-plane-v1.json"
ACTIVE_POINTER = ROOT / "data/cloud-forge-run-queue-active-v1.json"
BATCH_78 = ROOT / "data/secondary-cloud-forge-run-batch-78-locked-v1.json"
RECEIPT = Path.home() / ".sina/client-proof-batch-78-activate-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def activate(*, write: bool = False) -> dict:
    if not BATCH_78.is_file():
        return {"ok": False, "reason": "batch 78 file missing — run generate_client_proof_cloud_batch_v1.py first"}

    proc = subprocess.run(
        [__import__("sys").executable, str(ROOT / "scripts/verify_autorun_zero_manual_v1.py"), "--json"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    try:
        autorun = json.loads(proc.stdout)
    except json.JSONDecodeError:
        autorun = {"ok": False}

    batch = json.loads(BATCH_78.read_text(encoding="utf-8"))
    summary = batch.get("summary") or {}
    pointer = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.5.0",
        "batch_id": 78,
        "locked": True,
        "saved_at": _now(),
        "queue_path": str(BATCH_78.relative_to(ROOT)),
        "library": "client-proof-recipe",
        "registry_exhausted": False,
        "queue_batch_complete": False,
        "cloud_sec_range": summary.get("cloud_sec_range"),
        "rows_per_turn": summary.get("rows_per_turn", 100),
        "tasks_per_row": 1,
        "source_queue": "data/client-proof-recipe-queue-v1.json",
        "phase_reset": {
            "cloud_forge_run_head": summary.get("cloud_sec_range", "").split("..")[0].replace("CLOUD-SEC-", "CLOUD-SEC-"),
            "cloud_forge_run_last_completed": batch.get("summary", {}).get("cloud_sec_range", "").split("..")[0],
            "queue_batch_complete": False,
        },
    }
    head = str(summary.get("cloud_sec_range", "")).split("..")[0] if summary.get("cloud_sec_range") else ""
    if head:
        pointer["phase_reset"]["cloud_forge_run_head"] = head
        try:
            last_num = int(head.rsplit("-", 1)[-1]) - 1
            pointer["phase_reset"]["cloud_forge_run_last_completed"] = f"CLOUD-SEC-{last_num:04d}"
        except ValueError:
            pass

    row = {
        "ok": autorun.get("ok") is True,
        "autorun_ok": autorun.get("ok"),
        "batch_id": 78,
        "cloud_sec_range": summary.get("cloud_sec_range"),
        "head": pointer["phase_reset"].get("cloud_forge_run_head"),
    }

    if write and row["ok"]:
        ACTIVE_POINTER.write_text(json.dumps(pointer, indent=2) + "\n", encoding="utf-8")
        cp = json.loads(CONTROL_PLANE.read_text(encoding="utf-8"))
        cp["saved_at"] = _now()
        cp["active_batch"] = {
            "batch_id": 78,
            "locked": True,
            "status": "ACTIVE",
            "library": "client-proof-recipe",
            "head": pointer["phase_reset"]["cloud_forge_run_head"],
            "cloud_sec_range": summary.get("cloud_sec_range"),
            "rows_per_turn": summary.get("rows_per_turn", 100),
            "tasks_per_row": 1,
            "queue_path": str(BATCH_78.relative_to(ROOT)),
        }
        cp["ready_batch"] = None
        CONTROL_PLANE.write_text(json.dumps(cp, indent=2) + "\n", encoding="utf-8")
        row["wrote_pointer"] = True
        row["wrote_control_plane"] = True

    if write:
        RECEIPT.write_text(json.dumps({**row, "at": _now()}, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = activate(write=args.write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} batch={row.get('batch_id')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
