"""Tool graph verification pipeline orchestrator."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.tool_graph.dependency_mapper import load_tool_registry
from runtime.tool_graph_verification.context_checker import check_context_alignment
from runtime.tool_graph_verification.cycle_detector import detect_cycles
from runtime.tool_graph_verification.dependency_validator import validate_dependencies
from runtime.tool_graph_verification.plan_scorer import (
    compute_plan_score,
    historical_consistency_score,
    structural_integrity_score,
)
from runtime.tool_graph_verification.safety_checker import check_safety
from runtime.tool_graph_verification.verify_store import (
    VERIFIED_PATH,
    input_fingerprint,
    load_context,
    load_graph_entry,
    load_memory,
    load_planner,
    load_verified_snapshot,
    mark_built,
    should_skip,
    write_verified,
)

SCHEMA = "tool-graph-verified-v1"
DEFAULT_GOAL = "pos-run"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _recommendation(
    *,
    is_valid: bool,
    plan_score: float,
    cycle_detected: bool,
    safe_to_execute: bool,
    missing_dependencies: list,
    invalid_tools: list,
) -> str:
    if cycle_detected or invalid_tools or not safe_to_execute:
        return "reject"
    if not is_valid or missing_dependencies:
        return "needs_fix"
    if plan_score >= 0.65:
        return "approve"
    return "needs_fix"


def verify_tool_graph(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force: bool = False,
) -> dict:
    fp = input_fingerprint(goal=goal_tool_id, task_id=task_id)
    cache_key = f"{goal_tool_id}:{task_id}"

    if should_skip(fingerprint=fp, force=force):
        cached = load_verified_snapshot()
        entries = cached.get("verifications") or {}
        if cache_key in entries:
            return {**entries[cache_key], "ok": True, "skipped": True, "reason": "inputs unchanged"}

    graph_entry = load_graph_entry(goal_tool_id=goal_tool_id, task_id=task_id)
    if not graph_entry:
        from runtime.tool_graph.api import build_tool_graph  # noqa: WPS433

        graph_entry = build_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=force)
        if not graph_entry.get("ok"):
            return graph_entry

    memory = load_memory()
    planner = load_planner()
    context = load_context()
    registry = load_tool_registry()

    graph = graph_entry.get("graph") or {}
    nodes = [n.get("tool_id") for n in graph.get("nodes") or [] if n.get("tool_id")]
    edges = graph.get("edges") or graph_entry.get("dependencies") or []
    execution_path = graph_entry.get("execution_path") or []

    cycle = detect_cycles(nodes=nodes, edges=edges)
    deps = validate_dependencies(graph_entry=graph_entry, registry=registry)
    ctx = check_context_alignment(execution_path=execution_path, context=context, planner=planner)
    safety = check_safety(execution_path=execution_path, planner=planner, context=context)

    hist = historical_consistency_score(execution_path=execution_path, memory=memory)
    structural = structural_integrity_score(
        cycle_detected=cycle["cycle_detected"],
        topologically_valid=deps["topologically_valid"],
        goal_last=deps["goal_last"],
        estimated_steps=graph_entry.get("estimated_steps", len(execution_path)),
    )
    scoring = compute_plan_score(
        dependency_validity_score=deps["dependency_validity_score"],
        context_alignment_score=ctx["context_alignment_score"],
        historical_consistency=hist,
        structural_integrity=structural,
    )

    is_valid = (
        not cycle["cycle_detected"]
        and deps["topologically_valid"]
        and deps["goal_last"]
        and not deps["invalid_tools"]
        and safety["safe_to_execute"]
    )

    recommendation = _recommendation(
        is_valid=is_valid,
        plan_score=scoring["plan_score"],
        cycle_detected=cycle["cycle_detected"],
        safe_to_execute=safety["safe_to_execute"],
        missing_dependencies=deps["missing_dependencies"],
        invalid_tools=deps["invalid_tools"],
    )

    verified_path = [
        {"step": step.get("step"), "tool_id": step.get("tool_id")}
        for step in execution_path
        if step.get("tool_id")
    ]

    result = {
        "ok": True,
        "schema": SCHEMA,
        "skipped": False,
        "generated_at": _now(),
        "path": str(VERIFIED_PATH),
        "task_id": graph_entry.get("task_id") or task_id or f"goal:{goal_tool_id}",
        "goal_tool_id": goal_tool_id,
        "is_valid": is_valid,
        "cycle_detected": cycle["cycle_detected"],
        "cycle_nodes": cycle.get("cycle_nodes") or [],
        "missing_dependencies": deps["missing_dependencies"],
        "invalid_tools": deps["invalid_tools"],
        "forward_violations": deps.get("forward_violations") or [],
        "context_alignment_score": ctx["context_alignment_score"],
        "context_issues": ctx.get("issues") or [],
        "safety_score": safety["safety_score"],
        "safety_violations": safety.get("violations") or [],
        "plan_score": scoring["plan_score"],
        "score_breakdown": scoring["score_breakdown"],
        "execution_path_verified": verified_path,
        "recommendation": recommendation,
        "checks": {
            "cycle": cycle,
            "dependencies": deps,
            "context": ctx,
            "safety": safety,
        },
    }

    cached = load_verified_snapshot() if VERIFIED_PATH.is_file() else {}
    verifications = cached.get("verifications") or {}
    verifications[cache_key] = result
    store = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": result["generated_at"],
        "path": str(VERIFIED_PATH),
        "verifications": verifications,
        "latest": result,
    }
    write_verified(store)
    mark_built(store, fp)
    return result
