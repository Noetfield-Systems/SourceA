#!/usr/bin/env bash
# Closeout gate — block batch stamp; require receipt for broker path.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import json
import subprocess
import sys
from pathlib import Path

root = Path(".")
scripts = root / "scripts"

# Batch evidence must fail
proc = subprocess.run(
    [sys.executable, str(scripts / "closeout_sa_task.py"), "--id", "sa-9999", "--evidence",
     "pack30 commercial+pre-llm verify-only; wire+dispatch+hub PASS"],
    capture_output=True,
    text=True,
    cwd=str(root),
)
assert proc.returncode != 0, "batch evidence must be blocked"
out = proc.stdout + proc.stderr
assert (
    "BATCH_EVIDENCE_BLOCKED" in out
    or "MISSING_RECEIPT" in out
    or '"ok": false' in out
)
print("OK: batch evidence blocked")

# Unauthorized CLI must fail
proc2 = subprocess.run(
    [sys.executable, str(scripts / "closeout_sa_task.py"), "--id", "sa-9998",
     "--evidence", "unique per-sa validator output from find_critical_bugs critical 0"],
    capture_output=True,
    text=True,
    cwd=str(root),
)
assert proc2.returncode != 0
body2 = proc2.stdout + proc2.stderr
assert (
    "CLOSEOUT_UNAUTHORIZED" in body2
    or "MISSING_RECEIPT" in body2
    or '"ok": false' in proc2.stdout
)
print("OK: unauthorized closeout blocked")

# Receipt + broker path must pass for sa with receipt
rec_dir = root / "receipts"
rec_dir.mkdir(exist_ok=True)
sa = "sa-0154"
rec = rec_dir / f"{sa}-receipt.json"
if not rec.is_file():
    rec.write_text(
        json.dumps({"sa_id": sa, "status": "DONE", "at": "2026-06-08T00:00:00Z"}) + "\n",
        encoding="utf-8",
    )
# fake worker report
import pathlib
report = pathlib.Path.home() / ".sina" / "worker_round_report_v1.json"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(
    json.dumps({
        "status": "WORKER_ROUND_REPORT",
        "sa_focus": sa,
        "round_type": "verify",
        "critical_bugs": 0,
        "at": "2026-06-08T00:00:00Z",
    })
    + "\n",
    encoding="utf-8",
)
proc3 = subprocess.run(
    [
        sys.executable,
        str(scripts / "closeout_sa_task.py"),
        "--id",
        sa,
        "--evidence",
        "validate-closeout-gate-v1 unique proof string for sa-0154 gate test",
        "--source",
        "goal1_lane_broker",
        "--round-type",
        "verify",
    ],
    capture_output=True,
    text=True,
    cwd=str(root),
)
# sa-0154 may already be done — gate should still ok or registry already done
body = proc3.stdout
if '"ok": true' not in body and proc3.returncode != 0:
    print("FAIL: broker+receipt path", body, proc3.stderr, file=sys.stderr)
    sys.exit(1)
print("OK: broker+receipt gate path")

print("OK: validate-closeout-gate-v1")
PY
