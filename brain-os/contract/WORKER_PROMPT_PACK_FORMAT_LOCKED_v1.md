# Worker prompt pack format (LOCKED v1.1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_tag:** `AUTO-TRACE-WORKER-PACK-FORMAT-v1.1`  
**agent:** `Auto`  
**Locked:** 2026-06-07 · **Amended:** 2026-06-07 (ASF) · **Authority:** ASF order — no revert without explicit supersede  
**Tag law:** `brain-os/contract/DOC_TRACE_TAG_FORMAT_LOCKED_v1.md`  
**Supersedes:** any pack that splits CHECK / ACT / VERIFY into separate founder pastes per `sa-XXXX`

---

## Law (never violate)

### Founder-facing packs

| Rule | Required |
|------|----------|
| **One paste = one full turn** | Read + implement + **verify inside same prompt** + closeout |
| **One `sa-XXXX` = one prompt** | Never 2 or 3 pastes per sa |
| **Compressed fast-track** | Bundle related work; no ceremony, no role-play steps |
| **No STOP-wait games** | Founder may paste queue in order; never instruct “wait for STOP” between pack items |
| **Count discipline** | Default **10 per worker lane** unless ASF explicitly requests another count |
| **Every 3rd prompt** | Full E2E gate **inside that one paste** (see below) |
| **Every 5th prompt** | Full debug + E2E sweep **inside that one paste** (see below) |

### Rhythm gates (bundled — not extra pastes)

Gates are **suffix duties inside the same prompt** at positions 3, 6, 9, … and 5, 10, 15, …

| Position | Gate | Worker must (same turn) |
|----------|------|-------------------------|
| **Every 3** (`ow-03`, `ow-06`, `ow-09`, `nw-03`, …) | **E2E-3** | Check fully E2E · implement gaps · verify PASS · fix failures · search for anything missing from last 3 turns · `validate-execution-spine-v1.sh` + `find_critical_bugs` critical 0 |
| **Every 5** (`ow-05`, `ow-10`, `nw-05`, `nw-10`, …) | **DEBUG-5** | Full debug sweep · all validators E2E · hub health `http://127.0.0.1:13020` refresh/sync · inbox vs queue drift · runtime/terminal hygiene (hub up, orchestrator deliver, inject clear) · fix before closeout |

When position hits **both** (15, 30, …): run **E2E-3 + DEBUG-5** in the **same single prompt**.

**Forbidden:** emitting E2E-3 or DEBUG-5 as separate founder pastes — they are clauses inside prompt #3, #5, #6, etc.

### Forbidden forever (agent generators + advisors)

- Splitting `sa-0131` into `CHECK` / `ACT` / `VERIFY` **as three copy-paste prompts**
- “Playing games” with micro-step queues (4+ pastes to finish one sa)
- Regenerating tier mirrors (T0/T1 duplicate packs) for worker paste queues
- Padding pack size to look busy (20 when 10 suffices)
- Telling founder to open Terminal or wait on ceremony between pack lines
- Skipping every-3 / every-5 gates on generated packs

### Allowed (internal only — not separate pastes)

Worker **one turn** may still run check → act → verify **inside the same session** per `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`. That is **not** permission to emit three founder prompts.

---

## Canonical template (OLD worker — one sa)

```
PLAN WITH NO ASF — OLD WORKER sa-XXXX ONE TURN. Task: <title>.
Read <prompt_path> + session-start + spine + find_critical_bugs.
Implement gaps minimal diff.
Verify inside same turn: validate-eval-packet-v1b-live.sh + find_critical_bugs critical 0 + mark_done + PRIORITY row.
[<E2E-3 clause if position % 3 == 0>]
[<DEBUG-5 clause if position % 5 == 0>]
WORKER_ROUND_REPORT → broker submit.
One sa end-to-end — no separate CHECK/ACT/VERIFY pastes.
```

### E2E-3 clause (embed at every 3rd)

```
PLUS E2E-3 GATE: full E2E on last 3 turns — validate-execution-spine-v1.sh PASS, implement+verify+fix any gap, search missing wiring/docs/receipts, find_critical_bugs critical 0 before closeout.
```

### DEBUG-5 clause (embed at every 5th)

```
PLUS DEBUG-5 GATE: full debug sweep — brain_validate_goal1_v1.py --json, validate-goal1-loop-activation-chain-v1.sh, validate-eval-packet-v1b-live.sh, hub Refresh/sync state (13020), worker-prompt-inbox vs healthy-queue drift fix, orchestrator deliver + runtime hygiene; fix all before closeout.
```

## Canonical template (NEW worker — autoloop)

```
PLAN WITH NO ASF — NEW WORKER nw-XX ONE TURN: <bundled autoloop task>.
Autoloop engine only — no REGISTRY implement unless broker fix.
[<E2E-3 or DEBUG-5 clause when position matches>]
WORKER_ROUND_REPORT → broker submit.
```

---

## Authority unify map (what is in charge — 2026-06-07)

| Lane | In charge | Not in charge |
|------|-----------|---------------|
| **Manual founder paste** (Worker chat copy-paste) | **This doc v1.1** · `.sina-loop/*-PASTE-QUEUE.md` · `worker-dual-40/REGISTRY.json` | `HEALTHY_PROMPT_SEQUENCE` 3-paste rhythm · split CHECK/ACT/VERIFY founder pastes |
| **Headless AUTO-RUN** (Hub ▶ Goal 1) | `TODAY_AUTORUN_50_PLAN_LOCKED_v1.md` · `GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md` | Manual 40-paste play · `ft-*` manual curriculum |
| **Healthy drain inject** (orchestrator INBOX one turn) | `HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md` · `generate-healthy-prompt-pack-v1.py` · `INBOX.md` | Manual paste pack format (this doc) |
| **Broker / Brain curriculum** | `BROKER-PACK-1000-LOCK.md` | Worker paste queues |
| **Automation debug tags** | `AUTOMATION-FAST-TRACK-100-LOCK.md` (`ft-*`) | Manual paste default |
| **Retired** | — | `automation-converge-1000` (`ac-*`) · tier-mirror packs · CHECK/ACT/VERIFY **founder** triple-paste |

**Internal only (same session, not extra founder pastes):** `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` validators; `GOAL1_LOOP_ACTIVATION_CHAIN` `round_type` check/act/verify mapping for **one inject turn**.

## Active pack (this lock)

| Pack | Path | Shape (disk 2026-06-07) |
|------|------|-------------------------|
| Worker 1 REGISTRY | `brain-os/plan-registry/worker-dual-40/REGISTRY.json` | `AUTO-TRACE-WORKER-W1-REGISTRY-v1.2` · agent Auto |
| Paste queue | `.sina-loop/WORKER-1-PASTE-QUEUE.md` | `AUTO-TRACE-WORKER-W1-QUEUE-v1.2` |
| Runtime pointer | `~/.sina/worker-prompt-pack-active-v1.json` | `AUTO-TRACE-RUNTIME-WORKER-PACK-v1.2` |
| Exec rail | `~/.sina/active-execution-rail-v1.json` | `AUTO-TRACE-RUNTIME-EXEC-RAIL-A-v1.2` |
| Generator | `scripts/generate-worker-dual-40.py` | Emits `AUTO-TRACE-*` + `agent: Auto` |
| Tag law | `brain-os/contract/DOC_TRACE_TAG_FORMAT_LOCKED_v1.md` | `AUTO-TRACE-DOC-FORMAT-v1.1` |

**Default count law:** 10 per lane unless ASF orders expand (current disk = 20 per lane from broker regen).

## Line test (before shipping any new pack)

1. Would ASF paste **one prompt** per slot and move on? If no → reject.
2. Does every 3rd and 5th slot embed E2E-3 / DEBUG-5 **inside** that paste? If no → reject.

---

## Incident class

Violating this lock = **governance waste incident** — revert pack, regenerate compressed, do not debate in advisor compare loops.
