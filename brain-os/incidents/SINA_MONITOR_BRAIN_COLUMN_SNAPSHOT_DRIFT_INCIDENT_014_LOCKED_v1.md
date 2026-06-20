# Monitor Brain column PEND — snapshot drift (not worker redo) — INCIDENT-014 (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-014  
**Classification:** MANDATORY READ — Brain · Worker · Maintainer · all executor agents before monitor/progress claims  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-10 (founder: “validated until 40 — why Brain PEND / redo?” · monitor `:13021` screenshot)  
**Related:** INCIDENT-007 (broker/STALE) · INCIDENT-009 (session closeout / monitor honesty) · INCIDENT-013 (stale goal_progress parrot) · `MONITOR_HONESTY_LOCKED_v1.md` · `PROOF_VALIDATION_CHAIN_LOCKED_v1.md`  
**Not this incident:** INCIDENT-011 = REWRITE unauthorized disk edit · INCIDENT-013 = goal_progress inject parrot  
**Tags:** `INCIDENT-014`, `monitor-honesty`, `brain_validate`, `dual_proof`, `brain-column`, `display-drift`, `founder-trust`

---

## 1. Executive summary

The founder opened **SourceA Road Map** (`http://127.0.0.1:13021/monitor`) and saw **Brain PEND** on **every row** (including sa-0001..sa-0040 previously approved), plus header **Brain PEND/FAIL** and **dual_proof GAP**, while **Worker PASS · Broker PASS · Valid YES · Maint PASS** remained green.

**Severity:** **High** (founder trust) — **not** data loss, **not** receipt deletion, **not** worker redo.

**Root cause:** The **Brain column is a global system flag**, not per-sa brain work. It shows **PEND** when `~/.sina/brain-goal1-validation-v1.json` → `progress_honest.valid_yes` **≠** live monitor `valid_yes`. Pack 3 advanced honest count (**154 → 172**) without an immediate `brain_validate_goal1.py --write-receipt` sync after each batch.

**One-line law:**

> **Brain PEND on all green rows = brain validation snapshot stale — not “redo sa-0001”. Valid YES + receipt + REGISTRY done is the row truth.**

---

## 2. What the founder experienced

1. Morning: agent said rows through **~40** were **verified / Valid YES**.
2. Later: monitor showed **Brain PEND** on sa-0001..sa-0021+ with **dual_proof GAP**.
3. Founder conclusion: “you approved then changed without reasonable fact” / “redo” / “critical mistake”.
4. Agent language (“worker done and verified”) did **not** match monitor Brain column.

**Founder was right to challenge trust.** The **interpretation** “work was undone” was **wrong**; the **UI + agent vocabulary** caused the break.

---

## 3. Disk truth (verified at closeout)

| Check | Result |
|-------|--------|
| sa-0001..sa-0040 | **All Valid YES** · Worker PASS · Broker PASS · receipt logged · REGISTRY `done` |
| sa-0001..sa-0110 | **103/110 Valid YES** · 7 honest WAIT (not done) |
| Global honest | **172/1000** (did not roll backward) |
| STALE broker | **0** · PARTIAL **0** |
| Receipts deleted | **None** |
| REGISTRY reverted for closed sas | **None** |

After `brain_validate_goal1_v1.py --write-receipt` at **2026-06-10T05:46:03Z** (valid_yes **172**): API `/api/validator-list` returns **Brain PASS** per row and **dual_proof LOCKED OK**.

---

## 4. Root cause (technical)

### 4.1 Brain column is global — not per row

`scripts/monitor_honesty_lib_v1.py`:

```python
def brain_row_column(*, valid: str, proof: str, system_brain_ok: bool) -> str:
    if valid == "YES":
        return "PASS" if system_brain_ok else "PEND"
```

`system_brain_ok` is true only when:

```text
brain-goal1-validation-v1.json → progress_honest.valid_yes == live monitor valid_yes
```

So **one stale snapshot** paints **Brain PEND on every Valid YES row** — extremely misleading.

### 4.2 Snapshot lag after Pack 3

| Layer | During incident | Updated on each VERIFY? |
|-------|-----------------|-------------------------|
| Receipt + REGISTRY | 172 | Yes |
| Monitor Valid YES | 172 | Yes (live) |
| `brain-goal1-validation-v1.json` | **154** (stale) | **No** — not wired to `advance-healthy-queue-v1.py` |

`enforce-registry-hygiene-v1.sh` and `fix-ecosystem-all-v1.sh` **do** refresh brain validate; **autorun pack advance** often **does not**.

### 4.3 Vocabulary collision (agent ↔ monitor)

| Phrase agent used | Machine meaning | Monitor column |
|-------------------|-----------------|----------------|
| “Worker done” | Worker PASS + receipt | Worker ✓ |
| “Verified” | Validators + closeout | Valid YES ✓ |
| “Brain approved” (implied) | `brain_validate` snapshot synced | **Brain PEND** until sync |

---

## 5. Contributing factors

1. Monitor footer says “Brain = hygiene+brain_validate agrees” but **does not** say “PEND ≠ row failed”.
2. No header line `brain snapshot X vs live Y` when GAP.
3. Agent did not say: “Valid YES locked; refresh brain_validate / tap ↺”.
4. **HERE #31** with empty sa when queue exhausted (pos > 30) — extra confusion.
5. Pack 3 skipped eval-blocked sas (0099, 0101…) — honest, but looks like “gaps” without context.

---

## 6. What was NOT the cause

- Worker redo of sa-0001..0040  
- Receipt or REGISTRY rollback  
- Monitor FAKE / PARTIAL / STALE (all 0 at audit)  
- Intentional reversal of approved work  

---

## 7. Fixes applied

| Action | Status |
|--------|--------|
| `python3 scripts/brain_validate_goal1_v1.py --json --write-receipt` | Done — snapshot **172** |
| Verified sa-0001..0040 unchanged | Done |
| Hygiene PASS · dual_proof True (post-sync) | Done |

---

## 8. Recommended hardening (Maintainer / ASF order)

| Priority | Item |
|----------|------|
| P0 | After every pack / honest +N: **brain_validate --write-receipt** before telling founder “verified” |
| P1 | Wire `brain_validate` into post-VERIFY hook or `advance-healthy-queue-v1.py` |
| P1 | Monitor UI: rename column to **“Brain sync”**; tooltip when PEND |
| P1 | Header: show `brain_vy X · live_vy Y` when mismatch |
| P2 | Agent status template: always cite **Valid YES count + brain snapshot count + dual_proof** |

---

## 9. Never-again card (agents)

```text
Founder: "Brain PEND — you redid my work!"
  → Run goal-progress + registry_honest + sample receipts for sa-0001..N FIRST
  → If Valid YES still YES: explain snapshot lag; run brain_validate --write-receipt
  → Tell founder: tap ↺ on :13021/monitor — do NOT panic-redo sas

Never say "verified" alone — say:
  Valid YES N · receipts N · brain snapshot M (sync if M≠N) · dual_proof OK/GAP

Brain column PEND on all green rows ≠ redo — it is ONE global stale file.
```

---

## 10. Closeout checklist

- [x] LOCKED body in `brain-os/incidents/` (this file)  
- [x] Root pointer at `SourceA/`  
- [x] Row in `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`  
- [x] Hub `ecosystem_incidents_index.py` row (Maintainer)  
- [x] Wire auto brain sync — `brain_sync_lib_v1.py` on closeout/advance/autodrain/hub (2026-06-10)  

---

**END INCIDENT-014** — SA-2026-06-10-INCIDENT-014
