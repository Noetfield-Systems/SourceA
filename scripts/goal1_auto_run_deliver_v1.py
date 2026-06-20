#!/usr/bin/env python3
"""Deliver + detached headless Goal 1 auto-run — single EXECUTE entry (PEV).

PLAN: healthy queue + INBOX locally (orchestrator deliver)
EXECUTE: detached goal1_auto_run_v1.py → start_goal1_worker_turn_v1.py → agent -p -f
VERIFY: WORKER_ROUND_REPORT + machine validators
SYNC: orchestrator poll_once after each turn

Worker chat stays empty — watch ~/.sina/goal1-worker-batch-latest.log for AGENT START/DONE.
Law: SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md

TRACE: AUTO-TRACE-WORKER-AUTORUN-CAP-v1.0 · agent Auto
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOG_PATH = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
LOCK_PATH = Path.home() / ".sina" / "goal1-auto-run-lock-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_orch():
    spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _log(line: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _auto_run_running() -> dict | None:
    """Return live goal1_auto_run row if batch is in flight — do not STOP during prepare."""
    proc = subprocess.run(["pgrep", "-f", "goal1_auto_run_v1.py"], capture_output=True, text=True)
    pids = [int(x) for x in (proc.stdout or "").splitlines() if x.strip().isdigit()]
    alive = [p for p in pids if _pid_alive(p)]
    if alive:
        return {"pid": alive[0], "pids": alive, "source": "pgrep"}
    if LOCK_PATH.is_file():
        try:
            row = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            pid = int(row.get("pid") or 0)
            if pid and _pid_alive(pid):
                return {**row, "pid": pid, "source": "lock"}
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return None


# Back-compat alias for unified autorun import
_loop_running = _auto_run_running


def prepare(*, turns: int = 10) -> dict:
    """Feasibility → stop stale → deliver INBOX if empty. Does not spawn agent."""
    sys.path.insert(0, str(SCRIPTS))
    from prompt_feasibility_gate import check_session  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    feas = check_session(role="worker")
    if feas.get("action") == "STOP_INJECT":
        return {"ok": False, "step": "feasibility", "error": "STOP_INJECT", "feasibility": feas}

    running = _auto_run_running()
    autorun_flag = (Path.home() / ".sina" / "goal1-orchestrator-autorun-v1.json").is_file()
    if not running and not autorun_flag:
        subprocess.run(
            [sys.executable, str(SCRIPTS / "stop_goal1_auto_run_v1.py"), "--note", "auto_run_prepare"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )

    inbox = inbox_status()
    deliver = None
    if not inbox.get("pending"):
        orch = _load_orch()
        deliver = orch.deliver_current(force=True)
        if not deliver.get("ok"):
            return {"ok": False, "step": "deliver", "error": deliver}
        inbox = inbox_status()

    meta = inbox.get("meta") or {}
    st = _load_orch().status()
    out = {
        "ok": True,
        "step": "prepared",
        "turns": turns,
        "inbox_pending": inbox.get("pending"),
        "queue": f"{meta.get('queue_pos')}/{meta.get('queue_total')}",
        "sa_id": meta.get("sa_id"),
        "queue_role": meta.get("queue_role"),
        "orchestrator_brief": st.get("brief"),
        "deliver": deliver,
        "visibility": "headless_agent_cli — Worker chat stays empty; watch batch log AGENT START/DONE",
    }
    if running:
        out["auto_run_already_running"] = True
        out["running_pid"] = running.get("pid")
    return out


def spawn_detached(*, turns: int = 10, timeout_sec: int = 1800) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from factory_spawn_gate_v1 import drain_spawn_allowed  # noqa: WPS433

    gate = drain_spawn_allowed(caller="goal1_auto_run_deliver")
    if not gate.get("ok"):
        return gate
    prep = prepare(turns=turns)
    if not prep.get("ok"):
        return prep
    if prep.get("auto_run_already_running"):
        return {
            "ok": True,
            "status": "GOAL1_AUTO_RUN_ALREADY_RUNNING",
            "pid": prep.get("running_pid"),
            "turns": turns,
            "log_path": str(LOG_PATH),
            "queue": prep.get("queue"),
            "sa_id": prep.get("sa_id"),
            "queue_role": prep.get("queue_role"),
            "message": "Auto-run already in flight — hub prepare skipped STOP to avoid killing active batch",
            "background": True,
        }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(
            f"\n[{_now()}] AUTO-RUN START turns={turns} queue={prep.get('queue')} "
            f"sa={prep.get('sa_id')} role={prep.get('queue_role')} "
            f"(headless agent CLI — Worker chat empty)\n"
        )
        proc = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPTS / "goal1_auto_run_v1.py"),
                str(turns),
                str(timeout_sec),
            ],
            cwd=str(ROOT),
            stdout=fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    LOCK_PATH.write_text(
        json.dumps({"pid": proc.pid, "at": _now(), "turns": turns, "script": "goal1_auto_run_v1.py"}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "status": "GOAL1_AUTO_RUN_STARTED",
        "pid": proc.pid,
        "turns": turns,
        "log_path": str(LOG_PATH),
        "queue": prep.get("queue"),
        "sa_id": prep.get("sa_id"),
        "queue_role": prep.get("queue_role"),
        "message": (
            f"Auto-run {turns} started (pid {proc.pid}) — headless CLI. "
            "Worker chat stays empty. Hub Goal 1 → Batch log: AGENT START / AGENT DONE."
        ),
        "background": True,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Goal 1 deliver + detached auto-run")
    p.add_argument("--turns", type=int, default=10, help="Max turns (default 10)")
    p.add_argument("--timeout", type=int, default=1800, help="Per-turn agent timeout sec")
    p.add_argument("--prepare-only", action="store_true", help="Deliver only — no spawn")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    turns = min(max(1, args.turns), 50)
    if args.prepare_only:
        result = prepare(turns=turns)
    else:
        result = spawn_detached(turns=turns, timeout_sec=args.timeout)
    if args.json or True:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
