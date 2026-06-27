#!/usr/bin/env python3
"""Seal extension wave-2 Cloud Forge Run complete — pointer · pipeline · Mac phase."""
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
ACTIVE = ROOT / "data/cloud-forge-run-queue-active-v1.json"
PIPELINE = ROOT / "data/cloud-forge-run-batch-pipeline-v1.json"
RECEIPT = SINA / "cloud-forge-run-extension-wave2-complete-receipt-v1.json"
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


def _fetch_cloud_queue() -> dict[str, Any]:
    try:
        with urllib.request.urlopen(PROOF_URL, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160]}


def seal(*, cloud_row: dict[str, Any] | None = None) -> dict[str, Any]:
    cloud = cloud_row if cloud_row and cloud_row.get("ok") else _fetch_cloud_queue()
    if not cloud.get("ok"):
        return {"ok": False, "error": "cloud_queue_unreachable", "cloud": cloud}

    head = str(cloud.get("cloud_forge_run_head") or "")
    last = str(cloud.get("cloud_forge_run_last_completed") or "")
    batch_complete = bool(cloud.get("queue_batch_complete"))
    obs = cloud.get("observed") if isinstance(cloud.get("observed"), dict) else {}
    batch_id = int(obs.get("batch_id") or cloud.get("batch_id") or 70)

    if not batch_complete:
        return {
            "ok": False,
            "error": "batch_not_complete_on_cloud",
            "head": head,
            "for_founder": {"show_this": f"BLOCKER — cloud head {head} · batch not complete yet"},
        }

    ptr = _read(ACTIVE)
    archives = {k: v for k, v in ptr.items() if str(k).startswith("archive_batch")}
    new_ptr = {
        "schema": "cloud-forge-run-queue-active-v1",
        "version": "1.3.0",
        "batch_id": batch_id,
        "locked": True,
        "saved_at": _now(),
        "queue_path": ptr.get("queue_path") or f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json",
        **archives,
        "drain_status": "extension_wave2_complete",
        "registry_exhausted": True,
        "queue_batch_complete": True,
        "completed_at": _now(),
        "cloud_sec_range": "CLOUD-SEC-5001..CLOUD-SEC-6966",
        "maps_registry": "extension-wave2-noetfield+mono",
        "next_motor_ssot": "data/forge-real-blueprints-v01.json",
        "phase_reset": {
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last,
            "queue_batch_complete": True,
        },
        "cloud_workers_feed": ptr.get("cloud_workers_feed")
        or {
            "machine": "scripts/cloud_workers_hub_v1.py",
            "control_plane": "data/cloud-workers-control-plane-v1.json",
            "auto_runtime": "data/cloud-auto-runtime-v1.json",
        },
        "proof_url": PROOF_URL,
    }
    _write(ACTIVE, new_ptr)

    pipe = _read(PIPELINE)
    batches = []
    for row in pipe.get("batches") or []:
        bid = int(row.get("batch_id") or 0)
        status = "COMPLETE" if bid <= batch_id else row.get("status", "ready_locked")
        batches.append({**row, "status": status})
    pipe.update(
        {
            "version": "1.3.0",
            "saved_at": _now(),
            "active_batch_id": batch_id,
            "drain_status": "extension_wave2_complete",
            "registry_exhausted": True,
            "next_motor_ssot": "data/forge-real-blueprints-v01.json",
            "batches": batches,
        }
    )
    _write(PIPELINE, pipe)

    steps: list[dict[str, Any]] = [
        {"step": "pointer", "ok": True, "path": str(ACTIVE), "head": head, "batch_id": batch_id},
        {"step": "pipeline", "ok": True, "path": str(PIPELINE)},
    ]

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from cloud_workers_hub_v1 import apply_live_queue  # noqa: WPS433

        steps.append({"step": "mac_live_sync", **apply_live_queue(cloud)})
    except Exception as exc:
        steps.append({"step": "mac_live_sync", "ok": False, "error": str(exc)[:120]})

    phase_obs = SINA / "phase-observed-v1.json"
    phase = _read(phase_obs)
    phase.update(
        {
            "schema": "phase-observed-v1",
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last,
            "queue_batch_complete": True,
            "batch_id": batch_id,
            "registry_exhausted": True,
            "drain_status": "extension_wave2_complete",
            "next_motor_ssot": "data/forge-real-blueprints-v01.json",
            "rebuilt_at": _now(),
            "rebuilt_by": "cloud_forge_run_seal_extension_wave2_complete_v1",
        }
    )
    _write(phase_obs, phase)
    steps.append({"step": "phase_observed", "ok": True, "path": str(phase_obs)})

    try:
        from phase_observed_project_v1 import mark_forge_queue_exhausted  # noqa: WPS433

        steps.append({"step": "mark_queue_exhausted", **mark_forge_queue_exhausted()})
    except Exception as exc:
        steps.append({"step": "mark_queue_exhausted", "ok": False, "error": str(exc)[:120]})

    row = {
        "ok": True,
        "schema": "cloud-forge-run-extension-wave2-complete-receipt-v1",
        "at": _now(),
        "head": head,
        "last_completed": last,
        "batch_id": batch_id,
        "registry_exhausted": True,
        "next_motor_ssot": "data/forge-real-blueprints-v01.json",
        "steps": steps,
        "for_founder": {
            "show_this": (
                f"Extension wave-2 Cloud Forge Run SEALED · {last} · batch {batch_id} complete · "
                "registry exhausted · next: forge-real-blueprints"
            ),
        },
    }
    _write(RECEIPT, row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = seal()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("for_founder", {}).get("show_this") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
