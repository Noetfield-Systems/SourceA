"""Track per-task execution progress against verified path."""
from __future__ import annotations

from runtime.execution_router.router_store import load_task_progress, save_task_progress


def build_execution_state(
    *,
    task_id: str,
    execution_path: list[dict],
    graph_entry: dict | None = None,
) -> dict:
    saved = load_task_progress(task_id) if task_id else {}
    path_tools = [step.get("tool_id") for step in execution_path if step.get("tool_id")]
    completed = [t for t in saved.get("completed") or [] if t in path_tools]

    remaining = [t for t in path_tools if t not in completed]
    current_index = len(completed)
    last_executed = completed[-1] if completed else saved.get("last_executed_tool")

    state = {
        "completed": completed,
        "remaining": remaining,
        "current_index": current_index,
        "last_executed_tool": last_executed,
        "total_steps": len(path_tools),
        "is_complete": len(remaining) == 0 and bool(path_tools),
    }
    if graph_entry:
        state["goal_tool_id"] = graph_entry.get("goal_tool_id")
    return state


def mark_step_complete(*, task_id: str, tool_id: str, execution_path: list[dict]) -> dict:
    state = build_execution_state(task_id=task_id, execution_path=execution_path)
    if tool_id not in state["completed"] and tool_id in [s.get("tool_id") for s in execution_path]:
        state["completed"] = state["completed"] + [tool_id]
        state["remaining"] = [t for t in state["remaining"] if t != tool_id]
        state["current_index"] = len(state["completed"])
        state["last_executed_tool"] = tool_id
        state["is_complete"] = len(state["remaining"]) == 0
    save_task_progress(
        task_id,
        {
            "completed": state["completed"],
            "last_executed_tool": state["last_executed_tool"],
            "current_index": state["current_index"],
        },
    )
    return state
