"""Build recovery suggestion paths from tool graph + B-layer signals (recovery graph only)."""
from __future__ import annotations

from execution_intelligence.decision_memory.api import read_decisions
from execution_intelligence.decision_memory.fix_linker import link_fixes
from execution_intelligence.feedback_loop.loop_engine import read_signals
from execution_intelligence.pattern_engine.api import load_patterns_v1
from execution_intelligence.reader import read_execution_memory
from runtime.repair_loop.repair_loop_store import load_json, INPUT_PATHS


def _graph_tools(*, goal_tool_id: str, task_id: str) -> list[str]:
    store = load_json(INPUT_PATHS["graph"])
    key = f"{goal_tool_id}:{task_id}"
    entry = (store.get("graphs") or {}).get(key) or store.get("latest") or {}
    path = entry.get("execution_path") or []
    return [p.get("tool_id") for p in path if p.get("tool_id")]


def _prefer_actions() -> list[str]:
    signals = read_signals(limit=100)
    return [s.get("action_id") for s in signals if s.get("signal_type") == "prefer" and s.get("action_id")]


def build_recovery_suggestions(
    *,
    failure: dict,
    route: dict,
    goal_tool_id: str,
    task_id: str,
) -> list[dict]:
    """Recovery paths — suggestions only; dispatch_ready always false at repair layer."""
    failure_class = failure.get("failure_class") or "unknown"
    if failure_class == "healthy":
        return []

    suggestions: list[dict] = []
    tool_id = (route.get("next_step") or {}).get("tool_id") or ""
    path_tools = _graph_tools(goal_tool_id=goal_tool_id, task_id=task_id)

    if failure_class in ("verification_reject", "verification_needs_fix", "router_block", "router_wait"):
        suggestions.append(
            {
                "path_id": "reverify_execution_graph",
                "title": "Rebuild and re-verify tool graph",
                "steps": [
                    {"order": 1, "action": "rebuild_tool_graph", "tool_id": goal_tool_id},
                    {"order": 2, "action": "verify_tool_graph", "tool_id": goal_tool_id},
                    {"order": 3, "action": "reroute", "tool_id": goal_tool_id},
                ],
                "confidence": 0.75,
                "rationale": "Verification or router gate failed — refresh graph substrate",
            }
        )

    records = read_execution_memory()
    patterns = load_patterns_v1()
    fix_links = link_fixes(patterns, records)
    for link in fix_links:
        if tool_id and link.get("action_id") != tool_id:
            continue
        suggestions.append(
            {
                "path_id": f"known_fix:{link.get('action_id') or 'action'}",
                "title": "Apply known fix pattern from decision memory",
                "steps": [
                    {"order": 1, "action": "review_fix_pattern", "tool_id": link.get("action_id")},
                    {"order": 2, "action": "founder_confirm_retry", "tool_id": link.get("action_id")},
                ],
                "confidence": float(link.get("confidence") or 0.6),
                "rationale": link.get("recovery_signal") or "historical fix link",
                "links": {"pattern_id": link.get("pattern_id")},
            }
        )

    fix_decisions = [d for d in read_decisions(limit=50) if d.get("cause_type") == "fix_cause"]
    if fix_decisions and failure_class == "execution_failure":
        d0 = fix_decisions[-1]
        suggestions.append(
            {
                "path_id": "decision_memory_retry",
                "title": "Retry after fix cause (WHY layer)",
                "steps": [
                    {"order": 1, "action": "apply_fix_hint", "tool_id": d0.get("action_id") or tool_id},
                    {"order": 2, "action": "founder_confirm_retry", "tool_id": d0.get("action_id") or tool_id},
                ],
                "confidence": float(d0.get("confidence") or 0.55),
                "rationale": d0.get("why_summary") or "fix_cause decision",
                "links": {"decision_id": d0.get("decision_id")},
            }
        )

    prefer = _prefer_actions()
    for pref in prefer[:3]:
        if pref in path_tools or not path_tools:
            suggestions.append(
                {
                    "path_id": f"feedback_prefer:{pref}",
                    "title": "Feedback loop preferred action",
                    "steps": [
                        {"order": 1, "action": "select_preferred_tool", "tool_id": pref},
                        {"order": 2, "action": "founder_confirm_dispatch", "tool_id": pref},
                    ],
                    "confidence": 0.5,
                    "rationale": "B3 feedback prefer signal",
                }
            )

    if failure_class == "policy_block":
        suggestions.append(
            {
                "path_id": "manual_founder_review",
                "title": "Manual policy review",
                "steps": [
                    {"order": 1, "action": "review_planner_context"},
                    {"order": 2, "action": "adjust_avoid_list"},
                    {"order": 3, "action": "founder_confirm_dispatch", "tool_id": tool_id or goal_tool_id},
                ],
                "confidence": 0.45,
                "rationale": "Policy engine blocked candidates — founder adjusts constraints",
            }
        )

    if not suggestions:
        suggestions.append(
            {
                "path_id": "founder_manual_recovery",
                "title": "Founder-led recovery",
                "steps": [
                    {"order": 1, "action": "inspect_router_state"},
                    {"order": 2, "action": "founder_confirm_dispatch", "tool_id": tool_id or goal_tool_id},
                ],
                "confidence": 0.35,
                "rationale": "No automated recovery path matched",
            }
        )

    # Dedupe by path_id, keep highest confidence
    seen: dict[str, dict] = {}
    for s in suggestions:
        pid = s["path_id"]
        if pid not in seen or s.get("confidence", 0) > seen[pid].get("confidence", 0):
            seen[pid] = s
    ranked = sorted(seen.values(), key=lambda x: x.get("confidence", 0), reverse=True)
    return ranked[:6]
