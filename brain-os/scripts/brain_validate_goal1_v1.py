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

ROOT = Path(__file__).resolve().parents[2]  # SourceA root
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


def _pgrep(pattern: str) -> list[int]:
    proc = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    out: list[int] = []
    for line in (proc.stdout or "").splitlines():
        if line.strip().isdigit():
            out.append(int(line.strip()))
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
    worker_report = broker_st.get("last_worker_report") or orch.get("round_report") or {}
    validate_block = worker_report.get("validate") if isinstance(worker_report.get("validate"), dict) else {}

    pids = {
        "run_loop": _pgrep("goal1_run_loop"),
        "batch": _pgrep("goal1_worker_batch_loop"),
        "agent": _pgrep("agent -p -f"),
    }
    executor_busy = bool(pids["run_loop"] or pids["batch"] or pids["agent"])
    agent_events = _last_agent_events()

    inject_ok = feas.get("action") != "STOP_INJECT"
    if not inbox.get("pending") and o.get("status") == "awaiting_worker":
        inject_ok = inject_ok  # deliver may be needed — not fail inject gate alone
    inject_pass = inject_ok and (inbox.get("pending") or executor_busy or worker_report.get("sa_focus"))

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
    sync_pass = bool(
        worker_report.get("sa_focus")
        and last_sa
        and (worker_report.get("sa_focus") == last_sa or o.get("status") == "awaiting_worker")
    )
    if progress.get("status") == "RUNNING":
        sync_state = "WAIT"
    elif sync_pass or (agent_events.get("advance") is True):
        sync_state = "PASS"
    else:
        sync_state = "WAIT" if executor_busy else "FAIL"

    chain_ok = inject_pass and validate_state in ("PASS", "WAIT") and activate_pass and sync_state in ("PASS", "WAIT")

    sys.path.insert(0, str(SCRIPTS))
    try:
        from one_sa_per_turn_gate_v1 import gate_status  # noqa: WPS433

        one_sa = gate_status()
    except Exception as exc:
        one_sa = {"ok": False, "error": str(exc)}

    brain_action = "idle"
    if broker_st.get("status") == "checkpoint_pending":
        brain_action = "brain_checkpoint_ack"
    elif executor_busy:
        brain_action = "wait_batch_log_agent_done"
    elif not inbox.get("pending") and o.get("status") == "awaiting_worker":
        brain_action = "run_goal1_auto_loop_or_deliver"
    elif inbox.get("pending") and not executor_busy:
        brain_action = "run_goal1_auto_loop_activate"
    elif validate_state == "FAIL":
        brain_action = "worker_turn_missing_report_rerun"
    elif sync_state == "FAIL":
        brain_action = "broker_poll_worker_submit"

    out = {
        "status": "BRAIN_VALIDATION_REPORT",
        "at": _now(),
        "ok": chain_ok and validate_state != "FAIL" and activate_state != "FAIL",
        "chain": {
            "inject": "PASS" if inject_pass else "FAIL",
            "validate": validate_state,
            "activate": activate_state,
            "sync": sync_state,
        },
        "inbox": {
            "pending": inbox.get("pending"),
            "sa_id": (inbox.get("meta") or {}).get("sa_id"),
            "queue_role": (inbox.get("meta") or {}).get("queue_role"),
            "queue": f"{(inbox.get('meta') or {}).get('queue_pos')}/{(inbox.get('meta') or {}).get('queue_total')}",
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
            "last_completed_sa": o.get("last_completed_sa"),
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
            "fail_reason": progress.get("fail_reason") or (
                "missing_WORKER_ROUND_REPORT" if agent_events.get("report") is False else None
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
        "founder_surface": "Hub Goal 1 → Batch log (AGENT START/DONE) — Worker chat empty on headless path",
        "mandatory_next": (
            "python3 scripts/goal1_auto_loop_v1.py --turns 10 --json"
            if brain_action in ("run_goal1_auto_loop_or_deliver", "run_goal1_auto_loop_activate")
            else f"python3 scripts/goal1_lane_broker.py brain-poll"
        ),
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
    row = validate_goal1(strict=args.strict)
    if args.write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        (SINA / "brain-goal1-validation-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(_to_yaml(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
