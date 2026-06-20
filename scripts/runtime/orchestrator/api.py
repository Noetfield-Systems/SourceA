"""Hub API — /api/runtime-orchestrator-v1"""
from __future__ import annotations

from runtime.execution_router.router_engine import DEFAULT_GOAL
from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration
from runtime.orchestrator.orchestrator_store import ORCHESTRATOR_SSOT_PATH

SCHEMA = "runtime-orchestrator-v1"


def runtime_orchestrator_v1_payload(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
) -> dict:
    result = run_runtime_orchestration(goal_tool_id=goal_tool_id, task_id=task_id)
    if not result.get("ok"):
        return result
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(ORCHESTRATOR_SSOT_PATH),
        "task_id": result.get("task_id"),
        "goal_tool_id": result.get("goal_tool_id"),
        "runtime_stack_complete": result.get("runtime_stack_complete"),
        "pipeline": result.get("pipeline"),
        "overall_status": result.get("overall_status"),
        "dispatch_ready": bool(result.get("dispatch_ready")),
        "dispatch_ready_blockers": list(result.get("dispatch_ready_blockers") or []),
        "founder_confirm_required": True,
        "task_class": result.get("task_class"),
        "dispatch_decision": result.get("dispatch_decision"),
        "routing_decision": result.get("routing_decision"),
        "plan_status": result.get("plan_status"),
        "failure_class": result.get("failure_class"),
        "spine_handoff": result.get("spine_handoff"),
        "instruction": result.get("instruction"),
        "artifacts": result.get("artifacts"),
    }
