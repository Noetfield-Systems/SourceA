# Goal 1 batch checkpoint (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Problem

Brain-per-prompt loop is **slow and fragile** — Brain chat hangs, broker waits on `awaiting_brain_ack`, 30-pack drain stalls.

## Rhythm (fast + reliable)

| Layer | Who | When |
|-------|-----|------|
| **Planner** | Disk | `healthy-queue-30-active.json`, feasibility gate |
| **Executor** | **Worker** (clipboard inject + agent CLI) | Turns 1–4 in batch — paste into focused Worker chat; INBOX backup logged |
| **Checkpoint** | Machine + optional Brain | Every **5** or **10** prompts — not every prompt |
| **Verifier** | Validators in Worker turn | `WORKER_ROUND_REPORT` each turn |
| **Brain** | Advisory | Reads `goal1-batch-checkpoint-v1.json` — **does not block** if machine PASS |

## Hub (founder)

| Tap | Script |
|-----|--------|
| **▶ START WORKER BATCH (5)** | `goal1_worker_batch_loop_v1.py --batch-size 5 --max-batches 6` |
| **▶ START WORKER BATCH (10)** | `--batch-size 10 --max-batches 3` |
| **Brain checkpoint ack** | Only when `checkpoint_pending` (machine FAIL) |

## Worker batch flow

```
FOR each batch (max 6):
  turns 1–4: agent → worker_submit(auto_advance=True) → next INBOX (no Brain)
  turn 5:    agent → worker_submit(checkpoint=True)
             → machine_pass? auto-deliver + continue
             → fail? checkpoint_pending → Brain ack → Hub START BATCH again
```

## Brain role (not lazy gatekeeper)

- **Not required** every prompt.
- **Checkpoint advisory**: poll `goal1_lane_broker.py brain-poll` or read `~/.sina/goal1-batch-checkpoint-v1.json`.
- **Single-turn path** (`brain_execute_turn_v1.py`) remains for manual/debug — not default drain.

## When batch pauses (Brain alignment)

- **Orchestrator `feasibility_blocked`** on stale stop → deliver auto-recovers if **current queue item** is injectable (live pick sa-0129 may WARN only).
- **Impossible ACT** (OpenRouter) → CHECK completes → `skip_sa_slice` advances; do not run batch through blocked ACT.
- **Nested YAML** `WORKER_ROUND_REPORT:` — broker normalizes; agent prompt forbids parent key.

## Forbidden

| Forbidden | Why |
|-----------|-----|
| Brain ack after every Worker turn in batch mode | Defeats batch speed |
| `goal1_fast_loop.py` | Fake reports |
| `goal1_run_loop` multi-turn shell | Timeout / feasibility drift |
| Orchestrator `watch` as default rail | Stalls on FEASIBILITY_BLOCKED |
| 25-turn shell in Brain chat | Hang |

Pointer: Hub tab **Goal 1 loop** · `BRAIN_CORE_EXECUTOR_LOCKED_v1.md` (Brain = checkpoint + governance, Worker = default executor)
