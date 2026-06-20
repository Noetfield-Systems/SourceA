"""Select next valid unexecuted step from verified execution path."""
from __future__ import annotations


def _dependencies_for(tool_id: str, graph_entry: dict) -> list[str]:
    deps: list[str] = []
    for edge in graph_entry.get("dependencies") or []:
        if edge.get("to") == tool_id and edge.get("type") in ("requires", "static_transitive", "group"):
            src = edge.get("from")
            if src:
                deps.append(src)
    for step in graph_entry.get("execution_path") or []:
        if step.get("tool_id") == tool_id:
            deps.extend(step.get("requires") or [])
    return sorted(set(deps))


def dependencies_satisfied(tool_id: str, *, completed: list[str], graph_entry: dict) -> bool:
    required = _dependencies_for(tool_id, graph_entry)
    return all(r in completed for r in required)


def select_candidates(
    *,
    execution_path: list[dict],
    completed: list[str],
    graph_entry: dict,
) -> list[str]:
    candidates: list[str] = []
    for step in execution_path:
        tool_id = step.get("tool_id")
        if not tool_id or tool_id in completed:
            continue
        if dependencies_satisfied(tool_id, completed=completed, graph_entry=graph_entry):
            candidates.append(tool_id)
    return candidates


def step_detail(tool_id: str, execution_path: list[dict]) -> dict:
    for step in execution_path:
        if step.get("tool_id") == tool_id:
            return step
    return {"tool_id": tool_id, "step": 0, "title": tool_id}
