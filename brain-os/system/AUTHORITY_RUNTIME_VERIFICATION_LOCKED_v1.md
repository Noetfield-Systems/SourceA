# Authority runtime verification (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF  
**trace_tag:** `AUTO-TRACE-AUTHORITY-CONVERGENCE-LOCK-v1`  
**Supersedes:** partial Q2 read in `governance_goal_specialist-20260608-016` — hybrid reconciled chain is canonical  
**Parents:** `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` · `GOVERNANCE_P1_LOOPS_LOCKED_v1.md` · `authority.yaml` · `EVENT_CONTRACT.yaml`

---

## One sentence

> **Authority model is coherent — stop re-analyzing. Prove enforcement in live Rail A runs; strict gates are P2.**

---

## Golden law (unchanged)

Specialists advocate · Execution Core decides · Workers act · Disk remembers · ASF controls

---

## Stack (five-source consensus — closed)

```
ASF + Hub (override)
  → SourceA Brain (execution_authority: true — pick · reconcile · handoff)
    → Broker + validators (broker=yes before run counts)
      → Workers (build only — this chat is Worker/Auto)
        → Validators · RESEARCH mirror · Disk SSOT
```

| Role | execution_authority | Tonight |
|------|---------------------|---------|
| ASF + Hub | human override | L1 semi-auto |
| SourceA Brain | **true** | dual-mode narrator / activate loop |
| Broker + validators | false | gates inject + submit |
| Workers (SourceA · portfolio · headless CLI) | false | build when INBOX delivers |
| Commercial · Governance · RA | false | advocate / research |
| Old Brain · GPT · Claude | false | archive broker / EXTERNAL_CRITIC |

---

## Maturity ladder

| Level | Name | Status |
|-------|------|--------|
| L1 | Semi-auto | **NOW** |
| L2 | Pointer + runtime JSON | Shipped |
| L3 | Broker-enforced loops | Validator PASS |
| L3.5 | Live observability | Boundary test PASS · full AUTO-RUN chain **pending** |
| L4+ | Policy engine · scheduler | Interface only — defer impl |

---

## P0 — verified on disk

| Artifact | Path |
|----------|------|
| Authority map | `brain-os/system/authority.yaml` |
| Prose pointer | `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` |
| Next task | `~/.sina/next-execution-pointer-v1.json` |
| Runtime now | `~/.sina/runtime/execution.json` |
| Active rail | `~/.sina/active-execution-rail-v1.json` |
| Validator | `scripts/validate-authority-runtime-v1.sh` |

**Canonical paths tonight:** `authority.yaml` + `next-execution-pointer-v1.json` — no duplicate `~/.sina/runtime/authority.yaml` tree.

---

## P1 — enforced (code exists)

| # | Gate | Implementation |
|---|------|----------------|
| 1 | Rail A manual inject | `check_rail_manual_inject` → `worker_inject_lib` |
| 2 | Pick authority | `check_prompt_pick_authority` |
| 3 | Specialist traces | `~/.sina/brain/reconciled_decision.yaml` |
| 4 | Pointer alignment | `check_pointer_alignment` on broker submit |
| 5 | Verify | `scripts/validate-authority-p1-v1.sh` |

---

## P1.5 — hooks (hybrid — not overclaimed)

| Item | On disk | Honest note |
|------|---------|-------------|
| `EVENT_CONTRACT.yaml` | Yes | Interface defined; JSONL impl partial |
| `execution_event_log_v1.py` | Yes | Broker dual-write + orchestrator |
| `check_reconciled_before_inject` | Yes | Missing `issued_by` → REJECT |
| Pre-inject `sync_reconciled` | Yes | Orchestrator auto-write — **not** Brain-verify |
| `validate_manual_fallback` | Yes | Bare `true` → `MANUAL_FALLBACK_UNSIGNED` |
| `cursor_entry_gate --scan-text` | Yes | `AUTHORITY_ADVISOR_PICK_BREACH` |
| `run-rail-a-boundary-test-v1.sh` | Yes | Mechanical inject-path proof |

### Reconciled chain (017 correction — canonical)

```
deliver_current
  → sync_reconciled_decision (pre-inject, orchestrator auto-write)
  → check_reconciled_before_inject (missing issued_by → REJECT; sa drift → WARN only)
  → INBOX write
brain_ack → sync_reconciled_decision (post-turn receipt)
```

**Not yet (P2):** Brain-signed verify before auto-write · strict reject on `RECONCILED_POINTER_SA_DRIFT`.

### `manual_fallback` on rail JSON

Disk may carry `manual_fallback` as a **string path** (queue file hint) — that is **not** an active override. Active override requires ASF-signed object:

```yaml
manual_fallback:
  active: true
  set_by: ASF
  reason: Emergency
  set_at: ISO
  expires_at: ISO
```

P2: rename path field to `manual_fallback_path` + audit validator.

---

## Claude Q1–Q3 — final severity

| Q | Tonight | Residual (P2) |
|---|---------|---------------|
| **Q1** Advisor inject | INBOX + `--scan-text` block regex/advisor sources | NL pick · mandatory turn-start scan on direct Worker chat |
| **Q2** Gate vs receipt | Hybrid stub gate | Strict `next_sa == queue.sa_id` reject |
| **Q3** manual_fallback | String path ≠ active override (blocks by accident) | ASF-signed object + audit when override is real |

---

## Proof classes

| PASS proves | Does NOT prove |
|-------------|----------------|
| Enforcement libs + validators exist | Malformed inject blocked in live AUTO-RUN |
| Boundary test (4 mechanical blocks) | Full event chain in one Hub session |
| Advisor regex breach on inject path | NL bypass in free Worker chat |
| Reconciled stub + pre-inject sync | Brain SYNC preceded last delivery with matching sa |
| Event contract + partial JSONL | `TASK_PICKED` → `INBOX_DELIVERED` → `VALIDATOR_PASS` in one run |

**GPT scores (9.3/10 etc.) are not authority** — observation only.

---

## Event log (observation spine)

| Path | Purpose |
|------|---------|
| `~/.sina/events/{YYYY-MM-DD}.jsonl` | Primary append-only (contract in `EVENT_CONTRACT.yaml`) |
| `~/.sina/goal1-lane-broker-events.jsonl` | Broker mirror |

**Live chain target (L3.5 done):** `DECISION_RECONCILED` → `INBOX_DELIVERED` → `WORKER_SUBMIT` → `VALIDATOR_PASS` | `AUTHORITY_REJECT`

---

## Validators (run order)

```bash
bash scripts/validate-authority-convergence-v1.sh
```

Runs: P0 · P1 · boundary test · LOCKED doc presence · reconciled traces.

---

## Master Operating Tracker

**SSOT:** `brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md`  
**Golden Rule:** Not in tracker = operationally invisible · tracker contradicts disk → **disk wins**  
**Validator:** `scripts/validate-master-operating-tracker-v1.sh`  
**STALE gate:** `tracker_status: STALE` in `execution.json` → Worker INBOX blocked

## ASF unlock phrases

| Phrase | Action |
|--------|--------|
| **Run first Rail A boundary test** | `run-rail-a-boundary-test-v1.sh` — inject-path mechanical proof |
| **Run live AUTO-RUN verify** | Hub ▶ AUTO-RUN · tail `~/.sina/events/$(date +%Y-%m-%d).jsonl` for full chain |

**Founder:** Hub clicks only — no Terminal.

**Sole remaining move (ASF 2026-06-08):** Tap AUTO-RUN on Rail A · observe full event chain fire cleanly.

---

## P2 when ASF names it

1. Strict pre-delivery reconciled reject on sa drift  
2. NL pick hardening + mandatory handoff when body sa ≠ pointer  
3. `manual_fallback_path` vs ASF-signed override + audit  
4. Unified event tail (`INBOX_DELIVERED`, `VALIDATOR_PASS`, `AUTHORITY_REJECT` on deliver/submit)  
5. Policy evaluator interface (`can_pick`, `can_build`, …) — spec only until L4  

---

## RESEARCH cites

| trace_id | Topic |
|----------|-------|
| `governance_goal_specialist-20260608-013` | Authority map agreement |
| `governance_goal_specialist-20260608-014` | Four-way synthesis |
| `governance_goal_specialist-20260608-015` | P0 disk verify |
| `governance_goal_specialist-20260608-016` | Live-run gaps (Q2 superseded by 017) |
| `governance_goal_specialist-20260608-017` | P1.5 disk reconcile |
| `AUTO-TRACE-AUTHORITY-P1-LOOPS-2026-06-08` | Worker P1 ship |
| `AUTO-TRACE-AUTHORITY-CONVERGENCE-LOCK-2026-06-08` | This lock mirror |

---

*End AUTHORITY_RUNTIME_VERIFICATION_LOCKED_v1*
