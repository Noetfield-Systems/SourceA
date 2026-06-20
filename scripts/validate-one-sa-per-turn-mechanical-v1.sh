#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash scripts/validate-worker-one-sa-turn-v1.sh

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from one_sa_per_turn_gate_v1 import validate_agent_output, VIOLATION_LOG

good = """status: WORKER_ROUND_REPORT
sa_focus: sa-0999
round_type: audit
validate:
  spine: PASS
"""
bad = """status: WORKER_ROUND_REPORT
sa_focus: sa-0998
---
status: WORKER_ROUND_REPORT
sa_focus: sa-0999
"""
g = validate_agent_output(text=good, expected_sa="sa-0999")
assert g.get("ok"), g
b = validate_agent_output(text=bad, expected_sa="sa-0999")
assert not b.get("ok"), b
assert "multiple" in str(b.get("violations")).lower() or b.get("status") == "ONE_SA_BATCH_VIOLATION"
print("PASS: batch detection")
PY

grep -q "guard_broker_submit" scripts/goal1_lane_broker.py
grep -q "guard_before_agent_turn" scripts/start_goal1_worker_turn_v1.py
grep -q "inbox_status" scripts/cursor_entry_gate.py

echo "OK: validate-one-sa-per-turn-mechanical-v1"
