# INCIDENT-017 pointer — phase drift + system laziness → repair mode

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0  
**Canonical body:** `brain-os/incidents/SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_LOCKED_v1.md`  
**Pack draft:** `archive/attachments/2026-06-10/PHASE_PACK_REORG_DRAFT_s2-s9_ACHIEVABLE_v1.md`

## One paragraph

Automation was **lazy**: it picked the next 10 easy SAs (`pick_floor` forward), **skipped** s1/s4/s6 blockers without re-healing the plan, jumped to **s7 (~sa-0773)**, closed many SAs with **generic VERIFY**, and after STOP **did not rebuild** phase-strict packs. That **sickness** (holes + conduct INCIDENT-015/016) forced **repair mode** (FREEZE_DRAIN). Fix: ASF-curated phase packs + `PHASE_STRICT` — machine runs manifest, does not choose it.

## Key numbers

- s2/s3: **100% done** · s1: **21 backlog** (not s2)
- Jump: sa-0773..0782 while s1 open
- Headless achievable left: **119 SAs** (s7+s8+s9)
- Honest: **596/1000** · freeze **ON**

## ASF next

1. Approve pack reorg draft  
2. Audit conduct receipts  
3. `resume drain PHASE_STRICT s7-P1` only after yes

**Status:** OPEN
