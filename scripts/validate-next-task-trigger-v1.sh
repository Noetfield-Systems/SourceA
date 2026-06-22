#!/usr/bin/env bash
# validate-next-task-trigger-v1.sh — v2 always-on task/plan validation
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/sourcea-next-task-trigger-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/next_task_trigger_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/034-next-task-trigger-v1.mdc || { echo "FAIL missing rule 034"; exit 1; }

grep -q '"always_apply": true' data/sourcea-next-task-trigger-v1.json || { echo "FAIL SSOT always_apply not true"; exit 1; }
grep -qE 'always_apply|always-on' .cursor/rules/034-next-task-trigger-v1.mdc || { echo "FAIL rule missing always-on law"; exit 1; }

python3 scripts/next_task_trigger_v1.py --refresh --json >/dev/null
test -f "${SINA}/next-task-trigger-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }
test -f "${SINA}/task-plan-validation-always-v1.flag" || { echo "FAIL missing always-on flag"; exit 1; }

python3 scripts/next_task_trigger_v1.py --activate --text "next task" --json >/dev/null
test -f "${SINA}/next-task-trigger-active-v1.flag" || { echo "FAIL missing trigger flag after activate"; exit 1; }

python3 scripts/next_task_trigger_v1.py --detect-topic "what is the plan for B0006" --json | grep -q '"topic": true' \
  || { echo "FAIL topic detect"; exit 1; }

grep -q 'task_plan_validate_baseline' scripts/agent_session_gate_run_v1.py || { echo "FAIL session gate baseline not wired"; exit 1; }
grep -q 'next_task_trigger' scripts/agent_session_gate_run_v1.py || { echo "FAIL session gate not wired"; exit 1; }
grep -q 'next_task_trigger' scripts/agent_memory_mirror_v1.py || { echo "FAIL mirror not wired"; exit 1; }
grep -q 'next_task_line' scripts/disk_live_wire_sync_v1.py || { echo "FAIL live wire not wired"; exit 1; }
grep -q 'task-plan-validation-always' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct gate always-on not wired"; exit 1; }
grep -q 'detect_task_plan_topic' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct gate topic detect not wired"; exit 1; }
grep -q 'next_task_trigger' scripts/agent_behavior_settings_v1.py || { echo "FAIL behavior settings not wired"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
b = json.loads(Path("data/agent-behavior-settings-v1.json").read_text())
nt = b.get("next_task_trigger") or {}
if not nt.get("active"):
    raise SystemExit("behavior settings next_task_trigger not active")
if not nt.get("always_apply"):
    raise SystemExit("behavior settings always_apply not true")
r = json.loads(Path.home().joinpath(".sina/next-task-trigger-receipt-v1.json").read_text())
if not r.get("always_apply"):
    raise SystemExit("receipt always_apply not true")
p = r.get("pipeline") or {}
for k in ("what_is_task", "benefit_and_priority", "usefulness_verdict", "output_type", "proceed"):
    if k not in p:
        raise SystemExit(f"missing pipeline field {k}")
print("OK: pipeline fields v2")
PY

echo "PASS: validate-next-task-trigger-v1"
