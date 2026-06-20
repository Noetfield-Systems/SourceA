#!/usr/bin/env python3
"""GET /api/slice/<domain> — per-tab payload slices (HUB-LITE Phase 0)."""
from __future__ import annotations

from datetime import datetime, timezone

# tab id → payload keys (mirrors HEAVY_TAB_KEYS in app.js)
DOMAIN_KEYS: dict[str, tuple[str, ...]] = {
    "backlog": ("audit_backlog",),
    "fleet": ("fleet",),
    "roadmaps": ("roadmaps_goals",),
    "track": ("commitments",),
    "guide": ("guides",),
    "roles": ("roles_detail",),
    "hq": ("hq_duties_full",),
    "system-roadmap": ("system_roadmap",),
    "council-room": ("council_room",),
    "threads": ("ecosystem", "founder_threads"),
    "ecosystem": ("ecosystem",),
    "agent-loop": ("agent_loop",),
    "intelligence": ("intelligence_circle",),
    "semej": ("semej",),
    "order-guardian": ("order_guardian",),
    "incident-room": ("incident_room",),
    "conflict-room": ("conflict_room",),
    "agent-scoreboard": ("agent_scoreboard",),
    "knowledge-library": ("knowledge_library",),
    "ai-advisory": ("ai_advisory",),
    "rules": ("rules",),
    "notes": ("founder_notes",),
    "doc-library": ("important_docs",),
}

SCHEMA = "hub-slice-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _live_slice(domain: str) -> dict | None:
    """Prefer live API builders when disk cache may be stale."""
    try:
        if domain == "agent-loop":
            from agent_loop import loop_payload  # noqa: WPS433
            from sina_command_lib import get_hub_payload, warm_hub_cache_from_disk  # noqa: WPS433

            warm_hub_cache_from_disk()
            return {"agent_loop": loop_payload(hub_payload=get_hub_payload())}
        if domain == "intelligence":
            from intelligence_circle import circle_payload  # noqa: WPS433
            from sina_command_lib import get_hub_payload, warm_hub_cache_from_disk  # noqa: WPS433

            warm_hub_cache_from_disk()
            return {"intelligence_circle": circle_payload(hub_payload=get_hub_payload())}
        if domain == "ai-advisory":
            from sina_ai_advisory import load_cached_advisory  # noqa: WPS433

            return {"ai_advisory": load_cached_advisory()}
        if domain == "semej":
            from sina_command_lib import semej_payload  # noqa: WPS433

            return {"semej": semej_payload()}
    except Exception:
        return None
    return None


def slice_payload(domain: str) -> dict:
    keys = DOMAIN_KEYS.get(domain)
    if not keys:
        return {"ok": False, "schema": SCHEMA, "error": f"unknown_slice_domain:{domain}"}

    from hub_sync_slim_v1 import ensure_shell_generation_id  # noqa: WPS433
    from sina_command_lib import get_hub_payload, warm_hub_cache_from_disk  # noqa: WPS433

    gid = ensure_shell_generation_id()
    live = _live_slice(domain)
    if live:
        return {
            "ok": True,
            "schema": SCHEMA,
            "domain": domain,
            "generation_id": gid,
            "built_at": _now(),
            "keys": list(live.keys()),
            "data": live,
        }

    warm_hub_cache_from_disk()
    full = get_hub_payload()
    data = {k: full[k] for k in keys if k in full}
    missing = [k for k in keys if k not in data]
    return {
        "ok": bool(data),
        "schema": SCHEMA,
        "domain": domain,
        "generation_id": gid,
        "built_at": full.get("built_at") or _now(),
        "keys": list(data.keys()),
        "data": data,
        "missing_keys": missing or None,
    }
