"""Policy gates for D11 tool selection — pre-LLM advisory, not C3 execute."""
from __future__ import annotations

from typing import Any

_EXECUTE_BLOCKED_PRE_GATE = frozenset({"spine_queue"})
_WRITE_REQUIRES_PLAN = frozenset({"hub_build", "hub_refresh"})


def evaluate_tool_policy(
    *,
    capability: dict[str, Any],
    plan_node: dict[str, Any],
    goal_class: str,
    gate_mode: str = "shadow",
) -> dict[str, Any]:
    cap_id = capability.get("capability_id") or ""
    permission = capability.get("permission") or "read"
    cost = int(capability.get("cost") or 1)

    allowed = True
    policy_gate = "pass"
    reasons: list[str] = []

    if permission == "execute":
        if cap_id in _EXECUTE_BLOCKED_PRE_GATE:
            allowed = False
            policy_gate = "blocked_pre_llm"
            reasons.append("execute_blocked_until_D15_gate")
        else:
            policy_gate = "advisory_only"
            reasons.append("execute_advisory_pre_assembly")

    if cap_id in _WRITE_REQUIRES_PLAN and plan_node.get("kind") not in ("execute", "validate", "ship"):
        allowed = False
        policy_gate = "plan_step_mismatch"
        reasons.append("write_requires_execute_or_validate_step")

    if goal_class == "audit" and permission == "execute":
        allowed = False
        policy_gate = "audit_read_only"
        reasons.append("audit_lane_no_execute")

    if cost >= 8 and gate_mode == "shadow":
        policy_gate = "high_cost_shadow_ok"
        reasons.append("high_cost_logged_in_shadow")

    return {
        "allowed": allowed,
        "policy_gate": policy_gate,
        "permission": permission,
        "cost_estimate": cost,
        "reasons": reasons,
    }
