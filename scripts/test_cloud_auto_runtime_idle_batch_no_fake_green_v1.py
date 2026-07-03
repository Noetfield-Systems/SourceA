#!/usr/bin/env python3
"""Guard — idle batch-complete ticks must not verdict approved with processed=0."""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def _run_case() -> None:
    tmpdir = Path(tempfile.mkdtemp())
    cycles = tmpdir / "receipts" / "autonomous-forge-run-cycles"
    cycles.mkdir(parents=True)

    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib
    import cloud_auto_runtime_v1 as auto

    importlib.reload(auto)
    auto.ROOT = tmpdir
    auto.CYCLE_RECEIPTS_DIR = cycles
    auto.HUB_RECEIPT = tmpdir / "hub-receipt.json"

    idle_pack = {
        "ok": True,
        "idle_batch": True,
        "schema": "cloud-forge-run-pack-v1",
        "advanced": 0,
        "skipped": 0,
        "processed": 0,
        "max_advance": 100,
        "batch_complete": True,
        "head_now": "CLOUD-SEC-910",
        "last_completed": "CLOUD-SEC-910",
    }

    cycle = {
        "ok": True,
        "at": "2026-06-24T12:00:00Z",
        "decision": "batch_idle",
        "pack": idle_pack,
    }
    prove = {"ok": True, "summary_line": "chains PASS", "chains_up": 3, "chains_total": 3}

    with patch.object(auto, "_is_headless_cloud", return_value=False):
        path = auto._write_cycle_receipt(
            cycle=cycle,
            trigger_source="cloudflare_cron",
            head="CLOUD-SEC-910",
            prove=prove,
            ship={},
        )

    doc = json.loads(path.read_text(encoding="utf-8"))
    verdict = (doc.get("decision") or {}).get("verdict")
    assert verdict == "IDLE_NO_WORK", doc
    assert (doc.get("belt") or {}).get("SHIP", {}).get("ok") is False, doc
    assert idle_pack["idle_batch"] is True

    sys.path.insert(0, str(ROOT / "packages" / "sourcea-sdk" / "src"))
    import cloud_auto_runtime_v1 as auto_health
    import importlib

    importlib.reload(auto_health)
    auto_health.ROOT = tmpdir
    auto_health.SSOT = tmpdir / "data" / "cloud-auto-runtime-v1.json"
    auto_health.TRIGGER_REGISTRY = tmpdir / "data" / "trigger-registry-v1.json"
    auto_health.E2E_REGISTRY = tmpdir / "data" / "sourcea-e2e-check-registry-v1.json"
    auto_health.TICK_RECEIPT = tmpdir / "cloud-auto-runtime-tick-receipt-v1.json"

    (tmpdir / "data").mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmpdir / "data" / "cloud-auto-runtime-v1.json").write_text(
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
    (tmpdir / "data" / "trigger-registry-v1.json").write_text(
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
    (tmpdir / "data" / "sourcea-e2e-check-registry-v1.json").write_text(
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
    auto_health.TICK_RECEIPT.write_text(json.dumps({"at": stamp, "ok": True, "decision": "pack"}), encoding="utf-8")

    with patch.object(auto_health, "_trigger_registry_sweep_v1", return_value={"ok": True, "at": stamp, "report_line": "trigger_sweep_clean"}):
        with patch.object(auto_health, "_drift_check_v1", return_value={"checked": True, "ok": True, "mismatches": []}):
            with patch.object(auto_health, "_founder_blocked_snapshot", return_value={"count": 0}):
                report, receipt = auto_health._observe_sync_health_report(
                    head_row={"cloud_forge_run_head": "CLOUD-SEC-910"},
                    sink_inv={"ok": True},
                    trigger_source="cloudflare_cron",
                    drift={"checked": True, "ok": True, "mismatches": []},
                )

    assert report["schema"] == "autorun-heartbeat-v2", report
    assert report["escalations"] == ["sourcea-e2e-registry"], report
    assert report["loops"][2]["state"] == "missed", report
    assert receipt and receipt["schema"] == "improvement-receipt-v2", receipt
    assert Path(receipt["path"]).is_file(), receipt


def main() -> int:
    _run_case()
    print(json.dumps({"ok": True, "schema": "cloud-forge-run-idle-batch-no-fake-green-test-v1"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
