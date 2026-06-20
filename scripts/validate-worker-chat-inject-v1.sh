#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/brain-os/laws/WORKER_CHAT_INJECT_LOCKED_v1.md"
test -f "$ROOT/scripts/worker_chat_inject_v1.py"
grep -q "run_worker_chat_preflight" "$ROOT/scripts/cursor_window_preflight_v1.py"
grep -q "DEFAULT_WORKER_CHAT_ID" "$ROOT/scripts/cursor_window_preflight_v1.py"
grep -q "agent --resume" "$ROOT/scripts/cursor_window_preflight_v1.py" || grep -q '"--resume"' "$ROOT/scripts/cursor_window_preflight_v1.py"
grep -q "worker_chat_inject" "$ROOT/scripts/worker_drain_lib.py"
grep -q "SINA_WORKER_CHAT_RESUME_INJECT" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
grep -q "run_worker_chat_preflight" "$ROOT/scripts/auto_run_worker_batch_v1.py"
grep -q "pop_worker_editor_window" "$ROOT/scripts/worker_chat_inject_v1.py"
if grep -q "paste_into_focused_cursor" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"; then
  echo "FAIL: batch loop still uses clipboard paste" >&2
  exit 1
fi

python3 -c "
import json
from pathlib import Path
m = json.loads(Path.home().joinpath('.sina/worker-chat-marker-v1.json').read_text())
assert m.get('conversation_id'), m
print('marker_ok', m['conversation_id'])
"

echo "OK: validate-worker-chat-inject-v1"
