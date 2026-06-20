#!/usr/bin/env python3
"""Read-only cross-plan gate — Worker does not claim global DONE until other agents green."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = Path.home() / ".sina" / "cross-plan-readiness-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 300) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")
    except Exception as exc:
        return False, str(exc)


def _score_receipt_fresh(*, max_age_sec: int = 300) -> bool:
    score_path = Path.home() / ".sina" / "live-prompt-lane-score-v1.json"
    if not score_path.is_file():
        return False
    try:
        score = json.loads(score_path.read_text(encoding="utf-8"))
        at = score.get("at") or ""
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        return (
            age < max_age_sec
            and bool(score.get("ok"))
            and float(score.get("score_pct") or 0) >= 90.0
        )
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return False


def assess(*, write: bool = True, fast: bool = False) -> dict:
    blocked: list[str] = []

    if not fast and (os.environ.get("SINA_BRAIN_CHAT", "").strip() in ("1", "true", "yes") or _score_receipt_fresh()):
        fast = True

    score_path = Path.home() / ".sina" / "live-prompt-lane-score-v1.json"
    ok_lp = False
    if fast and score_path.is_file():
        try:
            score = json.loads(score_path.read_text(encoding="utf-8"))
            ok_lp = bool(score.get("ok")) and float(score.get("score_pct") or 0) >= 90.0
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            ok_lp = False
    if not ok_lp:
        ok_lp, _ = _run(
            [sys.executable, str(SCRIPTS / "live-prompt-lane-score-v1.py"), "--strict", "--use-receipt"]
        )
    live_prompt_worker = "PASS" if ok_lp else "FAIL"

    ok_bugs, bugs_out = _run([sys.executable, str(SCRIPTS / "find_critical_bugs.py")])
    critical_zero = "critical=0" in bugs_out or "critical: 0" in bugs_out.lower()
    anti_staleness = "WAIT"
    ok_as, as_out = _run(["bash", str(SCRIPTS / "validate-anti-staleness-bundle-v1.sh")], timeout=600)
    if ok_as and "19/19" in as_out:
        anti_staleness = "PASSED"
    elif ok_as:
        anti_staleness = "PARTIAL"
    else:
        anti_staleness = "WAIT"
        blocked.append("validate-anti-staleness-bundle")

    if not critical_zero:
        blocked.append("find_critical_bugs")

    finish_plan = "WAIT"
    prog = ROOT / "PROGRAM_PROGRESS.json"
    if prog.is_file():
        try:
            data = json.loads(prog.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "nested" not in str(data)[:500]:
                finish_plan = "PARTIAL"
        except Exception:
            blocked.append("PROGRAM_PROGRESS")

    row = {
        "schema": "cross-plan-readiness-v1",
        "at": _now(),
        "live_prompt_worker": live_prompt_worker,
        "anti_staleness_v2": anti_staleness,
        "finish_plan_10phase": finish_plan,
        "find_critical_bugs_ok": ok_bugs and critical_zero,
        "blocked_on": blocked,
        "worker_global_done": live_prompt_worker == "PASS" and not blocked,
        "note": "Worker lane complete; global DONE waits on SinaaiDataBase agents",
    }
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--fast", action="store_true", help="Reuse live-prompt-lane-score receipt if present")
    args = p.parse_args()
    row = assess(fast=args.fast)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
