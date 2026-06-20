# NO_DUPLICATE_INJECT_LOCKED_v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** LOCKED · **Assign:** sa-0720 · **Authority:** ASF P0 directive 2026-06-08

## Law

Same `sa_id` may not be injected more than once per **90 seconds** for the **same queue turn** (`queue_pos` + `queue_role`).

Autorun **must** check `~/.sina/goal1-worker-turn-bind-v1.json` and `~/.sina/worker-prompt-inbox-v1.json` before every inject.

**Violation = governance breach.**

## Required behavior

1. **Before ANY inject** — `duplicate_inject_guard_v1.preflight_inject()`:
   - If inbox `pending` matches same turn → `SKIP_INJECT`
   - If turn-bind `sa_id` matches pointer and inbox still pending → `SKIP_INJECT`
   - If inject-lock same turn within 90s → `SKIP_INJECT`

2. **Lock before paste** — write `~/.sina/goal1-inject-lock-v1.json` and turn-bind **immediately** on proceed, **before** INBOX write or `agent --resume`.

3. **Autorun gate** — `auto_run_worker_batch_v1.should_start_batch()` must skip when:
   - `INBOX_PENDING`
   - `AWAITING_WORKER` (orchestrator)
   - `WORKER_BATCH_BUSY`
   - duplicate inject guard would block

4. **Stuck watchdog** — `goal1_stuck_watchdog_v1.run_watchdog(max_age_sec=300)` wired into autorun daemon poll:
   - Kill `goal1_worker_batch_loop`, `start_goal1_worker_turn`, `goal1_run_loop`, `brain_run_loop` processes older than 5 minutes
   - Log `STUCK_PROCESS_KILLED` to `~/.sina/goal1-stuck-watchdog-v1.jsonl`
   - Clear stale batch lock; autorun retries on next poll

## Modules

| Module | Role |
|--------|------|
| `scripts/duplicate_inject_guard_v1.py` | Skip + lock |
| `scripts/goal1_stuck_watchdog_v1.py` | 5min pkill watchdog |
| `scripts/worker_inject_lib.py` | Calls guard at `deliver_to_worker_inbox` entry |
| `scripts/auto_run_worker_batch_v1.py` | Gate + watchdog on poll |

## Validator

`bash scripts/validate-no-duplicate-inject-v1.sh`
