"""Classify runtime failures from router, verification, memory, and decisions."""
from __future__ import annotations

from runtime.repair_loop.repair_loop_store import load_jsonl, INPUT_PATHS


FAILURE_CLASSES = (
    "healthy",
    "router_block",
    "router_wait",
    "verification_reject",
    "verification_needs_fix",
    "execution_failure",
    "policy_block",
    "unknown",
)


def _recent_failures(*, limit: int = 20) -> list[dict]:
    memory = load_jsonl(INPUT_PATHS["memory"], limit=limit * 3)
    return [r for r in memory if r.get("status") != "success"][-limit:]


def _related_decisions(*, task_id: str, action_id: str) -> list[dict]:
    decisions = load_jsonl(INPUT_PATHS["decisions"], limit=300)
    out = []
    for d in decisions:
        if task_id and d.get("task_id") == task_id:
            out.append(d)
        elif action_id and d.get("action_id") == action_id:
            out.append(d)
    return out[-10:]


def classify_failure(
    *,
    route: dict,
    verified: dict | None,
    task_id: str,
) -> dict:
    """Return failure_class + evidence — recovery graph is separate."""
    routing = route.get("routing_decision") or ""
    next_status = (route.get("next_step") or {}).get("status") or ""
    tool_id = (route.get("next_step") or {}).get("tool_id") or ""
    reason = route.get("reason") or ""

    recent_fails = _recent_failures()
    last_fail = recent_fails[-1] if recent_fails else {}
    fail_action = last_fail.get("action_id") or tool_id
    decisions = _related_decisions(task_id=task_id, action_id=fail_action)

    if routing == "allow" and next_status in ("ready", "complete") and not recent_fails:
        return {
            "failure_class": "healthy",
            "severity": "none",
            "summary": "No active failure — router path is healthy",
            "evidence": {"routing_decision": routing, "next_status": next_status},
            "links": {"decision_ids": [d.get("decision_id") for d in decisions if d.get("decision_id")]},
        }

    failure_class = "unknown"
    severity = "medium"

    if verified and verified.get("recommendation") == "reject":
        failure_class = "verification_reject"
        severity = "high"
    elif verified and verified.get("recommendation") == "needs_fix":
        failure_class = "verification_needs_fix"
        severity = "high"
    elif verified and verified.get("cycle_detected"):
        failure_class = "verification_reject"
        severity = "high"
        reason = reason or "cycle detected in verified graph"
    elif routing == "block":
        failure_class = "router_block"
        severity = "high"
    elif routing == "wait":
        failure_class = "router_wait"
        severity = "medium"
    elif "policy" in reason.lower() or "no policy-approved" in reason.lower():
        failure_class = "policy_block"
        severity = "medium"
    elif recent_fails:
        failure_class = "execution_failure"
        severity = "high"
        reason = reason or (last_fail.get("error_signature") or last_fail.get("status") or "execution failed")

    fix_decisions = [d for d in decisions if d.get("cause_type") == "fix_cause"]

    return {
        "failure_class": failure_class,
        "severity": severity,
        "summary": reason or f"classified as {failure_class}",
        "evidence": {
            "routing_decision": routing,
            "next_status": next_status,
            "tool_id": tool_id,
            "verification_recommendation": (verified or {}).get("recommendation"),
            "last_failure_action": fail_action,
            "last_failure_task": last_fail.get("task_id"),
        },
        "links": {
            "decision_ids": [d.get("decision_id") for d in fix_decisions if d.get("decision_id")],
            "pattern_ids": list({d.get("pattern_id") for d in decisions if d.get("pattern_id")}),
        },
    }
