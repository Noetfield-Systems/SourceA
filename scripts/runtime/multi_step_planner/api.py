"""Hub API — /api/multi-step-planner-v1"""
from __future__ import annotations

from runtime.execution_router.router_engine import DEFAULT_GOAL
from runtime.multi_step_planner.planner_engine import plan_multi_step_execution
from runtime.multi_step_planner.planner_store import PLANNER_SSOT_PATH

SCHEMA = "multi-step-planner-v1"


def multi_step_planner_v1_payload(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = plan_multi_step_execution(
        goal_tool_id=goal_tool_id,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(PLANNER_SSOT_PATH),
        "task_id": result.get("task_id"),
        "goal_tool_id": result.get("goal_tool_id"),
        "planning_authority": result.get("planning_authority"),
        "plan_status": result.get("plan_status"),
        "verification_recommendation": result.get("verification_recommendation"),
        "primary_chain": result.get("primary_chain"),
        "fallback_paths": result.get("fallback_paths"),
        "spine_sequence": result.get("spine_sequence"),
        "dispatch_ready": False,
        "instruction": result.get("instruction"),
    }
