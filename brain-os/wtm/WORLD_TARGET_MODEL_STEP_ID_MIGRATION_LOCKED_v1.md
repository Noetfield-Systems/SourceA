# World Target Model — Step ID alignment migration (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-INCIDENT-004  
**Trigger:** Founder law — **step ID prefix MUST match hub phase letter**  
**Payload:** `system_roadmap` v4.0  
**Map (current):** `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` · **Historical:** v4 in `archive/superseded/wtm/v4/`  

---

## Law (one sentence)

**Phase A steps are A1, A2… · Phase B steps are B1, B2… · never mix prefixes inside a phase.**

---

## Why we migrated

INCIDENT-003 kept old artifact IDs (`D1` spine, `C1` intel, `B4` runtime, `A1.1` pre-LLM) while hub phases were renamed A→B→C→D. Founder rejected that permanently.

---

## Full mapping (v3 → v4)

| Hub phase | Old ID | New ID | Layer |
|-----------|--------|--------|-------|
| **A** Spine | D1 | **A1** | Execution queue |
| A | D2 | **A2** | Worker + executor |
| A | D3 | **A3** | Memory writeback |
| A | D4 | **A4** | Artifact store |
| **B** Intel | C1 | **B1** | Pattern extraction |
| B | C2 | **B2** | Decision memory |
| B | C3 | **B3** | Feedback loop |
| B | C4 | **B4** | Planner upgrade |
| B | C5 | **B5** | Context intelligence |
| B | C6 | **B6** | Self-optimization |
| **C** Runtime | B1 | **C1** | Tool graph |
| C | B2 | **C2** | Graph verification |
| C | B3 | **C3** | Execution router |
| C | B4 | **C4** | Autonomous repair ● NOW |
| C | B5 | **C5** | Context fabric |
| C | B6 | **C6** | Multi-step planner |
| C | B7 | **C7** | Orchestrator |
| **D** Pre-LLM | A1.1 | **D1** | Code intelligence ● NOW strategic |
| D | A1.1.1 | **D2** | Graph fusion |
| D | A1.2 | **D3** | Dependency graph |
| D | A1.3 | **D4** | Intent engine |
| D | A2.1 | **D5** | Vector retrieval |
| D | A2.1.1 | **D6** | Memory + git bridge |
| D | A2.1b | **D7** | Query expansion |
| D | A2.2 | **D8** | Graph reasoning |
| D | A3.1 | **D9** | Context ranking |
| D | A3.2 | **D10** | Planning engine |
| D | A4.1 | **D11** | Tool router upgrade |
| D | A4.2 | **D12** | Validation layer |
| D | A5.1 | **D13** | Diff intelligence |
| D | A5.2 | **D14** | Compression |
| D | A5.3 | **D15** | Context assembly |
| D | A5.3.1 | **D16** | Memory merge into packet |

---

## Build now (v4)

| Track | Step |
|-------|------|
| Runtime (Phase C) | **C4** |
| Strategic (Phase D) | **D1** (parallel) |

---

## Archive

Superseded step-ID era: `archive/superseded/wtm/v3/` (MAP v3) · manifest updated.

**Script:** `scripts/migrate-wtm-step-ids-v4.py` (one-shot; keep for evidence)
