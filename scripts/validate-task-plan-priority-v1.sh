#!/usr/bin/env bash
# validate-task-plan-priority-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/sourcea-task-plan-priority-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/task_plan_priority_v1.py || { echo "FAIL missing script"; exit 1; }

python3 scripts/task_plan_priority_v1.py --refresh --json >/dev/null
test -f "${SINA}/task-plan-priority-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }

grep -q 'task_plan_priority' scripts/plans_unified_upgrade_v1.py || { echo "FAIL plans_unified not wired"; exit 1; }
grep -q 'task_plan_priority' scripts/agent_session_gate_run_v1.py || { echo "FAIL session gate not wired"; exit 1; }
grep -q 'task_plan_priority_line' scripts/disk_live_wire_sync_v1.py || { echo "FAIL live wire not wired"; exit 1; }
grep -q 'task_plan_priority_detail' scripts/agent_memory_mirror_v1.py || { echo "FAIL mirror not wired"; exit 1; }
grep -q 'task_plan_priority_v1' scripts/next_task_trigger_v1.py || { echo "FAIL next_task_trigger not wired"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/task-plan-priority-receipt-v1.json").read_text())
if not r.get("smart_pick"):
    raise SystemExit("missing smart_pick")
if not r.get("ranked"):
    raise SystemExit("missing ranked list")
if not r.get("task_plan_priority_line"):
    raise SystemExit("missing priority line")
b = json.loads(Path("data/agent-behavior-settings-v1.json").read_text())
if not b.get("task_plan_priority", {}).get("active"):
    raise SystemExit("behavior settings task_plan_priority not active")
print("OK: smart_pick", r["smart_pick"].get("task_id"))
PY

echo "PASS: validate-task-plan-priority-v1"
