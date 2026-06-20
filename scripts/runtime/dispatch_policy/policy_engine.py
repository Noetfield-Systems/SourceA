"""Dispatch policy — auto-execution classes gated on Eval-1b live proof."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.dispatch_policy.allowlist import (
    ALLOWLIST,
    ALLOWLIST_VERSION,
    TASK_CLASS_REGISTRY,
    TIER_BEHAVIORAL,
    TIER_CONFIRM,
    TIER_SAFE_AUTO,
    infer_task_class,
)
from runtime.dispatch_policy.classifier import classify_action
from runtime.dispatch_policy.store import POLICY_SSOT_PATH, SCHEMA, load_policy, record_decision, write_policy

EVAL_1B_REPORT = Path.home() / ".sina" / "eval_packet_v1b_report.json"
DOC = "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md"
LIVE_THRESHOLD = 80
DECISION_SCHEMA = "dispatch-policy-v1"
VALID_EVAL_TIERS = frozenset({"none", "structural", "behavioral_pass", "behavioral_fail"})
LAW_LAYER1_CLASSES = frozenset({"observe", "suggest", "auto_low_risk"})
LAW_LAYER2_TIERS = frozenset({TIER_SAFE_AUTO, TIER_BEHAVIORAL, TIER_CONFIRM})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def founder_spine_bridge_gate_status() -> tuple[bool, str]:
    """Founder confirm enqueue — allows structural scaffold when live is blocked (402)."""
    live_ok, live_note = eval_1b_gate_status()
    if live_ok:
        return True, live_note
    mode_path = Path.home() / ".sina" / "eval_1b_ci_mode_v1.json"
    if mode_path.is_file():
        try:
            mode_row = json.loads(mode_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            mode_row = {}
        if mode_row.get("structural_fallback") and EVAL_1B_REPORT.is_file():
            try:
                rep = json.loads(EVAL_1B_REPORT.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                rep = {}
            pct = int(rep.get("packet_win_pct") or rep.get("scaffold_win_pct") or 0)
            if rep.get("mode") == "scaffold" and pct >= LIVE_THRESHOLD and rep.get("ok"):
                return (
                    True,
                    "structural founder bridge — live blocked; orchestrator dispatch_ready stays false until live pass",
                )
    return False, live_note


def eval_1b_gate_status() -> tuple[bool, str]:
    if not EVAL_1B_REPORT.is_file():
        return False, "eval_packet_v1b_report.json missing"
    try:
        rep = json.loads(EVAL_1B_REPORT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, str(exc)
    if rep.get("mode") != "live":
        return False, "Eval-1b scaffold only — run live A/B (validate-eval-packet-v1b-live.sh)"
    live_pct = rep.get("live_pilot_win_pct")
    if live_pct is None:
        live_pct = rep.get("packet_win_pct")
    if int(live_pct or 0) < LIVE_THRESHOLD:
        return False, f"Eval-1b live below threshold ({live_pct}%)"
    if not rep.get("live_ok", rep.get("ok")):
        return False, "Eval-1b live run failed"
    return True, "Eval-1b live pass"


def _critical_count() -> int:
    path = Path.home() / ".sina/find-bugs/last-run.json"
    if not path.is_file():
        return 0
    try:
        return int(json.loads(path.read_text(encoding="utf-8")).get("critical_count") or 0)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0


def orchestrator_dispatch_ready(*, include_critical: bool = True) -> tuple[bool, list[str], dict[str, Any]]:
    """Top-level hub/orchestrator dispatch_ready — DISPATCH_POLICY_LOCKED v1.1 activation gates."""
    import model_dispatch  # noqa: WPS433

    blockers: list[str] = []
    eval_ok, eval_note = eval_1b_gate_status()
    if not eval_ok:
        blockers.append(eval_note)
    gate_mode = model_dispatch.current_gate_mode()
    if gate_mode != "enforce":
        blockers.append(f"gate_mode={gate_mode!r} (requires enforce)")
    founder_ok, founder_note = founder_spine_bridge_gate_status()
    if not founder_ok:
        blockers.append(founder_note)
    tier = current_eval_tier()
    if tier != "behavioral_pass":
        blockers.append(f"eval_tier={tier!r} (requires behavioral_pass)")
    crit = _critical_count() if include_critical else 0
    if include_critical and crit > 0:
        blockers.append(f"critical_count={crit}")
    meta = {
        "eval_1b_gate_ok": eval_ok,
        "eval_1b_note": eval_note,
        "gate_mode": gate_mode,
        "gate_is_enforce": gate_mode == "enforce",
        "founder_spine_bridge_gate_ok": founder_ok,
        "founder_spine_bridge_note": founder_note,
        "eval_tier": tier,
        "critical_count": crit,
    }
    return (not blockers, blockers, meta)


def orchestrator_dispatch_ready_payload() -> dict[str, Any]:
    ready, blockers, meta = orchestrator_dispatch_ready()
    return {
        "dispatch_ready": ready,
        "dispatch_ready_blockers": blockers,
        **meta,
    }


def _build_classes(*, eval_ok: bool) -> list[dict[str, Any]]:
    low_risk_status = "eligible" if eval_ok else "blocked"
    return [
        {
            "id": "observe",
            "title": "Observe only",
            "auto_dispatch": False,
            "status": "active",
            "examples": ["read-only validators", "hub refresh", "audit scripts"],
        },
        {
            "id": "suggest",
            "title": "Suggest + human confirm",
            "auto_dispatch": False,
            "status": "active",
            "examples": ["planner chains", "repair suggestions", "C7 instruct-only"],
        },
        {
            "id": "auto_low_risk",
            "title": "Auto low-risk spine",
            "auto_dispatch": False,
            "status": low_risk_status,
            "gate": "eval_1b_live_pass",
            "examples": ["spine-smoke-echo", "validate-only scripts"],
        },
    ]


def _locked_doc_path() -> Path:
    root = Path(__file__).resolve().parents[3]
    locked = root / "brain-os" / "law" / "DISPATCH_POLICY_LOCKED_v1.md"
    if locked.is_file():
        return locked
    return root / "DISPATCH_POLICY_LOCKED_v1.md"


def cross_check_law_policy_classes() -> list[str]:
    """Cross-check DISPATCH_POLICY_LOCKED_v1.md Layer-1 classes vs _build_classes()."""
    errors: list[str] = []
    locked_path = _locked_doc_path()
    if not locked_path.is_file():
        return [f"LOCKED doc missing: {locked_path}"]
    locked_text = locked_path.read_text(encoding="utf-8")

    for class_id in sorted(LAW_LAYER1_CLASSES):
        if f"`{class_id}`" not in locked_text:
            errors.append(f"LOCKED doc missing class {class_id!r}")
    for tier in sorted(LAW_LAYER2_TIERS):
        if tier not in locked_text:
            errors.append(f"LOCKED doc missing tier {tier!r}")

    allowlist_tiers = {TIER_SAFE_AUTO, TIER_BEHAVIORAL, TIER_CONFIRM}
    if allowlist_tiers != LAW_LAYER2_TIERS:
        errors.append(
            f"allowlist tiers {sorted(allowlist_tiers)} != law {sorted(LAW_LAYER2_TIERS)}"
        )

    for eval_ok in (True, False):
        built = _build_classes(eval_ok=eval_ok)
        by_id = {row["id"]: row for row in built}
        if set(by_id) != LAW_LAYER1_CLASSES:
            errors.append(
                f"_build_classes(eval_ok={eval_ok}) ids {sorted(by_id)} != "
                f"law {sorted(LAW_LAYER1_CLASSES)}"
            )
            continue
        for class_id in LAW_LAYER1_CLASSES:
            row = by_id[class_id]
            if row.get("auto_dispatch") is not False:
                errors.append(f"{class_id}: auto_dispatch must be False (eval_ok={eval_ok})")
        low_risk = by_id["auto_low_risk"]
        exp_status = "eligible" if eval_ok else "blocked"
        if low_risk.get("status") != exp_status:
            errors.append(
                f"auto_low_risk status={low_risk.get('status')!r} expected {exp_status!r}"
            )
        if low_risk.get("gate") != "eval_1b_live_pass":
            errors.append(f"auto_low_risk gate={low_risk.get('gate')!r} expected eval_1b_live_pass")

    return errors


def _block(
    *,
    reason: str,
    task_class: str,
    eval_tier: str,
    blocking_conditions: list[str],
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "schema": DECISION_SCHEMA,
        "dispatch_ready": False,
        "reason": reason,
        "task_class": task_class,
        "eval_tier": eval_tier,
        "requires_founder_confirm": False,
        "auto_dispatch_allowed": False,
        "blocking_conditions": blocking_conditions,
        "dry_run": dry_run,
    }


def _allow(
    *,
    reason: str,
    task_class: str,
    eval_tier: str,
    requires_founder_confirm: bool,
    dry_run: bool,
) -> dict[str, Any]:
    auto = not requires_founder_confirm and not dry_run
    decision = {
        "schema": DECISION_SCHEMA,
        "dispatch_ready": True,
        "reason": reason,
        "task_class": task_class,
        "eval_tier": eval_tier,
        "requires_founder_confirm": requires_founder_confirm,
        "auto_dispatch_allowed": auto,
        "blocking_conditions": [],
        "dry_run": dry_run,
    }
    if dry_run:
        decision["reason"] = "dry_run_simulated"
        decision["auto_dispatch_allowed"] = False
    return decision


def current_eval_tier() -> str:
    """Infer eval tier from Eval-1b report + CI mode SSOT."""
    if not EVAL_1B_REPORT.is_file():
        return "none"
    try:
        rep = json.loads(EVAL_1B_REPORT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "none"

    mode = rep.get("mode")
    ci = _ci_mode_snapshot()
    if mode != "live":
        if ci.get("mode") == "structural_only" or ci.get("structural_fallback"):
            return "structural"
        if rep.get("ok"):
            return "structural"
        return "none"

    live_pct = rep.get("live_pilot_win_pct")
    if live_pct is None:
        live_pct = rep.get("packet_win_pct")
    live_ok = bool(rep.get("live_ok", rep.get("ok")))
    if live_ok and int(live_pct or 0) >= LIVE_THRESHOLD:
        return "behavioral_pass"
    return "behavioral_fail"


def evaluate(
    *,
    verified_graph: dict,
    router: dict,
    eval_tier: str,
    task_class: str,
    founder_override: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Task-class dispatch decision — per-task simulation; top-level uses orchestrator_dispatch_ready()."""
    tier_key = (eval_tier or "none").strip()
    if tier_key not in VALID_EVAL_TIERS:
        tier_key = "none"
    task_key = (task_class or "").strip()

    recommendation = str(verified_graph.get("recommendation") or "")
    if recommendation == "reject":
        return _block(
            reason="graph_rejected",
            task_class=task_key,
            eval_tier=tier_key,
            blocking_conditions=["verified_graph.recommendation == reject"],
            dry_run=dry_run,
        )

    routing = str(router.get("routing_decision") or "")
    if routing == "block":
        reason_text = router.get("blocking_reason") or router.get("reason") or "router blocked"
        return _block(
            reason="router_blocked",
            task_class=task_key,
            eval_tier=tier_key,
            blocking_conditions=[str(reason_text)],
            dry_run=dry_run,
        )

    if tier_key == "behavioral_fail":
        return _block(
            reason="behavioral_fail_locked",
            task_class=task_key,
            eval_tier=tier_key,
            blocking_conditions=["eval_tier == behavioral_fail"],
            dry_run=dry_run,
        )

    tier = ALLOWLIST.get(task_key)
    if tier is None:
        return _block(
            reason="task_class_unknown",
            task_class=task_key,
            eval_tier=tier_key,
            blocking_conditions=[f"task_class {task_key!r} not in registry"],
            dry_run=dry_run,
        )

    if tier == TIER_SAFE_AUTO:
        if recommendation == "approve" and routing == "allow":
            return _allow(
                reason="allowlist_safe_task",
                task_class=task_key,
                eval_tier=tier_key,
                requires_founder_confirm=False,
                dry_run=dry_run,
            )
        blockers: list[str] = []
        if recommendation != "approve":
            blockers.append(f"verified_graph.recommendation is {recommendation!r} (requires approve)")
        if routing != "allow":
            blockers.append(f"router.routing_decision is {routing!r} (requires allow)")
        return _block(
            reason="allowlist_safe_task",
            task_class=task_key,
            eval_tier=tier_key,
            blocking_conditions=blockers or ["SAFE_AUTO gates not met"],
            dry_run=dry_run,
        )

    if tier == TIER_BEHAVIORAL:
        if tier_key == "behavioral_pass":
            return _allow(
                reason="behavioral_proof_required",
                task_class=task_key,
                eval_tier=tier_key,
                requires_founder_confirm=False,
                dry_run=dry_run,
            )
        if founder_override:
            return _allow(
                reason="founder_override_accepted",
                task_class=task_key,
                eval_tier=tier_key,
                requires_founder_confirm=False,
                dry_run=dry_run,
            )
        return _block(
            reason="behavioral_proof_required",
            task_class=task_key,
            eval_tier=tier_key,
            blocking_conditions=["eval_tier must be behavioral_pass"],
            dry_run=dry_run,
        )

    if tier == TIER_CONFIRM:
        return _allow(
            reason="allowlist_safe_task",
            task_class=task_key,
            eval_tier=tier_key,
            requires_founder_confirm=True,
            dry_run=dry_run,
        )

    return _block(
        reason="task_class_unknown",
        task_class=task_key,
        eval_tier=tier_key,
        blocking_conditions=[f"unknown tier {tier!r}"],
        dry_run=dry_run,
    )


def evaluate_action(action_id: str) -> dict[str, Any]:
    gate_ok, gate_note = eval_1b_gate_status()
    policy_class = classify_action(action_id)
    allowed = policy_class == "observe" or (policy_class == "auto_low_risk" and gate_ok)
    return {
        "action_id": action_id,
        "policy_class": policy_class,
        "allowed": allowed,
        "eval_1b_gate_ok": gate_ok,
        "eval_1b_note": gate_note,
        "auto_dispatch": False,
        "founder_confirm_required": True,
    }


def _eval_report_snapshot() -> dict[str, Any]:
    if not EVAL_1B_REPORT.is_file():
        return {}
    try:
        return json.loads(EVAL_1B_REPORT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _ci_mode_snapshot() -> dict[str, Any]:
    path = Path.home() / ".sina" / "eval_1b_ci_mode_v1.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _alignment_status(*, classes: list[dict[str, Any]]) -> dict[str, Any]:
    """Cross-check Layer-1 classifier vs Layer-2 task_class registry."""
    from runtime.dispatch_policy.classifier import classify_action

    from runtime.dispatch_policy.classifier import LOW_RISK_ACTIONS, LOW_RISK_TASK_CLASS

    expected: list[tuple[str, str, str, str]] = [
        ("pos-dispatch", "suggest", "packet-assemble", TIER_SAFE_AUTO),
    ]
    for action_id in sorted(LOW_RISK_ACTIONS):
        task_class = LOW_RISK_TASK_CLASS[action_id]
        expected.append((action_id, "auto_low_risk", task_class, TIER_SAFE_AUTO))
    checks: list[dict[str, Any]] = []
    mapping_ok = True
    for action_id, exp_class, exp_task, exp_tier in expected:
        got_class = classify_action(action_id)
        got_task = infer_task_class(action_id)
        got_tier = TASK_CLASS_REGISTRY.get(got_task, "")
        ok = got_class == exp_class and got_task == exp_task and got_tier == exp_tier
        if not ok:
            mapping_ok = False
        checks.append(
            {
                "action_id": action_id,
                "policy_class": got_class,
                "task_class": got_task,
                "tier": got_tier,
                "ok": ok,
            }
        )
    law_errors = cross_check_law_policy_classes()
    law_classes_ok = not law_errors
    return {
        "mapping_ok": mapping_ok and law_classes_ok,
        "law_classes_ok": law_classes_ok,
        "law_classes_errors": law_errors,
        "classifier_classes": classes,
        "task_class_registry_version": ALLOWLIST_VERSION,
        "checks": checks,
    }


def dispatch_policy_payload() -> dict[str, Any]:
    import model_dispatch  # noqa: WPS433

    eval_ok, eval_note = eval_1b_gate_status()
    rep = _eval_report_snapshot()
    ci = _ci_mode_snapshot()
    eval_tier = current_eval_tier()
    classes = _build_classes(eval_ok=eval_ok)
    alignment = _alignment_status(classes=classes)
    gate_mode = model_dispatch.current_gate_mode()
    orch = orchestrator_dispatch_ready_payload()
    dispatch_ready = bool(orch.get("dispatch_ready"))
    blockers = list(orch.get("dispatch_ready_blockers") or [])
    hub_fields = {
        "ok": True,
        "schema": SCHEMA,
        "built_at": _now(),
        "gate_mode": gate_mode,
        "current_gate_mode": gate_mode,
        "gate_mode_pref_path": str(model_dispatch.GATE_MODE_PREF_PATH),
        "gate_is_enforce": gate_mode == "enforce",
        "dispatch_ready": dispatch_ready,
        "dispatch_ready_blockers": blockers,
        "eval_1b_gate_ok": eval_ok,
        "eval_1b_note": eval_note,
        "eval_1b_mode": rep.get("mode"),
        "eval_1b_live_ok": rep.get("live_ok"),
        "eval_1b_win_pct": rep.get("live_pilot_win_pct") or rep.get("packet_win_pct"),
        "eval_1b_ci_mode": ci.get("mode"),
        "eval_1b_structural_fallback": bool(ci.get("structural_fallback")),
        "current_eval_tier": eval_tier,
        "doc_path": DOC,
        "classes": classes,
        "classifier": "runtime.dispatch_policy.classifier",
        "allowlist": "runtime.dispatch_policy.allowlist",
        "alignment": alignment,
        "bottleneck": (
            "orchestrator dispatch_ready active — spine bridge + OpenRouter enforce"
            if dispatch_ready
            else f"dispatch blocked: {'; '.join(blockers[:4]) or 'gates not met'}"
        ),
        "api": "/api/dispatch-policy-v1",
        "next": "graph_executor spine_bridge enqueue when dispatch_ready",
    }
    return record_decision(
        decision={
            "schema": DECISION_SCHEMA,
            "dispatch_ready": dispatch_ready,
            "reason": "activation_gates_pass" if dispatch_ready else "activation_gates_blocked",
            "task_class": "",
            "eval_tier": eval_tier,
            "requires_founder_confirm": True,
            "auto_dispatch_allowed": False,
            "blocking_conditions": blockers,
            "dry_run": False,
        },
        eval_tier=eval_tier,
        hub_fields=hub_fields,
    )
