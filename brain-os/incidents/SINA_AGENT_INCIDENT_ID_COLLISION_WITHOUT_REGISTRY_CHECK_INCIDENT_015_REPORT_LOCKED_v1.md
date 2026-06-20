# INCIDENT-015 — Incident ID filed without registry check — pointer

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-015  
**LOCKED body:** `brain-os/incidents/SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md`

## Summary

Executor agent labeled the monitor Brain PEND event **“INCIDENT-011”** in chat and `agent-governance-events.jsonl` **without** reading `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

**INCIDENT-011 is already taken:** REWRITE unauthorized disk edit (P0).

## Correct mapping

| Wrong | Correct |
|-------|---------|
| “INCIDENT-011” monitor Brain PEND | **INCIDENT-014** |
| (this filing mistake) | **INCIDENT-015** |

## Law

> Read registry → `rg INCIDENT-NNN` → next free id → LOCKED body + pointer + registry row. **No chat-only ids.**
