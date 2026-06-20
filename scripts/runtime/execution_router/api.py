"""Hub API — /api/execution-router-v1"""
from __future__ import annotations

from runtime.execution_router.router_engine import DEFAULT_GOAL, route_execution
from runtime.execution_router.router_store import ROUTER_SSOT_PATH

SCHEMA = "execution-router-v1"


def execution_router_v1_payload(*, goal_tool_id: str = DEFAULT_GOAL, task_id: str = "") -> dict:
    result = route_execution(goal_tool_id=goal_tool_id, task_id=task_id)
    if not result.get("ok"):
        return result
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(ROUTER_SSOT_PATH),
        "task_id": result.get("task_id"),
        "goal_tool_id": result.get("goal_tool_id"),
        "next_step": result.get("next_step"),
        "execution_state": result.get("execution_state"),
        "routing_decision": result.get("routing_decision"),
        "reason": result.get("reason"),
        "score_breakdown": result.get("score_breakdown"),
        "instruction": result.get("instruction"),
        "dispatch_ready": False,
    }
