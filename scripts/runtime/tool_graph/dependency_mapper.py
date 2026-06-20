"""Map tool dependencies from registry rules, history, planner, and context."""
from __future__ import annotations

from collections import Counter

# Locked workflow dependencies (Prompt OS + spine tools)
STATIC_DEPENDENCIES: dict[str, list[str]] = {
    "pos-run": ["pos-dispatch", "pos-decide"],
    "pos-execute": ["pos-dispatch", "pos-decide", "pos-run"],
    "pos-decide": ["pos-dispatch"],
    "pos-status": [],
    "pos-dispatch": [],
    "spine-smoke-echo": [],
}

GROUP_PREREQUISITES: dict[str, list[str]] = {
    "engines": ["pos-dispatch"],
    "ingest": ["pos-dispatch"],
}


def load_tool_registry() -> list[dict]:
    """Available spine-executable tools from hub registry (read-only)."""
    from execution_spine.types import SPINE_EXECUTABLE_KINDS  # noqa: WPS433
    from sina_command_lib import founder_actions_flat  # noqa: WPS433

    tools: list[dict] = []
    for act in founder_actions_flat():
        kind = act.get("kind") or ""
        if kind not in SPINE_EXECUTABLE_KINDS:
            continue
        tools.append(
            {
                "tool_id": act["id"],
                "title": act.get("title") or act["id"],
                "kind": kind,
                "group": act.get("group") or "other",
                "action": act.get("action"),
                "repo": act.get("repo"),
            }
        )
    return tools


def _historical_edges(memory: list[dict]) -> list[dict]:
    """Infer soft dependencies from sequential successful runs."""
    edges: list[dict] = []
    action_seq = [r.get("action_id") for r in memory if r.get("action_id")]
    pair_counts: Counter[tuple[str, str]] = Counter()
    for i in range(1, len(action_seq)):
        prev_a, cur_a = action_seq[i - 1], action_seq[i]
        if prev_a and cur_a and prev_a != cur_a:
            pair_counts[(prev_a, cur_a)] += 1

    for (src, dst), count in pair_counts.most_common(12):
        edges.append(
            {
                "from": src,
                "to": dst,
                "type": "historical",
                "weight": min(1.0, count / max(len(memory), 1) * 3),
                "source": "execution_memory",
                "reason": f"Observed {count}x sequential run",
            }
        )
    return edges


def _planner_priority(planner: dict) -> dict[str, float]:
    ranked = (planner.get("recommendation") or {}).get("ranked_actions") or []
    return {row.get("action_id"): float(row.get("score") or 0) for row in ranked if row.get("action_id")}


def map_dependencies(
    *,
    goal_tool_id: str,
    registry: list[dict],
    memory: list[dict],
    planner: dict,
    context: dict,
) -> list[dict]:
    registry_ids = {t["tool_id"] for t in registry}
    dependencies: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def add_edge(src: str, dst: str, *, edge_type: str, source: str, reason: str, weight: float = 1.0) -> None:
        if src not in registry_ids or dst not in registry_ids:
            return
        key = (src, dst, edge_type)
        if key in seen:
            return
        seen.add(key)
        dependencies.append(
            {
                "from": src,
                "to": dst,
                "type": edge_type,
                "weight": round(weight, 3),
                "source": source,
                "reason": reason,
            }
        )

    goal_tool = next((t for t in registry if t["tool_id"] == goal_tool_id), None)
    for prereq in STATIC_DEPENDENCIES.get(goal_tool_id, []):
        add_edge(prereq, goal_tool_id, edge_type="requires", source="static", reason="Locked workflow prerequisite")

    if goal_tool:
        for prereq in GROUP_PREREQUISITES.get(goal_tool.get("group") or "", []):
            add_edge(prereq, goal_tool_id, edge_type="requires", source="group", reason=f"Group '{goal_tool['group']}' prerequisite")

    for prereq in STATIC_DEPENDENCIES.get(goal_tool_id, []):
        for nested in STATIC_DEPENDENCIES.get(prereq, []):
            add_edge(nested, prereq, edge_type="requires", source="static_transitive", reason=f"Transitive via {prereq}")

    for edge in _historical_edges(memory):
        if edge["to"] == goal_tool_id or edge["from"] in STATIC_DEPENDENCIES.get(goal_tool_id, []):
            add_edge(
                edge["from"],
                edge["to"],
                edge_type="historical",
                source=edge["source"],
                reason=edge["reason"],
                weight=edge["weight"],
            )

    planner_scores = _planner_priority(planner)
    recommended = (planner.get("recommendation") or {}).get("recommended_actions") or []
    if goal_tool_id in recommended:
        for other in recommended:
            if other != goal_tool_id and other in registry_ids:
                add_edge(
                    other,
                    goal_tool_id,
                    edge_type="planner_hint",
                    source="planner_context",
                    reason="Planner recommended action ordering",
                    weight=min(1.0, planner_scores.get(other, 50) / 120),
                )

    critical = (context.get("repo_state") or {}).get("critical_paths") or []
    if critical and "pos-dispatch" in registry_ids and goal_tool_id != "pos-dispatch":
        add_edge(
            "pos-dispatch",
            goal_tool_id,
            edge_type="context_hint",
            source="context_intelligence",
            reason="Critical path active — dispatch first",
            weight=0.6,
        )

    dependencies.sort(key=lambda d: (-d["weight"], d["from"], d["to"]))
    return dependencies
