#!/usr/bin/env python3
"""GET /api/machine-hub/v1 — H2 Machine Hub payload (pending registry · rooms · receipts)."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "machine-hub-v1"
API_PATH = "/api/machine-hub/v1"
SINA = Path.home() / ".sina"
H2_REGISTRY = SINA / "h2-pending-registry-v1.json"
THREAD_SPINE = SINA / "thread-room" / "latest-curation-v1.json"
JUDGE_STRIP = SINA / "judge-center" / "latest-alarm-strip-v1.json"

_CACHE: dict = {"at": 0.0, "payload": None}
_CACHE_TTL = 5.0


def invalidate_machine_hub_cache() -> None:
    _CACHE["at"] = 0.0
    _CACHE["payload"] = None


def _maybe_sync_registry(registry: dict) -> dict:
    from machine_hub_staleness_v1 import machine_hub_staleness_probe  # noqa: WPS433

    health = machine_hub_staleness_probe(registry=registry)
    if health.get("auto_heal_recommended"):
        try:
            from h2_pending_registry_sync_v1 import sync_h2_registry  # noqa: WPS433

            sync_h2_registry(caller="machine_hub_payload")
            return _read_json(H2_REGISTRY)
        except Exception:
            pass
    return registry


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _live_form() -> dict:
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        return live_form_payload()
    except Exception:
        return {"open_questions_count": 0, "awaiting_founder_picks": False}


def machine_hub_payload(*, skip_cache: bool = False) -> dict:
    now = time.monotonic()
    if not skip_cache:
        cached = _CACHE.get("payload")
        if cached and (now - float(_CACHE.get("at") or 0)) < _CACHE_TTL:
            return cached

    from worker_hub_daily_rooms_v1 import daily_rooms_payload  # noqa: WPS433
    from machine_hub_staleness_v1 import machine_hub_staleness_probe  # noqa: WPS433

    registry = _read_json(H2_REGISTRY)
    registry = _maybe_sync_registry(registry)
    health = machine_hub_staleness_probe(registry=registry)
    form = _live_form()
    daily_rooms = daily_rooms_payload()
    thread = _read_json(THREAD_SPINE)
    judge_strip = _read_json(JUDGE_STRIP)

    buckets = {
        "form_open": registry.get("form_open") or {},
        "next_phase": registry.get("next_phase") or [],
        "deferred": registry.get("deferred") or [],
        "ops_blocker": registry.get("ops_blocker") or [],
        "maintainer_ship": registry.get("maintainer_ship") or [],
        "scheduled_cadence": registry.get("scheduled_cadence") or [],
        "maintainer_ship_closed": registry.get("maintainer_ship_closed") or [],
        "thread_room": registry.get("thread_room") or {},
    }
    from h2_pending_count_lib_v1 import count_h2_pending  # noqa: WPS433

    counts = count_h2_pending(registry)
    pending_total = counts["pending_total"]

    from h2_maintainer_enforce_slice_v1 import maintainer_enforce_slice_payload  # noqa: WPS433
    from h2_quarantine_bookmark_slice_v1 import quarantine_bookmark_slice_payload  # noqa: WPS433

    enforce_slice = maintainer_enforce_slice_payload()
    quarantine_slice = quarantine_bookmark_slice_payload()

    row = {
        "ok": True,
        "schema": SCHEMA,
        "api": API_PATH,
        "hub": "H2",
        "h1_url": "/",
        "legacy_url": "/legacy/",
        "legacy_retired": True,
        "built_at": registry.get("updated_at") or _now(),
        "health": health,
        "law": "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md §2",
        "form_live": {
            "open_questions_count": int(form.get("open_questions_count") or 0),
            "awaiting_founder_picks": bool(form.get("awaiting_founder_picks")),
            "form_clear": int(form.get("open_questions_count") or 0) == 0,
        },
        "pending_total": pending_total,
        "pending_breakdown": counts,
        "scheduled_total": counts.get("scheduled_total"),
        "buckets": buckets,
        "daily_rooms": daily_rooms,
        "thread_room_spine": {
            "pending_draft_rows": thread.get("pending_draft_rows")
            or (registry.get("thread_room") or {}).get("pending_draft_rows"),
            "status": (registry.get("thread_room") or {}).get("status"),
            "run_cadence": (registry.get("thread_room") or {}).get("run_cadence"),
            "headline": (daily_rooms.get("thread_room") or {}).get("headline"),
        },
        "judge_alarm": {
            "headline": judge_strip.get("headline") or (daily_rooms.get("judge_center") or {}).get("headline"),
            "summary": judge_strip.get("summary") or {},
        },
        "maintainer_enforce_slice": enforce_slice,
        "quarantine_bookmark_slice": quarantine_slice,
        "actions": {
            "rooms_run": {"path": "/api/worker-hub/rooms/run", "method": "POST"},
            "light_refresh": {"path": "/refresh", "method": "POST", "mode": "light"},
            "dual_heal": {"script": "hub_dual_heal_v1.py"},
            "form_api": "/api/live-founder-decision-form-v1",
        },
    }
    _CACHE["at"] = now
    _CACHE["payload"] = row
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Machine hub v1 payload")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-cache", action="store_true")
    args = p.parse_args()
    row = machine_hub_payload(skip_cache=args.no_cache)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"MACHINE-HUB: pending={row.get('pending_total')} form_open={row.get('form_live', {}).get('open_questions_count')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
