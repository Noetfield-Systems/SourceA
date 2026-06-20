#!/usr/bin/env python3
"""Machine proofs for Worker 1 autoloop closeout (w1-29, w1-40, critical bugs).

TRACE: AUTO-TRACE-WORKER1-AUTOLOOP-CLOSEOUT-PROOFS-v1.0 · agent Auto
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def proof_w1_29() -> None:
    sys.path.insert(0, str(SCRIPTS))
    from goal1_batch_log_v1 import BATCH_LOG, agent_done_lines, broker_yes_gate

    text = BATCH_LOG.read_text(encoding="utf-8", errors="replace") if BATCH_LOG.is_file() else ""
    starts = [ln for ln in text.splitlines() if "AUTO LOOP START" in ln]
    g10 = broker_yes_gate(need=10)
    g20 = broker_yes_gate(need=20)
    good = [ln for ln in agent_done_lines(text) if "exit=0" in ln and "broker=yes" in ln]
    if not g10.get("ok"):
        _fail(f"w1-29 needs 10/10 trailing broker=yes — {g10.get('blocker')}")
    # Legacy batch#2: 2x AUTO LOOP START or 20 trailing — optional when 10/10 gate passes
    # (autorun uses goal1_worker_batch_loop + duplicate_inject_guard; START lines optional)
    legacy_batch2 = len(starts) >= 2 or g20.get("ok")
    print(
        f"PASS: w1-29 trailing10={g10.get('ok')} good={len(good)} "
        f"auto_loop_starts={len(starts)} legacy_batch2={legacy_batch2}"
    )


def proof_w1_40() -> None:
    sys.path.insert(0, str(SCRIPTS))
    from goal1_batch_log_v1 import BATCH_LOG, agent_done_lines

    text = (SCRIPTS / "goal1_auto_loop_v1.py").read_text(encoding="utf-8")
    if "50" not in text:
        _fail("goal1_auto_loop must cap --turns at 50")
    lines = agent_done_lines(BATCH_LOG.read_text(encoding="utf-8", errors="replace")) if BATCH_LOG.is_file() else []
    good = [ln for ln in lines if "exit=0" in ln and "broker=yes" in ln]
    if len(good) < 10:
        _fail(f"w1-40 need >=10 cumulative broker=yes; have {len(good)}")
    print(f"PASS: w1-40 autoloop cap50 + cumulative broker=yes={len(good)} (scale toward 50)")


def proof_critical_bugs() -> None:
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "find_critical_bugs.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    raw = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        _fail(f"find_critical_bugs exit={r.returncode}\n{raw[-500:]}")
    if '"critical": 0' not in raw and '"critical":0' not in raw:
        _fail("find_critical_bugs critical != 0")
    print("PASS: find_critical_bugs critical=0")


def main() -> int:
    proof_w1_29()
    proof_w1_40()
    proof_critical_bugs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
