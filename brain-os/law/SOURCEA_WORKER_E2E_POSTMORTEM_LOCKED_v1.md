# Worker E2E Post-Mortem — Verdict, Permanent Fix, Agent Playbook (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
author: Worker+Brain+Maintainer-Consolidated
agent_tag: SOURCEA-WORKER-E2E-POSTMORTEM-20260609
doc_date: 2026-06-09
status: LOCKED
-->

| | |
|--|--|
| **Version** | `SOURCEA-WORKER-E2E-POSTMORTEM-1.0-LOCKED` |
| **sequence_id** | `SA-2026-06-09-WORKER-E2E-POSTMORTEM` |
| **Companion playbook** | `SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` (Rules 0–7) |
| **Result policy** | `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` |
| **Locked** | 2026-06-09 |

---

## Executive verdict on Worker’s report

Worker’s analysis is **correct and high quality**. It matches Brain’s post-mortem and what we proved in P0/P1 — with one more precise finding:

| Layer | Brain (earlier) | Worker (this session) |
|-------|-----------------|------------------------|
| **Symptom** | `hub_built_at` drift | Same |
| **Mis-location** | “phase-s0 / build retry” | **sa-0042 late check**, not sa-0017 |
| **Root cause** | Concurrent shell bump during long pack | **Inconsistent contract inside one 60–90s script** |
| **Fix** | 3× retry in build + sa-0017 | 3× retry in `validate-feedback-aggregate-hub-sync-v1.sh` → **consolidated shared module** |
| **Time waste** | Full E2E + tail + parallel runs | Re-proving green strict build while hunting 9s bug |

### One-line truth (Worker + Brain agree)

> The system wasn’t broken for 40 minutes — agents re-ran 5-minute green layers while a 9-second timing bug lived in the **wrong half** of the same validator pack.

---

## Exactly why E2E felt “stuck so long”

### Mental model — Full E2E (~5–7 min)

```text
Full E2E (~5–7 min)
├── Gates + pack        (~30s)   ← often PASS
├── Strict build        (~4–5m)  ← often PASS  ← agent kept re-proving this
├── Backend E2E         (~1–2m)  ← often PASS
└── find_critical_bugs  (~2–4m)
         └── phase-s0    (~60–90s) ← FAIL here (sa-0042 only)
```

**First full E2E (~336s):** strict build PASS, then `find_critical_bugs` FAIL → looked like “whole E2E broken” when only the **post-build pack** failed.

### The actual bug (with timing)

| Time | Event |
|------|--------|
| 22:33:50 | FA `hub_built_at` synced at **sa-0017** (early in pack) |
| … | ~40+ checks, 60–90s, hub `/refresh`, UI align, backend E2E activity |
| 22:33:59 | shell `built_at` bumps (**+9s**) |
| 22:33:59 | **sa-0042** single-read compare → FAIL “drift” |

| Checkpoint | Position in pack | Sync strategy | Result |
|------------|------------------|-----------------|--------|
| **sa-0017** | Early (~line 76) | 3× retry sync | Always PASS |
| **sa-0042** | Late (~line 377) | Single read (pre-fix) | **FLAKED** |

Same error string, different checkpoint — that’s why earlier sessions blamed sa-0017/build retry.

---

## Six reasons wall-clock exploded

1. **Wrong layer** — “E2E failed” ≠ “strict build failed”; ~5 min per rerun was mostly reproving green work.
2. **Symptom collision** — identical `hub_built_at` drift message at sa-0017 vs sa-0042.
3. **Full E2E as debugger** — optimal path after step 3 was ~10 min; session used ~40 min.
4. **Output loss** — `| tail -25` + background → empty logs → “still running” → more full E2Es.
5. **Debug instrumentation** — correct for investigation; +5–10 min overhead (`SINA_E2E_DEBUG_LOG=1` now gated).
6. **Noise** — one `sourcea-1000` pack IndexError (transient queue state), unrelated to drift.

---

## Minimum path (what should have happened)

| Step | Time | Command |
|------|------|---------|
| Repro | 9s | `bash scripts/validate-phase-s0-ssot-alignment-v1.sh` → line sa-0042 |
| Fix | 2m | Fix `validate-feedback-aggregate-hub-sync-v1.sh` → shared module |
| Verify | 3m | phase-s0 + `python3 find_critical_bugs.py` → PASS |
| Sign-off | 6m | **ONE** `validate-sourcea-e2e-standard-v1.sh` |
| **Total** | **~10 min** | (not 40+) |

---

## Architectural conflict (permanent lesson)

```text
sync + align          → hub_built_at = T0
/refresh, UI align, shell heal
single read (stale T0) → FAIL drift T0 vs T0+9s
60-90s, 40+ checks     → built_at → T0+9s
phase-s0 pack:
  sa-0017 early ←→ Hub :13020 ←→ sa-0042 late ←→ FEEDBACK_AGGREGATE
```

**Design rule:** `built_at` is intentionally mutable on refresh/align. Any assert after hub-touching steps in a long script must **sync-before-compare with retries** — not assume immutability for the whole run.

---

## Permanent fix shipped (consolidated)

Worker’s fix was right but duplicated (sa-0017 inline + sa-0042 script). **Consolidated:**

| Change | Purpose |
|--------|---------|
| `feedback_hub_sync_assert_v1.py` | Single shared 3× retry sync+assert for all `hub_built_at` checks |
| `validate-feedback-aggregate-hub-sync-v1.sh` | Calls shared module (sa-0042) |
| `validate-phase-s0-ssot-alignment-v1.sh` | sa-0017 uses same module — no drift early/late |
| `validate-hub-built-at-sync-contract-v1.sh` | CI contract: no new single-shot hub asserts |
| `_debug_e2e_log_v1.py` | Debug logs off by default; `SINA_E2E_DEBUG_LOG=1` to enable |
| `validate-ecosystem-safety-v1.sh` | Includes hub sync contract check |
| `validate-gatekeeper-v1.sh` | ACTIVE_NOW sync before gatekeeper (QUEUE_POS_DRIFT class) |

**Contract validator:** PASS on disk.

---

## Stack of defenses (full picture)

| Layer | Guard |
|-------|-------|
| sa-0042 flake | Shared retry assert (Worker + consolidation) |
| Eval synthesis | `sync_synthesis_eval_line_from_disk()` (P0) |
| Parallel E2E | Factory mutex (P0) |
| Agent runbook | Fast ladder + standard recipe (P1) |
| Monitor truth | Hygiene + STALE prune + ecosystem safety |
| Lane mix-ups | `FOUNDER_LANE_SEPARATION` + Canada STRATEGIC header |
| Hub restart | `SINA_FORCE_RESTART=1` in `serve-sina-command.sh` |
| Playbook lock | `validate-sourcea-e2e-playbook-locked-v1.sh` |

---

## Worker vs Brain vs Monitor — same class, different surface

| Surface | What looked broken | Real issue |
|---------|-------------------|------------|
| **Worker E2E** | phase-s0 / `find_critical_bugs` FAIL | sa-0042 single-shot vs moving `built_at` |
| **Brain E2E** | Same + eval synthesis flip-flop | sa-0042 + synthesis ahead of disk |
| **Monitor UI** | HERE #35, Queue empty, STALE 67 | Stale pointer + orphan broker events |

**All three:** “disk moved while UI/agent assumed frozen state.”

**Fix pattern everywhere:** resync at check site — don’t rerun the whole factory.

---

## Agent playbook (Rules 0–7)

**Canonical copy:** `SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md`

| Rule | Summary |
|------|---------|
| 0 | Parse failure section — re-run only that layer |
| 1 | Standalone repro: phase-s0, sa-0042, contract |
| 2 | One fix · two verifies · one standard E2E |
| 3 | Never `tail` full E2E — use tee / full log |
| 4 | New checks → `feedback_hub_sync_assert_v1.py` only |
| 5 | 3–10s gap = concurrent shell write → resync |
| 6 | Transient pack error → re-run pack once |
| 7 | Preflight: ecosystem safety → fast ladder → standard once |

---

## Golden recommendation

| Lane | Success |
|------|---------|
| **FACTORY** | 144 → 1000 Valid YES (one sa/turn, receipts) |
| **PRODUCT** | 3 TrustField demos (parallel — not Worker queue) |
| **AGENT** | 9s repro → targeted fix → 3m verify → 6m full E2E **once** |
| **NEVER AGAIN** | 40 min re-proving strict build for 9s late-check flake |

---

## Insight (maintainer)

Worker did **good engineering**. The session was long because of **process** (layer mis-location + full E2E as debugger), not because the bug was deep. That process is now **scripted** (ladder, standard recipe, shared assert, contract validator, locked playbook).

---

## Founder actions (updated 2026-06-10)

| Priority | Action |
|----------|--------|
| 1 | Don’t re-run E2E unless you want proof — factory structurally fixed |
| 2 | Refresh :13020 → **▶ START AUTO RUN** on **sa-0079** (was sa-0046 at post-mortem write time) |
| 3 | Close old debug Canvas/tabs — separate Worker chat |
| 4 | E2E proof: `validate-ecosystem-safety-v1.sh` → fast ladder → standard recipe **once** |
| 5 | Say **RUN STANDARD E2E ONCE** for one proof line + log path only |

---

## SAVE / LOCK / IMPLEMENT

| Item | Recommendation |
|------|----------------|
| This post-mortem | **SAVE + LOCK** |
| Shared assert module | **LOCK** |
| E2E standard recipe | **IMPLEMENT** as only sign-off |
| Factory queue | **IMPLEMENT** — Worker motion |
| Full E2E as debugger | **NEVER** |

---

*End SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1*
