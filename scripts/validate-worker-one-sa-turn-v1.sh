#!/usr/bin/env bash
# Mechanical one-sa-per-turn — worker_turn_state + round report gate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
test -f "$ROOT/scripts/worker_turn_lib.py"
grep -q "close_turn" "$ROOT/scripts/closeout_sa_task.py"
grep -q "turn_open_block" "$ROOT/scripts/cursor_entry_gate.py"

python3 <<PY
import json, sys
from pathlib import Path
sys.path.insert(0, "$ROOT/scripts")
from worker_turn_lib import close_turn, open_turn, turn_open_block, TURN_STATE, ROUND_REPORT

# simulate: open -> block -> close -> open ok
if TURN_STATE.is_file():
    TURN_STATE.unlink()
if ROUND_REPORT.is_file():
    ROUND_REPORT.unlink()

o = open_turn(sa_id="sa-TEST-0001", path="test")
if not o.get("ok"):
    print("FAIL: open_turn", o)
    sys.exit(1)
b = turn_open_block()
if not b:
    print("FAIL: expected block while turn open")
    sys.exit(1)
c = close_turn(sa_id="sa-TEST-0001")
if not c.get("ok"):
    print("FAIL: close_turn", c)
    sys.exit(1)
if not ROUND_REPORT.is_file():
    print("FAIL: missing round report file")
    sys.exit(1)
b2 = turn_open_block()
if b2:
    print("FAIL: still blocked after close", b2)
    sys.exit(1)
# Never leave test artifacts on production SSOT paths
if TURN_STATE.is_file():
    TURN_STATE.unlink()
if ROUND_REPORT.is_file():
    ROUND_REPORT.unlink()
print("OK: validate-worker-one-sa-turn-v1")
PY
