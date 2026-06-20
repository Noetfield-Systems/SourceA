# Sina Agent Lessons — Pre-LLM Gate & Research (v1)

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Type:** AGENT LESSONS — durable memory for Cursor agents (not locked source)  
**Status:** Active · append on every research session  
**Parent law:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` — lessons stage here; convinced items → attachment → sub-steps  
**Machine SSOT:** `scripts/system_roadmap.py` → `roadmap_attachments` + `implementation_hardening`  
**Related:** `CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md`, `GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md`  
**Note:** Claude AI / Claude chat = **trigger** (Layer A). This file + golden research + synthesis attachment = **Cursor agent work** (Layer B) — **both kept.**  
**Synthesis:** `CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md`  
**Updated:** 2026-06-05  

---

## Active threads (never drop these)

| Thread | ID | Goal now | WTM step |
|--------|-----|----------|----------|
| Pre-LLM world model + gate | WTM / Phase D | D13–D15 → ENFORCE planner | **D13** (current) |
| Factory P0 | THREAD-FACTORY | RunReceipt wire artifacts | Parallel — spine only |
| MergePack ship | THREAD-MERGEPACK | Product lane — not an agent | Parallel |
| Chat consolidation | THREAD-CHAT-CONSOLIDATION | Extracts → Chat Unify → L2/L3 | Feeds Super Brain |
| Execution spine | A1–A4 | Done — do not refactor | Frozen substrate |

**Agent rule:** When user sends research, tie conclusions to these threads. WTM gate thread is **primary** until D15 ENFORCE.

---

## Lesson 16 — Industry gate synthesis (2026-06-05, expanded research turn)

**Verdict:** Mantra matches production — WTM D4→D15 names the pipeline; gap = mechanical enforcement + conditional `retrieval` gate + golden-set quality layer.

**Seven convinced recommendations (filed in golden report §7):**

1. D15 = compiler; D15.1 = only hub OpenRouter door  
2. Declarative retrieval plan (D5+D7 hybrid+RRF+cap)  
3. Rule-based D9/D10 before any LLM polish  
4. Two-layer validation — structural (`validate_packet`) + quality (`validate-pre-llm-golden-v1.sh`)  
5. Conditional `retrieval` in `GATE_REQUIRED_SECTIONS`  
6. OFF → SHADOW → ENFORCE (shadow live on planner)  
7. Replay envelope in `gate_shadow_v1.jsonl` + D15.2 hub  

**Top 5 golden ideas:** harness > prompt · retrieval plan is code · plan before compress · golden-set CI · minimum sufficient context.

**Report:** `GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md` (expanded §4–§15)  
**Gather:** `knowledge-library/fields/pre-llm-world-model/02-gathered/GATHER_v2_INDUSTRY_GATE_SYNTHESIS.md`

---

## Lesson 1 — The real gap (one sentence)

**The gap is not ideas or founder thinking. It is one missing choke point in code.**

---

## Lesson 2 — Today vs target

| Today | Target |
|-------|--------|
| User / agent loop → OpenRouter directly (hub JSON + chat) | Task → D1–D15 assemble packet → `validate_packet()` → **ONLY THEN** → model |

---

## Lesson 3 — What we already have

- Strong execution spine (validators, queue, workspaces) — Phase A–C done  
- Packet law — `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md`  
- D1–D4 on disk (code, graph, deps, intent)  
- `validate_packet()` and `gate_eligible: false` by design (stub must not pass)  

---

## Lesson 4 — What we do not have yet

- `agent_loop.py` still calls chat completion with **no packet check** (verified)  
- No single `model_dispatch` gate every OpenRouter path must pass through  
- D5–D10, D14–D15 not shipped — gate cannot pass yet  

**“Make it happen”** = build pipeline in order + wire gate in one place + enforce in phases — **not** “think harder.”

---

## Lesson 5 — Industry agrees with WTM

| Pattern | Meaning for Sina |
|---------|------------------|
| Substrate vs projection | `~/.sina/*` + graphs = substrate; OpenRouter sees **one assembled packet per call** — discarded after |
| Assembly engine | D15 = **compiler**, not another feature |
| Explicit transforms + gates | D4→D5→D9→D10→D14, each validator PASS — not ad-hoc string concat |
| Stable prefix + dynamic chunks | `constraints` stable, `compressed_context` dynamic, task last |

---

## Lesson 6 — Three gate modes (implementation policy)

| Mode | Behavior | When |
|------|----------|------|
| **OFF** | Models run as now | Until D5 works |
| **SHADOW** | Build packet, log `gate_eligible`, still call model | D5 + partial D9/D10 |
| **ENFORCE** | Block model if `gate_eligible` false | D14 + D15 wired |

Do not flip a switch on day one.

---

## Lesson 7 — One architectural move

```
All tasks ──► assemble_packet() [D15]
                    │
                    ▼
              validate_packet()
                    │
         gate_eligible?
              ┌─────┴─────┐
             NO           YES
              │             │
        Hub: not ready   model_dispatch() → OpenRouter
        + missing sections
        Cursor executor still OK (spine)
```

**Gate hub planners first** (agent loop planner, Live maintainer, advisor). **Do not gate Cursor executing agent** at first.

---

## Lesson 8 — What not to do

| Don't | Do instead |
|-------|------------|
| Refactor execution spine | Add pre-LLM on top |
| Wait for all 16 steps before any gate | Shadow at D5, enforce at D15 |
| Let every agent call OpenRouter its own way | One `model_dispatch` |
| Big-bang “AI understands everything” | Rule-based D4/D9 first, LLM last |
| More hub JSON to the model | Smaller `compressed_context.narrative` |

---

## Lesson 9 — 90-day checklist (founder-visible)

**Weeks 1–4 (D5):** local vector index · API + validator PASS · `packet.retrieval` hydrates · hub packet readiness %  

**Weeks 5–8 (D7–D10):** D3 graph traversal · rule-based rank + plan · shadow log gate % on agent-loop start  

**Weeks 9–12 (D14–D15):** compression + narrative · `model_dispatch` on planner first · enforce `gate_eligible` · `validate-model-gate-enforced-v1.sh`  

**Success:** Before = big OpenRouter prompt. After = “Packet 87% ready” → one page ranked context. Maturity 4/10 → 7/10.

---

## Lesson 29 — D16 shipped (2026-06-06)

**Receipt:** `validate-packet-memory-merge-v1.sh` PASS  
**SSOT:** `~/.sina/packet_memory_merge_v1.json`  
**API:** `GET /api/packet-memory-merge-v1`  
**Wire:** D15 `assemble_packet` chains D16 writeback · `packet.memory.merge_ready`  
**Law:** D14 compress → D15 assemble → D16 writeback only — no re-rank/recompress  

---

## Lesson 28 — D15.2 shipped (2026-06-06)

**Receipt:** `validate-packet-readiness-v1.sh` PASS  
**Module:** `scripts/pre_llm/packet_readiness/hub_surface.py`  
**API:** `GET /api/packet-readiness-v1`  
**Wire:** WTM tab + Agent hub show readiness %, gate_eligible, missing sections plain-English  
**Law:** Founder sees think-before-model status on Refresh — no Terminal  

---

## Lesson 27 — D15.1 shipped (2026-06-05)

**Receipt:** `validate-model-gate-shadow-v1.sh` + `validate-model-gate-enforced-v1.sh` PASS  
**SSOT:** `~/.sina/model_dispatch_gate_v1.json`  
**API:** `GET /api/model-dispatch-gate-v1`  
**Wire:** `agent_loop._planner_chat` → `model_dispatch.dispatch_chat` (D15 assembly chain)  
**Law:** OFF/SHADOW/ENFORCE via `SINA_GATE_MODE` — enforce blocks when `gate_eligible` false  

---

## Lesson 26 — D15 shipped (2026-06-05)

**Receipt:** `validate-context-assembly-v1.sh` PASS  
**SSOT:** `~/.sina/llm_context_packet_v1.json`  
**API:** `GET /api/context-assembly-v1`  
**Wire:** `assemble_packet()` → constraints + provenance + full gate packet  
**Law:** D14 compress → D15 assemble+validate — model_dispatch uses assembly in shadow  

---

## Lesson 25 — D14 shipped (2026-06-05)

**Receipt:** `validate-context-compression-v1.sh` PASS  
**SSOT:** `~/.sina/context_compression_v1.json`  
**API:** `GET /api/context-compression-v1`  
**Wire:** `packet.compression.budget` + `packet.compressed_context.narrative` from D14  
**Law:** compress D9 ranked evidence only — no re-rank, no LLM  

---

## Lesson 24 — D13 shipped (2026-06-05)

**Receipt:** `validate-diff-intelligence-v1.sh` PASS  
**SSOT:** `~/.sina/diff_intelligence_v1.json`  
**API:** `GET /api/diff-intelligence-v1`  
**Wire:** `packet.diff.changes` + `impact_map` from D13 in hydrate  
**Law:** read-only git diff + D3 file impact — chains D12 validation before build  

---

## Lesson 23 — D12 shipped (2026-06-05)

**Receipt:** `validate-validation-layer-v1.sh` PASS  
**SSOT:** `~/.sina/validation_layer_v1.json`  
**API:** `GET /api/validation-layer-v1`  
**Wire:** `packet.validation.checks` from D12 in hydrate  
**Checks:** substrate D1–D11 · graph safety · policy · compile sim · packet dry-run  
**Milestone:** Execution prep phase (D11+D12) complete  

---

## Lesson 22 — D11 shipped (2026-06-05)

**Receipt:** `validate-tool-router-v1.sh` PASS  
**SSOT:** `~/.sina/tool_router_v1.json`  
**API:** `GET /api/tool-router-v1`  
**Wire:** `packet.tools.selection` from D11 in hydrate  
**Law:** capability + policy + cost per D10 plan step · execute blocked pre-D15 · not C3 router  

---

## Lesson 21 — D10 shipped (2026-06-05)

**Receipt:** `validate-planning-engine-v1.sh` PASS  
**SSOT:** `~/.sina/planning_engine_v1.json`  
**API:** `GET /api/planning-engine-v1`  
**Wire:** `packet.plan.graph` from D10 in hydrate  
**Law:** D10 = semantic pre-exec plan SSOT · C6 = runtime only · B4 = soft signal  
**Milestone:** Month 2 rule-based D9+D10 stack complete — shadow gate can log ranking+plan sections  

---

## Lesson 20 — D9 shipped (2026-06-05)

**Receipt:** `validate-context-ranking-v1.sh` PASS  
**SSOT:** `~/.sina/context_ranking_v1.json`  
**API:** `GET /api/context-ranking-v1`  
**Wire:** `packet.ranking.ranked_evidence` from D9 in hydrate  
**Scoring:** intent (D4) + query overlap + retrieval (D5) + graph (D8) — rule-based, no LLM  

---

## Lesson 19 — D8 shipped (2026-06-05)

**Receipt:** `validate-graph-reasoning-v1.sh` PASS  
**SSOT:** `~/.sina/graph_reasoning_v1.json`  
**API:** `GET /api/graph-reasoning-v1`  
**Wire:** `packet.reasoning.paths` from D8 in hydrate  
**Paths:** impact · root_cause · traversal on D3 graph — rule-based, no LLM  

---

## Lesson 18 — D7 shipped (2026-06-05)

**Receipt:** `validate-query-expansion-v1.sh` PASS  
**SSOT:** `~/.sina/query_expansion_v1.json`  
**API:** `GET /api/query-expansion-v1`  
**Wire:** `packet.retrieval.queries` + `retrieval_plan` from D7 in hydrate  
**Law:** rule-based only — D4 goal_class → multi-query + D1 symbol expansion + RRF plan  

---

## Lesson 17 — D6 shipped (2026-06-05)

**Receipt:** `validate-memory-git-bridge-v1.sh` PASS  
**SSOT:** `~/.sina/memory_git_bridge_v1.json`  
**API:** `GET /api/memory-git-bridge-v1`  
**Wire:** `packet.memory.slots` + retrieval feed from D6 in `schema.py` hydrate  
**Law:** read-only — B-layer truth; D6 indexes only, never overrides  

---

## Lesson 10 — Next three moves (locked recommendation)

1. ~~**Ship D5**~~ — **DONE**  
2. ~~**Ship D6**~~ — **DONE** `validate-memory-git-bridge-v1.sh` PASS  
3. ~~**Ship D7–D10**~~ — **DONE** · **Ship D14–D15** compress+assemble → ENFORCE planner gate  

## Lesson 14 — Naming correction (founder law)

**Claude ≠ Cloud.** External critic session was **Claude AI / Claude chat** (Anthropic), not a “cloud analyst.”

| Wrong | Correct |
|-------|---------|
| `CLOUD_ANALYST_*` | `CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md` |
| `SINA_POST_CLOUD_ANALYSIS_*` | `SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md` |
| “cloud analysis” | **Claude analysis** |

Old `CLOUD_*` paths are stubs pointing to Claude files.

---

## Lesson 15 — Dual lineage (founder law — do not lose agent work)

**Claude was the trigger. Cursor agent work after that is a separate layer — keep both.**

| Layer | Source | Preserve in |
|-------|--------|-------------|
| A — Trigger | Claude chat critic | `CLAUDE_ANALYST_*` |
| B — Synthesis | Cursor HQ agent | `CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_*`, golden research, this lessons file, knowledge library, D5 ship, hub |

**Never** rename or relabel in a way that drops Layer B (research, insights, recommendations, lessons, code ships).

---

## Lesson 13 — Ship-ready companion (2026-06-05)

**Doc:** `SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md`  
**Hub tab:** Knowledge Library · WTM `ship_ready` payload  
**D5:** `/api/vector-retrieval-v1` · 457 chunks · packet.retrieval hydrates  

---

## Lesson 11 — Research session 2026-06-05 (golden sources)

Best-of-worlds references captured in `GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md`:

- Context packet fail-before-call — AmtocSoft, ContextOS  
- Retrieve → rerank → compress — GenAI Patterns, ThynkQ, Nic Chin production RAG  
- Plan-aware compression — PAACE (arXiv 2512.16970)  
- CI quality gates — RAGAS, CircleCI  
- Orchestration interrupt — LangGraph `interrupt()` before expensive steps  
- Declarative retrieval plans — MDP context engineering  

**Schema gap to fix when D5 ships:** add `retrieval` to `GATE_REQUIRED_SECTIONS` when semantic path active (locked doc says yes; `schema.py` omits it today).

---

## Lesson 12 — Knowledge library (extract → book)

**Path:** `knowledge-library/fields/pre-llm-world-model/`

| Stage | File |
|-------|------|
| Extract | `01-extracts/MANIFEST.md` |
| Gather | `02-gathered/GATHER_v1_GATE_RESEARCH.md` |
| Merge | `03-merged/MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md` |
| Unify | `04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md` ← **first book page** |
| Book | `05-books/BOOK_OUTLINE_v1.md` |

**Law:** `knowledge-library/PIPELINE_LAW.md` — one field per subject; purity = pointers not copies; essay → chapter → book.

---

## Agent obligation (repeat every research turn)

When user sends **research**, **deep search**, **golden ideas**, **lessons**, or **book/essay**:

1. Run pipeline in `knowledge-library/fields/<field>/` (extract → gather → merge → unify → book)  
2. Append this lessons file  
3. Write research report under `archive/attachments/<track>/` if external refs  
4. Compare to locked source (Orders 1–6); place convinced extras as sub-steps  
5. Update `system_roadmap.py` if WTM-relevant  
6. Reply with paths — user should not repeat “write lessons” or “organize”  

Skill: `~/.cursor/skills/sina-research-lessons/SKILL.md`

---

## Lesson 17 — Blueprint × live market × 100 plans (2026-06-13)

**Verdict:** Market shifted to **runtime evidence + 30-day PoC** ($492M governance spend 2026); SourceA category is correct but **W3 outreach + W1 film + K1 receipt-on-read** are the only P0 plans — hub validator loops are anti-market.

**Today vs target:** W2 ~55% / W3 $0 /  $320M+ raised for control-plane · Target: CAD $2K deposit Week 4 per blueprint Stage 2.

**What we have / lack:** Receipt spine + tamper FAIL + SSOT v3.1 identity LOCKED · Lack: filmed demo, outreach sent, SOC2-in-progress pack, Art 12 export bundle.

**Next 3 moves:** (1) ASF send TF+NF outreach (2) Film W1 BLOCK/ALLOW/TAMPER (3) Ship K1 receipt validator on read.

**Threads:** STRATEGIC-SLICE · W1/W2/W3 · THREAD-ECOSYSTEM (not WTM — frozen).

**Files:** `knowledge-library/fields/commercial-governance/02-gathered/GATHER_v1_BLUEPRINT_MARKET_100_PLANS_2026-06-13.md` · `archive/attachments/commercial_goal_specialist/sina_os/BLUEPRINT_MARKET_100_PLANS_RESEARCH_REPORT_v1.md` (PLAN-001..100)

**Law note:** Cite `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` as authority; blueprint v2 is DRAFT inform only.

---

## Lesson 18 — Tier 1 world upgrade · 300 plans (2026-06-13)

**Verdict:** Tier 1 = **deposits × proof density × procurement unblock** at Geordie-speed — PLAN-101–300 extend foundation (001–100) with enterprise readiness, platform moat, EU/US GTM, and board metrics without thawing architecture (blueprint Part 4).

**Today vs target:** Same gap as Lesson 17 for Weeks 1–4 · Tier-1 adds SOC2 path, Receipt API, ABM scale, Art 12 named SKU — all **gated** until 3 deposits (PLAN-297).

**What we have / lack:** 300-plan library on disk · Lack: ASF FIVE-STEP lock (PLAN-300), north star dashboard (PLAN-291–296), 10-min scaffold (PLAN-201).

**Next 3 moves:** (1) ~~Lock PLAN-300 pick block on form~~ **DONE 2026-06-13** (2) Execute 11.01–11.05 P0 only (3) No PLAN-121+ until deposit gate.

**Files:** `SOURCEA_COMMERCIAL_P0_FIVE_STEP_PICK_BATCH_2026-06-13_LOCKED_v1.md` · `ASF_FIVE_STEP_PICK_BLOCK_PLAN-300_v1.txt` · `~/.sina/commercial-p0-five-step-pick-v1.json`

---

## Lesson 19 — SourceA  landscape (2026-06-15)

**Verdict:** SourceA competes at **L6 pre-execution governance**, not L3 orchestration or L0 models. Closest rivals: **Notenic, FuseGov, , AgentPEP, Predicate, Microsoft Authorization Fabric**. Noetfield lane rivals: **Securiti, , Credo AI, Purview, WitnessAI**.

**Today vs target:** Strong disk proof (`critic_boot`, validators, receipts) · weak enterprise SIEM/SaaS GTM vs funded players (Temporal $5B, WitnessAI $58M,  Gartner TRiSM).

**What we have / lack:** Constellation map + NF-RD demo script · Lack: NW1 battle card, W1 tamper FAIL film, partner story for Temporal+LangGraph under SourceA gate.

**Next 3 moves:** (1) ~~NW1 battle card~~ **DONE** `NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` (2) W1 demo film — **other repo** (3) ~~Partner integration note~~ **DONE** `SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md`

**Threads:** STRATEGIC-SLICE · NW1 · W3 · pre-LLM gate D15

**Files:** `archive/attachments/commercial/SOURCEA__LANDSCAPE_RESEARCH_REPORT_v1.md` · `NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` · `SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md` · `knowledge-library/fields/commercial-governance/02-gathered/GATHER_v2_SOURCEA__LANDSCAPE_2026-06-15.md`

