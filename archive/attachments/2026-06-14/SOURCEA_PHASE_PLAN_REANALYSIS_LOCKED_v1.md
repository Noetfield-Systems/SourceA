# SourceA phase plan — reanalysis (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Trigger:** ASF order — activate OpenRouter + dispatch; finish s2 if remaining; re-check skipped vs runnable  
**Authority:** REGISTRY.json · `~/.sina/phase-strict-drain-v1.json` · DISPATCH_POLICY_LOCKED_v1.md

---

## Activation status (executed)

| Layer | Before | Now | Proof |
|-------|--------|-----|-------|
| Eval-1b | live pass | **live pass** (100% pilots) | `~/.sina/eval_packet_v1b_report.json` |
| OpenRouter gate | shadow | **enforce** | `~/.sina/gate_mode_v1.txt` |
| dispatch_policy | eval gate ok | **activated** | `eval_1b_gate_ok: true` · `auto_low_risk: eligible` |
| Spine bridge | ready | **ready** | `graph_executor_v1.json` · `spine_bridge_ready: true` |
| Orchestrator `dispatch_ready` | false | **false** (law) | Founder confirm + graph_executor bridge — not silent auto |

**Validators PASS:** `validate-dispatch-policy-v1.sh` · `validate-spine-bridge-proof-matrix-v1.sh`

---

## s2 — no remaining work

| Check | Result |
|-------|--------|
| REGISTRY backlog | **0** (100/100 done) |
| Receipts for done rows | **0 missing** in `receipts/` |
| Phase-strict skip reason | Valid — s2 complete, re-drain not needed |

**Verdict:** s2 is **finished**. Do not re-queue s2 in factory drain.

---

## Phase-by-phase — still good vs do now

| Phase | Done | Backlog | Skipped in drain? | Verdict |
|-------|------|---------|-------------------|---------|
| **s0** SSOT | 100 | 0 | — | **Done** · P0 validator may need refresh post-enforce |
| **s1** eval/dispatch | 100 | 0 | cycle 1 OR pack | **Done** · OpenRouter proof shipped |
| **s2** hub-build-ci | 100 | 0 | yes (complete) | **Done** — no action |
| **s3** scoreboard | 100 | 0 | yes (complete) | **Done** — no action |
| **s4** spine-loop | 100 | 0 | founder lanes | **Done** — only if ASF picks lane work |
| **s5** commercial | 4 | **96** | **ACTIVE cycle 2** | **DO NOW** — head sa-0502 |
| **s6** WTM pre-LLM | 100 | 0 | yes | **Done** |
| **s7** council | 100 | 0 | cycle 1 tail | **Done** |
| **s8** hub-ui-ux | 24 | **76** | yes (hub archived) | **Defer** — ASF no-hub latch |
| **s9** research | 100 | 0 | cycle 1 packs | **Done** |

**Honest remaining:** **172 SAs** = 96 (s5) + 76 (s8 deferred)

---

## Skipped phases — can we do them now?

| Skip | Why skipped | Run now? |
|------|-------------|----------|
| s2 | 100% done | **No** |
| s3 | 100% done | **No** |
| s8 | Super Fast Hub archived · INCIDENT-031 no-hub | **No** until explicit hub reopen |
| s4/s5/s6 in cycle 1 | phase-strict law prioritized s1→s7→s9 | s5 **yes now** (cycle 2) |
| s9 blocked 4 IDs | sa-0954/964/979/989 infeasible | **No** until prompts fixed |

---

## Recommended execution order (updated)

```
1. Clear P0 validators (broker PEND · s0 alignment stale asserts) — executor
2. Founder: clear FREEZE → RUN INBOX
3. Drain s5-P1 (sa-0502..0511) — disk-only commercial, 30 turns
4. Expand s5-P2..P10 until s5 = 100%
5. Reassess s8 only if ASF reopens hub
6. Founder Hub: spine bridge Action (eval proof) — optional after unfreeze
```

**OpenRouter on factory turns:** enforce gate is **live for planner/agent_loop** paths. Phase-strict s5 pack stays **disk-only** (`allow_openrouter: false`) — commercial lane law unchanged.

---

## Cycle history

| Cycle | Law | Status |
|-------|-----|--------|
| 1 | s1 OR → s7 tail → s9 | **COMPLETE** (156 turns) |
| 2 | s5 commercial P1 (10) | **STAGED** · sa-0502 CHECK |

---

## Disk pointers

- Plan: `archive/attachments/2026-06-14/NEXT_FACTORY_CYCLE_ORGANIZED_LOCKED_v1.md`
- Queue: `~/.sina/healthy-queue-30-active.json` (30 turns)
- Gate: `~/.sina/gate_mode_v1.txt` = **enforce**
- Dispatch: `~/.sina/dispatch_policy_v1.json`

---

*End SOURCEA_PHASE_PLAN_REANALYSIS_LOCKED_v1*
