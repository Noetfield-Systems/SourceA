# Commercial Specialist — Plan · Report · Suggestions · Brainstorm (DRAFT v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Role:** Commercial Specialist (L1 rank 3) · **Chat:** `6245d9dd`  
**Authority:** `SOURCEA_EXECUTOR_IN_CHARGE_NO_HANDOFF_LOCKED_v1.md` · `SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1.md`  
**Status:** DRAFT — promote to LOCKED after ASF review

---

## 0. One-line mission

Ship founder commercial + factory health fixes logged with validator proof — never hand off to Maintainer, never report-only.

---

## 1. Report summary

### 1.1 Shipped and verified (this arc)

| Bundle | Status | Proof |
|--------|--------|-------|
| Commercial T3 pack **sa-0588→sa-0600** | **Closed 13/13** | All `validate-*-t3-crossref-v1` PASS · PRIORITY pack row · `worker_verify_fast` PASS |
| L1 `validate-daily-spine-v1` | PASS | G3 projection + hub-sync warm-up |
| L2 `audit_backend_e2e_light_v1` | PASS | Hub-sync budget 1200ms |
| L2 `validate-goal1-e2e-v1` | PASS | Resume token · bind heal · active_now sync · inbox cleanup trap |
| sa-0807 ACT path | Shipped | `validate-next-phase-founder-open-v1.sh` |

### 1.2 Open / not closed

| Item | Status | Notes |
|------|--------|-------|
| L3 `validate-e2e-fast-ladder-v1` | Not PASS | Strict build ~6 min; patches shipped (fleet 7-agent, G3 authorize, snapshot refresh) — one clean run pending |
| sa-0807 Hub 2 drain | Mid-cycle | CHECK+ACT done · VERIFY pending |
| Factory idle for L3 | Fragile | Goal1 e2e leaves INBOX pending unless cleanup trap runs |

### 1.3 Disk truth snapshot

- Goal 1: **924/1000** honest (92.4%) · receipts aligned
- Queue head: **sa-0807** · phase-s8 Hub 2 machine drain
- ASF latch: Hub 2 drain **ALLOWED** · Sina Command `/legacy/` **quarantine** · no panel rebuild homework
- Fleet roster: **7 agents** (sinaai_maintainer removed — pick 6.10)

### 1.4 Session lessons (anti-repeat)

1. “Factory lock” UI often meant **busy queue**, not validation lock file.
2. Do **not** loop full L3 (~6 min) after every small fix — fix once, run targeted validator, one ladder max.
3. E2E tests must **clear INBOX** or idle gate blocks L3.
4. Roster trim 8→7 requires validator alignment, not adding maintainer back.

---

## 2. Plan — next 7 days

### Phase A — Close current slice (priority 0)

| # | Action | Done when |
|---|--------|-----------|
| A1 | sa-0807 **VERIFY** closeout | Broker VERIFY PASS · receipt logged |
| A2 | Clear INBOX after any e2e | `factory_idle_gate_v1.py` → idle true |
| A3 | **One** L3 fast ladder run | `E2E-FAST-LADDER PASS` |
| A4 | PRIORITY + INBOX header sync | Gatekeeper SAFE TO EXECUTE |

### Phase B — Hub 2 machine drain (phase-s8)

```text
sa-0807 verify → sa-0808 deferred bucket → sa-0809 thread_room → sa-0810 judge alarm
→ sa-0811 hub_dual_heal → sa-0812 staleness → sa-0813 h2 reconcile → sa-0814 cadence → sa-0815 hub_surface
```

**Law:** CHECK = gap only · ACT = minimal disk · VERIFY = ultra + broker · **no Sina Command app edits**

### Phase C — Commercial lane hygiene (parallel, low heat)

| Track | Validator |
|-------|-----------|
| Founder attests | `validate-commercial-attests-priority-v1` |
| G3 vault evidence | `validate-commercial-lane-g3-vault-*` |
| Critique vs PROGRAM_PROGRESS | `validate-commercial-critique-program-progress-locks-v1` |

### Phase D — Goal 1 (76 remaining)

- Phase-first pick unchanged — no critic reorder
- Commercial loop: `SINA_COMMERCIAL_LOOP=1` · ultra verify · fast broker
- Soft target: 950/1000 before next commercial tranche (ASF decision)

---

## 3. Suggestions

### 3.1 Founder (clicks only — no Terminal)

1. Hub → **Safety** once if dual_proof or idle gate warn
2. Confirm **7-agent roster** is law (pick 6.10)
3. Keep Hub 2 drain on; defer `/legacy/` archive until latch lifts
4. Max **one L3 per session** — executor retries on FAIL, not founder

### 3.2 Executor

1. Pre-ladder checklist (~30s): idle gate · lock clear · INBOX pending=0 · resume if FREEZE
2. Post-ship: PRIORITY row + attachment + validator stdout
3. Respect ASF latch: no `build-sina-command-panel` unless ASF orders hub rebuild
4. Report Command bugs via `/api/agent-review` — do not patch panel

### 3.3 Process hardening (candidate sub-steps)

| Gap | Fix |
|-----|-----|
| Misleading “factory lock” | Label **factory busy** when mid-slice |
| E2E hot INBOX | Cleanup trap in `validate-goal1-e2e-v1.sh` (shipped) |
| Fleet snapshot drift | Re-log snapshot before scoreboard cross-check (shipped) |
| Strict build G3 block | Authorize hub projection at build entry (shipped) |
| L3 cost | Document T0/T1/T2 validator tiers (below) |

---

## 4. Validator tiers (brainstorm → candidate law)

| Tier | When | ~Time | Scripts |
|------|------|-------|---------|
| **T0** | Every sa VERIFY | 10s | ultra verify · broker |
| **T1** | Daily / post-pack | 60s | daily-spine · e2e-light |
| **T2** | Weekly / pre-ship | 6m | e2e-fast-ladder (strict build) |

Hub Safety could run T1; founder never waits on T2 unless shipping.

---

## 5. Brainstorm — forward tracks

### 5.1 Commercial pack tranche 2 (after Hub 2 slice)

- W3 outbound approve card execution proof
- TrustField B-001 law collision track
- MergePack Evidence Factory lane (not an agent)
- FR-003 founder request wired proof

Pattern: one cross-ref validator + attachment + PRIORITY row (same as 13/13).

### 5.2 Two-speed factory UX

- Tag factory-now: `hub2` vs `goal1` cursor
- Stop showing “BLOCKED factory lock” when queue is legitimately mid ACT/VERIFY

### 5.3 PICK drafts (advise only — ASF confirms)

- 9.07 A ship order — execution spine north star
- W3 NF outreach — approve when Safety green
- ENFORCEMENT W1 film — parallel, non-blocking for drain

### 5.4 Anti-patterns

| Kill | Replace |
|------|---------|
| L3 loop after every fix | Targeted validator + one ladder |
| Maintainer handoff | Same-turn disk + proof |
| Hot INBOX after test | Auto-cleanup |
| Expect 8 agents | 7 roster SSOT |

---

## 6. Done checklist (this thread)

```text
[x] Commercial pack 13/13 closed
[x] L2 goal1 e2e PASS
[ ] L3 fast ladder PASS (one clean run)
[ ] sa-0807 VERIFY closed
[ ] INBOX cleared · gatekeeper SAFE TO EXECUTE
```

---

*End DRAFT — Commercial Specialist · execution_authority true on scripts/attachments · promote via ASF order*
