"""Compute ordered execution path from tool graph (topological + priority)."""
from __future__ import annotations


def _topological_order(nodes: list[dict], edges: list[dict], goal_tool_id: str) -> list[str]:
    node_ids = [n["tool_id"] for n in nodes]
    incoming: dict[str, set[str]] = {nid: set() for nid in node_ids}
    outgoing: dict[str, set[str]] = {nid: set() for nid in node_ids}

    for edge in edges:
        src, dst = edge.get("from"), edge.get("to")
        if src in incoming and dst in incoming:
            incoming[dst].add(src)
            outgoing[src].add(dst)

    requires_edges = [e for e in edges if e.get("type") in ("requires", "historical", "group", "static_transitive")]
    if requires_edges:
        incoming = {nid: set() for nid in node_ids}
        outgoing = {nid: set() for nid in node_ids}
        for edge in requires_edges:
            src, dst = edge.get("from"), edge.get("to")
            if src in incoming and dst in incoming:
                incoming[dst].add(src)
                outgoing[src].add(dst)

    ordered: list[str] = []
    ready = [nid for nid in node_ids if not incoming[nid]]
    ready.sort()

    while ready:
        current = ready.pop(0)
        if current not in ordered:
            ordered.append(current)
        for nxt in sorted(outgoing.get(current, [])):
            incoming[nxt].discard(current)
            if not incoming[nxt] and nxt not in ordered and nxt not in ready:
                ready.append(nxt)
        ready.sort()

    for nid in node_ids:
        if nid not in ordered:
            ordered.append(nid)

    if goal_tool_id in ordered:
        ordered.remove(goal_tool_id)
        ordered.append(goal_tool_id)

    return ordered


def compute_execution_path(graph: dict, *, planner: dict | None = None) -> dict:
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    goal_tool_id = graph.get("goal_tool_id") or ""
    node_by_id = {n["tool_id"]: n for n in nodes}

    planner_rank = {}
    if planner:
        for row in (planner.get("recommendation") or {}).get("ranked_actions") or []:
            if row.get("action_id"):
                planner_rank[row["action_id"]] = float(row.get("score") or 0)

    tool_order = _topological_order(nodes, edges, goal_tool_id)
    topo_index = {tid: i for i, tid in enumerate(tool_order)}

    # Stable tie-break: higher planner score first; goal always last
    non_goal = [tid for tid in tool_order if tid != goal_tool_id]
    non_goal.sort(key=lambda tid: (-planner_rank.get(tid, 0), topo_index.get(tid, 999)))
    tool_order = non_goal + ([goal_tool_id] if goal_tool_id in node_by_id else [])

    execution_path: list[dict] = []
    edge_reasons: dict[tuple[str, str], str] = {}
    for edge in edges:
        edge_reasons[(edge.get("from"), edge.get("to"))] = edge.get("reason") or ""

    for idx, tool_id in enumerate(tool_order, start=1):
        node = node_by_id.get(tool_id) or {}
        prereqs = [e["from"] for e in edges if e.get("to") == tool_id and e.get("type") == "requires"]
        execution_path.append(
            {
                "step": idx,
                "tool_id": tool_id,
                "title": node.get("title") or tool_id,
                "kind": node.get("kind"),
                "group": node.get("group"),
                "is_goal": tool_id == goal_tool_id,
                "requires": prereqs,
                "reason": (
                    "Goal tool"
                    if tool_id == goal_tool_id
                    else edge_reasons.get((prereqs[0], tool_id), "Graph dependency") if prereqs else "Independent step"
                ),
            }
        )

    required_tools = [step["tool_id"] for step in execution_path]
    dependencies = [
        {
            "from": e.get("from"),
            "to": e.get("to"),
            "type": e.get("type"),
            "source": e.get("source"),
            "reason": e.get("reason"),
        }
        for e in edges
    ]

    return {
        "task_id": graph.get("task_id") or "",
        "goal_tool_id": goal_tool_id,
        "execution_path": execution_path,
        "required_tools": required_tools,
        "dependencies": dependencies,
        "estimated_steps": len(execution_path),
    }
