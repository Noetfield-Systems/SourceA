"""Classify spine actions into dispatch policy tiers."""
from __future__ import annotations

# Canonical low-risk action_ids — must match allowlist.ACTION_TO_TASK_CLASS (DISPATCH_POLICY_LOCKED §Phase 2a)
LOW_RISK_ACTIONS = frozenset(
    {
        "spine-smoke-echo",
        "validate-eval-packet-v1",
        "validate-eval-packet-v1b",
        "validate-gate-receipts-v1",
    }
)
LOW_RISK_TASK_CLASS: dict[str, str] = {
    "spine-smoke-echo": "validate-only",
    "validate-eval-packet-v1": "validate-only",
    "validate-eval-packet-v1b": "validate-only",
    "validate-gate-receipts-v1": "validate-only",
}
OBSERVE_PREFIXES = ("audit-", "validate-", "read-")
SUGGEST_PREFIXES = ("pos-", "plan-", "repair-")


def cross_check_classifier_task_ids() -> list[str]:
    """Cross-check Layer-1 action_ids vs Layer-2 task_class registry."""
    from runtime.dispatch_policy.allowlist import (  # noqa: WPS433
        ACTION_TO_TASK_CLASS,
        TASK_CLASS_REGISTRY,
        infer_task_class,
    )

    errors: list[str] = []
    if set(LOW_RISK_TASK_CLASS) != set(LOW_RISK_ACTIONS):
        errors.append(
            f"LOW_RISK_TASK_CLASS keys {sorted(LOW_RISK_TASK_CLASS)} != "
            f"LOW_RISK_ACTIONS {sorted(LOW_RISK_ACTIONS)}"
        )
    for action_id in sorted(LOW_RISK_ACTIONS):
        if classify_action(action_id) != "auto_low_risk":
            errors.append(f"{action_id}: classifier must be auto_low_risk")
        exp_task = LOW_RISK_TASK_CLASS.get(action_id)
        got_task = infer_task_class(action_id)
        if exp_task and got_task != exp_task:
            errors.append(f"{action_id}: infer_task_class={got_task} expected {exp_task}")
        if ACTION_TO_TASK_CLASS.get(action_id) != exp_task:
            errors.append(
                f"{action_id}: ACTION_TO_TASK_CLASS={ACTION_TO_TASK_CLASS.get(action_id)!r} "
                f"expected {exp_task!r}"
            )
        tier = TASK_CLASS_REGISTRY.get(got_task or "")
        if tier != "SAFE_AUTO":
            errors.append(f"{action_id}: tier={tier!r} expected SAFE_AUTO")
    return errors


def classify_action(action_id: str) -> str:
    aid = (action_id or "").strip()
    if aid in LOW_RISK_ACTIONS:
        return "auto_low_risk"
    if any(aid.startswith(p) for p in OBSERVE_PREFIXES):
        return "observe"
    if any(aid.startswith(p) for p in SUGGEST_PREFIXES):
        return "suggest"
    return "suggest"
