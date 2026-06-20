"""Hub API — /api/repair-loop-v1"""
from __future__ import annotations

from runtime.execution_router.router_engine import DEFAULT_GOAL
from runtime.repair_loop.repair_engine import run_repair_loop
from runtime.repair_loop.repair_loop_store import REPAIR_SSOT_PATH

SCHEMA = "repair-loop-v1"


def repair_loop_v1_payload(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_repair_loop(
        goal_tool_id=goal_tool_id,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(REPAIR_SSOT_PATH),
        "task_id": result.get("task_id"),
        "goal_tool_id": result.get("goal_tool_id"),
        "failure_class": result.get("failure_class"),
        "failure": result.get("failure"),
        "recovery_suggestions": result.get("recovery_suggestions"),
        "links": result.get("links"),
        "routing_snapshot": result.get("routing_snapshot"),
        "dispatch_ready": False,
        "instruction": result.get("instruction"),
    }
