"""Mac control plane dispatch policy — deploy/dispatch allowed; motor drain blocked.

Law (INCIDENT-042 + Mac Control Plane):
- Mac NEVER commands Cloud Forge Run motor (auto-tick / proceed / skip / forge drain).
- Mac ALWAYS proxies deploy + dispatch via Hub → Railway (cloud-worker, loop-specialist, forge run).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

MAC_MOTOR_BLOCKED_EXACT: tuple[str, ...] = (
    "/api/cloud-forge-run/auto-tick/v1",
    "/api/cloud-forge-run/proceed/v1",
)

MAC_MOTOR_BLOCKED_PREFIXES: tuple[str, ...] = (
    "/api/cloud-forge-run/skip",
)

MAC_DISPATCH_ALLOWED_PREFIXES: tuple[str, ...] = (
    "/api/cloud-worker/",
    "/api/loop-specialist/",
    "/api/signal-factory/",
    "/api/fbe/signal-factory/",
    "/api/forge/",
)

MAC_OBSERVE_ALLOWED_PREFIXES: tuple[str, ...] = (
    "/api/cloud-forge-run/health/",
    "/api/cloud-forge-run/status/",
    "/api/cloud-forge-run/queue/",
    "/api/cloud-forge-run/observer/",
    "/api/cloud-forge-run/evidence-audit/",
)

MAC_MOTOR_FORGE_SUFFIXES: tuple[str, ...] = (
    "/drain/v1",
)

MAC_HUB_MOTOR_ACTIONS: frozenset[str] = frozenset(
    {
        "proceed",
        "auto_tick",
        "skip_head",
        "skip_to_next_real",
    }
)

MAC_QUEUE_MUTATE_ACTIONS: frozenset[str] = frozenset(
    {
        "skip_head",
        "skip_to_next",
        "skip_to_next_real",
        "proceed",
        "auto_tick",
        "reset_pack_gate",
    }
)

OBSERVER_URL = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1"
QUEUE_URL = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1"


def is_mac_control_plane() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return False
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return False
    if Path("/app/receipts").is_dir():
        return False
    return True


def mac_deploy_bypass() -> bool:
    return os.environ.get("SOURCEA_RAILWAY_DEPLOY", "").strip().lower() in ("1", "true", "yes")


def path_is_mac_motor_blocked(path: str, *, body: dict[str, Any] | None = None) -> bool:
    """True when Mac must not proxy this path (motor drain). False = allow Hub→cloud."""
    if not path.startswith("/"):
        path = f"/{path}"

    if any(path.startswith(prefix) for prefix in MAC_DISPATCH_ALLOWED_PREFIXES):
        if path.startswith("/api/forge/") and any(path.endswith(suffix) for suffix in MAC_MOTOR_FORGE_SUFFIXES):
            return True
        return False

    if path in MAC_MOTOR_BLOCKED_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in MAC_MOTOR_BLOCKED_PREFIXES):
        return True

    if path.startswith("/api/cloud-forge-run/queue/") and body:
        action = str(body.get("action") or "").strip().lower()
        if action in MAC_QUEUE_MUTATE_ACTIONS:
            return True

    if path.startswith("/api/cloud-forge-run/"):
        if any(path.startswith(prefix) for prefix in MAC_OBSERVE_ALLOWED_PREFIXES):
            return False
        return True

    return False


def mac_hub_motor_action_blocked(action: str) -> bool:
    return str(action or "").strip().lower() in MAC_HUB_MOTOR_ACTIONS


def upgrade_mac_motor_block(
    row: dict[str, Any],
    *,
    cf_tick_row: dict[str, Any] | None = None,
    action: str = "proceed",
) -> dict[str, Any]:
    """When motor is blocked on Mac, return a helpful upgrade (CF tick) — not a dead-end error."""
    if row.get("error") != "mac_observe_only":
        return row
    cf = cf_tick_row or {}
    return {
        **row,
        "ok": True,
        "motor_blocked": True,
        "decision": "mac_trigger_cf_tick",
        "execution_plane": "mac_control_panel",
        "cf_tick": cf,
        "cf_tick_ok": bool(cf.get("ok")),
        "for_founder": cf.get("for_founder")
        or {
            "show_this": (
                f"Mac motor blocked for {action} — triggered CF full-pack tick instead. "
                "Deploy/dispatch via Hub still works · motor runs on cloud."
            ),
        },
        "mac_dispatch_hint": "python3 scripts/mac_cloud_deploy_dispatch_v1.py --target dispatch --plan-id MAC-CTL-002 --json",
    }


def mac_observe_only_block(*, path: str, body: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Return block receipt when Mac must not proxy; None when dispatch is allowed."""
    if not is_mac_control_plane() or mac_deploy_bypass():
        return None
    if not path_is_mac_motor_blocked(path, body=body):
        return None
    return {
        "ok": False,
        "error": "mac_observe_only",
        "schema": "mac-cloud-observe-only-v1",
        "execution_plane": "mac_control_panel",
        "path": path,
        "motor_blocked": True,
        "dispatch_allowed_prefixes": list(MAC_DISPATCH_ALLOWED_PREFIXES),
        "for_founder": {
            "show_this": (
                "Mac does not drain Cloud Forge Run motor — CF cron */10 runs full_pack×100. "
                "Use Hub dispatch (cloud-worker / loop-specialist / forge run) to deploy faster. "
                f"Proof: {OBSERVER_URL}"
            ),
        },
        "observer_url": OBSERVER_URL,
        "queue_url": QUEUE_URL,
        "mac_dispatch_hint": "POST /api/cloud-worker/dispatch/v1 via Hub :13027 or Worker Hub :13020",
    }
