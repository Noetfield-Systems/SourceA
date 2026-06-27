#!/usr/bin/env python3
"""Guard — idle batch-complete ticks must not verdict approved with processed=0."""
from __future__ import annotations

import json
import sys
import tempfile
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
        "batch_id": 10,
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
    assert verdict == "idle", doc
    assert (doc.get("belt") or {}).get("SHIP", {}).get("ok") is False, doc
    assert idle_pack["idle_batch"] is True


def main() -> int:
    _run_case()
    print(json.dumps({"ok": True, "schema": "cloud-forge-run-idle-batch-no-fake-green-test-v1"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
