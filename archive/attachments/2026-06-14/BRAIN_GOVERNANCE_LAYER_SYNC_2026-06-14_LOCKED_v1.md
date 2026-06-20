# Brain ↔ Governance layer sync receipt (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order  
**Law:** `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md`  
**Governance chat:** `e54ddfa8` · **Brain chat:** `58148ac9`

---

## Aligned stack

| Layer | Rank | Role |
|-------|------|------|
| L0 | — | ASF + Hub |
| L0.5 | — | Machine pipeline (Python) |
| **L1** | 1 | Brain |
| L1 | 2 | Governance Specialist |
| L1 | 3 | Commercial Specialist |
| L1 | 4 | Brief Specialist |
| **L2** | 5 | Worker |
| L2 | 6 | Researcher 2 |
| L2 | 7 | Maintainer 2 |
| L2 | 8 | Maintainer 3 |
| **L3** | 9+ | TrustField · Noetfield · Forge · other repos |

---

## Sync surfaces updated

| Surface | Change |
|---------|--------|
| `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` | Canonical law |
| `~/.sina/governance-chat-context-v1.json` | `layer_stack` + ranks |
| `scripts/brain_governance_wire_v1.py` | `active_decisions[]` + law path |
| `.cursor/rules/governance-specialist-in-charge.mdc` | Rank 2 · sync before reply |
| `MANDATORY_READ_BY_ROLE` v1.7 | Cross-cutting row |
| `MANDATORY_BRAIN_CHAT` | §LAYER STACK |

---

## Governance Specialist rule

**Before every reply:** `brain_governance_wire_v1.py` → read `governance-brain-wire-v1.json`  
**Never** outrank Brain · **never** contradict `active_decisions[]`

---

*End BRAIN_GOVERNANCE_LAYER_SYNC_2026-06-14_LOCKED_v1*
