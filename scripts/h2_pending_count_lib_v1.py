#!/usr/bin/env python3
"""H2 pending count SSOT — open vs scheduled vs closed (SOURCEA_SUPER_FAST_HUB §2a)."""
from __future__ import annotations

_DONE_STATUSES = frozenset({"shipped", "wired", "done", "closed", "pass"})


def _maintainer_open(row: dict) -> bool:
    status = str(row.get("status") or "").strip().lower()
    if status in _DONE_STATUSES:
        return False
    if row.get("shipped_at") or row.get("receipt"):
        if status in ("shipped", "wired"):
            return False
    # UP-* machine refinement rows are cadence-tracked, not open pending
    rid = str(row.get("id") or "")
    if rid.startswith("UP-"):
        return False
    if rid == "LEGACY-HERO":
        return False
    return True


def _scheduled_row(row: dict) -> bool:
    rid = str(row.get("id") or "")
    if rid.startswith("UP-"):
        return True
    if rid == "LEGACY-HERO":
        return True
    return bool(row.get("cadence")) and str(row.get("status") or "").lower() in _DONE_STATUSES


def count_h2_pending(registry: dict) -> dict:
    """Return open/scheduled/closed breakdown for H2 registry buckets."""
    next_phase = list(registry.get("next_phase") or [])
    deferred = list(registry.get("deferred") or [])
    ops_blocker = list(registry.get("ops_blocker") or [])
    maintainer = list(registry.get("maintainer_ship") or [])
    scheduled_bucket = list(registry.get("scheduled_cadence") or [])
    closed_bucket = list(registry.get("maintainer_ship_closed") or [])
    maintainer_open = [r for r in maintainer if _maintainer_open(r)]
    maintainer_scheduled = [r for r in maintainer if _scheduled_row(r)]
    maintainer_scheduled.extend(
        [r for r in scheduled_bucket if r not in maintainer_scheduled]
    )

    form_open = int((registry.get("form_open") or {}).get("count") or 0)
    thread_drafts = int(
        (registry.get("thread_room") or {}).get("pending_draft_rows")
        or 0
    )

    open_total = (
        form_open
        + len(next_phase)
        + len(deferred)
        + len(ops_blocker)
        + len(maintainer_open)
    )
    scheduled_total = len(maintainer_scheduled)
    closed_maintainer = len(closed_bucket) + max(
        0, len(maintainer) - len(maintainer_open) - len(maintainer_scheduled)
    )

    return {
        "pending_total": open_total,
        "pending_open": open_total,
        "scheduled_total": scheduled_total,
        "form_open": form_open,
        "next_phase": len(next_phase),
        "deferred": len(deferred),
        "ops_blocker": len(ops_blocker),
        "maintainer_open": len(maintainer_open),
        "maintainer_scheduled": scheduled_total,
        "maintainer_closed": closed_maintainer,
        "thread_draft_rows": thread_drafts,
        "maintainer_open_ids": [r.get("id") for r in maintainer_open],
        "ops_blocker_ids": [r.get("id") for r in ops_blocker],
        "next_phase_ids": [r.get("id") for r in next_phase],
        "deferred_ids": [r.get("id") for r in deferred],
    }
