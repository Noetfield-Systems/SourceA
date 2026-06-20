#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/ACTIVE_NOW.md"
test -f "$ROOT/scripts/active_now_v1.py"
test -f "$ROOT/brain-os/laws/ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md"
grep -q "ACTIVE_NOW.md" "$ROOT/scripts/cursor_entry_gate.py"
grep -q "active_now_v1" "$ROOT/scripts/brain-session-start.sh"
grep -q "active_now_v1" "$ROOT/scripts/claude_code_agent_v1.py"
grep -q "active_now_v1" "$ROOT/scripts/claude_api_agent_v1.py"
grep -q "active_now_v1" "$ROOT/scripts/auto_run_worker_batch_v1.py"
grep -q "active_now_v1" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
grep -q "active_now_v1" "$ROOT/scripts/healthy-drain-orchestrator-v1.py"
grep -q "active_now_v1" "$ROOT/scripts/start_goal1_worker_turn_v1.py"
grep -q "active_now_v1" "$ROOT/scripts/brain_validate_goal1_v1.py"
grep -q "active_now_v1" "$ROOT/scripts/brain_run_loop_trace_v1.py"

python3 "$ROOT/scripts/active_now_v1.py" --heartbeat --caller validate --json >/dev/null
test -f "${HOME}/.sina/active-now-heartbeat-v1.jsonl"

echo "OK: validate-active-now-heartbeat-v1"
