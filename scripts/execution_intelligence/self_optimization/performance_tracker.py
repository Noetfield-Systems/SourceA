"""Track per-action performance from historical evidence (read-only)."""
from __future__ import annotations

from collections import defaultdict

from execution_intelligence.pattern_engine.helpers import action_from_pattern


def _action_from_decision(decision: dict) -> str:
    if decision.get("action_id"):
        return str(decision["action_id"])
    why = decision.get("why_summary") or ""
    if why.startswith("'") and "'" in why[1:]:
        return why[1 : why.index("'", 1)]
    return ""


def _discover_actions(memory: list[dict], patterns: list[dict], decisions: list[dict], signals: list[dict]) -> list[str]:
    actions: set[str] = set()
    for rec in memory:
        if rec.get("action_id"):
            actions.add(str(rec["action_id"]))
    for pattern in patterns:
        act = action_from_pattern(pattern)
        if act:
            actions.add(act)
    for decision in decisions:
        act = _action_from_decision(decision)
        if act:
            actions.add(act)
    for signal in signals:
        if signal.get("action_id"):
            actions.add(str(signal["action_id"]))
    return sorted(actions)


def track_performance(
    *,
    memory: list[dict],
    patterns: list[dict],
    decisions: list[dict],
    signals: list[dict],
    planner: dict,
) -> list[dict]:
    actions = _discover_actions(memory, patterns, decisions, signals)
    runs: dict[str, list[dict]] = defaultdict(list)
    for rec in memory:
        act = rec.get("action_id") or "unknown"
        runs[act].append(rec)

    fix_by_action: dict[str, int] = defaultdict(int)
    fail_by_action: dict[str, int] = defaultdict(int)
    decision_conf: dict[str, list[float]] = defaultdict(list)
    for decision in decisions:
        act = _action_from_decision(decision)
        if not act:
            continue
        decision_conf[act].append(float(decision.get("confidence") or 0))
        if decision.get("cause_type") == "fix_cause":
            fix_by_action[act] += 1
        if decision.get("cause_type") == "failure_cause":
            fail_by_action[act] += 1

    planner_rank = {
        row.get("action_id"): float(row.get("score") or 0)
        for row in (planner.get("recommendation") or {}).get("ranked_actions") or []
    }

    metrics: list[dict] = []
    for action_id in actions:
        action_runs = runs.get(action_id, [])
        total = len(action_runs)
        successes = sum(1 for r in action_runs if r.get("status") == "success")
        failures = total - successes
        success_rate = round(successes / total, 3) if total else 0.0
        failure_rate = round(failures / total, 3) if total else 0.0

        statuses = [r.get("status") for r in action_runs]
        stability = 1.0
        if len(statuses) > 1:
            changes = sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i - 1])
            stability = round(1.0 - changes / (len(statuses) - 1), 3)

        recovery_denom = fail_by_action.get(action_id, 0) + failures
        recovery_rate = round(fix_by_action.get(action_id, 0) / max(recovery_denom, 1), 3)

        confs = decision_conf.get(action_id, [])
        decision_quality = round(sum(confs) / len(confs), 3) if confs else 0.0
        planner_quality = round(min(1.0, planner_rank.get(action_id, 0) / 120), 3) if planner_rank else 0.0

        metrics.append(
            {
                "action_id": action_id,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
                "recovery_rate": recovery_rate,
                "stability_score": stability,
                "decision_quality": decision_quality,
                "planner_quality": planner_quality,
                "run_count": total,
            }
        )

    metrics.sort(key=lambda m: (-m["success_rate"], -m["stability_score"], m["action_id"]))
    return metrics
