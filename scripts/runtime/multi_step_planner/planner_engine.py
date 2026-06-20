"""Multi-step planner v1 — verified graph → chain + fallbacks (runtime authority only)."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.execution_router.router_engine import DEFAULT_GOAL, route_execution
from runtime.multi_step_planner.chain_builder import build_primary_chain, spine_sequence_from_chain
from runtime.multi_step_planner.fallback_paths import build_fallback_paths
from runtime.multi_step_planner.planner_store import (
    PLANNER_SSOT_PATH,
    load_graph_entry,
    load_planner_snapshot,
    load_verified_entry,
    write_planner_snapshot,
)
from runtime.repair_loop.repair_engine import run_repair_loop

SCHEMA = "multi-step-planner-v1"
PLANNING_AUTHORITY = "execution-time sequencing only — NOT pre-LLM plan SSOT (D10 owns that)"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def plan_multi_step_execution(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    task_id = task_id or f"plan:{goal_tool_id}"

    if force_refresh:
        route_execution(goal_tool_id=goal_tool_id, task_id=task_id, force_refresh=True)
        run_repair_loop(goal_tool_id=goal_tool_id, task_id=task_id, force_refresh=True)

    verified = load_verified_entry(goal_tool_id=goal_tool_id, task_id=task_id)
    graph_entry = load_graph_entry(goal_tool_id=goal_tool_id, task_id=task_id)

    if not verified or not graph_entry:
        from runtime.tool_graph.api import build_tool_graph  # noqa: WPS433
        from runtime.tool_graph_verification.validation_engine import verify_tool_graph  # noqa: WPS433

        build_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=True)
        verify_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=True)
        verified = load_verified_entry(goal_tool_id=goal_tool_id, task_id=task_id)
        graph_entry = load_graph_entry(goal_tool_id=goal_tool_id, task_id=task_id)

    if not verified or not graph_entry:
        return {
            "ok": False,
            "error": "verified graph not found",
            "task_id": task_id,
            "goal_tool_id": goal_tool_id,
        }

    execution_path = graph_entry.get("execution_path") or []
    primary_chain = build_primary_chain(
        execution_path=execution_path,
        graph_entry=graph_entry,
        verified=verified,
    )
    fallback_paths = build_fallback_paths(task_id=task_id)
    spine_sequence = spine_sequence_from_chain(primary_chain)

    recommendation = verified.get("recommendation") or "unknown"
    plan_status = "ready" if recommendation == "approve" and not spine_sequence.get("blocked") else "needs_review"

    result = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(PLANNER_SSOT_PATH),
        "task_id": task_id,
        "goal_tool_id": goal_tool_id,
        "planning_authority": PLANNING_AUTHORITY,
        "verification_recommendation": recommendation,
        "plan_status": plan_status,
        "primary_chain": primary_chain,
        "fallback_paths": fallback_paths,
        "spine_sequence": spine_sequence,
        "dispatch_ready": False,
        "instruction": spine_sequence.get("instruction"),
        "links": {
            "verified_graph": str(graph_entry.get("path") or ""),
            "graph_goal": goal_tool_id,
        },
    }

    _persist_plan(task_id, result)
    return result


def _persist_plan(task_id: str, result: dict) -> None:
    snap = load_planner_snapshot() if PLANNER_SSOT_PATH.is_file() else {"plans": {}}
    snap["schema"] = SCHEMA
    snap["generated_at"] = result.get("generated_at")
    snap["path"] = str(PLANNER_SSOT_PATH)
    snap.setdefault("plans", {})[task_id] = result
    snap["latest"] = result
    write_planner_snapshot(snap)
