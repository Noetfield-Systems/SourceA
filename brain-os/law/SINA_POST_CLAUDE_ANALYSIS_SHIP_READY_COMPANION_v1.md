# Post–Claude Analysis · Ship-Ready Companion (v1)

**Version:** 1.0 — COMPANION (not locked source · operational SSOT for next ships)  
**sequence_id:** SA-2026-06-05-POST-CLAUDE-SHIP-READY  
**Scope:** Full session after **Claude AI / Claude chat** trigger — **both** layers kept  
**Note:** Claude = **trigger** (external critic). **Cursor agent** = research, insights, lessons, knowledge library, D5 ship, hub, shadow gate — **not discarded**. Not “cloud analysis.”  
**Synthesis attachment:** `archive/attachments/wtm/CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md`  
**Authority:** Subordinate to `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` · `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md`  
**Machine mirror:** `scripts/system_roadmap.py` → `ship_ready` · `implementation_hardening` · `roadmap_attachments`  
**Hub:** Sina Command → **Knowledge Library** tab · **World Target Model** tab  
**Knowledge field:** `knowledge-library/fields/pre-llm-world-model/`  
**Updated:** 2026-06-05  

---

## 0. Two layers — both kept (founder law)

| Layer | Source | What it contributed |
|-------|--------|---------------------|
| **A — Trigger** | Claude AI / Claude chat | Gate modes, `model_dispatch` choke, D15.1/D15.2, 90-day hardened order |
| **B — Synthesis** | Cursor HQ agent | Golden research, lessons, knowledge library, essay/book, D5 ship, hub tab, shadow wire |

**Do not collapse B into A.** “Post-Claude” = timeline after trigger, not “only Claude counted.”

---

## 0b. One picture (four layers)

```text
LAYER 1 — HUB UI     Council Room → Essentials → Knowledge Library / WTM → Agent hub
LAYER 2 — ROUTER     SINA_GOVERNANCE_ENTRY_LOCKED_v1.md
LAYER 3 — MACHINE    system_roadmap.py · command-data.json · APIs
LAYER 4 — FILES      Locked root · archive/attachments · knowledge-library/
```

**New agent start:** Council Room → Essentials read chain (first 5) → Knowledge Library → your Agent hub page.

---

## 1. The real lesson (Claude analysis)

| Misread | Truth |
|---------|-------|
| Founder didn't think enough | **System** does not force structured context before every hub model call |
| 4/10 = broken | **4/10 = spine strong, pre-LLM ~25%** (D1–D4 shipped) |
| Need more diagnosis | Need **one choke point in code** — `model_dispatch.py` |

**Gap today:** `agent_loop._planner_chat` → OpenRouter **without** `validate_packet()`.

**Target:** Task → D4→D5→D9→D10→D14→D15 assemble → `validate_packet()` → **only then** → model.

---

## 2. Everything logged (inventory — do not lose)

### 2.1 Attachments (`archive/attachments/wtm/`)

| File | Role |
|------|------|
| `CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md` | **Layer A** — Claude trigger · gate modes · D15.1/D15.2 |
| `CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md` | **Layer B** — agent insights · research · ships · code inventory |
| `GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md` | **Layer B** — industry refs · golden pipeline |
| `SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md` | **Layer B** — append-only lessons · active threads |

### 2.2 Knowledge library (`knowledge-library/`)

| Stage | pre-llm-world-model path |
|-------|--------------------------|
| Index | `KNOWLEDGE_LIBRARY_INDEX.md` · `PIPELINE_LAW.md` |
| Extract | `01-extracts/MANIFEST.md` |
| Gather | `02-gathered/GATHER_v1_GATE_RESEARCH.md` |
| Merge | `03-merged/MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md` |
| Unify | `04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md` |
| Book | `05-books/BOOK_OUTLINE_v1.md` |
| Ship plan | `04-unified/SHIP_PLAN_D5_AND_GATE_v1.md` |

### 2.3 Machine SSOT

| Artifact | Path |
|----------|------|
| Roadmap payload | `scripts/system_roadmap.py` |
| Packet schema | `scripts/pre_llm/context_packet/schema.py` |
| Gate shadow | `scripts/model_dispatch.py` |
| D5 module | `scripts/pre_llm/vector_retrieval/` |
| Cursor skill | `~/.cursor/skills/sina-research-lessons/SKILL.md` |

### 2.4 Hub surfaces

| Tab | Shows |
|-----|-------|
| **Knowledge Library** | Fields, pipeline, essay, ship plan, doc links |
| **World Target Model** | D-steps, attachments, hardening, gate modes |
| **Essentials** | Read chain includes this companion |

---

## 3. Golden pipeline (industry + WTM — one line)

```text
INTENT → RETRIEVE → RANK → PLAN → COMPRESS → ASSEMBLE → VALIDATE → MODEL
 D4      D5,D7      D9     D10    D14        D15        gate      D15.1
```

**Law:** The model is an executor on a compiled world model. **No compilation, no call.**

---

## 4. Three gate modes (implementation policy)

| Mode | Behavior | When |
|------|----------|------|
| **OFF** | Models as today | Until D5 PASS |
| **SHADOW** | Assemble + log `gate_eligible`; model still runs | D5 + partial D9/D10 |
| **ENFORCE** | Block hub OpenRouter if not gate-eligible | D14 + D15 PASS |

**Wire order:** agent_loop planner → live agents → advisor. **Do not gate** Cursor executing agent (Month 3 scope).

---

## 5. All recommendations (checklist — implement in order)

### Done or in progress

- [x] Claude analyst attachment + WTM `roadmap_attachments`
- [x] Golden research report + industry URL table
- [x] Agent lessons file + research skill
- [x] Knowledge library pipeline (extract→book)
- [x] First unified essay + book outline
- [x] Hub Knowledge Library tab
- [x] This ship-ready companion doc
- [x] `model_dispatch.py` SHADOW stub + log `~/.sina/gate_shadow_v1.jsonl`
- [x] **D5 scaffold** — local index, API, validator (rule-based retrieval first)

### D5 shipped (2026-06-05)

- [x] `validate-vector-retrieval-v1.sh` PASS (457 chunks)
- [x] `packet.retrieval` hydrates from D5 in `schema.py`
- [x] `GET /api/vector-retrieval-v1`
- [x] `model_dispatch.py` shadow + `agent_loop` planner wired
- [x] Hub **Knowledge Library** tab
- [ ] Hub packet readiness % on Agent loop (D15.2 partial)
- [ ] Add `retrieval` to conditional `GATE_REQUIRED_SECTIONS` when semantic path active

### Ship next (D6+)

### Month 2 (D7–D10 rule-based)

- [ ] D7 query templates from D4 goal_class
- [ ] D8 graph walk on D3 edges
- [ ] D9 ranking: intent + graph distance + recency (no LLM)
- [ ] D10 plan graph from D4 decomposition
- [ ] Shadow: log gate % every agent-loop start

### Month 3 (D14–D15 + enforce)

- [ ] D14 compression + `compressed_context.narrative`
- [ ] D15 `assemble_packet(task_id)`
- [ ] Wire `model_dispatch` into `agent_loop._planner_chat`
- [ ] `validate-model-gate-enforced-v1.sh`
- [ ] Golden set `~/.sina/golden/pre_llm_v1/`

### Hygiene (parallel — not blocking D5)

- [ ] Remove debug instrumentation from hub `app.js` (optional)
- [ ] Install Cursor from Applications (not installer DMG) — Mac lag
- [ ] Chat Unify extracts → manifest rows in library extract stage

---

## 6. What NOT to do (locked reject list)

- Refactor execution spine A1–A4
- Replace D1–D16 IDs with external critic list
- Big-bang ENFORCE before D15
- Ollama as default embed path
- Gate Cursor executor on day one
- One null blob — keep field purity in `knowledge-library/fields/`

---

## 7. Active threads (never drop)

| Thread | Focus |
|--------|-------|
| **WTM-D5** | Vector retrieval + shadow gate — **SHIP NOW** |
| THREAD-FACTORY | P0 RunReceipt — parallel |
| THREAD-MERGEPACK | Product lane |
| THREAD-CHAT-CONSOLIDATION | Chat Unify → L2/L3 |

---

## 8. D5 ship receipt (same playbook as D4)

| Deliverable | SSOT / API / Gate |
|-------------|-------------------|
| Index | `~/.sina/vector_index_v1.json` |
| API | `GET /api/vector-retrieval-v1?text=...` |
| Validator | `validate-vector-retrieval-v1.sh` |
| Packet wire | `packet.retrieval.chunks` from D5 |
| Rule | Local token retrieval first — one embed path later if needed |

Detail: `knowledge-library/fields/pre-llm-world-model/04-unified/SHIP_PLAN_D5_AND_GATE_v1.md`

---

## 9. Founder-visible success

| Before | After enforce |
|--------|----------------|
| Big OpenRouter prompt | “Packet N% ready” + one page context |
| 4/10 maturity | 7/10 — think-before-act forced |
| “Did we think?” | “Did system assemble and validate?” |

---

## 10. Next three moves (execute now)

1. **D6** — Memory + Logs + Git read bridge (current strategic step)  
2. **D7–D10** — rule-based rank + plan (shadow gate logging)  
3. **D14–D15 + ENFORCE** — planner gate law  

**Refresh hub** → **Knowledge Library** + **World Target Model** to see ship checklist.
