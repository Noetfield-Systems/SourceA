"""Current operational state from execution memory (read-only)."""
from __future__ import annotations

from execution_intelligence.reader import read_execution_memory


def analyze_operational_state(*, records: list[dict] | None = None, window: int = 25) -> dict:
    records = records if records is not None else read_execution_memory()
    recent = records[-window:] if records else []

    successes = sum(1 for r in recent if r.get("status") == "success")
    failures = sum(1 for r in recent if r.get("status") not in ("success", ""))
    active_tasks = len({r.get("task_id") for r in recent if r.get("task_id")})
    total = len(recent) or 1
    health = round(successes / total, 3)

    action_counts: dict[str, int] = {}
    for rec in recent:
        act = rec.get("action_id") or "unknown"
        action_counts[act] = action_counts.get(act, 0) + 1
    top_actions = sorted(action_counts.items(), key=lambda x: -x[1])[:5]

    return {
        "active_tasks": active_tasks,
        "recent_successes": successes,
        "recent_failures": failures,
        "system_health": health,
        "memory_total": len(records),
        "recent_window": len(recent),
        "last_run_at": recent[-1].get("timestamp") if recent else None,
        "last_action_id": recent[-1].get("action_id") if recent else None,
        "last_status": recent[-1].get("status") if recent else None,
        "top_recent_actions": [{"action_id": a, "count": c} for a, c in top_actions],
    }
