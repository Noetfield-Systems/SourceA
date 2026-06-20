# sa-0716 receipt — Worker clipboard inject

**Root cause:** Disk INBOX + `099-worker-inbox-active.mdc` requires SourceA Worker chat open.

**Fix:** Batch loop enables `SINA_WORKER_CLIPBOARD_INJECT=1` → `paste_into_focused_cursor` (pbcopy + osascript Cmd+V).

**Wired:** `worker_inject_lib.py` · `goal1_worker_batch_loop_v1.py` · `worker_drain_lib.py` · `clipboard_safe.py`

**Doc:** `AGENT_DESK_START_HERE.md` § Goal 1 AUTO-RUN setup

**Validator:** `bash scripts/validate-worker-clipboard-inject-v1.sh` PASS
