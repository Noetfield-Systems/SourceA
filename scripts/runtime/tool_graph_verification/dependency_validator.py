"""Validate tool registry membership, dependencies, and forward-only ordering."""
from __future__ import annotations

from runtime.tool_graph.dependency_mapper import STATIC_DEPENDENCIES, load_tool_registry


def validate_dependencies(
    *,
    graph_entry: dict,
    registry: list[dict] | None = None,
) -> dict:
    registry = registry if registry is not None else load_tool_registry()
    registry_ids = {t["tool_id"] for t in registry}

    execution_path = graph_entry.get("execution_path") or []
    dependencies = graph_entry.get("dependencies") or []
    goal_tool_id = graph_entry.get("goal_tool_id") or ""
    required_tools = graph_entry.get("required_tools") or []

    invalid_tools = [tid for tid in required_tools if tid not in registry_ids]
    missing_dependencies: list[dict] = []
    forward_violations: list[dict] = []

    step_index = {step.get("tool_id"): step.get("step", i + 1) for i, step in enumerate(execution_path)}

    for dep in dependencies:
        src, dst = dep.get("from"), dep.get("to")
        if dep.get("type") != "requires":
            continue
        if src not in registry_ids:
            invalid_tools.append(src)
            missing_dependencies.append({"from": src, "to": dst, "issue": "source_not_in_registry"})
        if dst not in registry_ids:
            invalid_tools.append(dst)
            missing_dependencies.append({"from": src, "to": dst, "issue": "target_not_in_registry"})
        if src in step_index and dst in step_index and step_index[src] >= step_index[dst]:
            forward_violations.append(
                {"from": src, "to": dst, "issue": "prerequisite_not_before_dependent", "steps": step_index}
            )

    for tool_id, prereqs in STATIC_DEPENDENCIES.items():
        if tool_id != goal_tool_id:
            continue
        for prereq in prereqs:
            if prereq in registry_ids and prereq not in required_tools:
                missing_dependencies.append(
                    {"from": prereq, "to": tool_id, "issue": "static_prerequisite_missing_from_path"}
                )

    goal_last = bool(execution_path) and execution_path[-1].get("tool_id") == goal_tool_id
    topo_valid = not forward_violations and goal_last and not invalid_tools

    return {
        "invalid_tools": sorted(set(invalid_tools)),
        "missing_dependencies": missing_dependencies,
        "forward_violations": forward_violations,
        "goal_last": goal_last,
        "topologically_valid": topo_valid,
        "dependency_validity_score": _dependency_score(
            invalid_tools=invalid_tools,
            missing=missing_dependencies,
            forward_violations=forward_violations,
            goal_last=goal_last,
        ),
    }


def _dependency_score(
    *,
    invalid_tools: list[str],
    missing: list[dict],
    forward_violations: list[dict],
    goal_last: bool,
) -> float:
    score = 1.0
    if invalid_tools:
        score -= 0.4
    if missing:
        score -= min(0.35, 0.1 * len(missing))
    if forward_violations:
        score -= min(0.35, 0.15 * len(forward_violations))
    if not goal_last:
        score -= 0.25
    return round(max(0.0, score), 3)
