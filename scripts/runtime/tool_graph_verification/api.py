"""Hub API — /api/tool-graph-verify-v1"""
from __future__ import annotations

from runtime.tool_graph_verification.validation_engine import DEFAULT_GOAL, verify_tool_graph
from runtime.tool_graph_verification.verify_store import VERIFIED_PATH

SCHEMA = "tool-graph-verified-v1"


def tool_graph_verify_v1_payload(*, goal_tool_id: str = DEFAULT_GOAL, task_id: str = "") -> dict:
    result = verify_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id)
    if not result.get("ok"):
        return result
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(VERIFIED_PATH),
        "skipped": result.get("skipped", False),
        "task_id": result.get("task_id"),
        "goal_tool_id": result.get("goal_tool_id"),
        "is_valid": result.get("is_valid"),
        "cycle_detected": result.get("cycle_detected"),
        "missing_dependencies": result.get("missing_dependencies") or [],
        "invalid_tools": result.get("invalid_tools") or [],
        "context_alignment_score": result.get("context_alignment_score"),
        "safety_score": result.get("safety_score"),
        "plan_score": result.get("plan_score"),
        "score_breakdown": result.get("score_breakdown") or {},
        "execution_path_verified": result.get("execution_path_verified") or [],
        "recommendation": result.get("recommendation"),
        "validated_graph": {
            "execution_path": result.get("execution_path_verified"),
            "dependencies_valid": not result.get("missing_dependencies"),
            "safe": result.get("safety_score", 0) >= 0.5,
        },
    }
