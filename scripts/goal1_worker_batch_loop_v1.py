#!/usr/bin/env python3
"""Worker-led Goal 1 batch loop — Hub starts; Brain checkpoints every N turns.

Rhythm (locked):
  Worker runs batch_size turns (default 5) with auto-advance — NO Brain per prompt.
  At checkpoint: machine validate batch → auto-continue if PASS; else pause for Brain.
  6 checkpoints × 5 = 30 healthy pack without Brain stuck on every turn.

Law: GOAL1_BATCH_CHECKPOINT_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOCK_PATH = Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json"
LOG_PATH = Path.home() / ".sina" / "goal1-worker-batch-runs.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock() -> dict:
    if LOCK_PATH.is_file():
        try:
            row = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            pid = row.get("pid")
            if pid and _pid_alive(int(pid)):
                return {"ok": False, "error": "WORKER_BATCH_BUSY", "pid": pid}
        except (OSError, json.JSONDecodeError):
            pass
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(
        json.dumps({"pid": os.getpid(), "at": _now()}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"ok": True}


def release_lock() -> None:
    if LOCK_PATH.is_file():
        try:
            row = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            if row.get("pid") == os.getpid():
                LOCK_PATH.unlink(missing_ok=True)
        except (OSError, json.JSONDecodeError):
            LOCK_PATH.unlink(missing_ok=True)


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _ensure_inbox() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from cursor_window_preflight_v1 import run_worker_chat_preflight  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433
    from worker_chat_inject_v1 import focus_worker_chat  # noqa: WPS433

    preflight = run_worker_chat_preflight(caller="goal1_worker_batch_loop")
    if not preflight.get("ok"):
        return {"ok": False, "step": "worker_chat_preflight", **preflight}

    chat_id = preflight.get("conversation_id")

    inbox = inbox_status()
    if inbox.get("pending"):
        return {
            "ok": True,
            "inbox": inbox,
            "worker_chat_id": chat_id,
            "worker_chat_focus": preflight,
        }

    from worker_drain_lib import healthy_drain_paste  # noqa: WPS433

    d = healthy_drain_paste(worker_chat_inject=True)
    if not d.get("ok"):
        orch = _load_module("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
        st = orch.orchestrator_state()
        if st.get("status") == "stopped":
            orch.reset(reason="worker_batch_restart")
        d2 = orch.deliver_current(force=True)
        if not d2.get("ok"):
            return {"ok": False, "step": "deliver", "error": d, "orchestrator": d2}
    return {"ok": True, "inbox": inbox_status()}


def _api_mode() -> bool:
    """True when ANTHROPIC_API_KEY is set — use headless Claude API instead of Cursor."""
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def run_batch(
    *,
    batch_size: int = 5,
    max_batches: int = 6,
    timeout_sec: int = 1800,
) -> dict:
    """Run up to max_batches × batch_size turns. Brain only at checkpoints."""
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="goal1_worker_batch_loop")
    if not hb.get("ok"):
        return {"ok": False, "step": "active_now", **hb}

    use_api = _api_mode()

    if not use_api:
        # Batch AUTO-RUN: agent --resume Worker chat ID — never clipboard into Brain.
        os.environ["SINA_WORKER_CHAT_RESUME_INJECT"] = "1"
        os.environ.pop("SINA_WORKER_CLIPBOARD_INJECT", None)
        os.environ.pop("SINA_ALLOW_CURSOR_PASTE", None)

    lock = acquire_lock()
    if not lock.get("ok"):
        return lock

    batch_size = min(max(1, batch_size), 10)
    max_batches = min(max(1, max_batches), 6)

    broker = _load_module("broker", SCRIPTS / "goal1_lane_broker.py")
    start = None if use_api else _load_module("start", SCRIPTS / "start_goal1_worker_turn_v1.py")
    api_agent = _load_module("api_agent", SCRIPTS / "claude_api_agent_v1.py") if use_api else None

    broker.start_batch(batch_size=batch_size)
    batches_run = 0
    turns_run = 0
    rows: list[dict] = []
    result: dict | None = None

    if use_api:
        print(f"[{_now()}] BATCH MODE: Claude API (headless — no Cursor required)")
    else:
        print(f"[{_now()}] BATCH MODE: Cursor agent CLI (set ANTHROPIC_API_KEY to use API mode)")

    try:
        for batch_idx in range(max_batches):
            batches_run = batch_idx + 1
            for turn_in_batch in range(1, batch_size + 1):
                is_checkpoint = turn_in_batch == batch_size

                if use_api:
                    # API mode: headless, no Cursor, no inbox prep
                    turn = api_agent.run_turn()
                else:
                    prep = _ensure_inbox()
                    if not prep.get("ok"):
                        result = {
                            "ok": False,
                            "status": "WORKER_BATCH_HALT",
                            "reason": prep,
                            "batches_run": batches_run,
                            "turns_run": turns_run,
                            "turns": rows,
                        }
                        _log(result)
                        return result

                    turn = start.run_turn(
                        dry_run=False,
                        timeout_sec=timeout_sec,
                        auto_advance=not is_checkpoint,
                        checkpoint=is_checkpoint,
                    )
                turns_run += 1
                row = {
                    "batch": batch_idx + 1,
                    "turn_in_batch": turn_in_batch,
                    "checkpoint": is_checkpoint,
                    "sa_id": turn.get("sa_id"),
                    "ok": turn.get("ok"),
                    "broker_status": (turn.get("broker") or {}).get("broker_status"),
                }
                rows.append(row)
                _log(row)

                if turn.get("ok"):
                    try:
                        from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

                        sync_brain_snapshot(mode="light", caller=f"worker_batch:{turn.get('sa_id')}")
                    except Exception:
                        pass

                if not turn.get("ok"):
                    result = {
                        "ok": False,
                        "status": "WORKER_BATCH_TURN_FAIL",
                        "turns_run": turns_run,
                        "last": row,
                        "turns": rows,
                    }
                    return result

                bst = broker.broker_state()
                if bst.get("status") == "checkpoint_pending":
                    result = {
                        "ok": False,
                        "status": "WORKER_BATCH_CHECKPOINT_PAUSE",
                        "message": "Batch failed machine gate — autorun will brain-checkpoint-ack",
                        "turns_run": turns_run,
                        "checkpoint": broker.load_checkpoint(),
                        "turns": rows,
                    }
                    return result

        result = {
            "ok": True,
            "status": "WORKER_BATCH_COMPLETE",
            "batch_size": batch_size,
            "max_batches": max_batches,
            "batches_run": batches_run,
            "turns_run": turns_run,
            "turns": rows,
            "founder_action": "AUTO-RUN — next batch scheduled automatically",
        }
        return result
    finally:
        release_lock()
        try:
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            sync_brain_snapshot(mode="light", caller="worker_batch_finally")
        except Exception:
            pass
        try:
            bl = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
            with bl.open("a", encoding="utf-8") as fh:
                fh.write(f"[{_now()}] BATCH END turns={turns_run} brain_receipt=1\n")
        except OSError:
            pass
        try:
            from auto_run_worker_batch_v1 import schedule_after_batch  # noqa: WPS433

            schedule_after_batch(result)
        except Exception:
            pass


def main() -> int:
    sys.path.insert(0, str(SCRIPTS))
    from mac_focus_freeze_v1 import is_focus_freeze, skip_receipt  # noqa: WPS433
    from factory_spawn_gate_v1 import exit_if_spawn_blocked  # noqa: WPS433
    from single_boss_loop_v1 import check_exclusive, claim  # noqa: WPS433

    if is_focus_freeze():
        print(json.dumps(skip_receipt(schema="goal1-worker-batch-v1", script="goal1_worker_batch_loop_v1.py"), indent=2))
        return 0

    exit_if_spawn_blocked("goal1_worker_batch_loop", require_bind=False)
    gate = check_exclusive(mode="worker_batch")
    if not gate.get("ok"):
        print(json.dumps({"ok": False, "error": "other_boss_loop_active", **gate}, indent=2))
        return 1
    claim(mode="worker_batch", kill_others=True)

    p = argparse.ArgumentParser(description="Worker-led Goal 1 batch loop (checkpoint every N)")
    p.add_argument("--batch-size", type=int, default=5, help="Turns per Brain checkpoint (5 or 10)")
    p.add_argument("--max-batches", type=int, default=6, help="Max checkpoint cycles (6×5=30)")
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--yaml", action="store_true")
    args = p.parse_args()

    result = run_batch(
        batch_size=args.batch_size,
        max_batches=args.max_batches,
        timeout_sec=args.timeout,
    )
    if args.yaml:
        lines = [
            f"status: {result.get('status')}",
            f"ok: {result.get('ok')}",
            f"turns_run: {result.get('turns_run')}",
            f"batches_run: {result.get('batches_run')}",
        ]
        print("\n".join(lines))
    else:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
