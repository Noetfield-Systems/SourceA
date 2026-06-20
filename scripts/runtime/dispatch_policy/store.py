"""Dispatch policy SSOT."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from runtime.dispatch_policy.allowlist import ALLOWLIST_VERSION

POLICY_SSOT_PATH = Path.home() / ".sina" / "dispatch_policy_v1.json"
SCHEMA = "dispatch-policy-v1"
SSOT_SCHEMA = "dispatch-policy-ssot-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_policy(payload: dict) -> None:
    POLICY_SSOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    POLICY_SSOT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_policy() -> dict | None:
    if not POLICY_SSOT_PATH.is_file():
        return None
    try:
        data = json.loads(POLICY_SSOT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def record_decision(*, decision: dict, eval_tier: str, hub_fields: dict | None = None) -> dict:
    """Merge hub payload + SSOT decision record."""
    existing = load_policy() or {}
    merged = {
        **existing,
        **(hub_fields or {}),
        "schema": SCHEMA,
        "ssot_schema": SSOT_SCHEMA,
        "last_evaluated_at": _now(),
        "current_eval_tier": eval_tier,
        "auto_dispatch_enabled": True,
        "allowlist_version": ALLOWLIST_VERSION,
        "last_decision": decision,
        "path": str(POLICY_SSOT_PATH),
    }
    write_policy(merged)
    return merged
