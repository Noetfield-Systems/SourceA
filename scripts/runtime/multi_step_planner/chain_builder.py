"""Build primary execution chain from verified tool graph path."""
from __future__ import annotations

from runtime.execution_router.step_selector import dependencies_satisfied


def build_primary_chain(
    *,
    execution_path: list[dict],
    graph_entry: dict,
    verified: dict | None,
) -> list[dict]:
    """Ordered spine-ready steps — runtime sequencing only."""
    path_verified = (verified or {}).get("execution_path_verified") or []
    source = execution_path
    if path_verified and not execution_path:
        source = [
            {"step": p.get("step"), "tool_id": p.get("tool_id"), "title": p.get("tool_id")}
            for p in path_verified
        ]

    completed: list[str] = []
    chain: list[dict] = []
    for idx, step in enumerate(source, start=1):
        tool_id = step.get("tool_id") or ""
        if not tool_id:
            continue
        deps_ok = dependencies_satisfied(tool_id, completed=completed, graph_entry=graph_entry)
        status = "ready" if deps_ok and tool_id not in completed else "pending"
        if not deps_ok:
            status = "blocked"
        chain.append(
            {
                "order": step.get("step") or idx,
                "tool_id": tool_id,
                "title": step.get("title") or tool_id,
                "status": status,
                "requires": step.get("requires") or [],
            }
        )
        if status == "ready":
            completed.append(tool_id)

    return chain


def spine_sequence_from_chain(chain: list[dict]) -> dict:
    action_ids = [s["tool_id"] for s in chain if s.get("tool_id")]
    blocked = any(s.get("status") == "blocked" for s in chain)
    return {
        "action_ids": action_ids,
        "step_count": len(action_ids),
        "dispatch_ready": False,
        "blocked": blocked,
        "instruction": {
            "action": "founder_confirm_then_enqueue_spine",
            "note": "Planner emits spine-ready sequence only — does not execute",
        },
    }
