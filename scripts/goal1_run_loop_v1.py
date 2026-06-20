#!/usr/bin/env python3
"""Run Goal 1 loop until queue exhausted — agent CLI per turn (real execution)."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
AUTO_LOCK = SINA / "goal1-auto-loop-lock-v1.json"
BATCH_LOG = SINA / "goal1-worker-batch-latest.log"


def _orch():
    spec = importlib.util.spec_from_file_location("o", ROOT / "scripts/healthy-drain-orchestrator-v1.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


def _release_auto_lock() -> None:
    if not AUTO_LOCK.is_file():
        return
    try:
        row = json.loads(AUTO_LOCK.read_text(encoding="utf-8"))
        if row.get("pid") == os.getpid():
            AUTO_LOCK.unlink(missing_ok=True)
    except (OSError, json.JSONDecodeError):
        AUTO_LOCK.unlink(missing_ok=True)


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    try:
        return _run(n, timeout)
    finally:
        _release_auto_lock()


def _log_batch(line: str) -> None:
    try:
        with BATCH_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line.rstrip() + "\n")
    except OSError:
        pass


def _run(n: int, timeout: int) -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    for i in range(n):
        orch = _orch()
        st = orch.status()
        pos_before = st.get("queue_pos") or 0
        total = st.get("queue_total") or 30
        if pos_before > total:
            print(json.dumps({"done": True, "reason": "queue_exhausted", "pos": pos_before}))
            return 0
        phase = (st.get("orchestrator") or {}).get("status")
        inbox = inbox_status()
        if not inbox.get("pending"):
            orch.deliver_current(force=True)
        elif phase != "awaiting_worker":
            orch.deliver_current(force=True)
        inbox = inbox_status()
        role_before = (inbox.get("meta") or {}).get("queue_role")
        _log_batch(f"[loop] turn {i + 1}/{n} queue={pos_before}/{total} starting")
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/start_goal1_worker_turn_v1.py"),
                "--timeout",
                str(timeout),
                "--auto-advance",
                "--quiet",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout + 120,
        )
        try:
            row = json.loads(proc.stdout)
        except json.JSONDecodeError:
            row = {"ok": False, "raw": (proc.stdout or "")[-500:], "stderr": (proc.stderr or "")[-300:]}
        print(json.dumps({"loop_turn": i + 1, **row}), flush=True)
        st_after = _orch().status()
        pos_after = st_after.get("queue_pos") or pos_before
        _log_batch(
            f"[loop] turn {i + 1} done ok={row.get('ok')} "
            f"queue {pos_before}->{pos_after} broker_ok={row.get('broker_ok')}"
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/brain_validate_goal1_v1.py"),
                "--write-receipt",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        try:
            val = json.loads((SINA / "brain-goal1-validation-v1.json").read_text(encoding="utf-8"))
            ch = val.get("chain") or {}
            _log_batch(
                f"[loop] BRAIN_VALIDATION inject={ch.get('inject')} validate={ch.get('validate')} "
                f"activate={ch.get('activate')} sync={ch.get('sync')}"
            )
        except (OSError, json.JSONDecodeError):
            pass
        if row.get("ok"):
            open_sa = str(row.get("sa_id") or "")
            if open_sa.startswith("sa-"):
                subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts/worker_turn_lib.py"),
                        "--close",
                        open_sa,
                        "--force",
                    ],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
        if not row.get("ok"):
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/goal1_lane_broker.py"),
                    "brain-ack",
                    "--note",
                    "run_loop_recovery",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            print(json.dumps({"stopped": True, "turn": i + 1, "error": row}), flush=True)
            return 1
        broker = row.get("broker") or {}
        report = broker.get("report") or {}
        role_before = (inbox.get("meta") or {}).get("queue_role")
        inbox_after = inbox_status()
        role_after = (inbox_after.get("meta") or {}).get("queue_role")
        advanced = row.get("advance_ok")
        if advanced is None:
            advanced = bool(
                broker.get("auto_advance")
                or (broker.get("deliver") or {}).get("ok")
                or pos_after > pos_before
                or role_after != role_before
                or report.get("turn_closed")
                or (broker.get("ok") and report.get("status") == "WORKER_ROUND_REPORT")
            )
        if row.get("ok") and advanced is False and i < n - 1:
            print(
                json.dumps(
                    {
                        "stopped": True,
                        "turn": i + 1,
                        "error": "queue_not_advanced",
                        "pos_before": pos_before,
                        "pos_after": pos_after,
                    }
                ),
                flush=True,
            )
            return 1
    print(json.dumps({"done": True, "turns_run": n, "status": _orch().status()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
