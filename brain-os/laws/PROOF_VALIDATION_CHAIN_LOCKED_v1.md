# PROOF VALIDATION CHAIN — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-09 · **Authority:** ASF  
**Code:** `scripts/monitor_honesty_lib_v1.py` · `scripts/enforce-registry-hygiene-v1.sh`  
**Parent:** `MONITOR_HONESTY_LOCKED_v1.md` · `REGISTRY_DRAIN_PROCESS_LOCKED_v1.md` · INCIDENT-006

---

## Six layers (never collapse)

| Layer | Who | Proof artifact |
|-------|-----|----------------|
| **1 Worker** | SourceA Worker chat | `receipts/sa-XXXX-receipt.json` · validators on VERIFY |
| **2 Broker** | `goal1_lane_broker.py` | `~/.sina/goal1-lane-broker-events.jsonl` CHECK→ACT→VERIFY |
| **3 Monitor** | `monitor_honesty_lib_v1.py` | Worker / Broker / Valid / Recipe / **Brain** / **Maintainer** columns |
| **4 Hygiene** | `enforce-registry-hygiene-v1.sh` | `~/.sina/last-hygiene-pass-v1.json` |
| **5 Brain** | SourceA Brain chat | `~/.sina/brain-goal1-validation-v1.json` · runs hygiene before progress |
| **6 Maintainer** | SinaaiDataBase maintainer | `~/.sina/track-validate-snapshot-v1.json` · gate scripts PASS |

**Progress bar = Valid YES only** = Layer 1 + 2 + 3 agree. Layers 5–6 must PASS at system level before founder trusts the bar.

---

## Monitor columns (machine — no human ticks)

| Column | PASS means |
|--------|------------|
| **Worker** | Honest receipt on disk |
| **Broker** | Full broker cycle + verify ok |
| **Valid** | Worker PASS **and** Broker PASS |
| **Recipe** | Proof type OK (not batch YAML fake) |
| **Brain** | Valid YES **and** Brain validation file matches Valid YES count |
| **Maintainer** | Valid YES **and** maintainer gates PASS **and** receipt source allowed |

| Column | FAIL / PEND |
|--------|-------------|
| **Brain PEND** | Row closed but Brain validation stale or count mismatch |
| **Maintainer PEND** | Row closed but hygiene snapshot stale |
| **Brain/Maintainer FAIL** | FAKE / NO / invalid receipt source |

---

## Hygiene chain (every Brain reply + after every 30-pack)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash enforce-registry-hygiene-v1.sh
```

This runs: honest gate · quarantine · broker repair · monitor gate · **brain_validate --write-receipt** · **track_validate --write --run-validators** · writes `last-hygiene-pass-v1.json`.

---

## Forbidden (INCIDENT-006)

- Chat claim without receipt
- YAML-only done
- Quote progress without hygiene
- Brain implements sa ACT/VERIFY
- Maintainer ticks monitor by hand

---

**End PROOF_VALIDATION_CHAIN_LOCKED_v1**
