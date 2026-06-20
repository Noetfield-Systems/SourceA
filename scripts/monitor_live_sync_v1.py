#!/usr/bin/env python3
"""Monitor disk live wire — background sync from ~/.sina + repo SSOT (no agent refresh).

Law: monitor :13021 reads disk; this module keeps sidecars fresh when files change.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "monitor-live-v1.json"

WATCH_PATHS = (
    ROOT / "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md",
    ROOT / "SINA_OS_SSOT_LOCKED.md",
    ROOT / "SINA_GOVERNANCE_ENTRY_LOCKED_v1.md",
    ROOT / "PROGRAM_PROGRESS.json",
    SINA / "healthy-queue-30-active.json",
    SINA / "healthy-queue-state-v1.json",
    SINA / "worker-prompt-inbox-v1.json",
    SINA / "factory-mode-v1.json",
    SINA / "factory-now-v1.json",
    SINA / "phase-strict-drain-v1.json",
    SINA / "live-ongoing-prompts-next-10-v1.json",
    SINA / "auto-run-disabled-v1.flag",
    SINA / "founder-stop-receipt-v1.json",
    SINA / "goal1-lane-broker-v1.json",
    ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json",
    SINA / "PROGRAM_1000_HONEST_STATUS.json",
    SINA / "PROGRAM_1000_STEP_MATRIX.json",
    SINA / "governance-zero-drift-live-wire-v1.json",
    SINA / "voyage-ai-live-wire-v1.json",
    SINA / "vector_index_v1.json",
    SINA / "anti-staleness-auto-wire-v1.json",
    SINA / "governance_drift_report_v1.json",
    SINA / "stranger-agent-admission-v1.json",
)

RECEIPTS_DIR = ROOT / "receipts"
BROKER_EVENTS = SINA / "goal1-lane-broker-events.jsonl"

_lock = threading.RLock()
_last_sig: str = ""
_last_sync_at: str = ""
_thread: threading.Thread | None = None
_running = False


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mtime_sig(path: Path) -> str:
    if not path.exists():
        return f"missing:{path}"
    try:
        st = path.stat()
        return f"{path}:{st.st_mtime_ns}:{st.st_size}"
    except OSError:
        return f"err:{path}"


def disk_signature() -> str:
    parts = [_mtime_sig(p) for p in WATCH_PATHS]
    if RECEIPTS_DIR.is_dir():
        try:
            n = len(list(RECEIPTS_DIR.glob("sa-*-receipt.json")))
            mt = RECEIPTS_DIR.stat().st_mtime_ns
            parts.append(f"receipts:{n}:{mt}")
        except OSError:
            parts.append("receipts:err")
    if BROKER_EVENTS.is_file():
        parts.append(_mtime_sig(BROKER_EVENTS))
    return "|".join(parts)


def _run_quick(cmd: list[str], *, timeout: int = 45) -> bool:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def sync_disk(*, force: bool = False, reason: str = "tick", light: bool = False) -> dict:
    """Refresh monitor sidecars when disk signature changes.

    light=True — skip G7/S10 monitor hooks (cascade/g3 drain must not recurse).
    """
    global _last_sig, _last_sync_at
    sig = disk_signature()
    with _lock:
        if not force and sig == _last_sig and OUT.is_file():
            try:
                row = json.loads(OUT.read_text(encoding="utf-8"))
                row["reason"] = "unchanged"
                return row
            except (OSError, json.JSONDecodeError):
                pass

        honest_ok = _run_quick(
            [sys.executable, str(SCRIPTS / "program-1000-honest-status-v1.py"), "--write"],
            timeout=30,
        )
        ssot: dict = {}
        factory_row: dict = {}
        run_inbox_truth: dict = {}
        try:
            sys.path.insert(0, str(SCRIPTS))
            from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

            ssot = unify_queue_ssot(write_brain=False, rebuild_factory=True)
            steps = ssot.get("steps") or {}
            factory_row = steps.get("factory_now") or {}
            run_inbox_truth = steps.get("run_inbox_truth") or {}
            if not factory_row:
                factory_row = {"error": "queue_ssot_unify missing factory_now", "ssot_ok": ssot.get("ok")}
        except Exception as exc:
            ssot = {"ok": False, "error": str(exc)}
            factory_row = {"error": str(exc)}

        pulse: dict = {}
        try:
            sys.path.insert(0, str(SCRIPTS))
            from monitor_honesty_lib_v1 import audit_monitor  # noqa: WPS433

            pulse = audit_monitor(filter_mode="road")
        except Exception as exc:
            pulse = {"ok": False, "error": str(exc)}

        prog = pulse.get("progress") or {}
        y = pulse.get("you_are_here") or {}
        row = {
            "schema": "monitor-live-v1",
            "at": _now(),
            "reason": reason,
            "signature_changed": sig != _last_sig or force,
            "honest_status_written": honest_ok,
            "valid_yes": prog.get("valid_yes"),
            "receipt_done": pulse.get("receipt_done"),
            "here_sa": y.get("sa_id"),
            "here_role": y.get("role"),
            "queue_pos": y.get("queue_pos"),
            "queue_total": y.get("queue_total"),
            "factory_mode": (pulse.get("factory_now") or {}).get("mode"),
            "freeze": (pulse.get("factory_now") or {}).get("kill_flag"),
            "phase_strict": (pulse.get("phase_strict") or {}).get("order"),
            "inbox_pending": (pulse.get("factory_now") or {}).get("inbox_pending"),
            "law": "disk-wired · no agent refresh required",
            "queue_ssot_unify": {
                "ok": ssot.get("ok"),
                "aligned": (ssot.get("steps") or {}).get("aligned"),
                "truth_match": (ssot.get("steps") or {}).get("truth_match"),
            },
        }
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if run_inbox_truth:
            row["run_inbox_truth"] = run_inbox_truth
        else:
            try:
                from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

                row["run_inbox_truth"] = write_truth(sync=False)
            except Exception as exc:
                row["run_inbox_truth_error"] = str(exc)
        try:
            from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

            row["live_ongoing_prompts"] = rebuild(write=True, preview=False)
        except Exception as exc:
            row["live_ongoing_error"] = str(exc)
        if not light:
            try:
                from s10_eternal_audit_loop_v1 import maybe_run_daily_from_monitor  # noqa: WPS433

                s10 = maybe_run_daily_from_monitor()
                if s10:
                    row["s10_eternal"] = {
                        "ran": True,
                        "ok": s10.get("ok"),
                        "pack": s10.get("pack"),
                        "counts": s10.get("counts"),
                    }
            except Exception as exc:
                row["s10_eternal_error"] = str(exc)
            try:
                from governance_self_heal_daemon_v1 import maybe_run_heal_from_monitor  # noqa: WPS433

                g7 = maybe_run_heal_from_monitor()
                if g7:
                    row["g7_self_heal"] = g7
            except Exception as exc:
                row["g7_self_heal_error"] = str(exc)
        _last_sig = sig
        _last_sync_at = row["at"]
        row["factory_now"] = factory_row
        return row


def load_pulse() -> dict:
    if OUT.is_file():
        try:
            return json.loads(OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return sync_disk(force=True, reason="cold_start")


def _loop(*, interval_sec: float = 5.0) -> None:
    global _running
    while _running:
        try:
            sync_disk(reason="background")
        except Exception:
            pass
        time.sleep(interval_sec)


def start_background(*, interval_sec: float = 5.0) -> None:
    global _thread, _running
    if _thread and _thread.is_alive():
        return
    _running = True
    sync_disk(force=True, reason="daemon_start")
    _thread = threading.Thread(target=_loop, kwargs={"interval_sec": interval_sec}, daemon=True)
    _thread.start()


def stop_background() -> None:
    global _running
    _running = False


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Monitor disk live sync")
    p.add_argument("--json", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--daemon", action="store_true", help="Run background loop (blocking)")
    p.add_argument("--interval", type=float, default=5.0)
    args = p.parse_args()
    if args.daemon:
        start_background(interval_sec=args.interval)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            stop_background()
        return 0
    row = sync_disk(force=args.force, reason="cli")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"MONITOR-LIVE: valid_yes={row.get('valid_yes')} here={row.get('here_sa')} "
            f"queue={row.get('queue_pos')}/{row.get('queue_total')} at={row.get('at')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
