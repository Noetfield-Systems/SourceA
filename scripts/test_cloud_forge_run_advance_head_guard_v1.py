#!/usr/bin/env python3
"""Guard test — advance_on_pass must not rewind queue when plan_id != head."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_case() -> None:
    tmpdir = Path(tempfile.mkdtemp())
    (tmpdir / "data").mkdir()
    phase_dir = tmpdir / "receipts" / "cloud-forge-run"
    phase_dir.mkdir(parents=True)
    phase = phase_dir / "phase-observed-v1.json"

    plans = [{"id": f"CLOUD-SEC-{i:03d}"} for i in range(1, 6)]
    (tmpdir / "data" / "secondary-cloud-forge-run-next-100-v1.json").write_text(
        json.dumps({"plans": plans}), encoding="utf-8"
    )
    (tmpdir / "data" / "cloud-forge-run-queue-active-v1.json").write_text(
        json.dumps({"batch_id": 1, "queue_path": "data/secondary-cloud-forge-run-next-100-v1.json"}),
        encoding="utf-8",
    )
    phase.write_text(
        json.dumps({"cloud_forge_run_head": "CLOUD-SEC-004", "cloud_forge_run_last_completed": "CLOUD-SEC-003"}),
        encoding="utf-8",
    )

    os.environ["CLOUD_DRAIN_PHASE_PATH"] = str(phase)
    os.environ.pop("FBE_HOME", None)
    os.environ.pop("FBE_MODE", None)

    sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))
    import importlib
    import cloud_forge_run_queue_v1 as q

    importlib.reload(q)
    q.ROOT = tmpdir
    q.ACTIVE_POINTER = tmpdir / "data/cloud-forge-run-queue-active-v1.json"
    q.LEGACY_DRAIN = tmpdir / "data/secondary-cloud-forge-run-next-100-v1.json"

    head_before = q.read_head()["cloud_forge_run_head"]
    stale = q.advance_on_pass(plan_id="CLOUD-SEC-001")
    head_after = q.read_head()["cloud_forge_run_head"]

    assert head_before == "CLOUD-SEC-004", head_before
    assert stale.get("ok") is False, stale
    assert stale.get("error") == "plan_not_queue_head", stale
    assert head_after == "CLOUD-SEC-004", head_after

    ok = q.advance_on_pass(plan_id="CLOUD-SEC-004")
    head_aligned = q.read_head()["cloud_forge_run_head"]
    assert ok.get("ok") is True, ok
    assert head_aligned == "CLOUD-SEC-005", head_aligned

    sys.path.insert(0, str(ROOT / "packages" / "sourcea-sdk" / "src"))
    from sourcea_sdk.workflow_health import score_slo_target

    skipped = score_slo_target(
        workflow_id="trigger-boundary-sweep",
        lane="boundary_check",
        targets=None,
        observed={"freshness_minutes": 0, "success_rate": 1.0, "latency_minutes": 0},
        evidence=[],
    )
    assert skipped["state"] == "skipped", skipped
    assert skipped["misses"] == ["missing_optional_slo"], skipped


def main() -> int:
    _run_case()
    print(json.dumps({"ok": True, "schema": "cloud-forge-run-advance-head-guard-test-v1"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
