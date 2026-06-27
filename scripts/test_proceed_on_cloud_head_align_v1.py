#!/usr/bin/env python3
"""E2E guard — proceed_on_cloud must align stale plan_id to Railway queue head."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def _wire_queue_module(mod, tmpdir: Path, phase_file: Path) -> None:
    mod.ROOT = tmpdir
    mod.ACTIVE_POINTER = tmpdir / "data/cloud-forge-run-queue-active-v1.json"
    mod.LEGACY_DRAIN = tmpdir / "data/secondary-cloud-forge-run-batch-1-v1.json"
    mod.phase_path = lambda: phase_file  # type: ignore[method-assign]


def _run_case() -> None:
    tmpdir = Path(tempfile.mkdtemp())
    phase_dir = tmpdir / "receipts" / "cloud-forge-run"
    phase_dir.mkdir(parents=True)
    (tmpdir / "data").mkdir()
    plans = [{"id": f"CLOUD-SEC-{i:03d}", "maps_registry": f"sa-mkt-{i:04d}"} for i in range(1, 8)]
    (tmpdir / "data" / "secondary-cloud-forge-run-batch-1-v1.json").write_text(
        json.dumps({"plans": plans}), encoding="utf-8"
    )
    (tmpdir / "data" / "cloud-forge-run-queue-active-v1.json").write_text(
        json.dumps(
            {
                "batch_id": 1,
                "queue_path": "data/secondary-cloud-forge-run-batch-1-v1.json",
                "phase_reset": {"cloud_forge_run_head": "CLOUD-SEC-001"},
            }
        ),
        encoding="utf-8",
    )
    phase_file = phase_dir / "phase-observed-v1.json"
    phase_file.write_text(
        json.dumps({"cloud_forge_run_head": "CLOUD-SEC-004", "cloud_forge_run_last_completed": "CLOUD-SEC-003"}),
        encoding="utf-8",
    )
    (tmpdir / "data" / "hub-cloud-forge-run-proceed-v1.json").write_text("{}", encoding="utf-8")

    os.environ.pop("FBE_HOME", None)
    os.environ["CLOUD_FORGE_RUN_AUTO_PROCEED"] = "true"

    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))

    import importlib
    import cloud_forge_run_queue_v1 as q
    from fbe.lib import cloud_forge_run_queue_v1 as fq

    importlib.reload(q)
    importlib.reload(fq)
    _wire_queue_module(q, tmpdir, phase_file)
    _wire_queue_module(fq, tmpdir, phase_file)

    import hub_cloud_forge_run_proceed_v1 as hub

    importlib.reload(hub)
    hub.ROOT = tmpdir

    fake_seed = {"ok": True, "dispatch_lane": "forge_seed", "cloud_dispatch": {"ok": True}}

    with patch.object(hub, "_is_headless_cloud", return_value=True):
        with patch("cloud_forge_seed_v1.run_forge_seed_cycle", return_value=fake_seed):
            row = hub.proceed_on_cloud(
                {
                    "plan_id": "CLOUD-SEC-001",
                    "dry_run": False,
                    "full_motor": False,
                    "_pack_internal": True,
                    "_cycle_claimed": True,
                    "_pack_prove_done": True,
                    "auto_tick": True,
                    "force": True,
                }
            )

    assert row.get("plan_id") == "CLOUD-SEC-004", row
    adv = row.get("queue_advance") or {}
    assert adv.get("ok") is True, adv
    assert adv.get("completed") == "CLOUD-SEC-004", adv
    assert fq.read_head()["cloud_forge_run_head"] == "CLOUD-SEC-005"


def main() -> int:
    _run_case()
    print(json.dumps({"ok": True, "schema": "proceed-on-cloud-head-align-test-v1"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
