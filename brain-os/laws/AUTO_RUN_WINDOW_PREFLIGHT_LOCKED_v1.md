# AUTO-RUN window preflight (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF  
**Location:** `brain-os/laws/AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1.md`  
**Validator:** `scripts/validate-auto-run-window-preflight-v1.sh`  
**Wired:** `cursor_window_preflight_v1.py` · `worker_inject_lib` · `clipboard_safe` · `start_goal1_worker_turn_v1.py` · `goal1_worker_batch_loop_v1.py`

---

## Problem

Cursor windows backgrounded → prompt injection fails. Two agent tabs fail. **All AUTO-RUN must target the single main Cursor window only.**

---

## Mandatory preflight (before every prompt delivery)

1. `open -a "Cursor"`
2. Sleep **1.0** seconds
3. Then execute prompt inject (INBOX write · agent CLI · or clipboard paste when explicitly allowed)

Applies to **all** prompt types: Brain turns · Worker turns · Broker checks · healthy-drain · batch loop.

---

## Implementation SSOT

| Module | When |
|--------|------|
| `scripts/cursor_window_preflight_v1.py` | Canonical `run_cursor_window_preflight()` |
| `scripts/worker_inject_lib.py` | Before `deliver_to_worker_inbox` write |
| `scripts/clipboard_safe.py` | Before osascript Cmd+V path |
| `scripts/start_goal1_worker_turn_v1.py` | Before `agent -p -f` |
| `scripts/goal1_worker_batch_loop_v1.py` | Before inbox ensure / deliver |

**Hub note:** `sina-command-server.py` / `sina_command_lib.py` routes through the modules above for Goal 1 AUTO-RUN — do not duplicate preflight in hub without importing `run_cursor_window_preflight`.

---

## Rules

1. **Single window** — never open a second agent tab for inject.
2. **Foreground first** — preflight runs even when delivery is INBOX-only (agent CLI still needs focused Cursor).
3. **No skip on Rail A** — AUTO-RUN batch loop must call preflight every turn.

---

*End AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1*
