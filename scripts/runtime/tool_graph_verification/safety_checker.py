"""Rule and constraint validation using planner + context (read-only)."""
from __future__ import annotations


def check_safety(
    *,
    execution_path: list[dict],
    planner: dict,
    context: dict,
) -> dict:
    path_tools = [step.get("tool_id") for step in execution_path if step.get("tool_id")]
    violations: list[str] = []
    warnings: list[str] = []

    avoid = set((planner.get("recommendation") or {}).get("avoid_actions") or [])
    for tool_id in path_tools:
        if tool_id in avoid:
            violations.append(f"tool_in_planner_avoid_list:{tool_id}")

    signals_avoid = set()
    for row in (context.get("behavior_state") or {}).get("behavioral_risks") or []:
        if row.get("kind") == "signal" and row.get("signal_type") == "avoid":
            act = row.get("action_id")
            if act:
                signals_avoid.add(act)
    for tool_id in path_tools:
        if tool_id in signals_avoid:
            warnings.append(f"tool_has_avoid_signal:{tool_id}")

    system_health = float((context.get("system_state") or {}).get("system_health") or 1.0)
    if system_health < 0.5 and "pos-execute" in path_tools:
        warnings.append("low_system_health_with_bulk_execute")

    constraints = [
        "Auto-paste into Cursor blocked by default (incident law)",
        "Execution spine SSOT: execution_memory.jsonl",
    ]
    repo_prog = (context.get("repo_state") or {}).get("progress_summary") or {}
    locks = repo_prog.get("locks") or {}
    if locks.get("p0_thread"):
        warnings.append(f"p0_thread_locked:{locks['p0_thread']}")

    score = 1.0
    if violations:
        score -= min(0.6, 0.25 * len(violations))
    if warnings:
        score -= min(0.3, 0.08 * len(warnings))

    return {
        "safety_score": round(max(0.0, score), 3),
        "violations": violations,
        "warnings": warnings,
        "active_constraints_acknowledged": constraints,
        "safe_to_execute": not violations,
    }
