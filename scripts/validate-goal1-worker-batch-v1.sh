#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
test -f "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
test -f "$ROOT/brain-os/law/enforcement/GOAL1_BATCH_CHECKPOINT_LOCKED_v1.md"
python3 -m py_compile "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
grep -q "auto_advance" "$ROOT/scripts/goal1_lane_broker.py"
grep -q "brain-checkpoint-ack" "$ROOT/scripts/goal1_lane_broker.py"
grep -q "founder-start-worker-batch-5" "$ROOT/scripts/sina_command_lib.py"
grep -q '"hidden": True' "$ROOT/scripts/sina_command_lib.py"
! grep -q 'data-action-id="founder-start-worker-batch-5"' "$ROOT/agent-control-panel/assets/app.js"
echo "OK: validate-goal1-worker-batch-v1"
