#!/usr/bin/env bash
# validate-main-problem-trigger-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/sourcea-main-problem-trigger-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/main_problem_trigger_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/029-main-problem-trigger-v1.mdc || { echo "FAIL missing rule 029"; exit 1; }

python3 scripts/main_problem_trigger_v1.py --activate --text "what is the main problem" --json >/dev/null
test -f "${SINA}/main-problem-trigger-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }
test -f "${SINA}/main-problem-trigger-active-v1.flag" || { echo "FAIL missing flag"; exit 1; }

grep -q 'main_problem_trigger' scripts/agent_memory_mirror_v1.py || { echo "FAIL mirror not wired"; exit 1; }
grep -q 'main_problem' scripts/agent_session_gate_run_v1.py || { echo "FAIL session gate not wired"; exit 1; }

grep -q 'main_problem_report_theater' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct gate not wired"; exit 1; }
grep -q 'main_problem_line' scripts/disk_live_wire_sync_v1.py || { echo "FAIL live wire not wired"; exit 1; }
grep -q 'main_problem_trigger' scripts/agent_behavior_settings_v1.py || { echo "FAIL behavior settings script not wired"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
b = json.loads(Path("data/agent-behavior-settings-v1.json").read_text())
if not b.get("main_problem_trigger", {}).get("active"):
    raise SystemExit("behavior settings main_problem_trigger not active")
print("OK: behavior settings")
PY

echo "PASS: validate-main-problem-trigger-v1"
