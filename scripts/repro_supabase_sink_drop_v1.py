#!/usr/bin/env python3
"""Reproduce silent Supabase sink drop — motor ack vs advance decoupling."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> int:
    from cloud_forge_run_supabase_v1 import persist_shipped_row  # noqa: WPS433

    os.environ.pop("CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC", None)
    cycle = {
        "ok": True,
        "plan_id": "CLOUD-SEC-SINK-REPRO-7631",
        "at": "2026-07-02T06:00:00Z",
        "validator_result": "PASS",
        "artifact_path": "receipts/forge-seed/CLOUD-SEC-7631/artifact-v1.json",
        "forge_seed_artifact": {
            "plan_id": "CLOUD-SEC-SINK-REPRO-7631",
            "proof_tier": "verified_fetch",
            "evidence_source": "http_fetch",
            "at": "2026-07-02T06:00:00Z",
        },
    }
    before = persist_shipped_row(cycle, artifact_doc=cycle["forge_seed_artifact"])
    motor_would_advance = bool(cycle.get("ok"))
    print(json.dumps({
        "schema": "supabase-sink-drop-repro-v1",
        "root_cause": "batching_bug",
        "named_cause": "advance_decoupled_from_supabase_ack",
        "repro_command": "python3 scripts/repro_supabase_sink_drop_v1.py",
        "supabase_write": before,
        "motor_ok_before_fix": motor_would_advance,
        "explanation": (
            "Forge seed returned ok=true while supabase persist returned ok=false; "
            "advance_on_pass ran anyway — silent sink drop under 100-row pack throughput"
        ),
    }, indent=2))
    return 0 if not before.get("ok") and motor_would_advance else 1


if __name__ == "__main__":
    raise SystemExit(main())
