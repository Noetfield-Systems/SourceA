# Execution kernel convergence — GPT critique + worker-dual-40 status

**Saved:** 2026-06-07T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `AUTO-TRACE-EXECUTION-KERNEL-CONVERGENCE-2026-06-07`  
**worker_id:** `worker`  
**subject:** `sina_os`  
**date:** 2026-06-07  
**execution_authority:** false  
**parent_blueprint:** `AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md` · `TODAY_AUTORUN_50_PLAN_LOCKED_v1.md`

---

## ACK

```yaml
research_save_lock: ACK_RESEARCH_INTAKE_AND_SAVE_LOCK_v1
```

---

## Research question

Does the SourceA worker stack (v1.1 packs, ow/nw lanes, ft-*, AUTO-RUN) constitute real automation or parallel schema explosion?

---

## Findings (disk-backed)

### Count truth

| Claim | Verdict |
|-------|---------|
| worker-dual-40 = **40 total** | **TRUE** — 20 OLD (`ow-01`…`ow-20`, `sa-0131`→`sa-0150`) + 20 NEW (`nw-01`…`nw-20`) |
| 40 per lane | **FALSE** |
| v1.1 = one paste = one full turn | **TRUE** — gates E2E-3/DEBUG-5 embedded inside paste |

### GPT critique assessment

| GPT claim | Verdict | Evidence |
|-----------|---------|----------|
| Multi-lane confusion (ow/nw/ft/sa/AUTO-RUN) | **ACCEPT** | Multiple pick scripts + paste queues coexist on disk |
| v1.1 is format not autonomy | **ACCEPT** | `WORKER_PROMPT_PACK_FORMAT_LOCKED_v1.md` defines turn shape only |
| Real blockers are broker/state not prompts | **ACCEPT** | `activate=FAIL`, `broker=no`, `sa_mismatch`, stale `worker_turn_state` |
| Deprecate ft-* as daily queue | **ACCEPT** | `TODAY_AUTORUN_50` lists ft-* as break-glass only |
| Deprecate ow/nw for normal ops | **ACCEPT** | Converge program forbids dual rails + manual paste per turn |
| Kill AUTO-RUN entirely | **REJECT** | Locked north star is Hub ▶ AUTO-RUN 50 tonight |

### Law already on disk (under-followed)

```text
INPUT (plan-no-asf-run.sh pick 1) → INBOX + broker → headless turn → validate/sync → repeat
```

Canonical pointer at save time: `bash scripts/plan-no-asf-run.sh pick 1` → **sa-0136**.

### Runtime snapshot (2026-06-07 session)

| Signal | Value |
|--------|-------|
| Hub | `http://127.0.0.1:13020` → 200 |
| Pack validator | `validate-worker-dual-40-pack-v1.sh` PASS |
| Autoloop validator | `validate-goal1-auto-loop-v1.sh` PASS |
| One-sa / inbox mechanical | PASS |
| activate chain | FAIL (last batch `broker=no` / `sa_mismatch`) |
| Healthy drain vs pick 1 | Competing (`sa-0360` queue vs `sa-0136` live pick) |

---

## Decisions (research-backed)

1. **Single execution kernel (operational)** — only `sourcea-1000` REGISTRY + `plan-no-asf-run.sh pick 1` + `goal1_auto_loop_v1.py` / Hub AUTO-RUN.
2. **v1.1 turn format** — mandatory shape inside every turn; not a routing system.
3. **worker-dual-40** — paste-helper / debug templates only; not founder daily queue.
4. **ft-*** — break-glass curriculum when autoloop breaks (ft-0005 = sa_mismatch).
5. **broker-pack-1000 / ac-1000** — not factory drain; retired or parallel curriculum only.
6. **Next build unlock** — `SINGLE_EXECUTION_KERNEL_LOCKED_v1.md` + validator “no parallel queue active” (proposed; not yet locked).

---

## Lane map (active vs archive)

| Surface | Role tonight |
|---------|----------------|
| `pick 1` + `goal1_auto_loop` | **ACTIVE** |
| v1.1 one-paste turn | **ACTIVE** (inside turn) |
| ow/nw paste queues | **DEBUG ONLY** |
| ft-* daily pick | **FORBIDDEN** unless break-glass |
| healthy-pack parallel rail | **FORBIDDEN** |
| broker-pack drain | **FORBIDDEN** |

---

## Minimal 3-layer architecture (target)

```text
LAYER 1 STATE     → sourcea-1000 REGISTRY + pick 1
LAYER 2 EXECUTOR  → goal1_auto_loop / goal1_run_loop
LAYER 3 RULES     → broker=yes · fail-stop 3× broker=no · v1.1 turn
```

---

## Sources cited

- `brain-os/contract/WORKER_PROMPT_PACK_FORMAT_LOCKED_v1.md` (v1.1)
- `brain-os/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md`
- `brain-os/contract/TODAY_AUTORUN_50_PLAN_LOCKED_v1.md`
- `brain-os/plan-registry/worker-dual-40/REGISTRY.json` (schema `worker-dual-40.v1.1`, count 40)
- `scripts/brain_validate_goal1_v1.py --json` (session capture)
- External advisor synthesis (GPT fragmentation critique, 2026-06-07)

---

## Closeout tail

```yaml
research_save:
  trace_id: AUTO-TRACE-EXECUTION-KERNEL-CONVERGENCE-2026-06-07
  worker_id: worker
  subject: sina_os
  vault_path: /Users/sinakazemnezhad/Desktop/SourceA/RESEARCH/vault/worker/AUTO-TRACE-EXECUTION-KERNEL-CONVERGENCE-2026-06-07_execution_kernel_convergence.md
  research_mirror_path: RESEARCH/by_date/2026-06-07/worker/sina_os/AUTO-TRACE-EXECUTION-KERNEL-CONVERGENCE-2026-06-07/
  enforcer_verify: PASS
  execution_authority: false
```
