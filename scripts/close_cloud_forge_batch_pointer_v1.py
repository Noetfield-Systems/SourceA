#!/usr/bin/env python3
"""Close active batch pointer from live Railway queue — receipt on stale Mac disk."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
ACTIVE = ROOT / "data" / "cloud-forge-run-queue-active-v1.json"
RECEIPT_DIR = ROOT / "receipts" / "cloud-forge-run"
PROOF_URL = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _fetch_cloud() -> dict[str, Any]:
    with urllib.request.urlopen(PROOF_URL, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def classify(*, ptr: dict[str, Any], cloud: dict[str, Any]) -> str:
    if not cloud.get("ok"):
        return "UNKNOWN"
    local_complete = bool(ptr.get("queue_batch_complete"))
    cloud_complete = bool(cloud.get("queue_batch_complete"))
    local_last = str((ptr.get("phase_reset") or {}).get("cloud_forge_run_last_completed") or "")
    cloud_last = str(cloud.get("cloud_forge_run_last_completed") or "")
    if cloud_complete and local_complete and local_last == cloud_last:
        return "COMPLETE"
    if cloud_complete and (not local_complete or local_last != cloud_last):
        return "POINTER_STALE"
    return "INCOMPLETE"


def close(*, batch_id: int | None = None) -> dict[str, Any]:
    cloud = _fetch_cloud()
    ptr = _read(ACTIVE)
    state = classify(ptr=ptr, cloud=cloud)
    bid = int(batch_id or cloud.get("batch_id") or ptr.get("batch_id") or 0)
    head = str(cloud.get("cloud_forge_run_head") or "")
    last = str(cloud.get("cloud_forge_run_last_completed") or "")

    if state == "INCOMPLETE":
        return {
            "ok": False,
            "state": state,
            "batch_id": bid,
            "head": head,
            "last_completed": last,
            "error": "batch_not_complete_on_cloud",
            "for_founder": {"show_this": f"Batch {bid} INCOMPLETE — head {head} · drain remaining rows first"},
        }

    if state == "COMPLETE" and ptr.get("queue_batch_complete") and str((ptr.get("phase_reset") or {}).get("cloud_forge_run_last_completed") or "") == last:
        receipt_path = SINA / f"cloud-forge-run-batch-{bid}-close-receipt-v1.json"
        row = {
            "ok": True,
            "state": state,
            "batch_id": bid,
            "head": head,
            "last_completed": last,
            "action": "none — pointer already synced",
            "receipt_path": str(receipt_path),
        }
        return row

    new_ptr = {
        **ptr,
        "saved_at": _now(),
        "batch_id": bid,
        "queue_batch_complete": True,
        "registry_exhausted": bool(cloud.get("registry_exhausted", ptr.get("registry_exhausted"))),
        "completed_at": _now(),
        "closed_by": "scripts/close_cloud_forge_batch_pointer_v1.py",
        "proof_url": PROOF_URL,
        "phase_reset": {
            **(ptr.get("phase_reset") or {}),
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last,
            "queue_batch_complete": True,
        },
    }
    _write(ACTIVE, new_ptr)

    phase = _read(SINA / "phase-observed-v1.json")
    phase.update(
        {
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last,
            "queue_batch_complete": True,
            "batch_id": bid,
            "registry_exhausted": bool(cloud.get("registry_exhausted")),
            "rebuilt_at": _now(),
            "rebuilt_by": "close_cloud_forge_batch_pointer_v1",
        }
    )
    _write(SINA / "phase-observed-v1.json", phase)

    receipt_path = RECEIPT_DIR / f"batch-{bid}-close-receipt-v1.json"
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt = {
        "ok": True,
        "schema": "cloud-forge-run-batch-close-receipt-v1",
        "at": _now(),
        "state": state,
        "batch_id": bid,
        "head": head,
        "last_completed": last,
        "action": "closed pointer from live Railway queue",
        "active_pointer": str(ACTIVE),
        "cloud_proof": PROOF_URL,
    }
    _write(receipt_path, receipt)
    sina_alias = SINA / f"cloud-forge-run-batch-{bid}-close-receipt-v1.json"
    sina_alias.write_text(json.dumps({"ok": True, "at": receipt["at"], "path": str(receipt_path)}, indent=2) + "\n")
    receipt["receipt_path"] = str(receipt_path)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-id", type=int)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = close(batch_id=args.batch_id)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("action") or row.get("error") or row.get("state"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
