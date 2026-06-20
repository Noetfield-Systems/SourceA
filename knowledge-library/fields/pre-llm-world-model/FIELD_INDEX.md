# Field — Pre-LLM World Model & Gate

**Field ID:** `pre-llm-world-model`  
**WTM phase:** D (D1–D16)  
**Current build step:** **D5** Vector Retrieval — **validator PASS** (ship D6 next)  
**Primary thread:** `WTM-D5`  
**One-line law:** The model is an executor on a compiled world model. No compilation, no call.

---

## What this field teaches

How Sina builds **understanding before action**: intent → retrieval → ranking → plan → packet → validate → model. For agent roles: **WTM builder**, **packet assembler**, **gate operator**, **hub planner** (not Cursor executor).

---

## Pipeline status

| Stage | File | Status |
|-------|------|--------|
| Extract | `01-extracts/MANIFEST.md` | ✅ 3 sources registered |
| Gather | `02-gathered/GATHER_v1_GATE_RESEARCH.md` | ✅ |
| Merge | `03-merged/MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md` | ✅ |
| Unify | `04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md` | ✅ first essay |
| Book | `05-books/BOOK_OUTLINE_v1.md` | ✅ outline started |

---

## Locked source (read for law — do not copy into essays)

- `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`
- `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md`
- `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md`
- `scripts/system_roadmap.py`
- `scripts/pre_llm/context_packet/schema.py`

---

## Next essays (planned)

| Essay ID | Topic | After step |
|----------|-------|------------|
| ESSAY_v2 | D5 local vector retrieval | D5 PASS |
| ESSAY_v3 | Rule-based D9/D10 | D9/D10 shadow |
| ESSAY_v4 | model_dispatch shadow → enforce | D15.1 |
