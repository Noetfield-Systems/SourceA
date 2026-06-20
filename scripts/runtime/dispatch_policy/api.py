"""Hub API — /api/dispatch-policy-v1"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.dispatch_policy.policy_engine import (
    current_eval_tier,
    dispatch_policy_payload,
    evaluate,
)
from runtime.dispatch_policy.store import record_decision
from runtime.execution_router.router_store import ROUTER_SSOT_PATH, load_json as load_router_json
from runtime.tool_graph_verification.verify_store import VERIFIED_PATH, load_json as load_verified_json

STATE_DIR = Path.home() / ".sina"


def _latest_verified_entry() -> dict:
    store = load_verified_json(VERIFIED_PATH)
    latest = store.get("latest") or {}
    if latest:
        return latest
    verifications = store.get("verifications") or {}
    if verifications:
        return next(iter(verifications.values()))
    return {}


def _latest_router_entry() -> dict:
    store = load_router_json(ROUTER_SSOT_PATH)
    latest = store.get("latest") or {}
    if latest:
        return latest
    routes = store.get("routes") or {}
    if routes:
        return next(iter(routes.values()))
    return {}


def _contract_verified_graph(entry: dict | None = None) -> dict:
    row = entry or _latest_verified_entry()
    violations: list[str] = []
    violations.extend(row.get("safety_violations") or [])
    violations.extend(row.get("forward_violations") or [])
    if row.get("cycle_detected"):
        violations.append("cycle_detected")
    return {
        "recommendation": row.get("recommendation") or "reject",
        "plan_score": float(row.get("plan_score") or 0.0),
        "has_cycles": bool(row.get("cycle_detected")),
        "violations": violations,
    }


def _contract_router(entry: dict | None = None) -> dict:
    row = entry or _latest_router_entry()
    breakdown = row.get("score_breakdown") or {}
    confidence = 0.0
    if breakdown:
        confidence = sum(float(v or 0) for v in breakdown.values()) / max(len(breakdown), 1)
    return {
        "routing_decision": row.get("routing_decision") or "block",
        "confidence": confidence,
        "blocking_reason": row.get("reason"),
    }


def _wrap_decision(
    *,
    decision: dict[str, Any],
    eval_tier: str,
    task_class: str,
    dry_run: bool,
) -> dict[str, Any]:
    """Hub task-class wrapper — top-level dispatch_ready mirrors orchestrator SSOT (v1.1)."""
    from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready_payload  # noqa: WPS433

    orch = orchestrator_dispatch_ready_payload()
    return {
        "ok": True,
        "schema": "dispatch-policy-api-v1",
        "dispatch_ready": bool(orch.get("dispatch_ready")),
        "dispatch_ready_blockers": list(orch.get("dispatch_ready_blockers") or []),
        "task_class": task_class,
        "eval_tier": eval_tier,
        "dry_run": dry_run,
        "decision": decision,
        "founder_law_note": "top-level dispatch_ready mirrors orchestrator — decision is task-class simulation",
        "api": "/api/dispatch-policy-v1",
    }


def dispatch_policy_v1_get(
    *,
    task_class: str = "",
    eval_tier: str = "",
    dry_run: bool = True,
    founder_override: bool = False,
) -> dict[str, Any]:
    if not task_class:
        return dispatch_policy_payload()

    tier = (eval_tier or current_eval_tier()).strip()
    verified = _contract_verified_graph()
    router = _contract_router()
    decision = evaluate(
        verified_graph=verified,
        router=router,
        eval_tier=tier,
        task_class=task_class,
        founder_override=founder_override,
        dry_run=dry_run,
    )
    record_decision(decision=decision, eval_tier=tier)
    return _wrap_decision(
        decision=decision,
        eval_tier=tier,
        task_class=task_class,
        dry_run=dry_run,
    )


def dispatch_policy_v1_post(body: dict | None) -> dict[str, Any]:
    row = body or {}
    task_class = str(row.get("task_class") or "").strip()
    if not task_class:
        return {"ok": False, "error": "task_class required"}

    tier = str(row.get("eval_tier") or current_eval_tier()).strip()
    if row.get("verified_graph"):
        verified = dict(row["verified_graph"])
    else:
        verified = _contract_verified_graph()
    if row.get("router"):
        router = dict(row["router"])
    else:
        router = _contract_router()

    dry_run = bool(row.get("dry_run", False))
    founder_override = bool(row.get("founder_override", False))
    decision = evaluate(
        verified_graph=verified,
        router=router,
        eval_tier=tier,
        task_class=task_class,
        founder_override=founder_override,
        dry_run=dry_run,
    )
    record_decision(decision=decision, eval_tier=tier)
    return _wrap_decision(
        decision=decision,
        eval_tier=tier,
        task_class=task_class,
        dry_run=dry_run,
    )
