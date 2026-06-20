# H2 pending 21 — root cause + fix plan (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order — no inflated pending counts  
**Registry:** `~/.sina/h2-pending-registry-v1.json`  
**Counter SSOT:** `scripts/h2_pending_count_lib_v1.py`

---

## Root cause (why you saw 21)

**Bug:** `pending_total` counted **every row** in `maintainer_ship`, including:
- **H2-ROUTE** — already **shipped**
- **N8N-GOV-WIRE** — already **wired**
- **UP-01…UP-06** — **scheduled cadence** (daily/weekly/quarterly), not open blockers
- **LEGACY-HERO** — **monthly** schedule

Real open work was **11**, not 21. Form was already **0 open**.

**Fixed logged:** `h2_pending_registry_reconcile_v1.py` · honest counter in `machine_hub_v1.py`.

---

## Honest open pending (fix every row)

### Next phase (4) — factory / enforcement

| ID | Fix | Owner | Done when |
|----|-----|-------|-----------|
| **sa-0101** | OpenRouter activation pack s1 CHECK | Worker | Receipt + validator PASS on OR credits |
| **W1-FILM** | Demo film + write-path validator evidence | Worker | W1 film receipt logged |
| **W3-BATCH-1** | NF outreach batch 1 (agentic — you never email) | Commercial | Batch approved + send receipt |
| **PHASE-3-10-RESUME** | Integrity playbook phases 3–10 | Maintainer | SYS-INTEGRITY index green |

### Deferred (4) — founder Form picks when ready

| ID | Fix | Owner | Done when |
|----|-----|-------|-----------|
| **Q-WIRE-G3** | RECONCILE → run G3 Tailscale proof | Worker | `WIRE_LANE_PROGRESS.md` row |
| **Q-1.10-SEAL** | DEFER until RT LIVE sealed | Maintainer | Phase 1.10 receipt |
| **ENF-13** | DEFER enforcement fork | Governance | Form row closed or promoted |
| **Q-M2-REG** | DEFER registry fork | Maintainer | Form row closed |

### Ops blockers (3) — ship gates

| ID | Fix | Owner | Done when |
|----|-----|-------|-----------|
| **MP-SHIP** | Disable Vercel Deployment Protection · `/health` 200 | ASF tap + Worker | MergePack live proof |
| **WIRE-G3** | g3 proof + progress file | Worker | Same as Q-WIRE-G3 reconcile |
| **B-001** | Review `ARCHITECT_REPORT.yaml` · ingest | Maintainer | Ingest receipt |

### Maintainer open (1)

| ID | Fix | Owner | Done when |
|----|-----|-------|-----------|
| **CHANGE-QUORUM-SHIP** | Run judge_center `--ssot-delta` · hub alarm strip | Maintainer | Judge strip receipt |

### Thread Room (3 draft rows — separate from pending_total)

Weekly scout · map only · not factory blockers. Run `thread_room_run_v1.py` on schedule.

### Scheduled cadence (7 — NOT pending)

UP-01…UP-06 + LEGACY-HERO → bucket `scheduled_cadence` · run on daily/weekly/monthly schedule only.

### Closed (moved off pending)

H2-ROUTE (shipped) · N8N-GOV-WIRE (wired) → `maintainer_ship_closed`.

---

## Execution order (no skip)

1. **Worker:** `RUN INBOX` (factory queue — not blocked by H2 list)  
2. **MP-SHIP** — highest commercial ship gate  
3. **WIRE-G3** + **Q-WIRE-G3** — one proof closes both  
4. **W1-FILM** + **W3-BATCH-1** — parallel after MP  
5. **CHANGE-QUORUM-SHIP** — Maintainer one pass  
6. **PHASE-3-10-RESUME** — after integrity index check  
7. **Deferred rows** — Form submit batch when you finish picks  

---

## Validators

```bash
python3 scripts/h2_pending_registry_reconcile_v1.py --json
bash scripts/validate-h2-pending-honest-count-v1.sh
bash scripts/validate-machine-hub-v1.sh
```

*End fix plan v1*
