# ATTACHMENT — Cursor agent · Post-Claude synthesis (v1)

**Saved:** 2026-06-06T18:42:41Z · **Retrofit:** doc-datetime-law batch retrofit
**Type:** STAGING ATTACHMENT — **Cursor HQ agent** research, insight, recommendation, and implementation after Claude trigger  
**Status:** Attached · **do not drop** — equal weight to Claude attachment for operational truth  
**Trigger (not sole source):** `CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md`  
**Session date:** 2026-06-05  
**Parent law:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md`  
**Machine mirror:** `scripts/system_roadmap.py` → `session_lineage` · `roadmap_attachments` · `implementation_hardening` · `ship_ready`  

---

## 0. Founder law — two layers, both kept

| Layer | Who | Role | Lose this? |
|-------|-----|------|------------|
| **A — Trigger** | Claude AI / Claude chat | External critic — convinced gate hardening, D15.1/D15.2, 90-day shape | **No** |
| **B — Synthesis** | Cursor HQ agent (this session) | Research, lessons, knowledge library, D5 ship, hub, shadow gate wire | **No** |

**“Post-Claude”** means **after the trigger** — not “only Claude.”  
Renaming Claude ≠ Cloud does **not** delete Layer B.

---

## 1. Agent insights (original — keep)

| # | Insight | Where preserved |
|---|---------|-----------------|
| 1 | Gap = **one choke point in code**, not founder thinking | Lessons L1 · companion §1 · `implementation_hardening.core_gap_clarified` |
| 2 | **Substrate vs projection** — `~/.sina/*` + graphs vs one packet per call | Merge §1 · hardening payload · essay |
| 3 | D15 = **compiler**, not another feature | Merge §2 · golden report §1 |
| 4 | **Gate hub planners first** — not Cursor executor on day one | Lessons L7 · companion §4 |
| 5 | **Shadow before enforce** — OFF → SHADOW → ENFORCE | Lessons L6 · Claude attachment + agent policy table |
| 6 | **Rule-based D4/D9 first**, LLM last | Lessons L8 · ship checklist |
| 7 | Industry golden pipeline maps 1:1 to D4→D15 | `GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md` |
| 8 | `retrieval` conditional in `GATE_REQUIRED_SECTIONS` when semantic path active | Lessons L11 · companion checklist |
| 9 | Knowledge library = **one field per subject**, purity = pointers | `PIPELINE_LAW.md` · manifest |
| 10 | **Active threads** never dropped (WTM, Factory, MergePack, Chat Unify) | Lessons · companion §7 |
| 11 | D5 ship playbook = SSOT + API + validator + packet wire (same as D4) | `SHIP_PLAN_D5_AND_GATE_v1.md` · companion §8 |
| 12 | Maturity **4/10 → 7/10** when enforce lands — “did system assemble?” not “did we think?” | Companion §9 |

---

## 2. Agent recommendations (locked — implement in order)

1. Ship **D5** local vector index + validator — **DONE** (`validate-vector-retrieval-v1.sh` PASS)  
2. **`model_dispatch.py` SHADOW** + log `~/.sina/gate_shadow_v1.jsonl` — **DONE**  
3. Wire **`agent_loop._planner_chat`** through dispatch — **DONE** (shadow)  
4. Hub **Knowledge Library** tab + WTM attachments/hardening — **DONE**  
5. **Research skill** mandatory on every research turn — **DONE** (`sina-research-lessons`)  
6. Ship **D6** → D7–D10 rule-based → D14–D15 → **ENFORCE** — **NEXT**  
7. Hub **packet readiness %** (D15.2) — partial  
8. Golden set `~/.sina/golden/pre_llm_v1/` — pending  
9. Remaining OpenRouter paths → `model_dispatch` — pending  

Full checklist: `SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md` §5.

---

## 3. Agent research artifacts (files — do not delete)

| Artifact | Path | Role |
|----------|------|------|
| Golden research | `GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md` | Industry URL table · pipeline proof |
| Lessons | `SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md` | Append-only agent memory |
| Ship companion | `SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md` | Master operational checklist |
| Library index | `knowledge-library/KNOWLEDGE_LIBRARY_INDEX.md` | Fields + pipeline |
| Pipeline law | `knowledge-library/PIPELINE_LAW.md` | Extract→book law |
| Gather | `fields/pre-llm-world-model/02-gathered/GATHER_v1_GATE_RESEARCH.md` | Curated pulls |
| Merge | `fields/pre-llm-world-model/03-merged/MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md` | Synthesis |
| Essay | `fields/pre-llm-world-model/04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md` | First teachable page |
| Book outline | `fields/pre-llm-world-model/05-books/BOOK_OUTLINE_v1.md` | Training spine |
| Ship plan D5 | `fields/pre-llm-world-model/04-unified/SHIP_PLAN_D5_AND_GATE_v1.md` | D5+gate receipt |
| Extract manifest | `fields/pre-llm-world-model/01-extracts/MANIFEST.md` | Provenance rows |

---

## 4. Agent implementation (code — shipped)

| Deliverable | Path |
|-------------|------|
| D5 module | `scripts/pre_llm/vector_retrieval/` |
| Vector index SSOT | `~/.sina/vector_index_v1.json` (457 chunks) |
| API | `GET /api/vector-retrieval-v1` |
| Validator | `validate-vector-retrieval-v1.sh` |
| Packet wire | `schema.py` — `packet.retrieval` hydrates from D5 |
| Gate shadow | `scripts/model_dispatch.py` |
| Shadow validator | `validate-model-gate-shadow-v1.sh` |
| Planner wire | `scripts/agent_loop.py` → `_planner_chat` via dispatch |
| Hub payload | `scripts/knowledge_library_payload.py` |
| Hub tab | Knowledge Library in `agent-control-panel/assets/app.js` |
| Roadmap SSOT | `scripts/system_roadmap.py` — attachments, hardening, ship_ready |
| Agent skill | `~/.cursor/skills/sina-research-lessons/SKILL.md` |

---

## 5. What agents must do on read

1. Read **Claude attachment** — convinced extras, gate modes, sub-steps.  
2. Read **this synthesis** — research, lessons, ships, code truth.  
3. Read **lessons file** — latest moves and threads.  
4. Never merge Layer A into Layer B or vice versa — **both** attach to WTM.

---

## 6. Changelog

| Date | Change |
|------|--------|
| 2026-06-05 | v1 — dual lineage attachment; founder law: Claude = trigger, Cursor agent work = kept synthesis |
