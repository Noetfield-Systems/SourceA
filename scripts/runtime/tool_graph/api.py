"""Tool Graph Engine v1 — graph-based execution paths (read-only intelligence inputs)."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.tool_graph.dependency_mapper import load_tool_registry
from runtime.tool_graph.execution_path import compute_execution_path
from runtime.tool_graph.graph_builder import build_graph
from runtime.tool_graph.graph_store import (
    GRAPH_SSOT_PATH,
    input_fingerprint,
    load_context_intelligence,
    load_memory,
    load_planner_context,
    load_snapshot,
    mark_built,
    should_skip,
    write_snapshot,
)

SCHEMA = "tool-graph-v1"
DEFAULT_GOAL = "pos-run"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_tool_graph(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
    force: bool = False,
) -> dict:
    registry = load_tool_registry()
    if not any(t["tool_id"] == goal_tool_id for t in registry):
        return {"ok": False, "error": f"unknown goal tool: {goal_tool_id}", "registry_tools": [t["tool_id"] for t in registry]}

    fp = input_fingerprint(registry_count=len(registry))
    cache_key = f"{goal_tool_id}:{task_id}"
    if should_skip(fingerprint={**fp, "goal": goal_tool_id, "task_id": task_id}, force=force):
        cached = load_snapshot()
        graphs = cached.get("graphs") or {}
        if cache_key in graphs:
            return {**graphs[cache_key], "ok": True, "skipped": True, "reason": "inputs unchanged"}

    memory = load_memory()
    planner = load_planner_context()
    context = load_context_intelligence()

    graph = build_graph(
        goal_tool_id=goal_tool_id,
        task_id=task_id,
        registry=registry,
        memory=memory,
        planner=planner,
        context=context,
    )
    path_result = compute_execution_path(graph, planner=planner)

    result = {
        "ok": True,
        "schema": SCHEMA,
        "skipped": False,
        "generated_at": _now(),
        "path": str(GRAPH_SSOT_PATH),
        "graph": graph,
        **path_result,
    }

    cached = load_snapshot() if GRAPH_SSOT_PATH.is_file() else {}
    graphs = cached.get("graphs") or {}
    graphs[cache_key] = result
    store = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": result["generated_at"],
        "path": str(GRAPH_SSOT_PATH),
        "registry_count": len(registry),
        "registry_tools": [t["tool_id"] for t in registry],
        "graphs": graphs,
        "latest": result,
    }
    write_snapshot(store)
    mark_built(store, {**fp, "goal": goal_tool_id, "task_id": task_id})
    return result


def tool_graph_v1_payload(*, goal_tool_id: str = DEFAULT_GOAL, task_id: str = "") -> dict:
    result = build_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id)
    if not result.get("ok"):
        return result
    graph = result.get("graph") or {}
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(GRAPH_SSOT_PATH),
        "skipped": result.get("skipped", False),
        "task_id": result.get("task_id"),
        "goal_tool_id": result.get("goal_tool_id"),
        "execution_path": result.get("execution_path") or [],
        "required_tools": result.get("required_tools") or [],
        "dependencies": result.get("dependencies") or [],
        "estimated_steps": result.get("estimated_steps", 0),
        "graph_summary": {
            "node_count": graph.get("node_count", 0),
            "edge_count": graph.get("edge_count", 0),
            "nodes": graph.get("nodes") or [],
        },
    }
