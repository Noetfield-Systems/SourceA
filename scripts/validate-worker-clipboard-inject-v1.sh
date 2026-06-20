#!/usr/bin/env bash
# Worker batch clipboard inject — sa-0716
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/brain-os/laws/WORKER_CLIPBOARD_INJECT_LOCKED_v1.md"
grep -q "paste_into_focused_cursor" "$ROOT/scripts/worker_inject_lib.py"
# Batch AUTO-RUN: resume Worker chat (primary) — clipboard env cleared to avoid Brain paste
grep -qE "SINA_WORKER_CHAT_RESUME_INJECT|SINA_WORKER_CLIPBOARD_INJECT" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
grep -qE "healthy_drain_paste|worker_chat_inject" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
grep -q "ensure_worker_chat_id" "$ROOT/scripts/start_goal1_worker_turn_v1.py"
test -f "$ROOT/scripts/worker_chat_session_v1.py"
grep -q "clipboard_inject" "$ROOT/scripts/worker_drain_lib.py"
grep -qE "SINA_WORKER_CLIPBOARD_INJECT|SINA_WORKER_CHAT_RESUME_INJECT" "$ROOT/scripts/clipboard_safe.py"
grep -q "SourceA Worker" "$ROOT/AGENT_DESK_START_HERE.md"

python3 <<PY
import os
import sys
sys.path.insert(0, "$ROOT/scripts")
from worker_inject_lib import _clipboard_inject_enabled, inject_worker_prompt

os.environ["SINA_WORKER_CLIPBOARD_INJECT"] = "1"
assert _clipboard_inject_enabled(delivery_mode="auto")
body = "[GOAL1_HEALTHY_DRAIN 1/30] test sa=sa-TEST"
# Dry inbox path only in validator (no osascript in CI)
out = inject_worker_prompt(body, source="validate", meta={"sa_id": "sa-TEST", "queue_pos": 1, "queue_total": 30, "queue_role": "check"}, delivery_mode="inbox")
assert out.get("ok"), out
print("OK: validate-worker-clipboard-inject-v1")
PY
