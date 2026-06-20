#!/usr/bin/env python3
"""Choice 1+ unified auto-run — one START, up to 30 turns, INBOX deliver + agent resume.

Law: supersedes fragmented batch/clipboard paths on Hub hero only.
Kill: factory_spawn_gate_v1.drain_spawn_allowed blocks all paths when FREEZE.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ORCH_FLAG = Path.home() / ".sina" / "goal1-orchestrator-autorun-v1.json"
STATE_PATH = Path.home() / ".sina" / "goal1-unified-autorun-v1.json"
DEFAULT_MAX_TURNS = 30


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_active() -> bool:
    return ORCH_FLAG.is_file()


def _load_state() -> dict:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(row: dict) -> dict:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _orch_status() -> dict:
    spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.status()


def status() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from goal1_auto_run_deliver_v1 import _auto_run_running as _loop_running  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    st = _load_state()
    orch = _orch_status()
    running = _loop_running()
    ib = inbox_status()
    meta = ib.get("meta") or {}
    orch_st = orch.get("orchestrator") or {}
    turns_done = int(orch_st.get("turns_completed") or st.get("turns_completed") or 0)
    max_turns = int(st.get("max_turns") or DEFAULT_MAX_TURNS)
    tp_path = Path.home() / ".sina" / "goal1-turn-progress-v1.json"
    turn_running = False
    if tp_path.is_file():
        try:
            turn_running = json.loads(tp_path.read_text(encoding="utf-8")).get("status") == "RUNNING"
        except (OSError, json.JSONDecodeError):
            pass
    live = bool(running) or turn_running
    flag_on = is_active()
    paused = bool(st.get("paused")) and not live
    return {
        "ok": True,
        "active": flag_on or live,
        "running": live,
        "paused": paused,
        "pid": (running or {}).get("pid") if running else None,
        "turns_done": turns_done,
        "max_turns": max_turns,
        "sa_id": meta.get("sa_id") or orch.get("queue_item", {}).get("sa_id"),
        "queue_role": meta.get("queue_role"),
        "queue": ib.get("queue") or f"{orch.get('queue_pos')}/{orch.get('queue_total') or 30}",
        "inbox_pending": ib.get("pending"),
        "orchestrator_status": orch_st.get("status"),
        "started_at": st.get("started_at"),
        "message": (
            f"Running {turns_done}/{max_turns} · {meta.get('sa_id') or '?'} "
            f"{meta.get('queue_role') or ''}".strip()
            if live
            else (
                "Paused — bounded resume on ASF order only"
                if paused
                else (
                    "Spawn gate armed — tap Factory STOP to cancel"
                    if flag_on
                    else "Idle — RUN INBOX when Brain routes · Cursor AUTO-RUN rejected"
                )
            )
        ),
    }


def start(*, max_turns: int = DEFAULT_MAX_TURNS) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from factory_spawn_gate_v1 import drain_spawn_allowed, exit_if_spawn_blocked  # noqa: WPS433

    exit_if_spawn_blocked("goal1_unified_autorun", require_bind=False)
    spawn_gate = drain_spawn_allowed(caller="goal1_unified_autorun")
    if not spawn_gate.get("ok"):
        return spawn_gate
    if is_active():
        cur = status()
        if cur.get("running"):
            return {
                "ok": True,
                "status": "ALREADY_RUNNING",
                "message": cur.get("message"),
                **cur,
            }

    max_turns = min(max(1, int(max_turns)), 50)
    ORCH_FLAG.parent.mkdir(parents=True, exist_ok=True)
    ORCH_FLAG.write_text(
        json.dumps(
            {
                "schema": "goal1-orchestrator-autorun-v1",
                "started_at": _now(),
                "max_turns": max_turns,
                "law": "Choice 1+ unified — not legacy batch",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _save_state({"started_at": _now(), "max_turns": max_turns, "turns_completed": 0, "paused": False})

    from goal1_auto_run_deliver_v1 import spawn_detached  # noqa: WPS433

    spawned = spawn_detached(turns=max_turns, timeout_sec=1800)
    if not spawned.get("ok"):
        ORCH_FLAG.unlink(missing_ok=True)
        return spawned

    out = {
        **spawned,
        "status": "GOAL1_UNIFIED_AUTORUN_STARTED",
        "max_turns": max_turns,
        "orchestrator_autorun": True,
        "message": (
            f"Auto-run started — up to {max_turns} turns. "
            f"INBOX deliver + Worker agent. Tap STOP to halt."
        ),
    }
    _save_state({**_load_state(), "pid": spawned.get("pid"), "last_start": out})
    return out


def stop(*, note: str = "hub_unified_stop") -> dict:
    """Fast hub stop — clear flags + return immediately; kill loop in background."""
    import subprocess as sp

    ORCH_FLAG.unlink(missing_ok=True)
    orch_reset: dict = {"ok": True}
    try:
        spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        orch_reset = mod.reset(reason=note)
    except Exception as exc:
        orch_reset = {"ok": False, "error": str(exc)}

    tp = Path.home() / ".sina" / "goal1-turn-progress-v1.json"
    try:
        tp.write_text(
            json.dumps(
                {"status": "STOPPED", "at": _now(), "message": "Hub stop — tap RESUME to continue"},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass

    sp.Popen(
        [sys.executable, str(SCRIPTS / "stop_goal1_auto_run_v1.py"), "--note", note, "--json"],
        cwd=str(ROOT),
        stdout=sp.DEVNULL,
        stderr=sp.DEVNULL,
        start_new_session=True,
    )

    state = {**_load_state(), "stopped_at": _now(), "note": note, "paused": True, "running": False}
    _save_state(state)
    return {
        "ok": True,
        "status": "GOAL1_UNIFIED_AUTORUN_STOPPED",
        "orchestrator_reset": orch_reset,
        "paused": True,
        "message": "Auto-run stopped — tap ▶ RESUME to continue",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Goal 1 unified auto-run (Choice 1+)")
    p.add_argument("cmd", nargs="?", default="status", choices=("status", "start", "stop"))
    p.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.cmd == "start":
        out = start(max_turns=args.max_turns)
    elif args.cmd == "stop":
        out = stop()
    else:
        out = status()
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
