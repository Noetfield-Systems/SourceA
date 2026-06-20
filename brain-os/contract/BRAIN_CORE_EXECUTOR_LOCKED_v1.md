# Brain = Core Executor (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Spawn phrases only:** `activate loop` · `execute turn` · `execute loop N`

**Run the loop default** — `brain_run_loop_trace_v1.py` (trace + spawn). **Watcher only** — `narrate only` → no spawn.

## Model (PEV)

| Role | Who | How |
|------|-----|-----|
| **Planner** | Disk | `healthy-queue-30-active.json`, REGISTRY, feasibility gate |
| **Executor (default)** | **Worker batch** | Hub `START WORKER BATCH (5)` → `goal1_worker_batch_loop_v1.py` |
| **Executor (debug)** | Brain | `brain_execute_turn_v1.py` — **one turn only**, not 30-pack default |
| **Verifier** | Machine | Per-turn validators + **checkpoint every 5/10** (`GOAL1_BATCH_CHECKPOINT_LOCKED_v1.md`) |
| **Brain** | Checkpoint advisory | Reviews batch summary — **not every prompt** |

Brain is the **orchestrator-worker lead** (Anthropic pattern): executes via tools/scripts, not by pretending chat alone runs code.

## Brain commands (ASF says in Brain chat)

| Say | Brain runs |
|-----|------------|
| `execute turn` | `python3 scripts/brain_execute_turn_v1.py --yaml` |
| `execute loop 3` | `python3 scripts/brain_execute_turn_v1.py --loop 3 --yaml` (max 5) |

Brain **must** run the script and return YAML. **Forbidden:** 9-minute shell wait on 25 turns in one command.

## Forbidden

| Forbidden | Why |
|-----------|-----|
| `goal1_fast_loop.py` | Fakes reports, drifts queue |
| Brain refuses when ASF says execute turn | Brain IS executor |
| Clipboard paste into focused chat | Wrong-window hijack |
| Worker chat required for every turn | Brain executor path exists |

## Hub parallel (founder zero Terminal)

Hub **▶ START Worker turn** = same backend as `brain_execute_turn_v1.py` for ASF who does not type in Brain.

## Broker

`goal1_lane_broker.py brain-poll` · `brain-ack` — Brain reads after each turn.

Pointer: `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` §Brain Core Executor
