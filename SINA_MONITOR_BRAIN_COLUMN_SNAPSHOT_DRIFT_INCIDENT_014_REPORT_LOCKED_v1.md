# INCIDENT-014 — Monitor Brain column PEND (snapshot drift) — pointer

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-014  
**LOCKED body:** `brain-os/incidents/SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md`

## Summary

Founder saw **Brain PEND** on all monitor rows and **dual_proof GAP** after Pack 3 (**172/1000** honest). **Work was not redone** — sa-0001..0040 remain **Valid YES** with receipts. Cause: **`brain-goal1-validation-v1.json` lagged** live count; Brain column is a **global sync flag**, not per-sa failure.

## Law

> Brain PEND on green rows = run `brain_validate_goal1.py --write-receipt` + monitor ↺ — **not** redo Worker turns.

## Fix

`brain_validate --write-receipt` synced to **172** · dual_proof **OK** after refresh.

**Not INCIDENT-011** (that is REWRITE disk edit).
