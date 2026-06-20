"""Repair loop v1 — classify failure → recovery suggestions (no spine writes)."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.execution_router.router_engine import DEFAULT_GOAL, route_execution
from runtime.execution_router.router_store import load_verified_entry
from runtime.repair_loop.failure_classifier import classify_failure
from runtime.repair_loop.recovery_graph import build_recovery_suggestions
from runtime.repair_loop.repair_loop_store import (
    REPAIR_SSOT_PATH,
    input_fingerprint,
    load_router_route,
    load_repair_snapshot,
    write_repair_snapshot,
)

SCHEMA = "repair-loop-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_repair_loop(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    task_id = task_id or f"repair:{goal_tool_id}"

    route = load_router_route(task_id=task_id)
    if not route or force_refresh:
        route = route_execution(goal_tool_id=goal_tool_id, task_id=task_id, force_refresh=force_refresh)

    if not route.get("ok"):
        return {
            "ok": False,
            "error": route.get("error") or "routing failed",
            "task_id": task_id,
            "goal_tool_id": goal_tool_id,
        }

    verified = load_verified_entry(goal_tool_id=goal_tool_id, task_id=task_id)
    failure = classify_failure(route=route, verified=verified, task_id=task_id)
    suggestions = build_recovery_suggestions(
        failure=failure,
        route=route,
        goal_tool_id=goal_tool_id,
        task_id=task_id,
    )

    result = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(REPAIR_SSOT_PATH),
        "task_id": task_id,
        "goal_tool_id": goal_tool_id,
        "failure_class": failure.get("failure_class"),
        "failure": failure,
        "recovery_suggestions": suggestions,
        "links": failure.get("links") or {},
        "routing_snapshot": {
            "routing_decision": route.get("routing_decision"),
            "reason": route.get("reason"),
            "next_step": route.get("next_step"),
        },
        "dispatch_ready": False,
        "instruction": {
            "action": "founder_review_recovery_suggestions",
            "note": "Repair loop suggests paths only — does not execute or enqueue spine",
        },
        "input_fingerprint": input_fingerprint(goal=goal_tool_id, task_id=task_id),
    }

    _persist_repair(task_id, result)
    return result


def _persist_repair(task_id: str, result: dict) -> None:
    snap = load_repair_snapshot() if REPAIR_SSOT_PATH.is_file() else {"schema": SCHEMA, "repairs": {}}
    snap["schema"] = SCHEMA
    snap["generated_at"] = result.get("generated_at")
    snap["path"] = str(REPAIR_SSOT_PATH)
    snap.setdefault("repairs", {})[task_id] = result
    snap["latest"] = result
    write_repair_snapshot(snap)
