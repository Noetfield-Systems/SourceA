"""Build dependency-aware tool graph for a goal task."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from runtime.tool_graph.dependency_mapper import map_dependencies


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_graph(
    *,
    goal_tool_id: str,
    task_id: str = "",
    registry: list[dict],
    memory: list[dict],
    planner: dict,
    context: dict,
) -> dict:
    dependencies = map_dependencies(
        goal_tool_id=goal_tool_id,
        registry=registry,
        memory=memory,
        planner=planner,
        context=context,
    )

    node_ids: set[str] = {goal_tool_id}
    for dep in dependencies:
        node_ids.add(dep["from"])
        node_ids.add(dep["to"])

    registry_by_id = {t["tool_id"]: t for t in registry}
    nodes = []
    for tool_id in sorted(node_ids):
        spec = registry_by_id.get(tool_id)
        if not spec:
            continue
        nodes.append(
            {
                "tool_id": tool_id,
                "title": spec.get("title"),
                "kind": spec.get("kind"),
                "group": spec.get("group"),
                "is_goal": tool_id == goal_tool_id,
            }
        )

    edges = [
        {
            "edge_id": str(uuid.uuid4())[:12],
            "from": d["from"],
            "to": d["to"],
            "type": d["type"],
            "weight": d["weight"],
            "source": d["source"],
            "reason": d["reason"],
        }
        for d in dependencies
    ]

    return {
        "graph_id": str(uuid.uuid4()),
        "task_id": task_id or f"goal:{goal_tool_id}",
        "goal_tool_id": goal_tool_id,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "built_at": _now(),
    }
