"""Execution Router v1 — verified graph → next-step instruction (no execute)."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.execution_router.execution_state import build_execution_state
from runtime.execution_router.policy_engine import evaluate_step, policy_context
from runtime.execution_router.priority_resolver import resolve_priority
from runtime.execution_router.router_store import (
    ROUTER_SSOT_PATH,
    input_fingerprint,
    load_context,
    load_graph_entry,
    load_memory,
    load_planner,
    load_router_snapshot,
    load_verified_entry,
    write_router_snapshot,
)
from runtime.execution_router.step_selector import dependencies_satisfied, select_candidates, step_detail

SCHEMA = "execution-router-v1"
DEFAULT_GOAL = "pos-run"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def route_execution(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    task_id = task_id or f"route:{goal_tool_id}"
    verified = load_verified_entry(goal_tool_id=goal_tool_id, task_id=task_id)
    graph_entry = load_graph_entry(goal_tool_id=goal_tool_id, task_id=task_id)

    if not verified or not graph_entry:
        from runtime.tool_graph.api import build_tool_graph  # noqa: WPS433
        from runtime.tool_graph_verification.validation_engine import verify_tool_graph  # noqa: WPS433

        build_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=force_refresh)
        verify_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=force_refresh)
        verified = load_verified_entry(goal_tool_id=goal_tool_id, task_id=task_id)
        graph_entry = load_graph_entry(goal_tool_id=goal_tool_id, task_id=task_id)

    if not verified or not graph_entry:
        return {"ok": False, "error": "verified graph not found", "task_id": task_id, "goal_tool_id": goal_tool_id}

    planner = load_planner()
    context = load_context()
    memory = load_memory()
    policy = policy_context(verified=verified, planner=planner, context=context)

    execution_path = graph_entry.get("execution_path") or []
    path_verified = verified.get("execution_path_verified") or []
    if path_verified and not execution_path:
        execution_path = [{"step": p.get("step"), "tool_id": p.get("tool_id"), "title": p.get("tool_id")} for p in path_verified]

    state = build_execution_state(task_id=task_id, execution_path=execution_path, graph_entry=graph_entry)

    # STEP A — gate on verification approval
    if not verified.get("is_valid"):
        return _blocked_result(
            task_id=task_id,
            goal_tool_id=goal_tool_id,
            state=state,
            reason="graph is_valid is false",
            routing_decision="block",
        )
    if verified.get("recommendation") != "approve":
        return _blocked_result(
            task_id=task_id,
            goal_tool_id=goal_tool_id,
            state=state,
            reason=f"verification recommendation is {verified.get('recommendation')} (requires approve)",
            routing_decision="block" if verified.get("recommendation") == "reject" else "wait",
        )
    if verified.get("cycle_detected"):
        return _blocked_result(
            task_id=task_id,
            goal_tool_id=goal_tool_id,
            state=state,
            reason="cycle detected in verified graph",
            routing_decision="block",
        )

    if state.get("is_complete"):
        return _complete_result(task_id=task_id, goal_tool_id=goal_tool_id, state=state)

    candidates = select_candidates(
        execution_path=execution_path,
        completed=state["completed"],
        graph_entry=graph_entry,
    )

    scored_candidates = []
    allowed_candidates = []
    for tool_id in candidates:
        deps_ok = dependencies_satisfied(tool_id, completed=state["completed"], graph_entry=graph_entry)
        pol = evaluate_step(tool_id=tool_id, policy=policy, dependencies_satisfied=deps_ok)
        if pol["allowed"]:
            allowed_candidates.append(tool_id)
        scored_candidates.append({"tool_id": tool_id, **pol})

    if not allowed_candidates:
        return _blocked_result(
            task_id=task_id,
            goal_tool_id=goal_tool_id,
            state=state,
            reason="no policy-approved candidates",
            routing_decision="wait",
            extra={"candidates_checked": scored_candidates},
        )

    winner = resolve_priority(candidates=allowed_candidates, policy=policy, memory=memory)
    if not winner:
        return _blocked_result(
            task_id=task_id,
            goal_tool_id=goal_tool_id,
            state=state,
            reason="priority resolution failed",
            routing_decision="wait",
        )

    step = step_detail(winner["tool_id"], execution_path)
    result = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(ROUTER_SSOT_PATH),
        "task_id": task_id,
        "goal_tool_id": goal_tool_id,
        "next_step": {
            "step": step.get("step") or state["current_index"] + 1,
            "tool_id": winner["tool_id"],
            "title": step.get("title") or winner["tool_id"],
            "status": "ready",
        },
        "execution_state": {
            "completed": state["completed"],
            "remaining": state["remaining"],
            "current_index": state["current_index"],
        },
        "routing_decision": "allow",
        "reason": "next step selected from verified path",
        "score_breakdown": winner["breakdown"],
        "dispatch_ready": False,
        "instruction": {
            "action": "founder_confirm_then_enqueue_spine",
            "tool_id": winner["tool_id"],
            "note": "Router emits instruction only — does not execute",
        },
    }
    _persist_route(task_id, result)
    return result


def _blocked_result(
    *,
    task_id: str,
    goal_tool_id: str,
    state: dict,
    reason: str,
    routing_decision: str,
    extra: dict | None = None,
) -> dict:
    result = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": task_id,
        "goal_tool_id": goal_tool_id,
        "next_step": {
            "step": state.get("current_index", 0) + 1,
            "tool_id": (state.get("remaining") or [""])[0] if state.get("remaining") else "",
            "title": "",
            "status": "blocked",
        },
        "execution_state": {
            "completed": state.get("completed") or [],
            "remaining": state.get("remaining") or [],
            "current_index": state.get("current_index", 0),
        },
        "routing_decision": routing_decision,
        "reason": reason,
        "score_breakdown": {"context": 0.0, "safety": 0.0, "history": 0.0, "planner": 0.0},
        "dispatch_ready": False,
    }
    if extra:
        result.update(extra)
    _persist_route(task_id, result)
    return result


def _complete_result(*, task_id: str, goal_tool_id: str, state: dict) -> dict:
    result = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": task_id,
        "goal_tool_id": goal_tool_id,
        "next_step": {
            "step": state.get("total_steps", 0),
            "tool_id": goal_tool_id,
            "title": "complete",
            "status": "complete",
        },
        "execution_state": {
            "completed": state.get("completed") or [],
            "remaining": [],
            "current_index": state.get("current_index", 0),
        },
        "routing_decision": "allow",
        "reason": "all steps completed",
        "score_breakdown": {"context": 0.0, "safety": 0.0, "history": 0.0, "planner": 0.0},
        "dispatch_ready": False,
    }
    _persist_route(task_id, result)
    return result


def _persist_route(task_id: str, result: dict) -> None:
    snap = load_router_snapshot() if ROUTER_SSOT_PATH.is_file() else {"schema": SCHEMA, "routes": {}}
    snap["schema"] = SCHEMA
    snap["generated_at"] = result.get("generated_at")
    snap["path"] = str(ROUTER_SSOT_PATH)
    snap.setdefault("routes", {})[task_id] = result
    snap["latest"] = result
    write_router_snapshot(snap)
