#!/usr/bin/env python3
"""Cloud Auto Runtime specialist tick — comprehension + optional bay dispatch on Railway FBE.

No Mac ~/.sina reads. Body carries founder_message, draft, optional system_snapshot.
Law: data/loop-specialist-cloud-contract-v1.json · Mac = glance only.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cloud_loop_tick(body: dict[str, Any]) -> dict[str, Any]:
    founder_message = str(body.get("founder_message") or "")
    draft = str(body.get("draft") or body.get("text") or founder_message)
    dispatch = bool(body.get("dispatch"))
    snap = body.get("system_snapshot") if isinstance(body.get("system_snapshot"), dict) else {}

    from fbe_comprehension_bay_v1 import run_comprehension_bay  # noqa: WPS433

    comp = run_comprehension_bay(
        draft=draft,
        founder_message=founder_message,
        system_snapshot=snap or None,
    )

    dispatch_result: dict[str, Any] = {"skipped": True}
    tick_decision = "observe_only"
    block_reasons: list[str] = []

    if not comp.get("ok"):
        tick_decision = "compose_blocked"
        block_reasons.append("comprehension_blocked")
    elif dispatch:
        from fbe_run_bay_v1 import run_bay_job  # noqa: WPS433

        dispatch_result = run_bay_job(
            bay_slug=str(body.get("bay_slug") or "noetfield-freemium-bay"),
            template_id=str(body.get("factory_id") or "noetfield-freemium-factory-v1"),
            tenant=str(body.get("tenant") or "sourcea"),
            work_order_id=str(body.get("work_order_id") or uuid.uuid4()),
        )
        tick_decision = "dispatch_done" if dispatch_result.get("ok") else "compose_blocked"
        if not dispatch_result.get("ok"):
            block_reasons.append("bay_dispatch_failed")
    else:
        tick_decision = "cloud_comprehend"

    one = str(comp.get("one_line") or "")[:96]
    line = f"loop-specialist · cloud · {tick_decision} · {one}".strip(" ·")

    ff = comp.get("for_founder") or {}
    next_action = (
        str(ff.get("show_this") or "")[:200]
        if ff.get("show_this")
        else "Hub glance only · cloud loop tick · no RUN INBOX · no Mac Terminal"
    )

    return {
        "schema": "loop-specialist-cloud-tick-receipt-v1",
        "ok": tick_decision in ("observe_only", "cloud_comprehend", "dispatch_done"),
        "at": _now(),
        "execution_plane": "headless_cloud",
        "execution_authority": False,
        "mac_role": "control_plane_only",
        "tick_decision": tick_decision,
        "loop_specialist_line": line,
        "loop_auto_dispatch_enabled": bool(body.get("loop_auto_dispatch_enabled", True)),
        "dispatch_requested": dispatch,
        "block_reasons": block_reasons,
        "comprehension": comp,
        "dispatch": dispatch_result,
        "next_founder_action": next_action,
        "for_founder": ff,
    }
