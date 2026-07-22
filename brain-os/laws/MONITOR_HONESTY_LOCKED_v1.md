# MONITOR HONESTY — progress + broker columns (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-09  
**SSOT code:** `scripts/monitor_honesty_lib_v1.py`  
**Gate:** `scripts/validate-monitor-honesty-v1.sh` (runs on every honest-gate build)  
**Progress verdict (tiers + snapshot):** `SOURCEA_VALID_YES_PROGRESS_VERDICT_LOCKED_v1.md` — pointer only

---

## §PROGRESS (what moves the bar)

| Shows in UI | Source | Counts as done? |
|-------------|--------|-----------------|
| **Valid YES** | Worker PASS + Broker PASS + receipt | **Yes — only this** |
| **Brain sync** | Valid YES + `brain-goal1-validation-v1.json` matches live count | Global system sign-off — PEND on all green rows = snapshot lag, not redo |
| **Maintainer** | Valid YES + hygiene + maintainer gates PASS | Dual proof sign-off |
| **Map DONE** | Same as Valid YES | Yes |
| **receipt_done** | `receipts/sa-XXXX-receipt.json` on disk | Shown separately — may exceed Valid YES if broker gap |
| **STRUCT_OK** | Prompt `.md` exists, registry backlog | **No** |
| **Broker STALE** | Old `WORKER_SUBMIT` on backlog, no receipt | **No** |

**Forbidden:** use `honest_done` / receipt count alone for progress % in Brain, hub, or monitor.

---

## §BROKER COLUMN (mechanical)

Broker **PASS** requires **all** of:

1. Registry `done` + honest receipt on disk  
2. Broker events include **check + act + verify** for that `sa_id`  
3. Last **verify** event: `orch_ok=true` (full CHECK→ACT→VERIFY in events)  
4. If `deliver_ok=false` but honest **receipt** exists → **PASS** (delivery gap only; receipt wins)

| Broker value | Meaning |
|--------------|---------|
| **PASS** | Full cycle + verify delivered |
| **PEND** | In queue, or done but broker cycle incomplete |
| **FAIL** | Full cycle but verify `deliver_ok=false` |
| **STALE** | Backlog + broker history, no receipt closeout |
| **WAIT** | No broker events |

`orch_ok` alone **never** equals PASS.

---

## §BRAIN (every Goal 1 status reply)

**Before** narrating progress, run:

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
python3 brain_sync_lib_v1.py --status --json
bash validate-monitor-honesty-v1.sh
bash validate-brain-snapshot-sync-v1.sh
```

**Paste** `progress.valid_yes` / `progress.pct` — not receipt count alone.

**Agent status template (mandatory — INCIDENT-014):**

```text
Valid YES N · brain snapshot M · dual_proof OK/GAP · receipts R
```

**Say:** “X/1000 Valid YES” and “Y receipts (Z PARTIAL broker gap)” when they differ.

**Automation SSOT:** `scripts/brain_sync_lib_v1.py` — wired on VERIFY closeout + queue advance + hub **Fix Brain sync**.

---

## §WORKER / BROKER (every turn)

1. CHECK → ACT-if-gap → VERIFY — one role per turn  
2. `WORKER_ROUND_REPORT` YAML  
3. `goal1_lane_broker.py worker-submit --stdin`  
4. VERIFY closeout writes `receipts/sa-XXXX-receipt.json` only on machine PASS  

Broker records `deliver_ok` on verify — monitor uses it.

---

## §AUTO-HYGIENE

`validate-monitor-honesty-v1.sh` quarantines `cursor-worker-batch` YAML sitting beside honest receipts (does not change REGISTRY).

---

## §FORBIDDEN (INCIDENT-006)

- Batch closeout without receipt  
- Label backlog as PASS / validated  
- Brain quote 607 / hub % without `validate-monitor-honesty-v1`  
- Trust YAML or chat as progress
