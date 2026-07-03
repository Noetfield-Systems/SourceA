#!/usr/bin/env python3
"""Workflow health guard — SLO scoring, heartbeat shape, Kaizen emission."""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "sourcea-sdk" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from sourcea_sdk.workflow_health import build_heartbeat_loop, build_heartbeat_report, emit_improvement_receipt, score_slo_target


def _assert_score_states() -> None:
    loop = build_heartbeat_loop(
        workflow_id="cloud-auto-runtime",
        lane="observe_sync",
        targets={
            "freshness_target_minutes": 15,
            "success_rate_target": 0.99,
            "latency_target_minutes": 30,
        },
        observed={"freshness_minutes": 5, "success_rate": 1.0, "latency_minutes": 2, "last_run_at": "2026-07-03T00:00:00Z"},
        evidence=[{"command": "probe", "exit_code": 0, "output": "ok"}],
        sink_invariant_ok=True,
    )
    assert loop["state"] == "healthy", loop
    assert loop["last_run_at"] == "2026-07-03T00:00:00Z", loop

    healthy = score_slo_target(
        workflow_id="cloud-auto-runtime",
        lane="observe_sync",
        targets={
            "freshness_target_minutes": 15,
            "success_rate_target": 0.99,
            "latency_target_minutes": 30,
        },
        observed={"freshness_minutes": 5, "success_rate": 1.0, "latency_minutes": 2},
        evidence=[],
    )
    assert healthy["state"] == "healthy", healthy
    assert healthy["explicit_miss"] is False, healthy
    assert healthy["score"] == 1.0, healthy

    degraded = score_slo_target(
        workflow_id="cloud-auto-runtime",
        lane="observe_sync",
        targets={
            "freshness_target_minutes": 15,
            "success_rate_target": 0.99,
            "latency_target_minutes": 30,
        },
        observed={"success_rate": 1.0},
        evidence=[],
    )
    assert degraded["state"] == "degraded", degraded
    assert "missing_observation:freshness" in degraded["misses"], degraded

    skipped = score_slo_target(
        workflow_id="trigger-boundary-sweep",
        lane="boundary_check",
        targets={},
        observed={},
        evidence=[],
    )
    assert skipped["state"] == "skipped", skipped
    assert skipped["misses"] == ["missing_optional_slo"], skipped

    missed = score_slo_target(
        workflow_id="sourcea-e2e-registry",
        lane="observe_sync",
        targets={
            "freshness_target_minutes": 10,
            "success_rate_target": 0.99,
            "latency_target_minutes": 5,
        },
        observed={"freshness_minutes": 20, "success_rate": 0.5, "latency_minutes": 9},
        evidence=[],
    )
    assert missed["state"] == "missed", missed
    assert missed["explicit_miss"] is True, missed
    assert {"freshness_target_missed", "success_rate_target_missed", "latency_target_missed"}.issubset(missed["misses"]), missed

    report = build_heartbeat_report(
        loops=[loop, missed],
        drift={"checked": True, "ok": True, "mismatches": []},
        founder_blocked_total=2,
        date="2026-07-03",
    )
    assert report["schema"] == "autorun-heartbeat-v2", report
    assert report["loops"][0]["spend_by_value_class"]["none"] == 0.0, report
    assert report["escalations"] == ["sourcea-e2e-registry"], report


def _assert_heartbeat_and_receipt() -> None:
    tmpdir = Path(tempfile.mkdtemp())
    data = tmpdir / "data"
    data.mkdir(parents=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    (data / "cloud-auto-runtime-v1.json").write_text(
        json.dumps(
            {
                "schema": "cloud-auto-runtime-v1",
                "slo": {
                    "freshness_target_minutes": 15,
                    "success_rate_target": 0.99,
                    "latency_target_minutes": 30,
                },
            }
        ),
        encoding="utf-8",
    )
    (data / "trigger-registry-v1.json").write_text(
        json.dumps(
            {
                "schema": "trigger-registry-v1",
                "slo": {
                    "freshness_target_minutes": 15,
                    "success_rate_target": 0.995,
                    "latency_target_minutes": 45,
                },
            }
        ),
        encoding="utf-8",
    )
    (data / "sourcea-e2e-check-registry-v1.json").write_text(
        json.dumps(
            {
                "schema": "sourcea-e2e-check-registry-v1",
                "generated_at": "2020-01-01T00:00:00Z",
                "slo": {
                    "freshness_target_minutes": 1,
                    "success_rate_target": 0.99,
                    "latency_target_minutes": 60,
                },
                "summary": {"filing_registry_validator_present": True, "total_checks": 1},
            }
        ),
        encoding="utf-8",
    )
    tick = tmpdir / "cloud-auto-runtime-tick-receipt-v1.json"
    tick.write_text(json.dumps({"at": now, "ok": True, "decision": "pack"}), encoding="utf-8")

    import cloud_auto_runtime_v1 as auto

    importlib.reload(auto)
    auto.ROOT = tmpdir
    auto.SSOT = data / "cloud-auto-runtime-v1.json"
    auto.TRIGGER_REGISTRY = data / "trigger-registry-v1.json"
    auto.E2E_REGISTRY = data / "sourcea-e2e-check-registry-v1.json"
    auto.TICK_RECEIPT = tick

    with patch.object(auto, "_trigger_registry_sweep_v1", return_value={"ok": True, "at": now, "report_line": "trigger_sweep_clean"}):
        with patch.object(auto, "_drift_check_v1", return_value={"checked": True, "ok": True, "mismatches": []}):
            with patch.object(auto, "_founder_blocked_snapshot", return_value={"count": 0}):
                report, receipt = auto._observe_sync_health_report(
                    head_row={"cloud_forge_run_head": "CLOUD-SEC-100"},
                    sink_inv={"ok": True},
                    trigger_source="cloudflare_cron",
                    drift={"checked": True, "ok": True, "mismatches": []},
                )

    assert report["schema"] == "autorun-heartbeat-v2", report
    assert report["queue_head"] == "CLOUD-SEC-100", report
    assert report["escalations"] == ["sourcea-e2e-registry"], report
    assert report["loops"][2]["state"] == "missed", report
    assert report["loops"][1]["state"] == "healthy", report
    assert receipt and receipt["schema"] == "improvement-receipt-v2", receipt
    assert Path(receipt["path"]).is_file(), receipt
    payload = json.loads(Path(receipt["path"]).read_text(encoding="utf-8"))
    assert payload["diff_summary"].startswith("Harden the observed workflow SLOs"), payload
    assert payload["evidence"], payload


def main() -> int:
    _assert_score_states()
    _assert_heartbeat_and_receipt()
    print(json.dumps({"ok": True, "schema": "workflow-health-test-v1"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
