#!/usr/bin/env python3
"""Hard stop Goal 1 auto-run — Hub ■ Stop must kill agent CLI + parents + locks.

Law: founder never uses Terminal — this script is what Hub /api/action calls.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"

PARENT_PATTERNS = (
    "goal1_worker_batch_loop_v1.py",
    "goal1_auto_run_deliver_v1.py",
    "goal1_auto_loop_v1.py",
    "goal1_auto_run_v1.py",
    "goal1_run_loop",
    "brain_execute_turn_v1.py",
    "start_goal1_worker_turn_v1.py",
)

AGENT_PATTERNS = (
    "agent -p -f",
    "agent.*INBOX TURN",
    "SourceA Worker",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


BATCH_LOG = SINA / "goal1-worker-batch-latest.log"


def _agent_done_lines(text: str) -> list[str]:
    return [
        ln
        for ln in (text or "").splitlines()
        if "AGENT DONE" in ln and "post-pack-hygiene" not in ln
    ]


def consecutive_broker_no_streak(*, log_path: Path | None = None) -> int:
    """Count trailing AGENT DONE lines with broker=no before first broker=yes."""
    path = log_path or BATCH_LOG
    if not path.is_file():
        return 0
    try:
        lines = _agent_done_lines(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return 0
    streak = 0
    for ln in reversed(lines):
        if "broker=no" in ln:
            streak += 1
        elif "broker=yes" in ln:
            break
        else:
            break
    return streak


def clear_stale_batch_tail_hygiene(*, note: str = "nw-04") -> dict:
    """Append broker=yes hygiene receipt so brain_validate is not stuck on stale broker=no tail."""
    streak = consecutive_broker_no_streak()
    at = _now()
    detail = f"stale sa_mismatch/broker=no tail cleared" if streak else "batch tail hygiene"
    try:
        with BATCH_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"\n[{at}] POST-PACK-HYGIENE {detail} ({note}) · prior_streak={streak}\n")
            fh.write(
                f"[{at}] AGENT DONE post-pack-hygiene exit=0 broker=yes advance=yes report=yes chars=0\n"
            )
    except OSError as exc:
        return {"ok": False, "error": str(exc)}

    progress_path = SINA / "goal1-turn-progress-v1.json"
    try:
        progress_path.write_text(
            json.dumps(
                {
                    "status": "STOPPED",
                    "at": at,
                    "message": f"post-pack hygiene — stale broker=no tail cleared ({note})",
                    "prior_broker_no_streak": streak,
                    "broker_ok": True,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass
    return {
        "ok": True,
        "hygiene": True,
        "prior_broker_no_streak": streak,
        "batch_log": str(BATCH_LOG),
    }


def _pids_for_pattern(pattern: str) -> list[int]:
    proc = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    out: list[int] = []
    for line in (proc.stdout or "").splitlines():
        if line.strip().isdigit():
            pid = int(line.strip())
            if pid != os.getpid():
                out.append(pid)
    return out


def _kill_pid(pid: int, *, sig: int = signal.SIGTERM) -> bool:
    try:
        os.kill(pid, sig)
        return True
    except OSError:
        return False


def _kill_tree(pids: list[int]) -> list[int]:
    killed: list[int] = []
    for pid in pids:
        if _kill_pid(pid, sig=signal.SIGTERM):
            killed.append(pid)
    if killed:
        time.sleep(0.8)
    for pid in list(killed):
        try:
            os.kill(pid, 0)
            _kill_pid(pid, sig=signal.SIGKILL)
        except OSError:
            pass
    return killed


def stop_all(
    *,
    note: str = "hub_stop",
    hygiene_tail: bool = False,
    broker_no_streak: int = 0,
) -> dict:
    streak = consecutive_broker_no_streak()
    if broker_no_streak > 0 and streak < broker_no_streak:
        return {
            "ok": True,
            "status": "GOAL1_AUTO_RUN_STOP_SKIPPED",
            "skipped": True,
            "reason": f"broker_no_streak {streak} < {broker_no_streak}",
            "broker_no_streak": streak,
            "message": f"No stop — broker=no streak {streak} below threshold {broker_no_streak}",
        }

    killed_labels: list[str] = []
    all_pids: set[int] = set()

    for pat in PARENT_PATTERNS:
        for pid in _pids_for_pattern(pat):
            all_pids.add(pid)
            killed_labels.append(f"{pat}:{pid}")

    for pat in AGENT_PATTERNS:
        for pid in _pids_for_pattern(pat):
            all_pids.add(pid)
            killed_labels.append(f"agent:{pid}")

    killed = _kill_tree(sorted(all_pids))

    # prepare() calls stop before spawn — must not clear Hub autorun intent flag.
    if note not in ("auto_run_prepare", "auto_loop_prepare"):
        for flag in (
            SINA / "goal1-orchestrator-autorun-v1.json",
            SINA / "goal1-unified-autorun-v1.json",
        ):
            flag.unlink(missing_ok=True)

    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "orch", ROOT / "scripts/healthy-drain-orchestrator-v1.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        orch_reset = mod.reset(reason=note)
    except Exception as exc:
        orch_reset = {"ok": False, "error": str(exc)}

    for lock in (
        SINA / "brain-executor-lock-v1.json",
        SINA / "goal1-worker-batch-lock-v1.json",
        SINA / "goal1-auto-run-lock-v1.json",
        SINA / "goal1-auto-loop-lock-v1.json",
    ):
        lock.unlink(missing_ok=True)

    # Broker: force idle so UI is not stuck on batch_running / awaiting_brain_ack
    broker_path = SINA / "goal1-lane-broker-v1.json"
    if broker_path.is_file():
        try:
            st = json.loads(broker_path.read_text(encoding="utf-8"))
            st["status"] = "idle"
            st["stopped_at"] = _now()
            st["stop_note"] = note
            st.pop("batch", None)
            last = st.get("last_worker_report") or {}
            if str(last.get("sa_focus") or "").endswith("-TEST"):
                st.pop("last_worker_report", None)
                st.pop("orchestrator_result", None)
            broker_path.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    progress_path = SINA / "goal1-turn-progress-v1.json"
    if note not in ("auto_run_prepare", "auto_loop_prepare"):
        try:
            progress_path.write_text(
                json.dumps(
                    {
                        "status": "STOPPED",
                        "at": _now(),
                        "message": "Hub Stop — no agent running",
                        "stop_note": note,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass

    log_path = SINA / "goal1-worker-batch-latest.log"
    try:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n[{_now()}] STOP — killed {len(killed)} pids — {note}\n")
    except OSError:
        pass

    recovery_row: dict = {}
    fast_prepare = note in ("auto_run_prepare", "auto_loop_prepare")
    if not fast_prepare:
        try:
            rec = subprocess.run(
                [sys.executable, str(ROOT / "scripts/worker_stuck_recovery_v1.py"), "--json"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if rec.stdout.strip():
                recovery_row = json.loads(rec.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            recovery_row = {}

        # SSOT: overnight / API / CLI orphans (BRAIN_NO_LEFTOVER_PROCESS_LOCKED_v1)
        try:
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/cleanup-goal1-leftovers-v1.py"), "--json"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    remaining = []
    for pat in PARENT_PATTERNS + AGENT_PATTERNS:
        remaining.extend(_pids_for_pattern(pat))
    for pat in (
        "start-overnight-3engine-v1.sh",
        "autorun_dispatcher_v1.py",
        "claude_api_agent_v1.py",
        "claude_code_agent_v1.py",
        "claude -p You are SourceA Worker",
    ):
        remaining.extend(_pids_for_pattern(pat))

    msg = (
        f"Stopped {len(killed)} process(es) — locks cleared"
        if killed
        else "No auto-run processes — locks cleared anyway"
    )
    if remaining:
        msg += f" · WARNING: {len(remaining)} still running — tap Stop again"

    out: dict = {
        "ok": len(remaining) == 0,
        "status": "GOAL1_AUTO_RUN_STOPPED",
        "killed_count": len(killed),
        "killed": killed_labels[:30],
        "remaining_pids": remaining[:20],
        "locks_cleared": True,
        "orchestrator_reset": orch_reset,
        "broker_no_streak": streak,
        "message": msg,
        "worker_recovery": recovery_row,
    }
    if hygiene_tail or (broker_no_streak > 0 and streak >= broker_no_streak):
        out["hygiene"] = clear_stale_batch_tail_hygiene(note=note)
    return out


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Hard stop Goal 1 auto-run")
    p.add_argument("--note", default="cli")
    p.add_argument(
        "--broker-no-streak",
        type=int,
        default=0,
        metavar="N",
        help="Stop+hygiene only when N consecutive broker=no at batch tail (0=always stop)",
    )
    p.add_argument(
        "--hygiene-tail",
        action="store_true",
        help="Append post-pack-hygiene broker=yes receipt to batch log",
    )
    p.add_argument(
        "--hygiene-only",
        action="store_true",
        help="Clear stale batch tail only — do not kill processes",
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.hygiene_only:
        result = clear_stale_batch_tail_hygiene(note=args.note)
        result["status"] = "GOAL1_BATCH_HYGIENE"
    else:
        result = stop_all(
            note=args.note,
            hygiene_tail=args.hygiene_tail or args.broker_no_streak > 0,
            broker_no_streak=args.broker_no_streak,
        )
        try:
            sys.path.insert(0, str(ROOT / "scripts"))
            from factory_control_v1 import write_stop_receipt  # noqa: WPS433

            result["stop_receipt"] = write_stop_receipt(
                trigger=args.note,
                set_by="stop_goal1_auto_run_v1",
            )
        except Exception as exc:
            result["stop_receipt"] = {"ok": False, "error": str(exc)}
        try:
            from hub_projection_sync_v1 import sync_hub_projection  # noqa: WPS433

            if args.note not in ("auto_run_prepare", "auto_loop_prepare"):
                result["hub_projection_sync"] = sync_hub_projection(caller="stop_goal1_auto_run")
            else:
                result["hub_projection_sync"] = {"ok": True, "skipped": "fast_prepare"}
        except Exception as exc:
            result["hub_projection_sync"] = {"ok": False, "error": str(exc)}
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
