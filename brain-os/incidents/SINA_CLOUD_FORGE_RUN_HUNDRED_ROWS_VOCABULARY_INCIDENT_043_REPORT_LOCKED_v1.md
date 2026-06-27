# INCIDENT-043 — Hundred rows per turn · agent vocabulary split (report pointer)

**Saved:** 2026-06-24T07:15:00Z  
**Canonical body:** `brain-os/incidents/SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md`  
**Law:** `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md`  
**SSOT:** `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json`

## One line

ASF order: **every ~10 minutes = 100 queue rows down in one Railway request (mandatory quota — NOT “up to 100”)** — not one row per cron, not “100 pack still running.” Agents disagreed; law now mandatory.

## Status

**OPEN** — vocabulary locked · close when agents stop Split A–E (see body §3).

## Proof

`GET https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1` → `pack.processed` / `pack.max_advance`

---

*Report pointer · INCIDENT-043 v1.0*
