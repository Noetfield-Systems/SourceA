#!/usr/bin/env python3
"""Auto Runtime specialist tick — observe · advise · compose · dispatch (Mac control plane).

Replaces founder RUN INBOX as trigger when loop_auto_dispatch_enabled.
Law: SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md — Brain execution_authority only
Receipt: ~/.sina/loop-specialist-tick-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
CONFIG = SINA / "loop-specialist-config-v1.json"
RECEIPT = SINA / "loop-specialist-tick-receipt-v1.json"
ORCH_STATE = SINA / "healthy-drain-orchestrator-v1.json"
TICK_DECISIONS = frozenset(
    {"observe_only", "compose_blocked", "dispatch_ready", "dispatch_done", "execute_pending", "idle", "auto_commercial"}
)
OUTBOUND_PHASE = "phase-s6-outbound-factory-upgrade"


def _outbound_plan_complete() -> bool:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from outbound_factory_phase_complete_v1 import outbound_plan_progress  # noqa: WPS433

        return bool(outbound_plan_progress().get("complete"))
    except Exception:
        plan = _read_json(ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json")
        upgrades = plan.get("upgrades") or []
        done = sum(1 for u in upgrades if u.get("status") == "done")
        return len(upgrades) > 0 and done >= len(upgrades)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_config(*, write_default: bool = True) -> dict:
    if CONFIG.is_file():
        try:
            row = json.loads(CONFIG.read_text(encoding="utf-8"))
            if row.get("schema") == "loop-specialist-config-v1":
                return row
        except (OSError, json.JSONDecodeError):
            pass
    row = {
        "schema": "loop-specialist-config-v1",
        "at": _now(),
        "loop_auto_dispatch_enabled": False,
        "loop_auto_observe_enabled": True,
        "loop_auto_mode": "off",
        "founder_motion": "ASF resume Cloud Forge Run when FREEZE · Auto Runtime specialist tick on Hub",
        "law": "CL10 safe rollout — graduate via loop_auto_graduation_v1.py after validators PASS",
    }
    if write_default:
        SINA.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def save_config(row: dict) -> None:
    row["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _orchestrator_idle() -> tuple[bool, dict]:
    st = _read_json(ORCH_STATE)
    status = str(st.get("status") or "idle")
    idle = status in ("idle", "stopped", "")
    return idle, st


def _queue_head() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

        return queue_head()
    except Exception:
        return {}


def _is_outbound_queue(head: dict, hq: dict) -> bool:
    phase = str(head.get("phase") or hq.get("phase") or "")
    return phase == OUTBOUND_PHASE or bool(hq.get("upgrade_plan_schema"))


def _outbound_drain_idle(head: dict, hq: dict | None = None) -> bool:
    """Outbound Cloud Forge Run is done — empty queue or no head, even if doc flag stale."""
    if not _outbound_plan_complete():
        return False
    hq = hq or _read_json(SINA / "healthy-queue-30-active.json")
    if head.get("queue_exhausted") or hq.get("queue_exhausted") or hq.get("phase_strict_complete"):
        return True
    if not head.get("sa_id"):
        return True
    items = hq.get("queue") or []
    if not items or int(hq.get("count") or 0) == 0:
        return True
    return False


def _heal_outbound_exhausted_queue() -> dict:
    if not _outbound_drain_idle(_queue_head(), _read_json(SINA / "healthy-queue-30-active.json")):
        return {"skipped": True}
    hq = _read_json(SINA / "healthy-queue-30-active.json")
    if hq.get("queue_exhausted"):
        return {"skipped": True, "reason": "already_exhausted"}
    try:
        from outbound_factory_phase_complete_v1 import mark_outbound_queue_exhausted  # noqa: WPS433

        return mark_outbound_queue_exhausted(write=True)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _run_commercial_auto() -> dict:
    """Smart loop owns commercial L3 prep — pulse + observe, not founder Hub Deliver."""
    steps: dict = {}
    for script, extra in (
        ("icp_output_compiler_v1.py", ["--fleet"]),
        ("agent_nerve_system_v1.py", []),
        ("w3_founder_review_v1.py", []),
        ("better_loop_pulse_v1.py", []),
        ("commercial_command_pulse_v1.py", []),
        ("outbound_factory_upgrade_pulse_v1.py", []),
    ):
        path = SCRIPTS / script
        if not path.is_file():
            steps[script] = {"skipped": True}
            continue
        try:
            import subprocess

            proc = subprocess.run(
                [sys.executable, str(path), *extra, "--json"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=90,
            )
            body = {}
            if proc.stdout.strip():
                try:
                    body = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    body = {"raw": proc.stdout.strip()[:500]}
            steps[script] = {"ok": proc.returncode == 0, "exit": proc.returncode, "body": body}
            if (
                script == "icp_output_compiler_v1.py"
                and not steps[script]["ok"]
                and body.get("schema") == "icp-compiler-fleet-receipt-v1"
            ):
                steps[script]["ok"] = True
                steps[script]["partial_fleet"] = True
        except Exception as exc:
            steps[script] = {"ok": False, "error": str(exc)}
    return {"ok": all(v.get("ok") for v in steps.values() if not v.get("skipped")), "steps": steps}


def _act_freeze_blocked() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import act_blocked_by_freeze  # noqa: WPS433

    head = _queue_head()
    role = str(head.get("role") or "act")
    return act_blocked_by_freeze(queue_role=role)


def _dispatch_allowed(*, obs: dict, config: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    freeze = obs.get("freeze") or {}
    act = _act_freeze_blocked()
    if act.get("blocked") or freeze.get("prompt_blocked_by_freeze"):
        reasons.append("freeze_no_resume")
    product = obs.get("product") or {}
    dual = product.get("dual_pick") or {}
    if not dual.get("ok"):
        reasons.append("dual_pick_fail")
    bugs = (obs.get("system") or {}).get("critical_bugs") or {}
    if bugs.get("ok") is False:
        reasons.append("critical_bugs")
    idle, st = _orchestrator_idle()
    if not idle:
        reasons.append(f"orchestrator_{st.get('status')}")
    inbox_pending = bool(product.get("inbox_pending"))
    auto_on = bool(config.get("loop_auto_dispatch_enabled"))
    if inbox_pending and not auto_on:
        reasons.append("inbox_already_pending")
    head = _queue_head()
    if head.get("queue_exhausted") or not head.get("sa_id"):
        reasons.append("queue_idle")
    if not auto_on:
        reasons.append("auto_dispatch_disabled")
    return not reasons, reasons


def _run_dispatch(*, head: dict, hq: dict) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    if _is_outbound_queue(head, hq):
        from brain_outbound_work_order_v1 import brain_work_order_enabled, dispatch_current  # noqa: WPS433
        from outbound_factory_queue_assign_v1 import build_assignment, write_queue  # noqa: WPS433

        if brain_work_order_enabled():
            bundle = build_assignment()
            write_queue(bundle)
            return {
                "path": "brain_outbound_work_order",
                "result": dispatch_current(dry_run=False, advance_queue=False, mode="sign_only"),
            }
        from outbound_factory_queue_assign_v1 import deliver_head  # noqa: WPS433

        bundle = build_assignment()
        write_queue(bundle)
        return {"path": "outbound_factory_queue_assign", "result": deliver_head(bundle)}
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "orch", SCRIPTS / "healthy-drain-orchestrator-v1.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return {"path": "healthy_drain_orchestrator", "result": mod.deliver_current(force=True)}


def _founder_line(
    *,
    decision: str,
    obs: dict,
    advisory: dict,
    config: dict,
    block_reasons: list[str],
    pending: dict | None = None,
) -> str:
    obs_line = str(obs.get("founder_one_line") or "")[:120]
    auto = "auto=ON" if config.get("loop_auto_dispatch_enabled") else "auto=OFF"
    top = ((advisory.get("ranked_prompts") or [{}])[0]).get("upgrade_id") or "?"
    pending_line = ""
    if pending and int(pending.get("count") or 0) > 0:
        pending_line = f" · {pending.get('report_line', '')[:80]}"
    if decision == "compose_blocked":
        return f"loop-specialist · blocked · {auto} · {','.join(block_reasons[:3])} · {obs_line}{pending_line}"
    if decision == "dispatch_ready":
        freeze = obs.get("freeze") or {}
        resume_hint = "" if freeze.get("outbound_queue_override") else " · ASF resume if FREEZE"
        return f"loop-specialist · ready · {auto} · top={top}{resume_hint}{pending_line}"
    if decision == "dispatch_done":
        return f"loop-specialist · dispatched · {auto} · Brain work-order executed{pending_line}"
    if decision == "execute_pending":
        return f"loop-specialist · execute_pending · {auto} · Brain work-order · Hub glance only{pending_line}"
    if decision == "auto_commercial":
        sys.path.insert(0, str(SCRIPTS))
        try:
            from execution_path_vocabulary_v1 import commercial_l3_blocker_summary  # noqa: WPS433

            return f"loop-specialist · auto · {commercial_l3_blocker_summary()} · Hub glance only{pending_line}"
        except Exception:
            pass
        try:
            from outbound_factory_phase_complete_v1 import outbound_plan_progress  # noqa: WPS433

            p = outbound_plan_progress()
            return f"loop-specialist · auto · outbound {p['done']}/{p['total']} · smart loop owns next motion{pending_line}"
        except Exception:
            pass
        return f"loop-specialist · auto · outbound complete · smart loop owns next motion{pending_line}"
    if decision == "idle":
        return f"loop-specialist · idle · queue exhausted or commercial P0{pending_line}"
    return f"loop-specialist · observe · {auto} · advisory={top} · {obs_line[:80]}{pending_line}"


def run_machine_process_cycle() -> dict:
    """Piggyback machine process loops on loop-specialist tick (SA-T-machine-cycle)."""
    steps: list[dict] = []
    py = sys.executable
    chain = [
        ("spine_probe", [py, str(SCRIPTS / "spine_live_probe_v1.py"), "--json"]),
        ("adversarial", ["bash", str(SCRIPTS / "adversarial_critique_gate_v1.sh")]),
        ("critic", [py, str(SCRIPTS / "adversarial_critic_receipt_v1.py"), "--json"]),
        ("merge_gate", [py, str(SCRIPTS / "machine_merge_gate_v1.py"), "--json"]),
        ("machine_cycle", [py, str(SCRIPTS / "machine_cycle_receipt_v1.py"), "--json"]),
        ("retirement_eval", [py, str(SCRIPTS / "founder_trigger_retirement_evaluator_v1.py"), "--json"]),
        ("kaizen_pick", [py, str(SCRIPTS / "autorun_kaizen_queue_v1.py"), "--pick", "--json"]),
    ]
    for name, cmd in chain:
        try:
            import subprocess as _sp

            r = _sp.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
            steps.append({"step": name, "ok": r.returncode == 0, "exit": r.returncode})
        except Exception as exc:
            steps.append({"step": name, "ok": False, "error": str(exc)[:80]})
    return {
        "schema": "machine-process-cycle-run-v1",
        "at": _now(),
        "ok": all(s.get("ok") for s in steps),
        "steps": steps,
    }


def run_tick(*, write: bool = True, dispatch: bool | None = None) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    config = load_config(write_default=True)
    do_dispatch = dispatch if dispatch is not None else bool(config.get("loop_auto_dispatch_enabled"))

    # Cloud primary — Railway loop tick (no Mac validator stack).
    try:
        from cloud_loop_specialist_client_v1 import tick_via_cloud  # noqa: WPS433

        cloud = tick_via_cloud(
            founder_message="Auto Runtime · cloud executes · Hub glance only · no RUN INBOX",
            dispatch=do_dispatch,
            write_receipt=False,
        )
        if cloud.get("ok") and cloud.get("loop_specialist_line"):
            raw = cloud.get("raw") or {}
            row = {
                "schema": "loop-specialist-tick-receipt-v1",
                "ok": True,
                "at": _now(),
                "execution_authority": False,
                "execution_plane": "headless_cloud",
                "cloud_primary": True,
                "tick_decision": cloud.get("tick_decision") or "cloud_comprehend",
                "loop_auto_dispatch_enabled": bool(config.get("loop_auto_dispatch_enabled")),
                "loop_auto_observe_enabled": bool(config.get("loop_auto_observe_enabled", True)),
                "loop_auto_mode": config.get("loop_auto_mode") or "shadow_auto",
                "founder_motion": config.get("founder_motion") or "",
                "dispatch_requested": do_dispatch,
                "block_reasons": raw.get("block_reasons") or [],
                "loop_specialist_line": cloud.get("loop_specialist_line"),
                "next_founder_action": cloud.get("next_founder_action")
                or "Hub glance only · cloud loop · no Mac Terminal",
                "founder_one_line": cloud.get("loop_specialist_line"),
                "comprehension": raw.get("comprehension"),
                "dispatch": raw.get("dispatch") or {"skipped": True},
                "hub_api": "POST /api/fbe/loop-specialist/tick/v1 (Railway)",
            }
            if write:
                SINA.mkdir(parents=True, exist_ok=True)
                RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            return row
    except Exception:
        pass

    try:
        from loop_observatory_report_v1 import run_report  # noqa: WPS433

        obs = run_report(write=True)
    except Exception as exc:
        obs = _read_json(SINA / "loop-observatory-report-v1.json")
        obs.setdefault("ok", False)
        obs["error"] = str(exc)

    try:
        from future_loop_prompt_advisory_circle_v1 import run_advisory  # noqa: WPS433

        advisory = run_advisory(write=True)
    except Exception as exc:
        advisory = _read_json(SINA / "future-loop-prompt-advisory-v1.json")
        advisory.setdefault("ok", False)
        advisory["error"] = str(exc)

    head = _queue_head()
    hq = _read_json(SINA / "healthy-queue-30-active.json")
    heal = _heal_outbound_exhausted_queue()
    if heal.get("ok"):
        head = _queue_head()
        hq = _read_json(SINA / "healthy-queue-30-active.json")
    phase_handoff: dict = {"skipped": True, "heal": heal}
    if _outbound_drain_idle(head, hq):
        try:
            from outbound_factory_phase_complete_v1 import run_auto_transition  # noqa: WPS433

            phase_handoff = {**run_auto_transition(write=True, dispatch=False), "heal": heal}
            head = _queue_head()
            hq = _read_json(SINA / "healthy-queue-30-active.json")
        except Exception as exc:
            phase_handoff = {"ok": False, "error": str(exc), "heal": heal}

    idle_orch, orch_st = _orchestrator_idle()
    product = obs.get("product") or {}
    freeze = obs.get("freeze") or {}
    act_freeze = _act_freeze_blocked()
    act_blocked = bool(act_freeze.get("blocked") or freeze.get("prompt_blocked_by_freeze"))
    inbox_pending = bool(product.get("inbox_pending"))
    auto_on = bool(config.get("loop_auto_dispatch_enabled"))

    can_dispatch, block_reasons = _dispatch_allowed(obs=obs, config=config)
    do_dispatch = dispatch if dispatch is not None else auto_on

    if _outbound_drain_idle(head, hq):
        if auto_on:
            decision = "auto_commercial"
            block_reasons = [r for r in block_reasons if r not in ("queue_idle", "auto_dispatch_disabled")]
        else:
            decision = "idle"
    elif auto_on and inbox_pending and not act_blocked:
        decision = "execute_pending"
        block_reasons = [r for r in block_reasons if r not in ("inbox_already_pending", "freeze_no_resume")]
    elif act_blocked:
        decision = "compose_blocked"
    elif can_dispatch and do_dispatch:
        decision = "dispatch_ready"
    elif can_dispatch and not do_dispatch:
        decision = "observe_only"
    else:
        decision = "compose_blocked" if block_reasons else "observe_only"

    dispatch_result: dict = {"skipped": True}
    if decision == "dispatch_ready" and do_dispatch:
        try:
            dispatch_result = _run_dispatch(head=head, hq=hq)
            if dispatch_result.get("result", {}).get("ok") or dispatch_result.get("result", {}).get(
                "blocked_by_freeze"
            ):
                decision = "dispatch_done" if not dispatch_result.get("result", {}).get(
                    "blocked_by_freeze"
                ) else "compose_blocked"
        except Exception as exc:
            dispatch_result = {"ok": False, "error": str(exc)}
            decision = "compose_blocked"
            block_reasons.append("dispatch_error")

    coherence_block: dict = {"skipped": True}
    if decision in ("dispatch_done", "execute_pending", "dispatch_ready"):
        try:
            from outbound_queue_coherence_v1 import assess_queue_coherence, heal_all  # noqa: WPS433

            coh = assess_queue_coherence()
            coherence_block = {"assess": coh}
            if not coh.get("ok"):
                coherence_block["heal"] = heal_all(write=True)
                coherence_block["after"] = assess_queue_coherence()
                coherence_block["ok"] = coherence_block["after"].get("ok")
            else:
                coherence_block["ok"] = True
        except Exception as exc:
            coherence_block = {"ok": False, "error": str(exc)}

    commercial_auto: dict = {"skipped": True}
    if decision == "auto_commercial":
        commercial_auto = _run_commercial_auto()

    top_advisory = (advisory.get("ranked_prompts") or [{}])[0]
    if decision == "execute_pending":
        try:
            from brain_outbound_work_order_v1 import brain_work_order_enabled, dispatch_current  # noqa: WPS433

            if brain_work_order_enabled():
                dispatch_result = {
                    "path": "brain_outbound_work_order",
                    "result": dispatch_current(dry_run=False, advance_queue=True, mode="execute_pending"),
                }
                if dispatch_result.get("result", {}).get("ok"):
                    decision = "dispatch_done"
                else:
                    block_reasons.append("brain_work_order_failed")
        except Exception as exc:
            dispatch_result = {"ok": False, "error": str(exc), "path": "brain_outbound_work_order"}
            block_reasons.append("brain_work_order_error")
    if decision == "execute_pending":
        sys.path.insert(0, str(SCRIPTS))
        from execution_path_vocabulary_v1 import execute_line  # noqa: WPS433

        next_action = execute_line()
    elif decision == "auto_commercial":
        sys.path.insert(0, str(SCRIPTS))
        from execution_path_vocabulary_v1 import commercial_smart_loop_line  # noqa: WPS433

        next_action = commercial_smart_loop_line()
    elif act_blocked:
        next_action = (
            (freeze.get("action") or execute_line())
            if auto_on and _outbound_plan_complete()
            else (freeze.get("action") or "ASF: Cloud Forge Run — max 1")
        )
    elif int((obs.get("commercial") or {}).get("commercial_red_count") or 0) > 0:
        if auto_on:
            sys.path.insert(0, str(SCRIPTS))
            from execution_path_vocabulary_v1 import execute_line  # noqa: WPS433

            next_action = execute_line()
        else:
            next_action = (obs.get("commercial") or {}).get("founder_action") or "commercial P0"
    elif decision == "observe_only":
        next_action = (
            "Enable Auto Runtime on Hub · Refresh loop chain"
            if not auto_on
            else "Auto Runtime observe · dispatch when resume valid"
        )
    else:
        next_action = "Auto Runtime · Brain work-order when inbox pending"

    try:
        from autorun_pending_v1 import write_pending_receipt  # noqa: WPS433

        pending = write_pending_receipt()
    except Exception as exc:
        pending = {
            "schema": "autorun-pending-v1",
            "ok": False,
            "count": 1,
            "items": [{"id": "pending_write_failed", "reason": str(exc)[:120]}],
            "report_line": f"pending_write_failed · {exc}",
        }

    machine_cycle = run_machine_process_cycle()

    row = {
        "schema": "loop-specialist-tick-receipt-v1",
        "ok": decision in (
            "observe_only",
            "compose_blocked",
            "dispatch_ready",
            "dispatch_done",
            "execute_pending",
            "idle",
            "auto_commercial",
        ),
        "at": _now(),
        "execution_authority": False,
        "tick_decision": decision,
        "loop_auto_dispatch_enabled": bool(config.get("loop_auto_dispatch_enabled")),
        "loop_auto_observe_enabled": bool(config.get("loop_auto_observe_enabled", True)),
        "loop_auto_mode": config.get("loop_auto_mode") or "off",
        "founder_motion": config.get("founder_motion") or "",
        "outbound_plan_complete": _outbound_plan_complete(),
        "phase_handoff": phase_handoff,
        "dispatch_requested": bool(do_dispatch),
        "block_reasons": block_reasons,
        "freeze": freeze,
        "outbound_queue_override": bool(freeze.get("outbound_queue_override")),
        "orchestrator": {"idle": idle_orch, "status": orch_st.get("status")},
        "queue_head": head,
        "advisory": {
            "deterministic_hash": advisory.get("deterministic_hash"),
            "top_pick": top_advisory,
            "advisory_line": advisory.get("advisory_line"),
        },
        "observatory_at": obs.get("at"),
        "dispatch": dispatch_result,
        "coherence": coherence_block,
        "commercial_auto": commercial_auto,
        "loop_specialist_line": _founder_line(
            decision=decision,
            obs=obs,
            advisory=advisory,
            config=config,
            block_reasons=block_reasons,
            pending=pending,
        ),
        "pending": pending,
        "pending_count": int(pending.get("count") or 0),
        "machine_process_cycle": machine_cycle,
        "next_founder_action": next_action,
        "founder_one_line": "",
        "command": "python3 scripts/loop_specialist_tick_v1.py --json",
        "hub_api": "POST /api/loop-specialist/tick/v1",
    }
    row["founder_one_line"] = row["loop_specialist_line"]
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "loop-specialist-tick-receipt-v1":
        row = run_tick(write=True, dispatch=False)
    config = load_config(write_default=False)
    advisory = _read_json(SINA / "future-loop-prompt-advisory-v1.json")
    return {
        "schema": "worker-hub-loop-specialist-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "tick_decision": row.get("tick_decision"),
        "loop_specialist_line": row.get("loop_specialist_line"),
        "loop_auto_dispatch_enabled": config.get("loop_auto_dispatch_enabled"),
        "next_founder_action": row.get("next_founder_action"),
        "block_reasons": row.get("block_reasons") or [],
        "advisory_top_pick": (advisory.get("ranked_prompts") or [{}])[0],
        "hub_api": "POST /api/loop-specialist/tick/v1",
    }


def handle_hub_post(body: dict | None = None) -> dict:
    body = body or {}
    dispatch = body.get("dispatch")
    if body.get("enable_auto_dispatch") is True:
        cfg = load_config()
        cfg["loop_auto_dispatch_enabled"] = True
        cfg["loop_auto_observe_enabled"] = True
        cfg["loop_auto_mode"] = cfg.get("loop_auto_mode") or "shadow_auto"
        cfg["founder_motion"] = "Hub glance only · Auto Runtime specialist auto-tick · no RUN INBOX verb"
        cfg["graduated_at"] = _now()
        save_config(cfg)
    if body.get("enable_auto_dispatch") is False:
        cfg = load_config()
        cfg["loop_auto_dispatch_enabled"] = False
        cfg["loop_auto_mode"] = "off"
        cfg["founder_motion"] = "ASF resume Cloud Forge Run when FREEZE · Auto Runtime specialist tick on Hub"
        save_config(cfg)
    return run_tick(
        write=True,
        dispatch=bool(dispatch) if dispatch is not None else None,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto Runtime specialist tick")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--dispatch", action="store_true", help="Attempt dispatch if policy allows")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--enable-auto-dispatch", action="store_true")
    ap.add_argument("--disable-auto-dispatch", action="store_true")
    args = ap.parse_args()
    if args.enable_auto_dispatch or args.disable_auto_dispatch:
        cfg = load_config()
        cfg["loop_auto_dispatch_enabled"] = bool(args.enable_auto_dispatch)
        save_config(cfg)
    if args.hub_slice:
        row = hub_slice()
    else:
        row = run_tick(
            write=not args.no_write,
            dispatch=True if args.dispatch else None,
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("loop_specialist_line") or row.get("founder_one_line") or "loop-specialist ok")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
