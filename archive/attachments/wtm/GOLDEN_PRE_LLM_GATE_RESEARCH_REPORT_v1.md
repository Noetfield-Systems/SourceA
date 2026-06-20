# RESEARCH REPORT — Golden pre-LLM gate · Best-of-worlds (v1)

**Saved:** 2026-06-06T18:42:41Z · **Retrofit:** doc-datetime-law batch retrofit
**Type:** STAGING ATTACHMENT — **Cursor agent** research synthesis (external refs + internal WTM map)  
**Status:** Attached · **Layer B** — complements Claude trigger attachment (Layer A)  
**Synthesis inventory:** `CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md`  
**Query:** “No model call until intent, retrieval, ranking, and plan are assembled and validated.”  
**Analyzed:** 2026-06-05  
**Lessons file:** `SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md`  
**Parent law:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md`  

---

## 1. Executive verdict

Production systems do **not** let the LLM be the brain. They treat the model as a **reasoning executor** on a **compiled context artifact** built by named transforms with validators. Sina’s WTM (D4→D5→D9→D10→D14→D15) matches this pattern. The missing piece is **mechanical enforcement** at one OpenRouter choke point — not more diagnosis or founder thinking.

---

## 2. Golden pipeline (industry consensus)

```text
TASK
  → INTENT (classify + decompose)           [D4]
  → RETRIEVE (hybrid + declarative plan)    [D5, D7]
  → RANK (cross-encoder / graph scores)     [D9]
  → PLAN (task graph)                       [D10]
  → COMPRESS (plan-aware, budgeted)         [D14]
  → ASSEMBLE (versioned packet)             [D15]
  → VALIDATE (schema + gate_eligible)       [validate_packet]
  → MODEL (only if gate passes)             [model_dispatch]
```

---

## 3. Reference table (reliable sources)

| Source | URL | Golden idea for Sina |
|--------|-----|----------------------|
| Anthropic — Context engineering for agents | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Context = managed state across turns; curate don't dump |
| ContextOS — Context packs | https://contextosai.com/blog/context-packs-in-practice | Pack = contract upstream of prompt; evaluation gates block release |
| AmtocSoft — Context packets | https://amtocsoft.blogspot.com/2026/05/context-packets-for-production-agents.html | Fail before model if no evidence; replay envelope for audits |
| MDP — Context engineering | https://mdpgroup.com/en/blog/how-does-context-engineering-affect-llm-systems/ | Declarative retrieval plans (YAML): dense + sparse, fuse, cap |
| GenAI Patterns — Retrieval refinement | https://www.genaipatterns.dev/patterns/rag/retrieval-refinement | Retrieve broad → rerank → compress → then LLM |
| ThynkQ — Production RAG | https://thynkq.com/writing/rag-pipeline-production-architecture | Six stages with P50 budgets; grounding check optional |
| Nic Chin — 12-component RAG | https://nicchin.com/blog/rag-architecture-production | Hybrid + rerank = largest recall jump (61% → 96.8%) |
| Stripe Systems — Production RAG | https://www.stripesys.com/blog/production-rag-pipelines | Quality = chunking + retrieval + rerank, not LLM choice |
| PAACE — Plan-aware compression | https://arxiv.org/abs/2512.16970 | Compress conditioned on **upcoming plan steps** (D14 after D10) |
| Context Kubernetes (arXiv) | https://arxiv.org/html/2604.11623v1 | Intent router + permission filter + token budget |
| LangGraph — Interrupts | https://docs.langchain.com/oss/python/langgraph/interrupts | Pause before critical/expensive step = gate analog |
| RAGAS + CircleCI | https://circleci.com/blog/automated-rag-pipeline-evaluation-and--with-ragas/ | CI gate on faithfulness/recall — matches validator culture |
| Harness engineering 2026 | https://www.aimagicx.com/blog/harness-engineering-replacing-prompt-engineering-2026 | Harness around model > prompt engineering |
| swarm-planner | https://github.com/Gabrielasu/swarm-planner | Self-contained task packets — contracts inlined per task |

---

## 4. Three ideas that repeat across strongest references

| Idea | Who says it | Why it matters for Sina |
|------|-------------|-------------------------|
| Packet = contract, not prompt | ContextOS Context Packs, AmtocSoft context packets | Matches `llm_context_packet_v1.json` — model is downstream of assembly |
| Fail before model if evidence missing | AmtocSoft: “If there is no evidence, the builder fails before the model call” | Same as `validate_packet()` — must live in `model_dispatch`, not docs |
| Declarative retrieval plans | MDP context engineering | YAML/JSON plan: dense + sparse, fuse, cap — maps to D5 + D7 |
| Retrieve → rerank → compress → validate | GenAI Patterns, ThynkQ production RAG | D5→D9→D14 chain; order is industry-standard |
| Plan-aware compression | PAACE (arXiv 2512.16970) | D14 after D10, not from raw chat |
| Evaluation gates in CI | RAGAS + CircleCI, Inductivee continuous eval | Extend `validate-*.sh` culture to retrieval/plan golden sets |
| Interrupt before expensive step | LangGraph interrupts, Pondero HITL | `model_dispatch` = interrupt node before OpenRouter |

**Anthropic framing:** context is managed state across turns — not a bigger prompt. Substrate (`~/.sina/*`) + per-task projection (packet) matches exactly.

---

## 5. Map to Sina roadmap (no new D17)

| Industry stage | Sina step | Ship note |
|----------------|-----------|-----------|
| Intent routing | D4 | **Done** |
| Vector + chunk index | D5 | **Shipped** — `~/.sina/vector_index_v1` · 457 chunks · validator PASS |
| Memory + logs + git | D6 | **Current** strategic step |
| Query templates | D7 | Intent class → retrieval plan JSON |
| Graph reasoning | D8 | Walk D3 call edges |
| Rerank evidence | D9 | Rule-based first (intent + graph distance + symbol overlap) |
| Plan graph | D10 | D4 decomposition → D3 dependency-ordered nodes |
| Token budget | D14 | Deterministic narrative of ranked evidence |
| Packet compiler | D15 | `assemble_packet(task_id)` |
| Gate choke | D15.1 | `model_dispatch.py` — **SHADOW shipped** · ENFORCE at D15 |
| Hub visibility | D15.2 | Packet readiness % + replay envelope |

---

## 6. Today vs target (code truth)

**Today:**

- D1–D4 hydrate into partial packet (`hydrate_from_disk_substrate`)
- `validate_packet()` exists; empty stub correctly returns `gate_eligible: false`
- `agent_loop._planner_chat` → OpenRouter **with** `model_dispatch` in SHADOW (logs, does not block yet)

**Target (Month 3 law):**

```text
task → D4 intent → D5 retrieval → D9 rank → D10 plan → D14 compress → D15 assemble
     → validate_packet(strict_gate=True) → model_dispatch → OpenRouter
```

Same shape as Context Kubernetes (intent router + permission filter + token budget) and Harness Engineering (validate input before model call).

---

## 7. Golden suggestions → roadmap (7 items)

### 7.1 Compiler + Gate (ContextOS pattern)

Treat D15 as **compiler**, not a feature:

| Stage | Step | Compiler output |
|-------|------|-----------------|
| Intent | D4 | `packet.intent` |
| Evidence | D5, D6, D7 | `packet.retrieval` |
| Salience | D9 | `packet.ranking` |
| Action graph | D10 | `packet.plan` |
| Budget | D14 | `packet.compression` + `compressed_context` |
| Manifest | D15 | `provenance` + `gate_eligible` |

**Action:** D15 = assembler; D15.1 = `model_dispatch.py` — only hub OpenRouter entry.

### 7.2 Declarative retrieval plan (D5 + D7) — highest ROI after D4

Standard production stack:

- **Hybrid retrieve** — dense (D5 vector) + sparse/BM25 (symbols, file paths)
- **Fuse** — Reciprocal Rank Fusion (RRF), parameter-light default
- **Rerank** — top 20–50 → cross-encoder or rule-based graph scores (D9 starts rule-based)
- **Cap** — per-corpus limits + token budget

**D5 shipped:** SSOT `~/.sina/vector_index_v1`, AST-aware chunks, API + validator. **Next:** retrieval plan JSON per task (intent-driven), golden queries recall@5.

### 7.3 Rule-based rank + plan first (Claude trigger + this synthesis — correct)

- **D9:** graph distance (D3), symbol overlap (D1), intent match (D4) — no LLM
- **D10:** dependency-ordered task graph from D3 + D4 decomposition — no LLM
- Optional LLM polish only after SHADOW proves rule-based packets stable

**Action:** Month 2 = D7–D10 rule-based; gate stays SHADOW.

### 7.4 Two-layer validation

| Layer | When | What | Artifact |
|-------|------|------|----------|
| Structural | Before every hub model call | `validate_packet()` — sections populated | `gate_eligible` |
| Quality | CI / nightly | Golden tasks — retrieval recall, plan completeness | `validate-pre-llm-golden-v1.sh` (proposed) |

Refs: RAGAS faithfulness/context recall; ThinkWithOps — CI blocks PR if faithfulness < 0.85.

**Action:** Golden set `~/.sina/golden/pre_llm_v1/` — 10–20 repo tasks with expected ranked files + plan nodes. Run in shadow before ENFORCE.

### 7.5 Schema gap: `retrieval` in gate

Locked doc (`LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` §3) requires `retrieval.chunks` when semantic path active. `GATE_REQUIRED_SECTIONS` in `schema.py` still omits `retrieval`.

**Fix (open):** Add `retrieval` conditionally — required if `intent.goal_class` needs semantic search; populate check `len(retrieval.chunks) >= 1` for code-edit intents.

### 7.6 Three gate modes (industry-aligned)

| Mode | Industry analog | Sina behavior |
|------|-----------------|---------------|
| OFF | Legacy, no harness | Pre-D5 |
| SHADOW | LangSmith trace + log-only gate | Assemble + log missing; model runs — **current** |
| ENFORCE | AmtocSoft fail-before-call; LangGraph `interrupt_before` | Block OpenRouter if not `gate_eligible` |

**Action:** D15.1 shadow on planner — **done**. ENFORCE after D14+D15.

### 7.7 Replay envelope (audit gold)

Every blocked or allowed model call logs:

```json
{
  "packet_id": "...",
  "task_id": "...",
  "readiness_score": 0.67,
  "gate_eligible": false,
  "missing_for_gate": ["retrieval", "ranking", "plan"],
  "producer_steps": ["D1", "D2", "D3", "D4"],
  "retrieval_query_id": "...",
  "policy_version": "governance-v1",
  "trace_id": "..."
}
```

Ref: AmtocSoft replay envelope. **Action:** D15.2 hub UI + shadow log `~/.sina/gate_shadow_v1.jsonl`.

---

## 8. Hardened build order (90-day)

| Phase | Ship | Gate mode | Receipt |
|-------|------|-----------|---------|
| Month 1 | D5 + D15.1 shadow | OFF → SHADOW | `validate-vector-retrieval-v1.sh` **PASS** |
| Month 2 | D7 + D9/D10 rule-based | SHADOW | D9/D10 validators + golden recall |
| Month 3 | D14 + D15 + ENFORCE planner | ENFORCE | `validate-model-gate-enforced-v1.sh` |

**Do not gate:** Cursor executing agent (execution spine) — tool execution separate from approval nodes (LangGraph pattern).

---

## 9. Top 5 golden ideas (roadmap thinking)

1. **Harness > prompt** — AI Magicx harness engineering: wrap the model; don't enlarge the prompt.
2. **Retrieval plan is code** — MDP declarative YAML plans: diffable, testable, auditable — fits validator culture.
3. **Plan before compress** — PAACE: D14 runs after D10, not before.
4. **Golden-set CI gate** — RAGAS in CI: structural gate for runtime, quality gate for releases.
5. **Minimum sufficient context** — AgentSwarm context packets: scoped packet per call, forbidden context explicit, output schema enforced.

---

## 10. Two-layer validation (summary)

| Layer | When | Tool |
|-------|------|------|
| **Structural** | Every hub model call | `validate_packet()` → `gate_eligible` |
| **Quality** | CI / nightly | Golden tasks + recall@5 + plan completeness (`validate-pre-llm-golden-v1.sh` — proposed) |

---

## 11. Schema fix (open — D5 shipped, gate conditional pending)

Locked doc requires `retrieval.chunks` for gate when semantic path active. `schema.py` `GATE_REQUIRED_SECTIONS` omits `retrieval` today. **Add conditional retrieval gate** — see §7.5.

---

## 12. Placement (alignment law)

| Item | Parent | ID |
|------|--------|-----|
| Golden research synthesis | WTM | attachment only (this file) |
| Lessons persistence | WTM | `SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md` |
| Agent research skill | Cursor | `sina-research-lessons` skill |

No change to D1–D16 IDs. Convinced implementation unchanged from Claude analyst attachment.

---

## 13. Founder one-liner

> **The model is an executor on a compiled world model. No compilation, no call.**

Backed by ContextOS, AmtocSoft, Anthropic, LangGraph, and production RAG — fits locked D1–D16 without renumbering.

---

## 14. Next execution

1. ~~D5~~ — **DONE**  
2. ~~D15.1 shadow on planner~~ — **DONE**  
3. **D6** — memory + logs + git read bridge  
4. D7–D10 rule-based → golden set → ENFORCE planner  

---

## 15. Extended reference table (this research turn)

| Source | URL | Golden idea |
|--------|-----|-------------|
| ThinkWithOps — CI faithfulness gate | https://thinkwithops.com/ | Block release if faithfulness < threshold |
| Inductivee — continuous eval | https://www.inductive.ai/ | Ongoing retrieval/plan quality monitoring |
| Niraj Kumar — RAG guide 2026 | https://nirajkumar.ai/ | Separate indexing vs query paths |
| AgentSwarm — context packets | https://agentswarm.ai/ | Minimum sufficient context per call |
| Pondero — production HITL | https://pondero.ai/ | Human-in-loop analog to SHADOW mode |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-05 | v1 initial |
| 2026-06-05 | Expanded — 7 golden suggestions, replay envelope, top 5 ideas, today vs target, D5/D15.1 ship status |
