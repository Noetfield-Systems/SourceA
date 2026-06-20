"""Bridge multi_step_planner spine_sequence → policy-classified handoff."""
from __future__ import annotations

from runtime.dispatch_policy.classifier import classify_action
from runtime.dispatch_policy.policy_engine import (
    eval_1b_gate_status,
    founder_spine_bridge_gate_status,
    orchestrator_dispatch_ready,
)
from runtime.multi_step_planner.planner_store import PLANNER_SSOT_PATH, load_planner_snapshot


def _branch_spec(action_id: str) -> dict | None:
    try:
        from sina_command_lib import _branch_action_index  # noqa: WPS433

        spec = _branch_action_index().get(action_id)
        if spec:
            return dict(spec)
    except Exception:
        pass
    return None


def _default_spine_spec(action_id: str) -> dict | None:
    branch = _branch_spec(action_id)
    if branch:
        return branch
    if action_id == "spine-smoke-echo":
        return {
            "kind": "shell",
            "argv": ["echo", "spine-bridge-ok"],
            "cwd": "~",
            "timeout": 30,
        }
    return None


def build_spine_bridge(*, goal_tool_id: str = "pos-run", task_id: str = "") -> dict:
    snap = load_planner_snapshot() or {}
    plans = snap.get("plans") or {}
    plan = None
    if task_id and task_id in plans:
        plan = plans[task_id]
    elif snap.get("latest"):
        plan = snap["latest"]
    elif plans:
        plan = next(iter(plans.values()))

    if not plan:
        return {
            "ok": False,
            "error": "no planner snapshot — run runtime orchestrator first",
            "planner_path": str(PLANNER_SSOT_PATH),
        }

    spine = plan.get("spine_sequence") or {}
    action_ids = list(spine.get("action_ids") or [])
    first = action_ids[0] if action_ids else ""
    policy_class = classify_action(first) if first else "observe"
    eval_live_ok, eval_live_note = eval_1b_gate_status()
    founder_gate_ok, founder_gate_note = founder_spine_bridge_gate_status()
    planner_bridge_ready = bool(
        first
        and not spine.get("blocked")
        and plan.get("plan_status") == "ready"
        and policy_class in ("auto_low_risk", "suggest")
        and founder_gate_ok
        and _default_spine_spec(first)
    )
    planner_auto_bridge_ready = planner_bridge_ready and policy_class == "auto_low_risk"
    bridge_ready = planner_auto_bridge_ready
    spec = _default_spine_spec(first) if first else None
    eval_proof_action = "spine-smoke-echo"
    eval_proof_class = classify_action(eval_proof_action)
    eval_proof_ready = bool(founder_gate_ok and eval_proof_class == "auto_low_risk")
    orch_ready, orch_blockers, _ = orchestrator_dispatch_ready()
    auto_dispatch = False
    if policy_class == "suggest":
        instruction_action = "founder_confirm_required"
    elif bridge_ready or eval_proof_ready:
        instruction_action = "founder_confirm_then_enqueue_spine"
    else:
        instruction_action = "blocked_or_review"
    eval_proof = {
        "action_id": eval_proof_action,
        "policy_class": eval_proof_class,
        "spine_bridge_ready": eval_proof_ready,
        "enqueue_spec": _default_spine_spec(eval_proof_action),
        "note": "Eval-1b live pass unlocks low-risk spine proof — founder confirm still required",
    }
    return {
        "ok": True,
        "goal_tool_id": plan.get("goal_tool_id") or goal_tool_id,
        "task_id": plan.get("task_id") or task_id,
        "plan_status": plan.get("plan_status"),
        "spine_sequence": spine,
        "first_action_id": first,
        "policy_class": policy_class,
        "eval_1b_gate_ok": eval_live_ok,
        "eval_1b_note": eval_live_note,
        "founder_spine_bridge_gate_ok": founder_gate_ok,
        "founder_spine_bridge_note": founder_gate_note,
        "planner_bridge_ready": planner_bridge_ready,
        "planner_bridge_note": (
            "pos-dispatch chain mapped via branches_registry — founder confirm required"
            if first and policy_class == "suggest"
            else ""
        ),
        "planner_auto_bridge_ready": planner_auto_bridge_ready,
        "spine_bridge_ready": bridge_ready or eval_proof_ready,
        "eval_proof_bridge": eval_proof,
        "branch_spec": _default_spine_spec(first) if first else None,
        "dispatch_ready": False,
        "orchestrator_dispatch_ready": orch_ready,
        "orchestrator_dispatch_ready": orch_ready,
        "dispatch_ready_blockers": orch_blockers,
        "auto_dispatch": auto_dispatch,
        "founder_confirm_required": True,
        "enqueue_spec": spec or eval_proof.get("enqueue_spec"),
        "instruction": {
            "action": instruction_action,
            "note": "Bridge classifies C7 output — eval proof via spine-smoke-echo when gate open",
        },
    }
