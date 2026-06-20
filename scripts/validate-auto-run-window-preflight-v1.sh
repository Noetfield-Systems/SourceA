#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f "$ROOT/brain-os/laws/AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1.md"
test -f "$ROOT/scripts/cursor_window_preflight_v1.py"

grep -q "run_cursor_window_preflight" "$ROOT/scripts/worker_inject_lib.py"
grep -q "run_cursor_window_preflight" "$ROOT/scripts/clipboard_safe.py"
grep -q "run_cursor_window_preflight" "$ROOT/scripts/start_goal1_worker_turn_v1.py"
grep -q "run_cursor_window_preflight" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"

python3 "$ROOT/scripts/cursor_window_preflight_v1.py" --caller validate_test --sleep 0.5 | python3 -c "
import json,sys
row=json.load(sys.stdin)
assert row.get('ok'), row
print('preflight_test: ok')
"

echo "OK: validate-auto-run-window-preflight-v1"
