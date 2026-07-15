#!/usr/bin/env python3
"""Mechanical Goal 1 validation for Brain — INJECT · VALIDATE · ACTIVATE · SYNC.

Brain MUST run this and paste YAML to founder on every Goal 1 status reply.
Law: GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
BATCH_LOG = SINA / "goal1-worker-batch-latest.log"
PROGRESS = SINA / "goal1-turn-progress-v1.json"
BROKER = SINA / "goal1-lane-broker-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _effective_worker_report(*, broker_st: dict, orch: dict, o: dict) -> dict:
    """Prefer live orchestrator report; drop test/stale broker cache."""
    live = orch.get("round_report") if isinstance(orch.get("round_report"), dict) else {}
    cached = broker_st.get("last_worker_report") if isinstance(broker_st.get("last_worker_report"), dict) else {}
    snap = (broker_st.get("orchestrator_snapshot") or {}).get("orchestrator") or {}
    live_status = o.get("status")
    snap_status = snap.get("status")
    if str(live.get("status") or "") == "CLEARED" or (
        o.get("status") == "idle" and not live.get("sa_focus")
    ):
        report = {}
    elif live.get("sa_focus"):
        report = live
    elif snap_status and live_status and snap_status != live_status:
        report = live
    else:
        report = cached
    sa = str(report.get("sa_focus") or "")
    if sa.startswith("sa-TEST"):
        return {}
    if str(report.get("status") or "") == "CLEARED":
        return {}
    return report


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _pgrep(pattern: str) -> list[int]:
    proc = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    out: list[int] = []
    for line in (proc.stdout or "").splitlines():
        if line.strip().isdigit():
            pid = int(line.strip())
            if _pid_alive(pid):
                out.append(pid)
    return out


def _batch_log_tail(n: int = 12) -> list[str]:
    if not BATCH_LOG.is_file():
        return []
    try:
        lines = BATCH_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-n:]
    except OSError:
        return []


def _last_agent_events() -> dict:
    events = {"start": None, "done": None, "exit": None, "broker": None, "advance": None, "report": None}
    for line in reversed(_batch_log_tail(40)):
        if "sa-TEST-GATE" in line or "sa-TEST" in line:
            continue
        if "AGENT START" in line and events["start"] is None:
            events["start"] = line.strip()
        if "AGENT DONE" in line and events["done"] is None:
            events["done"] = line.strip()
            m = re.search(r"exit=(\d+)", line)
            if m:
                events["exit"] = int(m.group(1))
            if "broker=yes" in line:
                events["broker"] = True
            elif "broker=no" in line:
                events["broker"] = False
            if "advance=yes" in line:
                events["advance"] = True
            elif "advance=no" in line:
                events["advance"] = False
            if "report=yes" in line:
                events["report"] = True
            elif "report=no" in line:
                events["report"] = False
        if events["start"] and events["done"]:
            break
    return events


def _orch_status() -> dict:
    spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.status()


def validate_goal1(*, strict: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from prompt_feasibility_gate import check_session  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    feas = check_session(role="worker")
    inbox = inbox_status()
    orch = _orch_status()
    o = orch.get("orchestrator") or {}
    broker_st = _load_json(BROKER)
    progress = _load_json(PROGRESS)

    try:
        from one_sa_per_turn_gate_v1 import gate_status as _gate_status  # noqa: WPS433

        one_sa_early = _gate_status()
    except Exception as exc:
        one_sa_early = {"ok": False, "error": str(exc), "turn_open": False}

    worker_report = _effective_worker_report(broker_st=broker_st, orch=orch, o=o)
    validate_block = worker_report.get("validate") if isinstance(worker_report.get("validate"), dict) else {}

    queue_head: dict = {"sa_id": "", "role": "", "pos": 0, "total": 0}
    try:
        from queue_ssot_unify_v1 import queue_head as _canonical_queue_head  # noqa: WPS433

        qh = _canonical_queue_head()
        if qh.get("ok"):
            queue_head = {
                "sa_id": qh.get("sa_id"),
                "role": qh.get("role"),
                "pos": qh.get("pos"),
                "total": qh.get("total"),
            }
    except Exception:
        pass
    if not queue_head.get("sa_id"):
        try:
            from monitor_honesty_lib_v1 import queue_context  # noqa: WPS433

            _, here_sa, here_pos, here_role = queue_context()
            total = int(orch.get("queue_total") or 30)
            queue_head = {
                "sa_id": here_sa,
                "role": here_role,
                "pos": here_pos,
                "total": total,
            }
        except Exception:
            pass

    # Drop stale worker report when turn closed and sa_focus ≠ queue head.
    wr_sa = str(worker_report.get("sa_focus") or "")
    if (
        wr_sa
        and queue_head.get("sa_id")
        and wr_sa != queue_head["sa_id"]
        and not one_sa_early.get("turn_open")
    ):
        worker_report = {}
        validate_block = {}

    pids = {
        "run_loop": _pgrep("goal1_run_loop"),
        "batch": _pgrep("goal1_worker_batch_loop"),
        "agent": _pgrep("agent -p -f"),
        "healthy_pack": _pgrep("worker_healthy_pack"),
    }
    headless_drain = bool(pids["healthy_pack"])
    executor_busy = bool(pids["run_loop"] or pids["batch"] or pids["agent"] or headless_drain)
    agent_events = _last_agent_events()

    inject_ok = feas.get("action") != "STOP_INJECT"
    if not inbox.get("pending") and o.get("status") == "awaiting_worker":
        inject_ok = inject_ok  # deliver may be needed — not fail inject gate alone
    idle_ready = (
        not inbox.get("pending")
        and o.get("status") in ("idle", "done", "stopped")
        and not executor_busy
        and inject_ok
    )
    inject_pass = inject_ok and (
        inbox.get("pending")
        or executor_busy
        or worker_report.get("sa_focus")
        or idle_ready
        or bool(queue_head.get("sa_id"))
    )

    has_report = str(worker_report.get("status") or "").rstrip(":") == "WORKER_ROUND_REPORT" or bool(
        worker_report.get("sa_focus")
    )
    spine = validate_block.get("spine")
    validate_pass = has_report and (spine in (None, "PASS", "FAIL") or worker_report.get("round_type"))
    if progress.get("status") == "RUNNING":
        validate_state = "WAIT"
    elif validate_pass:
        validate_state = "PASS"
    else:
        validate_state = "FAIL" if strict else "WAIT"

    if executor_busy or progress.get("status") == "RUNNING":
        activate_state = "RUNNING"
        activate_pass = True
    elif headless_drain and o.get("status") == "awaiting_worker":
        activate_state = "RUNNING"
        activate_pass = True
    elif inbox.get("pending") and not executor_busy:
        # INBOX logged — Worker handoff ready; READY not "stuck" (ignore stale AGENT DONE broker=no)
        activate_state = "READY"
        activate_pass = True
    elif not inbox.get("pending") and o.get("status") in ("idle", "done") and not executor_busy:
        # Clean idle or pack exhausted — no dangling turn; ready for next pick/deliver
        activate_state = "WAIT"
        activate_pass = True
    elif agent_events.get("done") and agent_events.get("exit") == 0 and agent_events.get("broker"):
        activate_state = "PASS"
        activate_pass = True
    elif agent_events.get("done"):
        activate_state = "FAIL"
        activate_pass = False
    else:
        activate_state = "FAIL"
        activate_pass = False

    pos = orch.get("queue_pos")
    expected_sa = o.get("expected_sa")
    last_sa = o.get("last_completed_sa") or worker_report.get("sa_focus")
    head_sa = str(queue_head.get("sa_id") or "")
    broker_closed = bool(
        worker_report.get("status") == "WORKER_ROUND_REPORT"
        and str(worker_report.get("sa_focus") or "") == str(last_sa or "")
    )
    last_completed_stale = bool(
        last_sa and head_sa and str(last_sa) != head_sa and not broker_closed
    )
    if last_completed_stale:
        last_sa = head_sa or last_sa
    sync_pass = bool(
        worker_report.get("sa_focus")
        and last_sa
        and (worker_report.get("sa_focus") == last_sa or o.get("status") == "awaiting_worker")
    )
    meta = inbox.get("meta") or {}
    fn_row = _load_json(SINA / "factory-now-v1.json")
    outbound_handoff = bool(
        inbox.get("pending")
        and str(queue_head.get("role") or "").lower() == "act"
        and head_sa
        and (
            meta.get("truth_match") is True
            or str(meta.get("sa_id") or "") == head_sa
        )
        and str(fn_row.get("mode") or "") == "SINGLE_SA"
    )
    if progress.get("status") == "RUNNING":
        sync_state = "WAIT"
    elif sync_pass or (agent_events.get("advance") is True):
        sync_state = "PASS"
    elif outbound_handoff and not executor_busy:
        sync_state = "READY"
        sync_pass = True
    elif not inbox.get("pending") and o.get("status") in ("idle", "done") and not executor_busy:
        sync_state = "WAIT"
    else:
        sync_state = "WAIT" if executor_busy else "FAIL"

    chain_ok = (
        inject_pass
        and validate_state in ("PASS", "WAIT")
        and activate_pass
        and sync_state in ("PASS", "WAIT", "READY")
    )

    sys.path.insert(0, str(SCRIPTS))
    one_sa = one_sa_early

    head_sa = str(queue_head.get("sa_id") or (inbox.get("meta") or {}).get("sa_id") or expected_sa or "")
    head_role = str(
        queue_head.get("role")
        or (inbox.get("meta") or {}).get("queue_role")
        or o.get("expected_role")
        or "check"
    )
    head_pos = int(queue_head.get("pos") or (inbox.get("meta") or {}).get("queue_pos") or pos or 0)
    head_total = int(queue_head.get("total") or (inbox.get("meta") or {}).get("queue_total") or 30)

    sys.path.insert(0, str(SCRIPTS))
    from execution_path_vocabulary_v1 import brain_work_order_primary, queue_founder_line  # noqa: WPS433

    brain_action = "idle"
    if broker_st.get("status") == "checkpoint_pending":
        brain_action = "brain_checkpoint_ack"
    elif executor_busy:
        brain_action = "wait_batch_log_agent_done"
    elif brain_work_order_primary() and inbox.get("pending") and not executor_busy and head_sa:
        brain_action = f"brain_work_order_dispatch_{head_sa}_{head_role}"
    elif brain_work_order_primary() and head_sa and not inbox.get("pending"):
        brain_action = f"brain_work_order_signed_{head_sa}_{head_role}"
    elif inbox.get("pending") and not executor_busy and head_sa:
        brain_action = f"worker_execute_inbox_{head_sa}_{head_role}"
    elif head_sa and not inbox.get("pending"):
        brain_action = f"worker_run_inbox_{head_sa}_{head_role}"
    elif not inbox.get("pending") and o.get("status") == "awaiting_worker":
        brain_action = "orchestrator_deliver_next_slice"
    elif validate_state == "FAIL":
        brain_action = "worker_turn_missing_report_rerun"
    elif sync_state == "FAIL":
        brain_action = "broker_poll_worker_submit"

    founder_line = queue_founder_line(
        sa=head_sa or "",
        role=head_role or "act",
        pos=head_pos,
        total=head_total,
        inbox_pending=bool(inbox.get("pending")),
    )
    if not head_sa:
        founder_line = "Queue head unknown — run python3 scripts/queue_ssot_unify_v1.py"

    progress_honest: dict = {}
    try:
        from monitor_honesty_lib_v1 import audit_monitor  # noqa: WPS433

        mh = audit_monitor(filter_mode="road")
        progress_honest = {
            "law": (mh.get("progress") or {}).get("law") or mh.get("law"),
            "valid_yes": (mh.get("progress") or {}).get("valid_yes"),
            "map_done": (mh.get("progress") or {}).get("map_done"),
            "pct": (mh.get("progress") or {}).get("pct"),
            "receipt_done": mh.get("receipt_done"),
            "valid_partial": (mh.get("counts") or {}).get("valid_partial"),
            "broker_stale": (mh.get("integrity") or {}).get("broker_stale"),
            "unproven_done": mh.get("unproven_done"),
            "gate": "validate-monitor-honesty-v1.sh",
        }
    except Exception as exc:
        progress_honest = {"error": str(exc)[:200]}

    out = {
        "status": "BRAIN_VALIDATION_REPORT",
        "at": _now(),
        "ok": chain_ok and validate_state != "FAIL" and activate_state != "FAIL",
        "progress_honest": progress_honest,
        "chain": {
            "inject": "PASS" if inject_pass else "FAIL",
            "validate": validate_state,
            "activate": activate_state,
            "sync": sync_state,
        },
        "queue_head": {
            "sa_id": head_sa,
            "role": head_role,
            "pos": head_pos,
            "total": head_total,
            "truth_match": head_sa == str((inbox.get("meta") or {}).get("sa_id") or "") or inbox.get("pending"),
        },
        "founder_line": founder_line,
        "inbox": {
            "pending": inbox.get("pending"),
            "sa_id": head_sa or (inbox.get("meta") or {}).get("sa_id"),
            "queue_role": head_role or (inbox.get("meta") or {}).get("queue_role"),
            "queue": f"{head_pos}/{head_total}",
        },
        "feasibility": {
            "action": feas.get("action"),
            "ok": feas.get("action") != "STOP_INJECT",
        },
        "worker_report": {
            "sa_focus": worker_report.get("sa_focus"),
            "round_type": worker_report.get("round_type"),
            "phase": worker_report.get("phase"),
            "validate": {
                "spine": spine or "?",
                "critical_bugs": validate_block.get("critical_bugs", "?"),
            },
            "present": has_report,
        },
        "orchestrator": {
            "phase": o.get("status"),
            "queue_pos": pos,
            "expected_sa": expected_sa,
            "expected_role": o.get("expected_role"),
            "last_completed_sa": last_sa if not last_completed_stale else o.get("last_completed_sa"),
            "last_completed_stale": last_completed_stale,
            "turns_completed": o.get("turns_completed"),
            "brief": orch.get("brief"),
        },
        "loop": {
            "executor_busy": executor_busy,
            "pids": {k: v[:3] for k, v in pids.items() if v},
            "progress_status": progress.get("status"),
            "progress_sa": progress.get("sa_id"),
            "last_agent_start": agent_events.get("start"),
            "last_agent_done": agent_events.get("done"),
            "agent_exit": agent_events.get("exit"),
            "broker_ok": agent_events.get("broker"),
            "advanced": agent_events.get("advance"),
            "has_report": agent_events.get("report"),
            "fail_reason": (
                progress.get("fail_reason")
                or (
                    None
                    if (
                        "post-pack-hygiene" in str(agent_events.get("done") or "")
                        or (
                            not inbox.get("pending")
                            and o.get("status") == "idle"
                            and not executor_busy
                        )
                    )
                    else (
                        "missing_WORKER_ROUND_REPORT"
                        if agent_events.get("report") is False
                        else None
                    )
                )
            ),
        },
        "broker_status": broker_st.get("status"),
        "one_sa_per_turn": {
            "ok": one_sa.get("ok"),
            "turn_open": one_sa.get("turn_open"),
            "open_sa": one_sa.get("open_sa"),
            "inbox_sa": one_sa.get("inbox_sa"),
            "blocked": one_sa.get("block") is not None,
        },
        "brain_action": brain_action,
        "founder_surface": founder_line,
        "mandatory_next": founder_line if head_sa else "python3 scripts/queue_ssot_unify_v1.py --json",
    }
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
                lines.append(f"{prefix}  - {item}")
        elif isinstance(val, bool):
            lines.append(f"{prefix}{key}: {'true' if val else 'false'}")
        elif val is None:
            lines.append(f"{prefix}{key}: null")
        else:
            s = str(val)
            if any(c in s for c in (":", "#", "\n", '"')) or len(s) > 80:
                esc = s.replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'{prefix}{key}: "{esc}"')
            else:
                lines.append(f"{prefix}{key}: {s}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Brain Goal 1 validation report (mandatory YAML)")
    p.add_argument("--json", action="store_true", help="JSON output (default YAML)")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--write-receipt", action="store_true", help="Write ~/.sina/brain-goal1-validation-v1.json")
    args = p.parse_args()
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="brain_validate_goal1")
    if not hb.get("ok"):
        print(json.dumps({"ok": False, "step": "active_now", **hb}, indent=2))
        return 1
    row = validate_goal1(strict=args.strict)
    if args.write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        (SINA / "brain-goal1-validation-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        qh = row.get("queue_head") or {}
        inbox = row.get("inbox") or {}
        sa = str(qh.get("sa_id") or inbox.get("sa_id") or "")
        pos = qh.get("pos") or inbox.get("queue_pos")
        total = qh.get("total") or inbox.get("queue_total")
        role = str(qh.get("role") or inbox.get("queue_role") or "")
        queue_str = f"{pos}/{total}" if pos and total else str(inbox.get("queue") or "")
        sys.path.insert(0, str(SCRIPTS))
        from execution_path_vocabulary_v1 import queue_founder_line  # noqa: WPS433

        pos_i = int(pos) if str(pos).isdigit() else 0
        total_i = int(total) if str(total).isdigit() else 0
        if sa:
            fl = queue_founder_line(
                sa=sa,
                role=role or "act",
                pos=pos_i,
                total=total_i,
                inbox_pending=bool(inbox.get("pending")),
            )
        else:
            fl = row.get("founder_line", "")
        action = {
            "schema": "brain-current-action-v1",
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "brain_ok": row.get("ok") is True,
            "inbox": {
                "pending": bool(inbox.get("pending")),
                "sa_id": sa,
                "queue_role": role,
                "queue": queue_str,
            },
            "founder_line": fl,
            "synced_from": "brain_validate_goal1_v1.py --write-receipt",
            "law": "INCIDENT-033 · brain-current-action must track brain receipt",
        }
        (SINA / "brain-current-action-v1.json").write_text(json.dumps(action, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(_to_yaml(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
