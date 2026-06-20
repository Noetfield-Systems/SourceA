"""Cross-check execution path against context_intelligence snapshot."""
from __future__ import annotations


def check_context_alignment(
    *,
    execution_path: list[dict],
    context: dict,
    planner: dict,
) -> dict:
    path_tools = [step.get("tool_id") for step in execution_path if step.get("tool_id")]
    issues: list[str] = []
    bonuses: list[str] = []

    planner_rec = (planner.get("recommendation") or {}).get("recommended_actions") or []
    planner_ranked = (planner.get("recommendation") or {}).get("ranked_actions") or []
    top_planner = planner_ranked[0].get("action_id") if planner_ranked else None

    behavior = context.get("behavior_state") or {}
    dominant = [p.get("action_id") for p in behavior.get("dominant_patterns") or [] if p.get("action_id")]
    habits = [h.get("action_id") for h in behavior.get("execution_habits") or [] if h.get("action_id")]

    critical = (context.get("repo_state") or {}).get("critical_paths") or []
    if critical and "pos-dispatch" in path_tools and path_tools[0] == "pos-dispatch":
        bonuses.append("aligns_with_critical_path_dispatch_first")

    overlap_rec = len([t for t in path_tools if t in planner_rec])
    if planner_rec and overlap_rec == 0:
        issues.append("no_overlap_with_planner_recommended_actions")
    elif overlap_rec:
        bonuses.append(f"planner_recommended_overlap_{overlap_rec}")

    if top_planner and top_planner in path_tools:
        bonuses.append(f"includes_planner_top_action_{top_planner}")

    habit_overlap = len([t for t in path_tools if t in habits[:3]])
    if habits and habit_overlap:
        bonuses.append(f"historical_habit_overlap_{habit_overlap}")

    dominant_overlap = len([t for t in path_tools if t in dominant[:3]])
    if dominant and dominant_overlap:
        bonuses.append(f"dominant_pattern_overlap_{dominant_overlap}")

    denom = max(len(path_tools), 1)
    alignment = (overlap_rec + habit_overlap + dominant_overlap) / (denom * 3)
    if bonuses:
        alignment = min(1.0, alignment + 0.15 * len(bonuses))
    if issues:
        alignment = max(0.0, alignment - 0.2 * len(issues))

    return {
        "context_alignment_score": round(min(1.0, alignment), 3),
        "issues": issues,
        "bonuses": bonuses,
        "planner_recommended": planner_rec,
        "path_tools": path_tools,
    }
