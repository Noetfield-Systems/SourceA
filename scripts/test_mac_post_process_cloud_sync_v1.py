#!/usr/bin/env python3
"""E2E guard — Mac post-process syncs head from cloud pack receipt, not local advance."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _run_case() -> None:
    tmpdir = Path(tempfile.mkdtemp())
    (tmpdir / "data").mkdir()
    batch5 = [{"id": f"CLOUD-SEC-{i:03d}"} for i in range(401, 411)]
    batch7 = [{"id": f"CLOUD-SEC-{i:03d}"} for i in range(601, 611)]
    (tmpdir / "data" / "secondary-cloud-forge-run-batch-5-locked-v1.json").write_text(
        json.dumps({"plans": batch5}), encoding="utf-8"
    )
    (tmpdir / "data" / "secondary-cloud-forge-run-batch-7-locked-v1.json").write_text(
        json.dumps({"plans": batch7}), encoding="utf-8"
    )
    (tmpdir / "data" / "cloud-forge-run-queue-active-v1.json").write_text(
        json.dumps(
            {
                "batch_id": 5,
                "queue_path": "data/secondary-cloud-forge-run-batch-5-locked-v1.json",
                "phase_reset": {"cloud_forge_run_head": "CLOUD-SEC-401"},
            }
        ),
        encoding="utf-8",
    )
    (tmpdir / "data" / "cloud-auto-runtime-v1.json").write_text("{}", encoding="utf-8")
    (tmpdir / "data" / "cloud-workers-control-plane-v1.json").write_text("{}", encoding="utf-8")
    (tmpdir / "data" / "hub-cloud-forge-run-proceed-v1.json").write_text("{}", encoding="utf-8")
    (tmpdir / "receipts").mkdir()

    phase_path = tmpdir / "phase-observed-v1-test-mac-sync-v1.json"
    phase_path.write_text(
        json.dumps({"cloud_forge_run_head": "CLOUD-SEC-401", "batch_id": 5, "rebuilt_at": "2020-01-01T00:00:00Z"}),
        encoding="utf-8",
    )

    os.environ.pop("FBE_HOME", None)
    os.environ.pop("FBE_MODE", None)

    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))

    import importlib
    import cloud_workers_hub_v1 as cwh
    import hub_cloud_forge_run_proceed_v1 as hub

    importlib.reload(cwh)
    importlib.reload(hub)
    cwh.ROOT = tmpdir
    hub.ROOT = tmpdir
    cwh.PHASE_OBS = phase_path
    cwh.SCRIPTS = ROOT / "scripts"

    cloud_row = {
        "ok": True,
        "at": "2026-06-24T00:30:00Z",
        "head": "CLOUD-SEC-614",
        "pack": {
            "head_now": "CLOUD-SEC-614",
            "last_completed": "CLOUD-SEC-613",
            "batch_id": 7,
            "batch_complete": False,
            "processed": 42,
        },
    }

    noop = {"ok": True}

    def _fake_wire(*, active_batch_id: int | None = None) -> dict:
        bid = int(active_batch_id or 7)
        ptr_path = tmpdir / "data/cloud-forge-run-queue-active-v1.json"
        ptr = json.loads(ptr_path.read_text(encoding="utf-8"))
        ptr["batch_id"] = bid
        ptr["queue_path"] = f"data/secondary-cloud-forge-run-batch-{bid}-locked-v1.json"
        ptr_path.write_text(json.dumps(ptr, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "active_batch_id": bid}

    with patch("cloud_forge_run_wire_batch_chain_v1.wire", side_effect=_fake_wire):
        with patch("brain_cloud_reasoning_plan_pulse_v1.run_pulse", return_value=noop):
            with patch("task_plan_priority_v1.refresh", return_value=noop):
                with patch("agent_nerve_system_v1.run_nerve_pulse", return_value=noop):
                    out = hub._mac_post_process(plan_id="CLOUD-SEC-469", registry="sa-mkt-0500", cloud_row=cloud_row)

    phase = json.loads(phase_path.read_text(encoding="utf-8"))
    assert phase.get("cloud_forge_run_head") == "CLOUD-SEC-614", phase
    assert int(phase.get("batch_id") or 0) == 7, phase
    obs_step = next(s for s in out.get("steps") or [] if s.get("step") == "observed_head")
    assert obs_step.get("ok") is True, obs_step
    assert obs_step.get("source") == "cloud_receipt_not_local_advance", obs_step
    ptr = json.loads((tmpdir / "data/cloud-forge-run-queue-active-v1.json").read_text(encoding="utf-8"))
    assert int(ptr.get("batch_id") or 0) == 7, ptr


def main() -> int:
    _run_case()
    print(json.dumps({"ok": True, "schema": "mac-post-process-cloud-sync-test-v1"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
