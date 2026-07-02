#!/usr/bin/env python3
"""Signal Factory cloud client — POST tick to Railway FBE (CLOUD_ONLY).

Receipt: ~/.sina/signal-factory-cloud-tick-receipt-v1.json
"""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "signal-factory-cloud-tick-receipt-v1.json"
CLOUD_PATH = "/api/fbe/signal-factory/tick/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tick_via_cloud(
    *,
    max_batch: int = 5,
    trigger_source: str = "hub",
    write_receipt: bool = True,
) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    body = {
        "job_id": str(uuid.uuid4()),
        "factory_id": "signal-factory-v1",
        "tenant": "sourcea",
        "execution_mode": "CLOUD_ONLY",
        "max_batch": max_batch,
        "trigger_source": trigger_source,
    }
    row = proxy_to_cloud(path=CLOUD_PATH, body=body, timeout_s=120)
    out = {
        "schema": "signal-factory-cloud-tick-client-receipt-v1",
        "at": _now(),
        "ok": bool(row.get("ok")),
        "proxied": True,
        "execution_plane": row.get("execution_plane") or "headless_cloud",
        "decision": row.get("decision"),
        "signal_factory_line": row.get("signal_factory_line"),
        "next_founder_action": row.get("next_founder_action"),
        "raw": row,
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out
