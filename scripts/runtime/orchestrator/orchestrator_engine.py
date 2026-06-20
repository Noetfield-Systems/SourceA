"""Coordinate C1→C7 runtime pipeline — founder confirm preserved."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.context_fabric.fabric_engine import build_context_fabric
from runtime.execution_router.router_engine import DEFAULT_GOAL, route_execution
from runtime.multi_step_planner.planner_engine import plan_multi_step_execution
from runtime.orchestrator.orchestrator_store import ORCHESTRATOR_SSOT_PATH, load_snapshot, write_snapshot
from runtime.repair_loop.repair_engine import run_repair_loop
from runtime.dispatch_policy.allowlist import infer_task_class
from runtime.dispatch_policy.policy_engine import current_eval_tier, evaluate, orchestrator_dispatch_ready
from runtime.tool_graph.api import build_tool_graph
from runtime.tool_graph_verification.validation_engine import verify_tool_graph

SCHEMA = "runtime-orchestrator-v1"
PIPELINE_STAGES = (
    ("C1", "tool_graph"),
    ("C2", "tool_graph_verify"),
    ("C3", "execution_router"),
    ("C4", "repair_loop"),
    ("C5", "context_fabric"),
    ("C6", "multi_step_planner"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _contract_verified(entry: dict) -> dict:
    violations: list[str] = []
    violations.extend(entry.get("safety_violations") or [])
    violations.extend(entry.get("forward_violations") or [])
    if entry.get("cycle_detected"):
        violations.append("cycle_detected")
    return {
        "recommendation": entry.get("recommendation") or "reject",
        "plan_score": float(entry.get("plan_score") or 0.0),
        "has_cycles": bool(entry.get("cycle_detected")),
        "violations": violations,
    }


def _contract_router(entry: dict) -> dict:
    breakdown = entry.get("score_breakdown") or {}
    confidence = 0.0
    if breakdown:
        confidence = sum(float(v or 0) for v in breakdown.values()) / max(len(breakdown), 1)
    return {
        "routing_decision": entry.get("routing_decision") or "block",
        "confidence": confidence,
        "blocking_reason": entry.get("reason"),
    }


def _instruction_from_decision(decision: dict, *, orchestrator_ready: bool = False) -> dict:
    """Hub instruction — activation gates (orchestrator_ready) override task-class simulation."""
    blockers = list(decision.get("blocking_conditions") or [])
    if orchestrator_ready:
        tier_note = (
            f"CONFIRM tier — {decision.get('task_class')}"
            if decision.get("requires_founder_confirm")
            else "dispatch_ready active — founder spine Action to enqueue"
        )
        return {
            "action": "founder_confirm_then_enqueue_spine",
            "note": tier_note,
            "blocking_conditions": [],
            "founder_spine_action_required": bool(decision.get("requires_founder_confirm")),
        }
    if not blockers:
        blockers = ["dispatch_ready blocked — see dispatch_ready_blockers on hub"]
    if not decision.get("dispatch_ready"):
        return {
            "action": "dispatch_blocked",
            "note": decision.get("reason", "dispatch blocked"),
            "blocking_conditions": blockers,
            "founder_spine_action_required": True,
        }
    tier_note = f"CONFIRM tier — {decision.get('task_class')}" if decision.get("requires_founder_confirm") else (
        "task-class simulation eligible — founder spine Action still required"
    )
    return {
        "action": "founder_confirm_required",
        "note": tier_note,
        "blocking_conditions": blockers,
        "founder_spine_action_required": True,
    }


def run_runtime_orchestration(
    *,
    goal_tool_id: str = DEFAULT_GOAL,
    task_id: str = "",
) -> dict:
    task_id = task_id or f"orchestrate:{goal_tool_id}"
    pipeline: list[dict] = []
    stage_outputs: dict[str, dict] = {}

    for step_id, name in PIPELINE_STAGES:
        if name == "tool_graph":
            out = build_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=True)
        elif name == "tool_graph_verify":
            out = verify_tool_graph(goal_tool_id=goal_tool_id, task_id=task_id, force=True)
        elif name == "execution_router":
            out = route_execution(goal_tool_id=goal_tool_id, task_id=task_id, force_refresh=True)
        elif name == "repair_loop":
            out = run_repair_loop(goal_tool_id=goal_tool_id, task_id=task_id, force_refresh=True)
        elif name == "context_fabric":
            out = build_context_fabric(task_id=task_id)
        else:
            out = plan_multi_step_execution(goal_tool_id=goal_tool_id, task_id=task_id, force_refresh=True)

        ok = bool(out.get("ok")) if isinstance(out, dict) else False
        pipeline.append({"step": step_id, "stage": name, "ok": ok, "schema": (out or {}).get("schema", "")})
        stage_outputs[name] = out if isinstance(out, dict) else {}

        if not ok and name in ("tool_graph", "tool_graph_verify"):
            break

    verified = stage_outputs.get("tool_graph_verify") or {}
    router = stage_outputs.get("execution_router") or {}
    planner = stage_outputs.get("multi_step_planner") or {}
    repair = stage_outputs.get("repair_loop") or {}

    spine = planner.get("spine_sequence") or {}
    action_ids = list(spine.get("action_ids") or [])
    first_action = action_ids[0] if action_ids else ""
    task_class = infer_task_class(first_action)

    dispatch_decision = evaluate(
        verified_graph=_contract_verified(verified),
        router=_contract_router(router),
        eval_tier=current_eval_tier(),
        task_class=task_class,
        dry_run=True,
    )
    orch_ready, orch_blockers, _orch_meta = orchestrator_dispatch_ready()
    dispatch_decision = {**dispatch_decision, "dry_run": True}

    routing_decision = router.get("routing_decision") or "unknown"
    plan_status = planner.get("plan_status") or "unknown"
    failure_class = repair.get("failure_class") or "unknown"

    if routing_decision == "allow" and plan_status == "ready":
        overall = "ready"
    elif routing_decision in ("block", "wait") or plan_status == "needs_review":
        overall = "needs_review"
    else:
        overall = "partial"

    result = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(ORCHESTRATOR_SSOT_PATH),
        "task_id": task_id,
        "goal_tool_id": goal_tool_id,
        "runtime_stack_complete": True,
        "pipeline": pipeline,
        "overall_status": overall,
        "dispatch_ready": orch_ready,
        "dispatch_ready_blockers": orch_blockers,
        "founder_confirm_required": True,
        "task_class": task_class,
        "dispatch_decision": dispatch_decision,
        "routing_decision": routing_decision,
        "plan_status": plan_status,
        "failure_class": failure_class,
        "spine_handoff": spine,
        "instruction": _instruction_from_decision(dispatch_decision, orchestrator_ready=orch_ready),
        "artifacts": {
            "tool_graph": "~/.sina/tool_graph_v1.json",
            "tool_graph_verified": "~/.sina/tool_graph_verified_v1.json",
            "execution_router": "~/.sina/execution_router_v1.json",
            "repair_loop": "~/.sina/repair_loop_v1.json",
            "context_fabric": "~/.sina/semantic_context_fabric_v1.json",
            "multi_step_planner": "~/.sina/multi_step_planner_v1.json",
        },
    }

    _persist(task_id, result)
    return result


def _persist(task_id: str, result: dict) -> None:
    snap = load_snapshot() if ORCHESTRATOR_SSOT_PATH.is_file() else {"runs": {}}
    snap["schema"] = SCHEMA
    snap["generated_at"] = result.get("generated_at")
    snap["path"] = str(ORCHESTRATOR_SSOT_PATH)
    snap["latest"] = result
    snap.setdefault("runs", {})[task_id] = result
    write_snapshot(snap)
