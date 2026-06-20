#!/usr/bin/env python3
"""FORM founder supremacy — agents MUST NOT submit or apply picks without ASF.

Law: SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md · INCIDENT-037
Flag: ~/.sina/form-agent-submit-forbidden-v1.flag (present = agent block ON)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
FORBIDDEN_FLAG = SINA / "form-agent-submit-forbidden-v1.flag"
FOUNDER_UNLOCK = SINA / "form-founder-submit-unlock-v1.flag"
INCIDENT_RECEIPT = SINA / "form-incident-029-block-receipt-v1.json"

# Trusted only when real founder UI invokes server/canvas — never CLI spoof.
TRUSTED_CHANNELS = frozenset({"hub_browser", "m1_canvas"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_human_actor(actor: str) -> bool:
    return actor.strip().lower() in ("founder", "asf", "human")


def agent_submit_blocked(*, actor: str = "agent", channel: str = "cli") -> bool:
    """True when this actor/channel must not write form picks."""
    block = assert_founder_submit_allowed(actor=actor, action="probe", channel=channel)
    return bool(block.get("blocked"))


def assert_founder_submit_allowed(*, actor: str, action: str, channel: str = "cli") -> dict:
    """Fail-closed while form-agent-submit-forbidden flag is ON (INCIDENT-037 permanent)."""
    if not FORBIDDEN_FLAG.is_file():
        return {"ok": True, "blocked": False, "actor": actor, "action": action, "channel": channel}

    if not _is_human_actor(actor):
        return {
            "ok": False,
            "blocked": True,
            "error": "FORM_AGENT_SUBMIT_FORBIDDEN",
            "action": action,
            "actor": actor,
            "channel": channel,
            "law": "INCIDENT-037 — agents never submit/apply form picks",
            "flag": str(FORBIDDEN_FLAG),
            "guard": "form-agent-submit-forbidden-v1.flag ON",
            "surface": "hub_form",
        }

    if channel in TRUSTED_CHANNELS:
        return {"ok": True, "blocked": False, "actor": actor, "action": action, "channel": channel}

    if FOUNDER_UNLOCK.is_file():
        return {"ok": True, "blocked": False, "actor": actor, "action": action, "channel": channel}

    return {
        "ok": False,
        "blocked": True,
        "error": "FOUNDER_HUB_SUBMIT_ONLY",
        "action": action,
        "actor": actor,
        "channel": channel,
        "law": "INCIDENT-037 — CLI cannot write §ANSWERED · trusted channels only",
        "flag": str(FORBIDDEN_FLAG),
        "guard": "form-agent-submit-forbidden-v1.flag ON",
        "surface": "hub_form",
        "unlock_flag": str(FOUNDER_UNLOCK),
    }


def write_block_receipt(*, reason: str, reverted_ids: list[str] | None = None) -> Path:
    SINA.mkdir(parents=True, exist_ok=True)
    FORBIDDEN_FLAG.write_text(f"INCIDENT-037 agent form submit forbidden · {_now()}\n", encoding="utf-8")
    body = {
        "schema": "form-incident-029-block-receipt-v1",
        "at": _now(),
        "ok": True,
        "incident": "INCIDENT-037",
        "reason": reason,
        "agent_submit_blocked": True,
        "forbidden_flag": str(FORBIDDEN_FLAG),
        "reverted_question_ids": reverted_ids or [],
        "law": "Founder never submitted FORM 116 — Worker bulk-applied recommended picks (INCIDENT-037)",
    }
    INCIDENT_RECEIPT.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return INCIDENT_RECEIPT
