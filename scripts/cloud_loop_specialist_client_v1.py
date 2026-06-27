#!/usr/bin/env python3
"""Cloud Auto Runtime specialist client — POST tick to Railway FBE (CLOUD_ONLY).

Mac never runs observatory validators for tick — cloud executes comprehension + optional bay.

Receipt: ~/.sina/loop-specialist-cloud-tick-receipt-v1.json
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
RECEIPT = SINA / "loop-specialist-cloud-tick-receipt-v1.json"
CLOUD_PATH = "/api/fbe/loop-specialist/tick/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def light_snapshot() -> dict:
    surf = _read(SINA / "agent-live-surfaces-v1.json")
    return {
        "factory_now_line": str(surf.get("factory_now_line") or "")[:200],
        "queue_sa": str(surf.get("queue_sa") or ""),
        "founder_daily_ops": str(surf.get("founder_daily_ops") or "")[:120],
    }


def tick_via_cloud(
    *,
    founder_message: str = "",
    draft: str = "",
    dispatch: bool = False,
    write_receipt: bool = True,
) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    body = {
        "job_id": str(uuid.uuid4()),
        "factory_id": "comprehension-loop-factory-v1",
        "bay_slug": "noetfield-freemium-bay",
        "tenant": "sourcea",
        "execution_mode": "CLOUD_ONLY",
        "founder_message": founder_message,
        "draft": draft or founder_message,
        "dispatch": dispatch,
        "loop_auto_dispatch_enabled": True,
        "system_snapshot": light_snapshot(),
    }
    row = proxy_to_cloud(path=CLOUD_PATH, body=body, timeout_s=180)
    out = {
        "schema": "loop-specialist-cloud-tick-client-receipt-v1",
        "at": _now(),
        "ok": bool(row.get("ok")),
        "proxied": True,
        "execution_plane": row.get("execution_plane") or "headless_cloud",
        "tick_decision": row.get("tick_decision"),
        "loop_specialist_line": row.get("loop_specialist_line"),
        "next_founder_action": row.get("next_founder_action"),
        "for_founder": row.get("for_founder") or {},
        "raw": row,
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
