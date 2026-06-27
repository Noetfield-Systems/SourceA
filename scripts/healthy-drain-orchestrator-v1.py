#!/usr/bin/env python3
"""Goal 1 healthy drain orchestrator — non-LLM PEV sync (Conductor/LangGraph lesson).

State machine (disk SSOT, not chat):
  IDLE → deliver INBOX → AWAITING_WORKER → validate WORKER_ROUND_REPORT → advance → IDLE
  STOP on mismatch, timeout, feasibility block, or iteration cap.

Never clipboard-pastes into focused chat. Founder never runs this — executor daemon only.
Law: HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md · GOAL_EXECUTION_ACTIVE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATE_PATH = Path.home() / ".sina" / "healthy-drain-orchestrator-v1.json"
ROUND_REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"
QUEUE_STATE = Path.home() / ".sina" / "healthy-queue-state-v1.json"
QUEUE_REPO = ROOT / "os/plan-library/sourcea-1000/prompts/healthy-queue-30-active.json"
QUEUE_HOME = Path.home() / ".sina/healthy-queue-30-active.json"
SKIP_RECEIPT_DIR = Path.home() / ".sina" / "skip-receipts-v1"
OVERNIGHT_SKIP_LOG = Path.home() / ".sina" / "overnight-orchestrator-v1.jsonl"

# Conductor DO_WHILE cap — semi-unattended, not infinite
DEFAULT_MAX_TURNS = 30
DEFAULT_POLL_SEC = 25.0
DEFAULT_TURN_TIMEOUT_SEC = 1800.0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save(st: dict) -> dict:
    st["updated_at"] = _now()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
    return st


def _queue_path() -> Path:
    return QUEUE_HOME if QUEUE_HOME.is_file() else QUEUE_REPO


def queue_item(pos: int | None = None) -> dict:
    q = json.loads(_queue_path().read_text(encoding="utf-8"))
    items = q.get("queue") or []
    if pos is None:
        pos = int(_load(QUEUE_STATE).get("next_pos") or 1)
    if pos < 1 or pos > len(items):
        return {"ok": False, "error": f"pos {pos} out of range"}
    item = items[pos - 1]
    return {"ok": True, "pos": pos, "total": len(items), "item": item}


def _founder_absent() -> bool:
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433

    return "absent" in (load_active_now().get("founder_mode") or "")


def _orchestrator_autorun_active() -> bool:
    """Choice 1+ unified path — ~/.sina/goal1-orchestrator-autorun-v1.json set on Hub START."""
    return (Path.home() / ".sina" / "goal1-orchestrator-autorun-v1.json").is_file()


def _overnight_headless() -> bool:
    """Headless API/CLI only when overnight armed — kill flags force Worker INBOX."""
    sina = Path.home() / ".sina"
    if (sina / "auto-run-disabled-v1.flag").is_file():
        sys.path.insert(0, str(SCRIPTS))
        try:
            from factory_control_v1 import load_resume_token  # noqa: WPS433

            if not load_resume_token():
                return False
        except Exception:
            return False
    if _orchestrator_autorun_active():
        for name in ("api-disabled-v1.flag", "cli-disabled-v1.flag"):
            if (sina / name).is_file():
                return False
        return _founder_absent()
    for name in (
        "auto-run-disabled-v1.flag",
        "api-disabled-v1.flag",
        "cli-disabled-v1.flag",
    ):
        if (sina / name).is_file():
            return False
    return _founder_absent()


def _log_overnight_skip(*, sa_id: str, reason: str, extra: dict | None = None) -> None:
    row = {"event": "OVERNIGHT_SKIP", "sa_id": sa_id, "reason": reason, "at": _now(), **(extra or {})}
    print(f"[{_now()}] OVERNIGHT_SKIP sa={sa_id} reason={reason}", flush=True)
    OVERNIGHT_SKIP_LOG.parent.mkdir(parents=True, exist_ok=True)
    with OVERNIGHT_SKIP_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def _write_skip_receipt(
    *,
    sa_id: str,
    pos: int,
    role: str,
    turn_result: dict,
) -> Path:
    SKIP_RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = SKIP_RECEIPT_DIR / f"{sa_id}-skip.json"
    payload = {
        "schema": "skip-receipt-v1",
        "sa_id": sa_id,
        "status": "SKIP",
        "reason": "BLOCKED_NO_WORKER",
        "queue_pos": pos,
        "queue_role": role,
        "turn_status": turn_result.get("status"),
        "turn_ok": turn_result.get("ok"),
        "turn_error": turn_result.get("error"),
        "at": _now(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def orchestrator_state() -> dict:
    st = _load(STATE_PATH)
    if not st:
        st = {
            "schema": "healthy-drain-orchestrator-v1",
            "status": "idle",
            "turns_completed": 0,
            "max_turns": DEFAULT_MAX_TURNS,
        }
    return st


def _skip_override_turn(*, qi: dict, reason: str, st: dict) -> dict:
    """Skip deliver for quarantined/excluded queue_pos — advance cursor, no INBOX."""
    pos = int(qi.get("pos") or 0)
    SKIP_RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "skip-receipt-v1",
        "at": _now(),
        "reason": reason,
        "queue_pos": pos,
        "sa_id": (qi.get("item") or {}).get("sa_id"),
        "queue_role": (qi.get("item") or {}).get("queue_role"),
    }
    path = SKIP_RECEIPT_DIR / f"override-pos-{pos}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    try:
        import importlib.util

        spec_adv = importlib.util.spec_from_file_location(
            "advance_hq", SCRIPTS / "advance-healthy-queue-v1.py"
        )
        adv_mod = importlib.util.module_from_spec(spec_adv)
        spec_adv.loader.exec_module(adv_mod)  # type: ignore[union-attr]
        adv = adv_mod.advance()
    except Exception as exc:
        adv = {"ok": False, "error": str(exc)}
    try:
        from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

        rebuild(write=True, preview=False)
    except Exception:
        pass
    st["last_skip"] = receipt
    st["status"] = "idle"
    _save(st)
    return {
        "ok": True,
        "skipped": True,
        "skip_reason": reason,
        "receipt": str(path),
        "advance": adv,
        "state": st,
    }


def _freeze_blocks_role(role: str) -> bool:
    r = (role or "check").lower()
    if r in ("check",):
        return False
    sina = Path.home() / ".sina"
    hq_path = sina / "healthy-queue-30-active.json"
    if hq_path.is_file():
        try:
            hq = json.loads(hq_path.read_text(encoding="utf-8"))
            if (
                str(hq.get("thread") or "") == "OUTBOUND-FACTORY"
                or str(hq.get("product") or "").startswith("Outbound Factory")
            ):
                return False
            queue = hq.get("queue") or []
            if queue and "outbound-factory" in str(queue[0].get("phase") or ""):
                return False
        except (OSError, json.JSONDecodeError):
            pass
    try:
        from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

        fn = rebuild_factory_now(caller="healthy_drain_orchestrator", force=False)
        if bool(fn.get("kill_flag")):
            return True
    except Exception:
        pass
    return False


def _build_paste_body(qi: dict) -> str:
    sys.path.insert(0, str(SCRIPTS))
    from healthy_prompt_turn_v1 import build_turn_prompt  # noqa: WPS433

    item = qi["item"]
    return build_turn_prompt(
        item=item,
        pos=int(qi["pos"]),
        total=int(qi["total"]),
        engine="WORKER",
    )


def _commercial_fast() -> bool:
    import os

    keys = ("SINA_BROKER_FAST", "SINA_COMMERCIAL_LOOP", "SINA_BRAIN_FAST")
    return any(os.environ.get(k, "").strip().lower() in ("1", "true", "yes") for k in keys)


def deliver_current(*, force: bool = False, fast: bool | None = None) -> dict:
    """Planner+Executor handoff: INBOX only + heads-up. No clipboard."""
    if fast is None:
        fast = _commercial_fast()
    sys.path.insert(0, str(SCRIPTS))
    from factory_spawn_gate_v1 import drain_spawn_allowed  # noqa: WPS433

    spawn_gate = drain_spawn_allowed(caller="healthy_drain_orchestrator")
    if not spawn_gate.get("ok"):
        return spawn_gate
    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="healthy-drain-orchestrator:deliver")
    if not hb.get("ok"):
        return {"ok": False, "step": "active_now", **hb}
    from prompt_feasibility_gate import check_session  # noqa: WPS433
    from worker_inject_lib import inject_worker_prompt  # noqa: WPS433

    st = orchestrator_state()
    if st.get("status") == "awaiting_worker" and not force:
        return {
            "ok": False,
            "error": "AWAITING_WORKER — poll for report or reset",
            "state": st,
        }

    from brain_outbound_work_order_v1 import brain_work_order_enabled, dispatch_current  # noqa: WPS433

    if brain_work_order_enabled():
        from worker_inject_lib import inbox_status  # noqa: WPS433

        ib = inbox_status()
        if ib.get("pending") or force:
            row = dispatch_current(dry_run=False, advance_queue=True, mode="execute_pending")
            return {"ok": bool(row.get("ok")), "path": "brain_outbound_work_order", "result": row}
        return {
            "ok": True,
            "path": "brain_outbound_work_order",
            "relay": True,
            "note": "Auto Runtime · Brain work-order primary · no Worker INBOX paste",
        }

    # Worker lane: never pile INBOX while turn open or inbox already pending (stops 18× queue).
    if not _overnight_headless():
        from worker_factory_evidence_gate_v1 import run_factory_gate  # noqa: WPS433
        from worker_inject_lib import inbox_status  # noqa: WPS433
        from worker_turn_lib import turn_open_block  # noqa: WPS433

        fg = run_factory_gate(
            caller="healthy-drain:deliver",
            require_inbox=False,
        )
        if not fg.get("ok") and "INBOX_NOT_READY" not in (fg.get("reasons") or []):
            return {
                "ok": False,
                "error": "WORKER_FACTORY_GATE_BLOCKED",
                "factory_gate": fg,
                "hint": "Unstick Worker / heal INBOX per WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md",
                "state": st,
            }

        busy = turn_open_block()
        ib = inbox_status()
        if busy or ib.get("pending"):
            return {
                "ok": False,
                "error": "WORKER_BUSY_NO_REDELIVER",
                "worker_turn": busy,
                "inbox_pending": ib.get("pending"),
                "hint": "Finish current Worker turn — do not deliver again",
                "state": st,
            }

    # Recover stale feasibility stop when current queue item is injectable (live pick may still warn).
    if st.get("status") == "stopped" and st.get("stop_reason") == "feasibility_blocked":
        feas_probe = check_session(role="worker")
        if feas_probe.get("action") != "STOP_INJECT":
            st.update(
                {
                    "status": "idle",
                    "stop_reason": None,
                    "feasibility_recovered_at": _now(),
                    "last_feasibility_probe": feas_probe,
                }
            )
            _save(st)

    if not fast:
        try:
            import importlib.util

            from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

            rebuild(write=True, preview=False)
            spec = importlib.util.spec_from_file_location(
                "validate_pack_live",
                SCRIPTS / "validate-next-prompt-pack-live-v1.py",
            )
            vmod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vmod)  # type: ignore[union-attr]
            pack_val = vmod.validate(write_receipt=True)
            if not pack_val.get("ok") and not _overnight_headless():
                st["status"] = "stopped"
                st["stop_reason"] = "live_pack_validator_blocked"
                st["live_pack_validator"] = pack_val
                _save(st)
                return {
                    "ok": False,
                    "error": "LIVE_PACK_VALIDATOR_BLOCKED",
                    "validator": pack_val,
                    "state": st,
                }
            if pack_val.get("ok"):
                st.pop("stop_reason", None)
                st["live_pack_validator"] = pack_val
                _save(st)
        except Exception as exc:
            if not _overnight_headless():
                return {"ok": False, "error": "LIVE_PACK_VALIDATOR_ERROR", "detail": str(exc), "state": st}

    feas = check_session(role="worker")
    # Overnight headless: API/CLI agents run without Worker inject — inject feasibility does not apply.
    if feas.get("action") == "STOP_INJECT" and not _overnight_headless():
        st["status"] = "stopped"
        st["stop_reason"] = "feasibility_blocked"
        st["feasibility"] = feas
        _save(st)
        return {"ok": False, "error": "FEASIBILITY_BLOCKED", "feasibility": feas, "state": st}

    qi = queue_item()
    if not qi.get("ok"):
        return qi

    item = qi["item"]
    pos = int(qi.get("pos") or 0)
    try:
        from live_ongoing_prompts_v1 import load_overrides  # noqa: WPS433

        ov = load_overrides()
        quarantine = {int(x) for x in (ov.get("quarantine") or []) if str(x).isdigit()}
        excluded = {int(x) for x in (ov.get("excluded") or []) if str(x).isdigit()}
        if pos in quarantine:
            return _skip_override_turn(qi=qi, reason="quarantine", st=st)
        if pos in excluded:
            return _skip_override_turn(qi=qi, reason="excluded", st=st)
    except Exception:
        pass

    role = str(item.get("queue_role") or "check")
    if _freeze_blocks_role(role) and not _overnight_headless():
        st["status"] = "stopped"
        st["stop_reason"] = "freeze_act_blocked"
        st["freeze_blocked_role"] = role
        _save(st)
        return {
            "ok": False,
            "error": "FREEZE_ACT_BLOCKED",
            "role": role,
            "hint": "FREEZE allows CHECK only — ASF Cloud Forge Run PHASE_STRICT for ACT/VERIFY",
            "state": st,
        }

    try:
        import importlib.util

        spec_p1 = importlib.util.spec_from_file_location(
            "authority_p1", SCRIPTS / "authority_enforce_p1_lib.py"
        )
        p1_mod = importlib.util.module_from_spec(spec_p1)
        spec_p1.loader.exec_module(p1_mod)  # type: ignore[union-attr]
        p1_mod.sync_reconciled_decision(
            next_sa=str(item.get("sa_id") or ""),
            note="pre_inject_deliver_current",
        )
        from execution_event_log_v1 import append_event  # noqa: WPS433

        append_event(
            event="DECISION_RECONCILED",
            actor="sourcea_execution_core",
            data={"sa_id": item.get("sa_id"), "pos": qi.get("pos")},
        )
    except Exception:
        pass

    body = _build_paste_body(qi)
    import os

    # Overnight: headless API/CLI. Worker awake or engines paused: disk INBOX.
    if _overnight_headless():
        inj = {"ok": True, "delivered": True, "mode": "overnight_headless", "skipped_inject": True}
    else:
        from worker_manual_only_v1 import is_manual_only, manual_hint  # noqa: WPS433

        if is_manual_only():
            inj = {
                "ok": True,
                "mode": "manual_only",
                "skipped_inject": True,
                "message": manual_hint(
                    sa_id=str(item.get("sa_id") or ""),
                    role=str(item.get("queue_role") or ""),
                    pos=f"{qi['pos']}/{qi['total']}",
                ),
            }
        else:
            worker_chat = (
                not fast
                and os.environ.get("SINA_WORKER_CHAT_RESUME_INJECT", "").strip().lower() in ("1", "true", "yes")
            )
            inj = inject_worker_prompt(
                body,
                source="healthy-drain-orchestrator",
                meta={
                    "queue_pos": qi["pos"],
                    "queue_total": qi["total"],
                    "queue_role": item.get("queue_role"),
                    "sa_id": item.get("sa_id"),
                },
                delivery_mode="worker_chat" if worker_chat else "auto",
                fast=fast,
            )

    baseline = _load(ROUND_REPORT).get("at") or ""
    overnight = _overnight_headless()
    manual = not overnight and inj.get("mode") == "manual_only"
    st.update(
        {
            "status": (
                "dispatching_overnight"
                if overnight
                else ("idle" if manual else "awaiting_worker")
            ),
            "delivered_at": _now(),
            "expected_pos": qi["pos"],
            "expected_sa": item.get("sa_id"),
            "expected_role": item.get("queue_role"),
            "report_baseline_at": baseline,
            "delivery": inj.get("delivered"),
            "clipboard_paste": False,
            "await_timeout_sec": DEFAULT_TURN_TIMEOUT_SEC,
            "overnight_no_worker": overnight,
        }
    )
    _save(st)
    deliver_ok = True if overnight or manual else bool(inj.get("ok"))
    return {"ok": deliver_ok, "deliver": inj, "state": st, "queue": qi, "overnight": overnight, "manual_only": manual}


def _round_type_role(rt: str) -> str:
    rt_map = {
        "audit": "check",
        "implement": "act",
        "verify": "verify",
        "check": "check",
        "act": "act",
    }
    return rt_map.get(str(rt or "").lower(), str(rt or "").lower())


def _report_matches(st: dict, report: dict) -> tuple[bool, str]:
    if report.get("status") != "WORKER_ROUND_REPORT":
        return False, "report_not_worker_round_report"
    at = report.get("at") or ""
    if not at or at == st.get("report_baseline_at"):
        return False, "no_new_report"
    sa = report.get("sa_focus") or ""
    if st.get("expected_sa") and sa != st.get("expected_sa"):
        return False, f"sa_mismatch expected={st.get('expected_sa')} got={sa}"
    report_role = _round_type_role(str(report.get("round_type") or ""))
    expected_role = _round_type_role(str(st.get("expected_role") or ""))
    if expected_role and report_role and report_role != expected_role:
        return False, f"role_mismatch expected={expected_role} got={report_role}"
    return True, "ok"


def _advance_after_turn(*, sa: str, pos: int, role: str, skip_slice: bool) -> dict:
    import subprocess

    subprocess.run(
        [sys.executable, str(SCRIPTS / "worker_turn_lib.py"), "--close", sa, "--force"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    adv_cmd = [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py")]
    if skip_slice:
        adv_cmd.append("--skip-sa-slice")
    proc = subprocess.run(adv_cmd, capture_output=True, text=True, timeout=30)
    try:
        adv = json.loads(proc.stdout) if proc.returncode == 0 else {"ok": False, "error": proc.stderr}
    except json.JSONDecodeError:
        adv = {"ok": False, "raw": proc.stdout}
    return {"ok": proc.returncode == 0, "advanced": adv}


def complete_overnight_turn(turn_result: dict) -> dict:
    """Advance queue after successful overnight API/CLI turn — fixes zero-advance spam."""
    if not _founder_absent():
        return {"ok": True, "skipped": True, "reason": "founder_busy_unchanged"}

    st = orchestrator_state()
    if st.get("status") not in ("awaiting_worker", "dispatching_overnight", "idle"):
        return {"ok": True, "skipped": True, "reason": "orchestrator_not_dispatching", "state": st}

    status = (turn_result.get("status") or "").upper()
    ok = bool(turn_result.get("ok"))
    if not ok or status != "PASS":
        return handle_turn_result(turn_result)

    sa = turn_result.get("sa_id") or st.get("expected_sa")
    pos = int(turn_result.get("pos") or st.get("expected_pos") or 1)
    qi = queue_item(pos=pos)
    item = qi.get("item") or {}
    role = item.get("queue_role") or st.get("expected_role") or "check"

    from healthy_queue_blocker_lib import blocker_after_check, record_blocker  # noqa: WPS433

    skip_slice = False
    if "check" in (role or "").lower():
        blocker = blocker_after_check(sa_id=sa, queue_role=role, queue_item=item)
        if blocker:
            record_blocker(blocker)
            skip_slice = True

    adv = _advance_after_turn(sa=sa, pos=pos, role=role, skip_slice=skip_slice)
    turns = int(st.get("turns_completed") or 0) + 1
    next_pos = (adv.get("advanced") or {}).get("next_pos")
    total = qi.get("total") or queue_item().get("total", 30)
    exhausted = isinstance(next_pos, int) and next_pos > total

    st.update(
        {
            "status": "done" if exhausted else "idle",
            "turns_completed": turns,
            "last_completed_at": _now(),
            "last_completed_sa": sa,
            "last_completed_role": role,
            "last_overnight_complete": status,
            "advanced": adv.get("advanced"),
            "stop_reason": None if not exhausted else "queue_exhausted",
        }
    )
    _save(st)

    try:
        from overnight_turn_guard_v1 import record_turn  # noqa: WPS433

        record_turn(
            sa_id=sa,
            role=role,
            pos=pos,
            engine=turn_result.get("engine") or "",
            ok=True,
            cost_usd=float(turn_result.get("cost_usd") or 0),
            status=status,
        )
    except Exception:
        pass

    return {
        "ok": adv.get("ok", False),
        "overnight_complete": True,
        "sa_id": sa,
        "role": role,
        "advanced": adv.get("advanced"),
        "state": st,
    }


def handle_turn_result(turn_result: dict) -> dict:
    """Overnight only: on BLOCKED/failed API/CLI turn, skip-advance without Worker."""
    if not _founder_absent():
        return {"ok": True, "skipped": True, "reason": "founder_busy_unchanged"}

    st = orchestrator_state()
    if st.get("status") not in ("awaiting_worker", "dispatching_overnight"):
        return {"ok": True, "skipped": True, "reason": "orchestrator_not_dispatching", "state": st}

    sa = turn_result.get("sa_id") or st.get("expected_sa")
    status = (turn_result.get("status") or "").upper()
    ok = bool(turn_result.get("ok"))
    blocked = status == "BLOCKED" or not ok
    if not blocked:
        return complete_overnight_turn(turn_result)

    pos = int(st.get("expected_pos") or turn_result.get("pos") or 1)
    qi = queue_item(pos=pos)
    item = qi.get("item") or {}
    role = item.get("queue_role") or st.get("expected_role") or "check"

    receipt_path = _write_skip_receipt(sa_id=sa, pos=pos, role=role, turn_result=turn_result)
    _log_overnight_skip(
        sa_id=sa,
        reason="BLOCKED_NO_WORKER",
        extra={"pos": pos, "role": role, "receipt": str(receipt_path)},
    )

    import subprocess

    # BLOCKED CHECK → advance by 1 only (CLI will take ACT next tick)
    # BLOCKED ACT or VERIFY → skip entire slice (unrecoverable without Worker)
    role_lower = (role or "").lower()
    skip_slice = "act" in role_lower or "verify" in role_lower
    adv_cmd = [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py")]
    if skip_slice:
        adv_cmd.append("--skip-sa-slice")
    proc = subprocess.run(adv_cmd, capture_output=True, text=True, timeout=30)
    try:
        adv = json.loads(proc.stdout) if proc.returncode == 0 else {"ok": False, "error": proc.stderr}
    except json.JSONDecodeError:
        adv = {"ok": False, "raw": proc.stdout}

    turns = int(st.get("turns_completed") or 0) + 1
    next_pos = adv.get("next_pos")
    total = qi.get("total") or queue_item().get("total", 30)
    exhausted = isinstance(next_pos, int) and next_pos > total

    st.update(
        {
            "status": "done" if exhausted else "idle",
            "turns_completed": turns,
            "last_completed_at": _now(),
            "last_completed_sa": sa,
            "last_completed_role": role,
            "last_overnight_skip": "BLOCKED_NO_WORKER",
            "skip_receipt": str(receipt_path),
            "advanced": adv,
            "stop_reason": None if not exhausted else "queue_exhausted",
        }
    )
    _save(st)

    return {
        "ok": proc.returncode == 0,
        "overnight_skip": True,
        "reason": "BLOCKED_NO_WORKER",
        "sa_id": sa,
        "skip_receipt": str(receipt_path),
        "advanced": adv,
        "state": st,
    }


def complete_if_ready() -> dict:
    """Verifier gate: advance only when disk report matches bound queue item."""
    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_blocker_lib import blocker_after_check, record_blocker  # noqa: WPS433

    st = orchestrator_state()
    if st.get("status") != "awaiting_worker":
        return {"ok": False, "error": "not_awaiting_worker", "state": st}

    report = _load(ROUND_REPORT)
    ok, reason = _report_matches(st, report)
    if not ok:
        return {"ok": False, "waiting": True, "reason": reason, "state": st}

    item = queue_item(pos=int(st.get("expected_pos") or 1)).get("item") or {}
    role = item.get("queue_role") or st.get("expected_role") or "check"
    sa = st.get("expected_sa") or report.get("sa_focus")

    fast = _commercial_fast()

    import subprocess

    # Close turn + commercial blocker skip (CHECK → STOP, no ACT)
    if not fast:
        subprocess.run(
            [sys.executable, str(SCRIPTS / "worker_turn_lib.py"), "--close", sa, "--force"],
            capture_output=True,
            text=True,
            timeout=30,
        )

    blocker = blocker_after_check(sa_id=sa, queue_role=role, queue_item=item)
    skip_slice = bool(blocker)
    if blocker:
        record_blocker(blocker)

    adv_cmd = [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py")]
    if skip_slice:
        adv_cmd.append("--skip-sa-slice")
    if fast:
        adv_cmd.append("--fast")
    proc = subprocess.run(adv_cmd, capture_output=True, text=True, timeout=30)
    try:
        adv = json.loads(proc.stdout) if proc.returncode == 0 else {"ok": False, "error": proc.stderr}
    except json.JSONDecodeError:
        adv = {"raw": proc.stdout}

    turns = int(st.get("turns_completed") or 0) + 1
    next_pos = adv.get("next_pos")
    total = queue_item().get("total", 30)
    exhausted = isinstance(next_pos, int) and next_pos > total

    st.update(
        {
            "turns_completed": turns,
            "last_completed_at": _now(),
            "last_completed_sa": sa,
            "last_completed_role": role,
            "last_report_at": report.get("at"),
            "commercial_blocker": blocker,
            "advanced": adv,
            "stop_reason": None if not exhausted else "queue_exhausted",
        }
    )
    if exhausted:
        st["status"] = "done"
        _save(st)
    deliver_out: dict = {}
    if exhausted:
        pass
    elif proc.returncode == 0:
        from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: WPS433

        clear_inject_lock()
        deliver_out = deliver_current(force=True, fast=fast)
        st = orchestrator_state()
        if not deliver_out.get("ok"):
            st["status"] = "idle"
            _save(st)
    else:
        st["status"] = "idle"
        _save(st)

    out = {
        "ok": proc.returncode == 0,
        "completed": True,
        "sa_id": sa,
        "role": role,
        "skip_act_verify": skip_slice,
        "advanced": adv,
        "state": orchestrator_state(),
        "done_all_30": exhausted,
    }

    if not exhausted and proc.returncode == 0:
        out["next_deliver"] = deliver_out

    brain_sync: dict = {}
    import os

    if os.environ.get("SINA_BROKER_FAST", "").strip().lower() in ("1", "true", "yes"):
        brain_sync = {"ok": True, "skipped": "broker_fast"}
    else:
        try:
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            brain_sync = sync_brain_snapshot(
                mode="full" if exhausted else "light",
                caller=f"complete_if_ready:{sa}",
            )
        except Exception as exc:
            brain_sync = {"ok": False, "error": str(exc)}
    out["brain_sync"] = brain_sync
    return out


def poll_once() -> dict:
    st = orchestrator_state()
    if st.get("status") != "awaiting_worker":
        if st.get("status") == "idle":
            report = _load(ROUND_REPORT)
            if report.get("status") == "WORKER_ROUND_REPORT" and report.get("at"):
                if report.get("at") != st.get("report_baseline_at"):
                    rt_map = {
                        "audit": "check",
                        "implement": "act",
                        "verify": "verify",
                        "check": "check",
                    }
                    heal_role = rt_map.get(
                        str(report.get("round_type") or "").lower(),
                        str(report.get("round_type") or "").lower(),
                    )
                    heal_sa = report.get("sa_focus") or st.get("expected_sa")
                    heal_pos = int(st.get("expected_pos") or 0)
                    qpath = QUEUE_HOME if QUEUE_HOME.is_file() else QUEUE_REPO
                    if qpath.is_file() and heal_sa and heal_role:
                        try:
                            for row in json.loads(qpath.read_text()).get("queue") or []:
                                if row.get("sa_id") == heal_sa and row.get("queue_role") == heal_role:
                                    heal_pos = int(row.get("queue_pos") or heal_pos)
                                    break
                        except (OSError, json.JSONDecodeError, ValueError, TypeError):
                            pass
                    heal = dict(st)
                    heal.update(
                        {
                            "status": "awaiting_worker",
                            "expected_pos": heal_pos or heal.get("expected_pos"),
                            "expected_sa": heal_sa,
                            "expected_role": heal_role or heal.get("expected_role"),
                        }
                    )
                    ok, _reason = _report_matches(heal, report)
                    if ok:
                        _save(heal)
                        return complete_if_ready()
        return {"ok": True, "idle": True, "state": st}
    delivered = st.get("delivered_at") or ""
    report = _load(ROUND_REPORT)
    ok_match, _match_reason = _report_matches(st, report)
    if ok_match:
        return complete_if_ready()

    if delivered:
        try:
            dt = datetime.fromisoformat(delivered.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
            limit = float(st.get("await_timeout_sec") or DEFAULT_TURN_TIMEOUT_SEC)
            if elapsed > limit * 0.5 and not _commercial_fast():
                sys.path.insert(0, str(SCRIPTS))
                from worker_stuck_recovery_v1 import run_recovery  # noqa: WPS433

                run_recovery(redeliver=False)
            if elapsed > limit:
                from worker_stuck_recovery_v1 import heal_orchestrator_timeout, replay_pending_inbox  # noqa: WPS433

                healed = heal_orchestrator_timeout(redeliver=True)
                replay = replay_pending_inbox()
                st = orchestrator_state()
                return {
                    "ok": True,
                    "recovered": True,
                    "reason": "turn_timeout_auto_heal",
                    "elapsed_sec": elapsed,
                    "healed": healed,
                    "inbox_replay": replay,
                    "state": st,
                }
        except ValueError:
            pass
    return complete_if_ready()


def watch(
    *,
    poll_sec: float = DEFAULT_POLL_SEC,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> int:
    """Semi-unattended loop — waits for real report before each advance."""
    st = orchestrator_state()
    if st.get("status") == "idle":
        first = deliver_current()
        print(json.dumps(first, indent=2), flush=True)
        if not first.get("ok"):
            return 1

    turns = int(st.get("turns_completed") or 0)
    while turns < max_turns:
        st = orchestrator_state()
        if st.get("status") in ("stopped", "done"):
            print(json.dumps({"watch": "halt", "state": st}, indent=2))
            return 0 if st.get("status") == "done" else 1

        result = poll_once()
        print(json.dumps(result, indent=2), flush=True)

        if result.get("completed"):
            turns = int((result.get("state") or {}).get("turns_completed") or turns + 1)
            if result.get("done_all_30"):
                return 0
        elif result.get("waiting"):
            time.sleep(poll_sec)
        elif result.get("idle"):
            deliver = deliver_current()
            print(json.dumps(deliver, indent=2), flush=True)
            if not deliver.get("ok"):
                return 1
            time.sleep(poll_sec)
        else:
            time.sleep(poll_sec)
    print(json.dumps({"watch": "max_turns", "turns": turns}, indent=2))
    return 0


def status() -> dict:
    st = orchestrator_state()
    qi = queue_item()
    return {
        "ok": True,
        "orchestrator": st,
        "queue_item": qi.get("item"),
        "queue_pos": qi.get("pos"),
        "queue_total": qi.get("total"),
        "round_report": _load(ROUND_REPORT),
        "brief": _brief(st, qi),
    }


def _brief(st: dict, qi: dict) -> str:
    item = qi.get("item") or {}
    pos = qi.get("pos") or "?"
    total = qi.get("total") or 30
    role = (item.get("queue_role") or "?").upper()
    sa = item.get("sa_id") or "—"
    phase = st.get("status") or "idle"
    if phase == "awaiting_worker":
        return f"Queue {pos}/{total} · {role} · {sa} · AWAITING Worker INBOX"
    if phase == "stopped":
        return f"STOPPED · {st.get('stop_reason') or 'unknown'}"
    return f"Queue {pos}/{total} · {role} · {sa} · Worker INBOX ready"


def reset(*, reason: str = "manual") -> dict:
    st = {
        "schema": "healthy-drain-orchestrator-v1",
        "status": "idle",
        "turns_completed": 0,
        "max_turns": DEFAULT_MAX_TURNS,
        "reset_at": _now(),
        "reset_reason": reason,
    }
    _save(st)
    return {"ok": True, "state": st}


def main() -> int:
    p = argparse.ArgumentParser(description="Goal 1 healthy drain orchestrator (wait-on-report)")
    p.add_argument("cmd", nargs="?", default="status", choices=("status", "deliver", "poll", "watch", "reset"))
    p.add_argument("--poll-sec", type=float, default=DEFAULT_POLL_SEC)
    p.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    sys.path.insert(0, str(SCRIPTS))
    from agent_cancel_guard_v1 import agent_cancel_active, agent_cancel_skip, write_cancel_receipt  # noqa: WPS433

    if args.cmd not in ("status", "reset") and agent_cancel_active():
        write_cancel_receipt(caller=f"healthy-drain-orchestrator:{args.cmd}")
        out = agent_cancel_skip(caller=f"healthy-drain-orchestrator:{args.cmd}")
        print(json.dumps(out, indent=2))
        return 0

    if args.cmd == "status":
        print(json.dumps(status(), indent=2))
        return 0
    if args.cmd == "deliver":
        print(json.dumps(deliver_current(force=args.force), indent=2))
        return 0
    if args.cmd == "poll":
        print(json.dumps(poll_once(), indent=2))
        return 0
    if args.cmd == "watch":
        return watch(poll_sec=args.poll_sec, max_turns=args.max_turns)
    if args.cmd == "reset":
        print(json.dumps(reset(), indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
