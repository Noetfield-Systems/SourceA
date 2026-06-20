# INCIDENT-016 — Plan todo ghost reactivation (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Severity:** HIGH · CONDUCT  
**Canonical body:** `brain-os/incidents/SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_LOCKED_v1.md`  
**Parent:** INCIDENT-015 conduct (archive) — UI/session half of same failure mode

## One-line

After ASF **“cancel all pending”**, agent cancelled p4–p7 only; **p0–p3 stayed `completed`** → Cursor showed **“4 of 4 To-dos Completed”** → next question re-surfaced old Drain Recovery plan context.

## Fix now

`TodoWrite` **all** plan ids → `cancelled` · reply **`PLAN_REVOKED`** · STOP scripts before status on new turn.

**Status:** OPEN
