# Worker clipboard inject (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF · **sa:** sa-0716

## Root cause

Disk-only delivery (`.cursor/rules/099-worker-inbox-active.mdc` + `INBOX.md`) **does not run** unless **SourceA Worker** Cursor chat is open — rules do not fire in background.

## Permanent fix (batch AUTO-RUN)

`goal1_worker_batch_loop_v1.py` sets:

- `SINA_WORKER_CLIPBOARD_INJECT=1`
- `SINA_ALLOW_CURSOR_PASTE=1`

Then `inject_worker_prompt(..., delivery_mode=clipboard)`:

1. Writes INBOX backup on disk (audit + agent CLI path)
2. Pastes full prompt into **focused** Cursor chat via `pbcopy` + `osascript` Cmd+V (same as Brain inject)

## Founder one-time setup

See `AGENT_DESK_START_HERE.md` § Goal 1 AUTO-RUN — keep **SourceA Worker** chat focused before ▶ START WORKER BATCH.

## Modules

| Module | Role |
|--------|------|
| `worker_inject_lib.paste_into_focused_cursor` | osascript inject |
| `goal1_worker_batch_loop_v1.py` | Enables clipboard mode per batch |
| `worker_drain_lib.healthy_drain_paste(clipboard_inject=True)` | Hub/batch deliver |
| `clipboard_safe.py` | Respects `SINA_WORKER_CLIPBOARD_INJECT` |

*End WORKER_CLIPBOARD_INJECT_LOCKED_v1*
