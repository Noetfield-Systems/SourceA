#!/usr/bin/env bash
# Goal 1 / Worker prompts must use INBOX — never osascript Cmd+V into focused chat.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

grep -q "inject_worker_prompt" "$ROOT/scripts/worker_drain_lib.py"
grep -q "open_inbox_in_editor" "$ROOT/scripts/worker_inject_lib.py"
grep -q "GOAL1_HEALTHY_DRAIN" "$ROOT/scripts/clipboard_safe.py"
grep -q "inject_worker_prompt" "$ROOT/scripts/clipboard_safe.py"
grep -q "is_worker_prompt" "$ROOT/scripts/clipboard_safe.py"
! grep -q 'tell application "Cursor" to activate' "$ROOT/scripts/worker_inject_lib.py"

python3 <<PY
import sys
sys.path.insert(0, "$ROOT/scripts")
from worker_inject_lib import clear_inbox, inject_worker_prompt, inbox_status, open_inbox_in_editor

clear_inbox(reason="validate_worker_inbox_delivery")
body = "[GOAL1_HEALTHY_DRAIN 1/30] test inject"
out = inject_worker_prompt(body, source="validate", meta={"queue_pos": 1, "queue_total": 30, "queue_role": "check", "sa_id": "sa-TEST"})
assert out.get("delivered") == "inbox", out
assert out.get("clipboard_paste") is False, out
assert out.get("focus_steal") is False, out
st = inbox_status()
assert st.get("pending"), st
ed = open_inbox_in_editor(background=True)
assert ed.get("ok"), ed
clear_inbox(reason="validate_worker_inbox_delivery_done")
from duplicate_inject_guard_v1 import clear_inject_lock
from healthy_pack_bind_lib_v1 import clear_stale_turn_bind
clear_inject_lock()
clear_stale_turn_bind()
print("OK: validate-worker-inbox-delivery-v1")
PY
