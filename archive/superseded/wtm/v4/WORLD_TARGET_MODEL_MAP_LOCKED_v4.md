# World Target Model Map (Locked)

**Saved:** 2026-06-05T11:45:07Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 4.0 — LOCKED  
**Supersedes:** `archive/superseded/wtm/v3/WORLD_TARGET_MODEL_MAP_LOCKED_v3.md`  
**Migration:** `WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md` (INCIDENT-004)  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  
**Payload:** `system_roadmap` v4.0  

**Law:** Step ID prefix = hub phase letter. **A1** is Phase A. **D1** is Phase D. Never mixed.

---

## Phase map

| Phase | Steps | Status |
|-------|-------|--------|
| **A** Execution Spine | A1–A4 | ✅ done |
| **B** Intelligence OS | B1–B6 | ✅ frozen |
| **C** Runtime Stack | C1–C7 | 🔄 **C4** now |
| **D** Pre-LLM World Model | D1–D16 | ❌ **D1** next (parallel) |

---

## Phase D build order (16 steps)

| # | ID | Layer |
|---|-----|-------|
| 1 | **D1** | Code Intelligence v1 **BUILD** |
| 2 | D2 | Graph Fusion v1 |
| 3 | D3 | Dependency Graph v1 |
| 4 | D4 | Intent Engine v1 |
| 5 | D5 | Vector Retrieval v1 |
| 6 | D6 | Memory + Logs + Git bridge |
| 7 | D7 | Query Expansion v1 |
| 8 | D8 | Graph Reasoning v1 |
| 9–D16 | … | Ranking → packet (see payload) |

---

## Build now

- **C4** — Autonomous Repair Loop v1 (Phase C)  
- **D1** — Code Intelligence Layer v1 (Phase D, parallel)
