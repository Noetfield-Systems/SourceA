#!/usr/bin/env python3
"""Goal 1 lane broker — Worker YAML ↔ disk ↔ Brain ack ↔ next INBOX.

Why: INBOX-only delivery does not auto-run Worker chat. Broker closes the loop:
  Worker STOP + YAML → broker → orchestrator advance → Brain poll/ack → next INBOX

Law: SINA_GOAL1_OPERATING_MODEL_LOCKED_v1.md · GOAL_EXECUTION_ACTIVE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BROKER_STATE = Path.home() / ".sina" / "goal1-lane-broker-v1.json"
BROKER_EVENTS = Path.home() / ".sina" / "goal1-lane-broker-events.jsonl"
BRAIN_INBOX = Path.home() / ".sina" / "brain-broker-inbox-v1.json"
CHECKPOINT_PATH = Path.home() / ".sina" / "goal1-batch-checkpoint-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _append_event(kind: str, payload: dict) -> dict:
    row = {"at": _now(), "kind": kind, **payload}
    BROKER_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with BROKER_EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    try:
        sys.path.insert(0, str(SCRIPTS))
        from execution_event_log_v1 import append_event  # noqa: WPS433

        append_event(
            event=kind,
            actor=str(payload.get("actor") or "broker_validators"),
            trace_id=str(payload.get("trace_id") or ""),
            data=payload,
        )
    except Exception:
        pass
    return row


def append_spine_worker_round(
    *,
    sa: str,
    round_type: str,
    orch_ok: bool | None = None,
    deliver_ok: bool | None = None,
    source: str = "worker_chat",
) -> dict:
    """G4 — governance spine WORKER_ROUND (never silent fail)."""
    try:
        sys.path.insert(0, str(SCRIPTS))
        from governance_event_spine_v1 import append_event as spine_append  # noqa: WPS433

        res = spine_append(
            event_type="WORKER_ROUND",
            object_id=sa,
            object_kind="task",
            agent_id="sourcea_worker",
            law_id="GOV_EVENT_SPINE",
            skill_id="goal1-lane-broker",
            validator_set=["validate-governance-event-spine-v1.sh"],
            affected_objects=[sa, "projection:hub", "projection:monitor", "projection:truth_bundle"],
            payload={
                "round_type": round_type,
                "orch_ok": orch_ok,
                "deliver_ok": deliver_ok,
                "source": source,
            },
            projection_targets=["hub", "monitor", "truth_bundle"],
            gate="goal1_lane_broker:worker-submit",
            proof=str(BROKER_EVENTS),
        )
    except Exception as exc:
        res = {"ok": False, "error": str(exc)}
    if res.get("ok"):
        ev = res.get("event") or {}
        _append_event(
            "SPINE_WORKER_ROUND",
            {
                "sa": sa,
                "round_type": round_type,
                "event_id": ev.get("event_id"),
                "replay_pointer": ev.get("replay_pointer"),
            },
        )
    else:
        _append_event(
            "SPINE_WORKER_ROUND_FAIL",
            {"sa": sa, "round_type": round_type, "error": res.get("error")},
        )
    return res


def _maybe_spine_worker_round(
    *,
    fast: bool,
    sa: str,
    round_type: str,
    orch_ok: bool | None,
    deliver_ok: bool | None,
    source: str,
) -> dict:
    if fast and round_type.lower() != "verify":
        return {"ok": True, "skipped": "broker_fast"}
    return append_spine_worker_round(
        sa=sa,
        round_type=round_type,
        orch_ok=orch_ok,
        deliver_ok=deliver_ok,
        source=source,
    )


def broker_state() -> dict:
    st = _load(BROKER_STATE)
    if not st:
        st = {
            "schema": "goal1-lane-broker-v1",
            "status": "idle",
            "updated_at": _now(),
        }
    return st


def _save_broker(st: dict) -> dict:
    st["updated_at"] = _now()
    _save(BROKER_STATE, st)
    return st


def _parse_yaml_loose(text: str) -> dict:
    """Minimal YAML-ish parser for WORKER_ROUND_REPORT blocks (no PyYAML dep)."""
    out: dict = {}
    current_key = None
    current_list: list | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            if current_list is None:
                current_list = []
                out[current_key] = current_list
            current_list.append(line.strip()[2:].strip())
            continue
        current_list = None
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if not val:
            current_key = key
            out[key] = {}
            continue
        current_key = key
        if val.lower() in ("true", "false"):
            out[key] = val.lower() == "true"
        elif val.isdigit():
            out[key] = int(val)
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            out[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        else:
            out[key] = val.strip("'\"")
    return out


def _normalize_worker_report(parsed: dict, text: str) -> dict:
    """Accept flat or nested agent YAML — broker must not miss valid turns."""
    out = dict(parsed or {})
    for key in ("WORKER_ROUND_REPORT", "WORKER_ROUND_REPORT:"):
        nested = out.get(key)
        if isinstance(nested, dict) and nested:
            out = {
                **nested,
                "status": "WORKER_ROUND_REPORT",
                **{k: v for k, v in out.items() if k not in ("WORKER_ROUND_REPORT", "WORKER_ROUND_REPORT:")},
            }
            break
    status = str(out.get("status") or "").strip()
    if status.rstrip(":") == "WORKER_ROUND_REPORT":
        out["status"] = "WORKER_ROUND_REPORT"
    if not out.get("sa_focus"):
        m = re.search(r"sa_focus:\s*[\"']?(sa-\d+)", text, re.I)
        if m:
            out["sa_focus"] = m.group(1)
    if not out.get("round_type"):
        m = re.search(r"round_type:\s*(\w+)", text, re.I)
        if m:
            out["round_type"] = m.group(1)
    if not out.get("status") and re.search(r"WORKER_ROUND_REPORT", text, re.I):
        if out.get("sa_focus") or out.get("round_type") or out.get("validate"):
            out["status"] = "WORKER_ROUND_REPORT"
    return out


def _extract_report_blob(text: str) -> dict:
    blocks = re.findall(
        r"```ya?ml\s*\n(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    candidates: list[dict] = []
    for blob in blocks or [text]:
        if "status:" not in blob and "WORKER_ROUND_REPORT" not in blob:
            continue
        candidates.append(_normalize_worker_report(_parse_yaml_loose(blob), blob))
    if not candidates:
        if "WORKER_ROUND_REPORT" not in text:
            return {}
        return _normalize_worker_report(_parse_yaml_loose(text), text)
    for row in reversed(candidates):
        if str(row.get("status") or "").rstrip(":") == "WORKER_ROUND_REPORT" or row.get("sa_focus"):
            return row
    return _normalize_worker_report(candidates[-1], text)


def _inbox_prompt_text() -> str:
    inbox_json = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
    if not inbox_json.is_file():
        return ""
    try:
        return str(json.loads(inbox_json.read_text(encoding="utf-8")).get("prompt") or "")
    except (OSError, json.JSONDecodeError):
        return ""


def _resolve_expected_sa(
    *,
    report_sa: str,
    source: str,
    inbox_pre: dict,
) -> dict:
    """Bind sa_focus to INBOX meta sa_id — prompt header wins over drifted meta."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import heal_inbox_meta, load_turn_bind, normalize_sa_id, parse_prompt_bind_sa  # noqa: WPS433

    prompt = _inbox_prompt_text()
    prompt_sa = parse_prompt_bind_sa(prompt)
    healed = heal_inbox_meta(inbox_pre.get("meta") or {}, prompt)
    meta_sa = normalize_sa_id(str(healed.get("sa_id") or inbox_pre.get("sa_id") or ""))
    bind_sa = str((load_turn_bind() or {}).get("sa_id") or "")

    expected = ""
    bind_source = "none"
    if bind_sa:
        expected = normalize_sa_id(bind_sa)
        bind_source = "turn_bind"
    elif prompt_sa:
        expected = normalize_sa_id(prompt_sa)
        bind_source = "prompt_header"
    elif meta_sa:
        expected = meta_sa
        bind_source = "inbox_meta"
    elif source == "agent_cli":
        try:
            import importlib.util

            spec_orch = importlib.util.spec_from_file_location(
                "orch", SCRIPTS / "healthy-drain-orchestrator-v1.py"
            )
            orch_mod = importlib.util.module_from_spec(spec_orch)
            spec_orch.loader.exec_module(orch_mod)  # type: ignore[union-attr]
            orch_sa = str((orch_mod.orchestrator_state() or {}).get("expected_sa") or "")
            if orch_sa.startswith("sa-"):
                expected = orch_sa
                bind_source = "orchestrator"
        except Exception:
            pass
    if not expected and report_sa.startswith("sa-"):
        expected = report_sa
        bind_source = "report_sa"

    match = (
        not expected
        or report_sa.lower() == expected.lower()
        or (prompt_sa and report_sa.lower() == normalize_sa_id(prompt_sa).lower())
        or (bind_sa and report_sa.lower() == normalize_sa_id(bind_sa).lower())
    )
    return {
        "expected_sa": expected,
        "bind_source": bind_source,
        "prompt_sa": prompt_sa,
        "meta_sa": meta_sa,
        "bind_sa": bind_sa,
        "match": match,
    }


def check_stdin_report(*, text: str, source: str = "worker_chat") -> dict:
    """Parse WORKER_ROUND_REPORT from stdin and verify sa_focus vs INBOX bind."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    parsed = _normalize_worker_report(_extract_report_blob(text), text)
    status = str(parsed.get("status") or "").rstrip(":")
    if status != "WORKER_ROUND_REPORT":
        return {
            "ok": False,
            "error": "missing WORKER_ROUND_REPORT",
            "parsed": parsed,
        }
    sa = str(parsed.get("sa_focus") or parsed.get("sa_id") or "")
    if not sa.startswith("sa-"):
        return {"ok": False, "error": "sa_focus required", "parsed": parsed}
    inbox_pre = inbox_status()
    bind = _resolve_expected_sa(report_sa=sa, source=source, inbox_pre=inbox_pre)
    return {
        "ok": bool(bind.get("match")),
        "status": "STDIN_PARSE_CHECK",
        "sa_focus": sa,
        "parsed": parsed,
        "bind": bind,
    }


def load_checkpoint() -> dict:
    return _load(CHECKPOINT_PATH)


def start_batch(*, batch_size: int = 5) -> dict:
    st = broker_state()
    st.update(
        {
            "status": "batch_running",
            "batch": {
                "batch_size": min(max(1, batch_size), 10),
                "turns_in_batch": 0,
                "checkpoints_completed": int((st.get("batch") or {}).get("checkpoints_completed") or 0),
                "recent_turns": [],
                "started_at": _now(),
            },
        }
    )
    _save_broker(st)
    _append_event("BATCH_START", {"batch_size": batch_size})
    return {"ok": True, "batch": st["batch"]}


def _broker_founder_action(inbox: dict) -> str:
    """Auto Runtime smart loop owns next motion — never Hub Deliver when auto ON."""
    sys.path.insert(0, str(SCRIPTS))
    try:
        from execution_path_vocabulary_v1 import execute_line, loop_auto_on  # noqa: WPS433

        if loop_auto_on():
            return execute_line()
    except Exception:
        pass
    if inbox.get("pending"):
        return "Auto Runtime · Worker inbox pending · specialist tick dispatch"
    return "Auto Runtime specialist auto-tick · smart loop owns queue motion"


def _auto_deliver_next() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    if inbox.get("pending"):
        return {"ok": True, "skipped": "inbox_already_pending", "inbox": inbox}
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "orch", SCRIPTS / "healthy-drain-orchestrator-v1.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        orch_st = mod.orchestrator_state() or {}
        if orch_st.get("status") in ("idle", "awaiting_worker"):
            if orch_st.get("status") == "stopped":
                mod.reset(reason="batch_auto_deliver")
            deliver = mod.deliver_current(force=orch_st.get("status") != "awaiting_worker", fast=True)
            return {"ok": deliver.get("ok", False), "deliver": deliver, "inbox": inbox_status()}
    except Exception as exc:
        from worker_drain_lib import healthy_drain_paste  # noqa: WPS433

        import os

        os.environ.setdefault("SINA_WORKER_CHAT_RESUME_INJECT", "1")
        d = healthy_drain_paste(worker_chat_inject=True)
        return {"ok": d.get("ok", False), "deliver": d, "error": str(exc)}
    return {"ok": False, "error": "deliver_failed"}


def _turn_summary(parsed: dict, sa: str, round_type: str) -> dict:
    validate = parsed.get("validate") if isinstance(parsed.get("validate"), dict) else {}
    return {
        "sa_focus": sa,
        "round_type": round_type,
        "at": _now(),
        "spine": validate.get("spine", "?"),
        "critical_bugs": int(validate.get("critical_bugs") or 0),
        "gate": validate.get("gate", "?"),
    }


def _checkpoint_machine_pass(turns: list[dict]) -> bool:
    if not turns:
        return False
    for t in turns:
        if int(t.get("critical_bugs") or 0) > 0:
            return False
        spine = str(t.get("spine") or "").upper()
        if spine == "FAIL":
            return False
        gate = str(t.get("gate") or "").upper()
        if gate == "FAIL":
            return False
    return True


def worker_submit(
    *,
    text: str,
    source: str = "worker_chat",
    auto_advance: bool = False,
    checkpoint: bool = False,
    fast: bool | None = None,
) -> dict:
    import os

    if fast is None:
        fast = os.environ.get("SINA_BROKER_FAST", "1").strip().lower() in ("1", "true", "yes")
    if fast:
        os.environ["SINA_BROKER_FAST"] = "1"
        os.environ["SINA_COMMERCIAL_LOOP"] = "1"

    sys.path.insert(0, str(SCRIPTS))
    from worker_turn_lib import close_turn, write_round_report  # noqa: WPS433
    from worker_inject_lib import clear_inbox, inbox_status  # noqa: WPS433

    parsed = _normalize_worker_report(_extract_report_blob(text), text)
    status = str(parsed.get("status") or "")
    if not status or status.rstrip(":") != "WORKER_ROUND_REPORT":
        if parsed.get("sa") and not parsed.get("sa_focus"):
            parsed["sa_focus"] = parsed.get("sa")
        if parsed.get("role") and not parsed.get("round_type"):
            parsed["round_type"] = parsed.get("role")
    status = str(parsed.get("status") or "")
    if status.rstrip(":") != "WORKER_ROUND_REPORT":
        return {
            "ok": False,
            "error": "missing WORKER_ROUND_REPORT status in YAML",
            "hint": "End Worker turn with status: WORKER_ROUND_REPORT block",
        }

    sa = str(parsed.get("sa_focus") or parsed.get("sa_id") or "")
    round_type = str(parsed.get("round_type") or "check")
    rt_norm = round_type.lower().strip()
    if rt_norm in ("implement",):
        round_type = "act"
        rt_norm = "act"
    if rt_norm in ("closeout", "done", "complete", "verify_backend"):
        return {
            "ok": False,
            "error": "CLOSEOUT_WITHOUT_BROKER_VERIFY",
            "hint": "round_type must be check | act | verify. REGISTRY done only on broker VERIFY + receipt.",
            "got": round_type,
        }
    if rt_norm not in ("check", "act", "verify"):
        return {
            "ok": False,
            "error": "INVALID_ROUND_TYPE",
            "hint": "round_type must be check | act | verify",
            "got": round_type,
        }

    sys.path.insert(0, str(SCRIPTS))
    from registry_honest_lib_v1 import enforce_honest_registry  # noqa: WPS433

    honest = enforce_honest_registry(dry_run=False)
    if not (honest.get("after") or {}).get("ok", True) and (honest.get("after") or {}).get("unproven_done"):
        return {
            "ok": False,
            "error": "REGISTRY_UNPROVEN_DONE",
            "hint": "Run worker_factory_heal_v1.py — done rows without receipt reverted",
            "honest": honest,
        }

    critical = int(parsed.get("critical_bugs") or parsed.get("verify", {}).get("critical_bugs", 0) if isinstance(parsed.get("verify"), dict) else parsed.get("critical_bugs") or 0)
    if isinstance(parsed.get("validate"), dict):
        critical = int(parsed["validate"].get("critical_bugs") or critical)

    if not sa.startswith("sa-"):
        return {"ok": False, "error": "sa_focus required (sa-XXXX)"}

    if sa.endswith("-TEST") or sa == "sa-TEST":
        return {
            "ok": False,
            "error": "sa-TEST rejected — stale test inject; re-run turn on live INBOX sa",
        }

    inbox_pre = inbox_status()
    bind = _resolve_expected_sa(report_sa=sa, source=source, inbox_pre=inbox_pre)
    expected_sa = str(bind.get("expected_sa") or "")
    if expected_sa.startswith("sa-") and not bind.get("match"):
        return {
            "ok": False,
            "error": f"sa_mismatch expected={expected_sa} got={sa}",
            "hint": "YAML sa_focus must match INBOX meta sa_id (prompt header / turn bind)",
            "bind": bind,
        }

    import importlib.util

    spec_p1 = importlib.util.spec_from_file_location(
        "authority_p1", SCRIPTS / "authority_enforce_p1_lib.py"
    )
    p1_mod = importlib.util.module_from_spec(spec_p1)
    spec_p1.loader.exec_module(p1_mod)  # type: ignore[union-attr]
    ptr_gate = p1_mod.check_pointer_alignment(sa_id=sa)
    p1_mod.touch_execution(status="SUBMITTING", sa_id=sa, worker_id="sourcea_worker")

    def _p1_finish_submit() -> None:
        p1_mod.touch_execution(status="IDLE", sa_id=None, worker_id=None)
        try:
            subprocess.run(
                [sys.executable, str(SCRIPTS / "sync_next_execution_pointer_v1.py")],
                cwd=str(ROOT),
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception:
            pass
        try:
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "governance_propagation_cascade_v1.py"),
                    "--reason",
                    "worker_round_complete",
                    "--fast",
                ],
                cwd=str(ROOT),
                capture_output=True,
                timeout=15,
                check=False,
            )
        except Exception:
            pass

    # Headless VERIFY closeout may open next-pick turn before broker ingests report.
    if source == "agent_cli" and sa.startswith("sa-"):
        from worker_turn_lib import close_turn as _close_turn, turn_open_block as _turn_open_block, turn_state as _turn_state  # noqa: WPS433

        if _turn_open_block():
            open_sa = str((_turn_state() or {}).get("sa_id") or "")
            if open_sa.startswith("sa-") and open_sa != sa:
                _close_turn(sa_id=open_sa, force=True)
                expected_sa = sa

    gate_mod = importlib.util.spec_from_file_location(
        "one_sa_gate", SCRIPTS / "one_sa_per_turn_gate_v1.py"
    )
    gate_m = importlib.util.module_from_spec(gate_mod)
    gate_mod.loader.exec_module(gate_m)  # type: ignore[union-attr]
    one_sa = gate_m.guard_broker_submit(text=text, expected_sa=expected_sa or sa)
    if not one_sa.get("ok"):
        return {
            "ok": False,
            "error": one_sa.get("error") or one_sa.get("status"),
            "one_sa_gate": one_sa,
            "hint": "One sa per turn — close prior turn; single WORKER_ROUND_REPORT only",
        }

    report = write_round_report(sa_id=sa, round_type=round_type, critical=critical)
    close_turn(sa_id=sa, round_type=round_type, critical=critical, force=True)
    clear_inbox(reason="broker_worker_submit")
    from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: WPS433

    clear_inject_lock()

    spec = importlib.util.spec_from_file_location(
        "orch", SCRIPTS / "healthy-drain-orchestrator-v1.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    orch_before = mod.status()
    orch_st_before = (orch_before or {}).get("orchestrator") or orch_before or {}
    if orch_st_before.get("status") == "idle":
        role_map = {"audit": "check", "implement": "act", "verify": "verify", "check": "check"}
        heal_role = role_map.get(round_type.lower(), round_type.lower())
        heal_pos = 0
        heal_st = dict(orch_st_before)
        try:
            qpath = Path.home() / ".sina" / "healthy-queue-30-active.json"
            if qpath.is_file():
                for row in json.loads(qpath.read_text()).get("queue") or []:
                    if row.get("sa_id") == sa and row.get("queue_role") == heal_role:
                        heal_pos = int(row.get("queue_pos") or 0)
                        break
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            pass
        if not heal_pos:
            qi_heal = mod.queue_item()
            heal_pos = int(qi_heal.get("pos") or 0)
        heal_st.update(
            {
                "status": "awaiting_worker",
                "expected_pos": heal_pos,
                "expected_sa": sa,
                "expected_role": heal_role,
                "report_baseline_at": heal_st.get("report_baseline_at")
                or heal_st.get("last_report_at")
                or "",
            }
        )
        mod._save(heal_st)
        orch_st_before = heal_st
    orch_result = mod.poll_once()
    orch_status = mod.status

    closeout_result = None
    if round_type.lower() == "verify" and critical == 0:
        orch_role = str(orch_st_before.get("expected_role") or "").lower()
        if orch_role != "verify":
            closeout_result = {
                "ok": False,
                "error": "CLOSEOUT_ILLEGAL_ORCH_ROLE",
                "expected_role": orch_role,
                "hint": "Closeout only when INBOX orchestrator expected_role is verify",
            }
        else:
            from closeout_sa_task import ReceiptGateError, closeout  # noqa: WPS433
            from worker_receipt_v1 import write_receipt  # noqa: WPS433

            evidence = str(
                parsed.get("summary")
                or parsed.get("evidence")
                or (parsed.get("validate") or {}).get("summary")
                or "VERIFY PASS — goal1_lane_broker worker-submit"
            )
            rec = write_receipt(
                sa_id=sa,
                round_type="verify",
                critical_bugs=0,
                evidence=evidence[:500],
                source="goal1_lane_broker",
            )
            if rec.get("ok"):
                try:
                    closeout_result = closeout(
                        task_id=sa,
                        evidence=evidence,
                        authorized_source="goal1_lane_broker",
                        round_type="verify",
                        critical_bugs=0,
                    )
                except ReceiptGateError as exc:
                    closeout_result = {"ok": False, "error": str(exc), "gate": "receipt_hard"}
            else:
                closeout_result = {
                    "ok": False,
                    "error": rec.get("error") or "RECEIPT_WRITE_FAILED",
                    "hint": "Honest done requires receipts/sa-XXXX-receipt.json from broker VERIFY",
                }

    outbound_post_ship: dict = {"skipped": True}
    if round_type.lower() == "verify" and critical == 0 and (closeout_result or {}).get("ok"):
        try:
            from outbound_post_ship_v1 import post_ship_after_verify  # noqa: WPS433

            outbound_post_ship = post_ship_after_verify(sa_id=sa)
        except Exception as exc:
            outbound_post_ship = {"ok": False, "error": str(exc)}

    inbox = inbox_status()
    st = broker_state()
    turn_row = _turn_summary(parsed, sa, round_type)
    batch = dict(st.get("batch") or {})
    recent = list(batch.get("recent_turns") or [])
    recent.append(turn_row)
    batch["recent_turns"] = recent[-10:]
    batch["turns_in_batch"] = int(batch.get("turns_in_batch") or 0) + 1

    base_update = {
        "last_worker_report": {**parsed, **report},
        "last_worker_source": source,
        "orchestrator_result": orch_result,
        "orchestrator_snapshot": orch_status() if callable(locals().get("orch_status")) else {},
        "inbox_after": inbox,
        "batch": batch,
        "closeout_result": closeout_result,
        "outbound_post_ship": outbound_post_ship,
    }

    if auto_advance and not checkpoint:
        deliver = _auto_deliver_next()
        inbox = inbox_status()
        st.update(
            {
                **base_update,
                "status": "batch_running",
                "last_auto_deliver": deliver,
                "inbox_after": inbox,
            }
        )
        _save_broker(st)
        _append_event("WORKER_SUBMIT_AUTO", {"sa": sa, "round_type": round_type, "orch_ok": orch_result.get("ok")})
        spine = _maybe_spine_worker_round(
            fast=fast,
            sa=sa,
            round_type=round_type,
            orch_ok=orch_result.get("ok"),
            deliver_ok=deliver.get("ok"),
            source=source,
        )
        _p1_finish_submit()
        return {
            "ok": True,
            "broker_status": "batch_running",
            "auto_advance": True,
            "report": report,
            "orchestrator": orch_result,
            "deliver": deliver,
            "inbox_pending": inbox.get("pending"),
            "authority_pointer": ptr_gate,
            "spine": spine,
        }

    if checkpoint:
        batch_size = int(batch.get("batch_size") or 5)
        checkpoint_payload = {
            "schema": "goal1-batch-checkpoint-v1",
            "at": _now(),
            "batch_size": batch_size,
            "turns": recent[-batch_size:],
            "machine_pass": _checkpoint_machine_pass(recent[-batch_size:]),
            "orchestrator": orch_result,
            "last_sa": sa,
        }
        _save(CHECKPOINT_PATH, checkpoint_payload)
        batch["turns_in_batch"] = 0
        batch["checkpoints_completed"] = int(batch.get("checkpoints_completed") or 0) + 1
        batch["recent_turns"] = []

        if checkpoint_payload["machine_pass"]:
            deliver = _auto_deliver_next()
            inbox = inbox_status()
            st.update(
                {
                    **base_update,
                    "status": "batch_running",
                    "batch": batch,
                    "last_checkpoint": checkpoint_payload,
                    "last_auto_deliver": deliver,
                    "inbox_after": inbox,
                }
            )
            _save_broker(st)
            _append_event("CHECKPOINT_AUTO_PASS", {"sa": sa, "n": batch["checkpoints_completed"]})
            spine = _maybe_spine_worker_round(
                fast=fast,
                sa=sa,
                round_type=round_type,
                orch_ok=orch_result.get("ok"),
                deliver_ok=deliver.get("ok"),
                source=source,
            )
            brain_note = {
                "schema": "brain-broker-inbox-v1",
                "at": _now(),
                "status": "checkpoint_advisory",
                "checkpoint": checkpoint_payload,
                "founder_action": "Brain optional async review — Worker batch continues",
            }
            _save(BRAIN_INBOX, brain_note)
            return {
                "ok": True,
                "broker_status": "batch_running",
                "checkpoint": True,
                "machine_pass": True,
                "report": report,
                "orchestrator": orch_result,
                "deliver": deliver,
                "spine": spine,
            }

        st.update(
            {
                **base_update,
                "status": "checkpoint_pending",
                "batch": batch,
                "last_checkpoint": checkpoint_payload,
            }
        )
        _save_broker(st)
        _append_event("CHECKPOINT_PAUSE", {"sa": sa, "machine_pass": False})
        spine = _maybe_spine_worker_round(
            fast=fast,
            sa=sa,
            round_type=round_type,
            orch_ok=orch_result.get("ok"),
            deliver_ok=False,
            source=source,
        )
        brain_note = {
            "schema": "brain-broker-inbox-v1",
            "at": _now(),
            "status": "checkpoint_pending",
            "checkpoint": checkpoint_payload,
            "founder_action": "Brain: goal1_lane_broker.py brain-checkpoint-ack — then Hub START WORKER BATCH",
        }
        _save(BRAIN_INBOX, brain_note)
        return {
            "ok": True,
            "broker_status": "checkpoint_pending",
            "checkpoint": True,
            "machine_pass": False,
            "report": report,
            "orchestrator": orch_result,
            "brain_inbox": str(BRAIN_INBOX),
            "spine": spine,
        }

    if isinstance(orch_result, dict) and (orch_result.get("next_deliver") or orch_result.get("completed")):
        inbox_probe = inbox_status()
        if inbox_probe.get("pending"):
            deliver = {
                "ok": True,
                "skipped": "orch_already_delivered",
                "next_deliver": orch_result.get("next_deliver"),
            }
        else:
            deliver = _auto_deliver_next()
    else:
        deliver = _auto_deliver_next()
    inbox = inbox_status()
    broker_status = "awaiting_worker" if inbox.get("pending") else "idle"
    st.update(
        {
            **base_update,
            "status": broker_status,
            "last_auto_deliver": deliver,
            "inbox_after": inbox,
        }
    )
    _save_broker(st)
    _append_event(
        "WORKER_SUBMIT",
        {"sa": sa, "round_type": round_type, "orch_ok": orch_result.get("ok"), "deliver_ok": deliver.get("ok")},
    )
    spine = _maybe_spine_worker_round(
        fast=fast,
        sa=sa,
        round_type=round_type,
        orch_ok=orch_result.get("ok"),
        deliver_ok=deliver.get("ok"),
        source=source,
    )
    _p1_finish_submit()

    verify_failed = rt_norm == "verify" and critical == 0 and (
        closeout_result is None or not closeout_result.get("ok")
    )
    if verify_failed:
        return {
            "ok": False,
            "error": closeout_result.get("error") or "VERIFY_CLOSEOUT_FAILED",
            "hint": "Receipt + closeout required on VERIFY — do not mark REGISTRY done in chat",
            "closeout_result": closeout_result,
            "report": report,
            "orchestrator": orch_result,
        }

    return {
        "ok": True,
        "broker_status": broker_status,
        "report": report,
        "orchestrator": orch_result,
        "deliver": deliver,
        "inbox_pending": inbox.get("pending"),
        "founder_action": _broker_founder_action(inbox),
        "authority_pointer": ptr_gate,
        "spine": spine,
    }


def brain_poll(*, as_yaml: bool = True) -> dict:
    st = broker_state()
    brain = _load(BRAIN_INBOX)
    sys.path.insert(0, str(SCRIPTS))
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "orch", SCRIPTS / "healthy-drain-orchestrator-v1.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        orch = mod.status()
    except Exception as exc:
        orch = {"ok": False, "error": str(exc)}

    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    validation: dict = {}
    try:
        spec_v = importlib.util.spec_from_file_location(
            "bval", SCRIPTS / "brain_validate_goal1_v1.py"
        )
        mod_v = importlib.util.module_from_spec(spec_v)
        spec_v.loader.exec_module(mod_v)  # type: ignore[union-attr]
        validation = mod_v.validate_goal1()
    except Exception as exc:
        validation = {"status": "BRAIN_VALIDATION_REPORT", "ok": False, "error": str(exc)}

    st["orchestrator_snapshot"] = orch
    st["updated_at"] = _now()
    o_st = orch.get("orchestrator") or {}
    if o_st.get("status") == "idle" and not inbox.get("pending"):
        stale = st.get("last_worker_report") or {}
        sa = str(stale.get("sa_focus") or "")
        if sa.startswith("sa-TEST") or sa.startswith("sa-036"):
            st.pop("last_worker_report", None)
    _save_broker(st)

    queue_ssot_head = ""
    try:
        from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

        qh = queue_head()
        queue_ssot_head = str(qh.get("sa_id") or "")
    except Exception:
        pass
    orch_expected = str((orch.get("orchestrator") or {}).get("expected_sa") or "")

    out = {
        "status": "BRAIN_BROKER_POLL",
        "at": _now(),
        "validation": validation,
        "broker": {
            "state": st.get("status"),
            "last_worker_sa": (st.get("last_worker_report") or {}).get("sa_focus"),
            "last_worker_round": (st.get("last_worker_report") or {}).get("round_type"),
        },
        "orchestrator": {
            "phase": (orch.get("orchestrator") or {}).get("status"),
            "queue_pos": orch.get("queue_pos"),
            "expected_sa": orch_expected,
            "queue_ssot_head": queue_ssot_head,
            "queue_head_match": bool(queue_ssot_head and queue_ssot_head == orch_expected),
            "turns_completed": (orch.get("orchestrator") or {}).get("turns_completed"),
            "brief": orch.get("brief"),
        },
        "inbox": {
            "pending": inbox.get("pending"),
            "sa_id": (inbox.get("meta") or {}).get("sa_id"),
            "role": (inbox.get("meta") or {}).get("queue_role"),
            "queue": f"{(inbox.get('meta') or {}).get('queue_pos')}/{(inbox.get('meta') or {}).get('queue_total')}",
        },
        "brain_inbox_pending_ack": st.get("status") == "awaiting_brain_ack",
        "worker_report": st.get("last_worker_report") or brain.get("worker_report"),
        "action": _brain_action(st, inbox, orch),
    }
    try:
        sys.path.insert(0, str(SCRIPTS))
        from brain_cloud_yaml_pick_emit_v1 import emit_brain_pick, to_yaml_block  # noqa: WPS433

        yaml_pick = emit_brain_pick()
        out["brain_yaml_pick"] = yaml_pick
        if yaml_pick.get("ok"):
            out["brain_yaml_block"] = to_yaml_block(yaml_pick)
    except Exception as exc:
        out["brain_yaml_pick"] = {"ok": False, "error": str(exc)}
    if as_yaml:
        block = out.get("brain_yaml_block")
        if block:
            print(block)
            print("---")
        print(_to_yaml(out))
    else:
        print(json.dumps(out, indent=2))
    return out


def _brain_action(st: dict, inbox: dict, orch: dict) -> str:
    if st.get("status") == "checkpoint_pending":
        return "brain_checkpoint_ack_then_hub_start_worker_batch"
    if st.get("status") == "batch_running":
        return "worker_batch_in_progress_hub_or_wait"
    if st.get("status") == "awaiting_brain_ack":
        return "brain_ack_then_tell_founder_open_worker_run_inbox"
    if inbox.get("pending"):
        return "founder_open_worker_say_run_inbox"
    phase = (orch.get("orchestrator") or {}).get("status")
    if phase == "awaiting_worker":
        return "founder_open_worker_say_run_inbox"
    return "idle_or_deliver"


def brain_checkpoint_ack(*, note: str = "", force: bool = False) -> dict:
    """Brain clears checkpoint pause — batch loop can resume from Hub."""
    st = broker_state()
    if st.get("status") != "checkpoint_pending" and not force:
        return {"ok": False, "error": "not checkpoint_pending", "status": st.get("status")}
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    deliver = _auto_deliver_next()
    inbox = inbox_status()
    batch = dict(st.get("batch") or {})
    batch["turns_in_batch"] = 0
    st.update(
        {
            "status": "batch_running" if inbox.get("pending") else "idle",
            "last_brain_checkpoint_ack": {"at": _now(), "note": note},
            "last_auto_deliver": deliver,
            "inbox_after_ack": inbox,
            "batch": batch,
        }
    )
    _save_broker(st)
    _append_event("BRAIN_CHECKPOINT_ACK", {"note": note})
    out = {
        "status": "BRAIN_CHECKPOINT_ACK",
        "at": _now(),
        "broker_status": st["status"],
        "inbox_pending": inbox.get("pending"),
        "founder_action": "AUTO-RUN — next batch spawns automatically (no tap)",
    }
    print(_to_yaml(out))
    return out


def brain_ack(*, note: str = "") -> dict:
    st = broker_state()
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    orch_snap: dict = {}
    if not inbox.get("pending"):
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "orch", SCRIPTS / "healthy-drain-orchestrator-v1.py"
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            if (mod.orchestrator_state() or {}).get("status") == "idle":
                mod.deliver_current()
            orch_snap = mod.status()
            inbox = inbox_status()
        except Exception as exc:
            orch_snap = {"ok": False, "error": str(exc)}

    st.update(
        {
            "status": "awaiting_worker" if inbox.get("pending") else "idle",
            "last_brain_ack": {"at": _now(), "note": note},
            "orchestrator_snapshot": orch_snap,
            "inbox_after_ack": inbox,
        }
    )
    _save_broker(st)
    _save(
        BRAIN_INBOX,
        {
            "schema": "brain-broker-inbox-v1",
            "at": _now(),
            "status": "acked",
            "last_brain_ack": st.get("last_brain_ack"),
            "inbox_after_ack": {
                "pending": inbox.get("pending"),
                "sa_id": (inbox.get("meta") or {}).get("sa_id"),
                "queue_role": (inbox.get("meta") or {}).get("queue_role"),
            },
            "founder_action": "Open SourceA Worker → say: run inbox",
        },
    )
    _append_event("BRAIN_ACK", {"note": note, "inbox_pending": inbox.get("pending")})

    try:
        import importlib.util

        spec_p1 = importlib.util.spec_from_file_location(
            "authority_p1", SCRIPTS / "authority_enforce_p1_lib.py"
        )
        p1_mod = importlib.util.module_from_spec(spec_p1)
        spec_p1.loader.exec_module(p1_mod)  # type: ignore[union-attr]
        reconciled = p1_mod.sync_reconciled_decision(note=note)
    except Exception as exc:
        reconciled = {"ok": False, "error": str(exc)}

    out = {
        "status": "BRAIN_BROKER_ACK",
        "at": _now(),
        "broker_status": st["status"],
        "inbox": {
            "pending": inbox.get("pending"),
            "sa_id": (inbox.get("meta") or {}).get("sa_id"),
            "role": (inbox.get("meta") or {}).get("queue_role"),
            "path": str(ROOT / ".sina-loop/INBOX.md"),
        },
        "founder_action": "Open SourceA Worker → say: run inbox",
        "orchestrator_brief": orch_snap.get("brief") if isinstance(orch_snap, dict) else None,
        "reconciled_decision": reconciled,
    }
    print(_to_yaml(out))
    return out


def _to_yaml(obj: dict, indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent
    for key, val in obj.items():
        if isinstance(val, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_to_yaml(val, indent + 1))
        elif isinstance(val, list):
            lines.append(f"{prefix}{key}:")
            for item in val:
                if isinstance(item, dict):
                    lines.append(f"{prefix}  -")
                    lines.append(_to_yaml(item, indent + 2))
                else:
                    lines.append(f"{prefix}  - {item}")
        elif isinstance(val, bool):
            lines.append(f"{prefix}{key}: {'true' if val else 'false'}")
        elif val is None:
            lines.append(f"{prefix}{key}: null")
        else:
            s = str(val)
            if any(c in s for c in (":", "#", "\n")):
                lines.append(f'{prefix}{key}: "{s}"')
            else:
                lines.append(f"{prefix}{key}: {s}")
    return "\n".join(lines)


def watch(*, poll_sec: float = 12.0, max_cycles: int = 0) -> int:
    """Brain-side broker watch — prints YAML when state changes."""
    seen = ""
    cycles = 0
    while True:
        st = broker_state()
        inbox = _load(BRAIN_INBOX)
        fingerprint = json.dumps({"b": st.get("status"), "i": inbox.get("at")}, sort_keys=True)
        if fingerprint != seen:
            seen = fingerprint
            brain_poll(as_yaml=True)
            sys.stdout.flush()
        cycles += 1
        if max_cycles and cycles >= max_cycles:
            return 0
        time.sleep(poll_sec)


def pickup_prompt_for_worker() -> dict:
    """Mechanical INBOX read — Worker agent runs this on 'run inbox'."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433
    from worker_stuck_recovery_v1 import kill_hung_processes, sync_orchestrator_from_inbox  # noqa: WPS433
    from worker_turn_lib import turn_open_block  # noqa: WPS433

    truth_gate: dict = {}
    brain_wire: dict = {}
    try:
        from brain_governance_wire_v1 import wire_brain_governance  # noqa: WPS433

        brain_wire = wire_brain_governance(sync_brain=False)
    except Exception as exc:
        brain_wire = {"ok": False, "error": str(exc)}
    try:
        from run_inbox_disk_truth_v1 import gate_pickup, format_truth_block  # noqa: WPS433

        truth_gate = gate_pickup()
    except Exception as exc:
        truth_gate = {"ok": False, "error": str(exc)}

    kill_hung_processes()
    try:
        from worker_factory_heal_v1 import heal as factory_heal  # noqa: WPS433

        factory_heal(deliver=False, sync_queue=True)
    except Exception:
        pass
    sync_orchestrator_from_inbox()

    from worker_manual_only_v1 import is_manual_only, manual_hint  # noqa: WPS433

    if is_manual_only():
        out = {
            "status": "WORKER_MANUAL_ONLY",
            "action": "STOP",
            "hint": manual_hint(),
        }
        print(_to_yaml(out))
        return out

    try:
        from worker_asf_directive_latch_v1 import read_latch  # noqa: WPS433

        lat = read_latch()
        if lat.get("plan_only"):
            out = {
                "status": "WORKER_FOUNDER_CHAT_FIRST",
                "action": "STOP",
                "hint": (
                    "plan_only latch ON — read founder chat · reply with PLAN bullets only · "
                    "no pickup until founder says 'run inbox'"
                ),
                "latch": lat,
            }
            print(_to_yaml(out))
            return out
    except Exception:
        pass

    try:
        from founder_directive_ssot_v1 import hub_closed, block_hub_item  # noqa: WPS433
        from worker_inject_lib import inbox_status  # noqa: WPS433

        if hub_closed():
            st_pre = inbox_status()
            meta = st_pre.get("meta") or {}
            try:
                from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

                qh = queue_head()
            except Exception:
                qh = {}
            sa_pick = meta.get("sa_id") or st_pre.get("sa_id")
            phase_pick = meta.get("phase") or (qh.get("phase") if isinstance(qh, dict) else "") or ""
            blocked, reason = block_hub_item({"sa_id": sa_pick, "phase": phase_pick})
            if blocked:
                out = {
                    "status": "WORKER_HUB_CLOSED",
                    "action": "STOP",
                    "hint": f"HUB ARCHIVED — ASF closed hub lane. {reason}",
                    "founder_directive": "no_hub",
                }
                print(_to_yaml(out))
                return out
    except Exception:
        pass

    st = inbox_status()
    block = turn_open_block()
    if block:
        inbox_sa = str(st.get("sa_id") or (st.get("meta") or {}).get("sa_id") or "")
        open_sa = str(block.get("open_sa") or "")
        if inbox_sa and open_sa == inbox_sa and st.get("pending"):
            pass
        else:
            from worker_stuck_recovery_v1 import heal_stale_worker_turn  # noqa: WPS433

            healed = heal_stale_worker_turn(inbox_sa=inbox_sa)
            if healed.get("healed"):
                block = turn_open_block()
            if block and not (inbox_sa and str(block.get("open_sa") or "") == inbox_sa and st.get("pending")):
                out = {
                    "status": "WORKER_TURN_BUSY",
                    "action": "STOP",
                    "hint": (
                        "Different turn open — tap Hub **Unstick Worker** then run inbox once"
                        if open_sa and inbox_sa and open_sa != inbox_sa
                        else "Finish current turn — do NOT spam run inbox"
                    ),
                    "recovery": healed,
                    **block,
                }
                print(_to_yaml(out))
                return out

    if not st.get("pending"):
        st = inbox_status()
    if not st.get("pending"):
        out = {
            "status": "WORKER_INBOX_EMPTY",
            "action": "disk_truth_redeliver_failed",
            "hint": "Machine gate could not deliver — check ~/.sina/run-inbox-disk-truth-v1.json",
            "truth_gate": truth_gate,
        }
        print(_to_yaml(out))
        return out
    data = _load(Path.home() / ".sina" / "worker-prompt-inbox-v1.json")
    meta = data.get("meta") or {}
    disk_truth = ""
    try:
        from run_inbox_disk_truth_v1 import format_truth_block  # noqa: WPS433

        disk_truth = format_truth_block()
    except Exception:
        disk_truth = ""
    out = {
        "status": "WORKER_INBOX_PICKUP",
        "queue": f"{meta.get('queue_pos')}/{meta.get('queue_total')}",
        "role": meta.get("queue_role"),
        "sa_id": meta.get("sa_id"),
        "chars": data.get("chars"),
        "disk_truth": disk_truth,
        "truth_gate": truth_gate.get("action"),
        "brain_wire": {
            "queue_head": (brain_wire.get("queue_head") or {}).get("sa_id"),
            "active_decisions": [d.get("id") for d in (brain_wire.get("active_decisions") or [])],
            "reconciled_stale": (brain_wire.get("reconciled_decision") or {}).get("stale"),
        },
        "execution_lane": "run_inbox",
        "next_steps_lane": "advisory_only",
        "prompt": data.get("prompt") or "",
        "mandatory_end": "WORKER_ROUND_REPORT YAML then: python3 scripts/goal1_lane_broker.py worker-submit --stdin",
    }
    print(_to_yaml(out))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Goal 1 Brain↔Worker lane broker")
    p.add_argument(
        "cmd",
        choices=(
            "worker-submit",
            "check-stdin",
            "brain-poll",
            "brain-ack",
            "brain-checkpoint-ack",
            "watch",
            "pickup",
            "status",
        ),
    )
    p.add_argument("--stdin", action="store_true", help="Read YAML/report body from stdin")
    p.add_argument("--file", help="Read YAML from file")
    p.add_argument("--note", default="", help="Brain ack note")
    p.add_argument("--poll-sec", type=float, default=12.0)
    p.add_argument("--max-cycles", type=int, default=0)
    p.add_argument("--json", action="store_true", help="JSON instead of YAML for poll/ack")
    args = p.parse_args()

    sys.path.insert(0, str(SCRIPTS))
    from agent_cancel_guard_v1 import agent_cancel_active, agent_cancel_skip, write_cancel_receipt  # noqa: WPS433

    if args.cmd not in ("status",) and agent_cancel_active():
        write_cancel_receipt(caller=f"goal1_lane_broker:{args.cmd}")
        out = agent_cancel_skip(caller=f"goal1_lane_broker:{args.cmd}")
        if args.json or args.cmd in ("check-stdin",):
            print(json.dumps(out, indent=2))
        else:
            print(_to_yaml(out))
        return 0

    if args.cmd == "status":
        print(json.dumps({"broker": broker_state(), "brain_inbox": _load(BRAIN_INBOX)}, indent=2))
        return 0
    if args.cmd == "pickup":
        pickup_prompt_for_worker()
        return 0
    if args.cmd == "worker-submit":
        body = ""
        if args.file:
            body = Path(args.file).read_text(encoding="utf-8")
        elif args.stdin:
            body = sys.stdin.read()
        else:
            print("FAIL: use --stdin or --file", file=sys.stderr)
            return 1
        result = worker_submit(text=body)
        print(_to_yaml(result if result.get("ok") else {"status": "BROKER_ERROR", **result}))
        return 0 if result.get("ok") else 1
    if args.cmd == "check-stdin":
        body = ""
        if args.file:
            body = Path(args.file).read_text(encoding="utf-8")
        elif args.stdin:
            body = sys.stdin.read()
        else:
            print("FAIL: use --stdin or --file", file=sys.stderr)
            return 1
        result = check_stdin_report(text=body, source="agent_cli")
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(_to_yaml(result))
        return 0 if result.get("ok") else 1
    if args.cmd == "brain-poll":
        brain_poll(as_yaml=not args.json)
        return 0
    if args.cmd == "brain-ack":
        brain_ack(note=args.note)
        return 0
    if args.cmd == "brain-checkpoint-ack":
        brain_checkpoint_ack(note=args.note)
        return 0
    if args.cmd == "watch":
        return watch(poll_sec=args.poll_sec, max_cycles=args.max_cycles)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
