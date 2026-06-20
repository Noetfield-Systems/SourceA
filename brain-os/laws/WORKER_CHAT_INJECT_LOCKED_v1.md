# Worker chat inject (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF · **sa:** sa-0718

## P0 fix

`open -a Cursor` + clipboard paste targets **last active chat** (Brain). **Forbidden** for Goal 1 Worker delivery.

## Rule

**Before every inject:** `pop_worker_editor_window` — foreground Cursor + INBOX editor tab + `agent --resume <worker-chat-id>`. Never `-g` background open (that leaves Brain/Cowork focused).

All Worker injects use **`agent --resume <worker-chat-id>`** from `~/.sina/worker-chat-marker-v1.json`.

| Module | Behavior |
|--------|----------|
| `worker_chat_inject_v1.py` | `focus_worker_chat` · `inject_into_worker_chat` |
| `cursor_window_preflight_v1.py` | `run_worker_chat_preflight` for worker/goal1 callers |
| `goal1_worker_batch_loop_v1.py` | Worker chat preflight only — no clipboard |
| `auto_run_worker_batch_v1.py` | `SINA_WORKER_CHAT_RESUME_INJECT=1` |
| `start_goal1_worker_turn_v1.py` | `agent -p -f --resume <id>` executes turn in Worker chat |

*End WORKER_CHAT_INJECT_LOCKED_v1*
