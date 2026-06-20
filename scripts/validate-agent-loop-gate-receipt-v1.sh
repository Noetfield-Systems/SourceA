#!/usr/bin/env bash
# Agent loop must block without valid worker gate receipt (Layer 3).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

grep -q "loop_gate_block" "$ROOT/scripts/agent_loop.py" || {
  echo "FAIL: agent_loop.py must call loop_gate_block"
  exit 1
}
test -f "$ROOT/scripts/gate_receipt_lib.py"

python3 "$ROOT/scripts/_worker_turn_validate_restore.py" >/dev/null

python3 <<PY
import sys
sys.path.insert(0, "$ROOT/scripts")
from gate_receipt_lib import gate_receipt_ok, loop_gate_block
ok, err, _ = gate_receipt_ok(role="worker", max_age_hours=24)
if not ok:
    print(f"FAIL: gate after run: {err}")
    sys.exit(1)
if loop_gate_block() is not None:
    print("FAIL: loop_gate_block should pass after fresh gate")
    sys.exit(1)
print("OK: validate-agent-loop-gate-receipt-v1")
PY
