#!/usr/bin/env python3
"""G3.2 — rolling smooth truth score from validators + dual-pick + AS-01."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "agent-smooth-truth-score-v1.json"
HISTORY = SINA / "agent-smooth-truth-history.jsonl"


def _run(cmd: list[str], *, timeout: int = 120) -> bool:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def compute_score() -> dict:
    checks = {
        "dual_pick": _run([sys.executable, str(ROOT / "scripts" / "_ecosystem_safety_dual_pick_check_v1.py")]),
        "as01": _run(["bash", str(ROOT / "scripts" / "validate-hub-p0-no-autorun-v1.sh")]),
        "factory_conduct": _run(["bash", str(ROOT / "scripts" / "validate-factory-conduct-v1.sh")]),
        "ecosystem_safety": _run(["bash", str(ROOT / "scripts" / "validate-ecosystem-safety-v1.sh")], timeout=180),
    }
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    score = round(100.0 * passed / max(total, 1), 1)
    row = {
        "schema": "agent-smooth-truth-score-v1",
        "at": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "passed": passed,
        "total": total,
        "checks": checks,
        "law": "projection + control planes aligned",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def main() -> int:
    row = compute_score()
    print(json.dumps(row, indent=2))
    return 0 if row.get("score", 0) >= 75 else 1


if __name__ == "__main__":
    raise SystemExit(main())
