# sa-0957 — World-model agent OS patterns vs Sina D-layer stack

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No new D-modules**

## Factory today (disk truth)

| Phase | Status | SSOT |
|-------|--------|------|
| **A** Execution spine | ✅ DONE | D1–D4 legacy spine |
| **B** Intelligence OS | ✅ FROZEN | C1–C6 learning-after-action |
| **C** Runtime stack | 🔄 Active | B4 verify → router |
| **D** Pre-LLM world model | 🔄 **D1 ✅ · D2 active** | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` |

**Gate artifact:** `llm_context_packet_v1.json` (D15 + D16) — LLM is last step, not the brain.

## Compare matrix — industry agent OS vs Sina D-layer

| Industry pattern | Representative | Sina D-layer mapping | Fit | Gap |
|------------------|----------------|----------------------|-----|-----|
| **Substrate / store** | Zylos, Google ADK long memory | `~/.sina/*` · D1 graphs · D6 git bridge · D16 merge | **High** | D2 fusion SSOT in progress |
| **Projection / packet** | ContextOS, Cursor context compile | D15 Context Assembly · `validate-llm-context-packet-v1.sh` | **High** | Packet ships; upstream L2/L3 thin |
| **Compiler pipeline** | intent → retrieve → rank → plan | D4 → D7 → D5/D6 → D9 → D10 | **Designed** | **D4 Intent missing** · D7 partial |
| **Graph + RAG** | GraphRAG, Mem0, Neo4j agents | D2 fusion · D3 deps · D8 reasoning | **Partial** | Code graph ≠ execution tool graph |
| **Agent runtime loop** | LangGraph, AutoGPT, CrewAI | Phase C orchestrator + Worker broker | **Different layer** | Runtime built; world model lags |
| **Autonomous SWE** | Devin, SWE-agent | Worker + receipts + `eval_1b` gate | **Governance moat** | No honest closeout in external runtimes |
| **Eval / gate before LLM** | RAGAS CI, model routers | Eval-1b · `model_dispatch` ENFORCE | **Unique** | Industry rarely binds dispatch to behavioral proof |

## D-layer stack (canonical — what we compare against)

```text
USER → D4 Intent → D1 Code → D2 Fusion → D3 Deps
  → D5 Retrieve + D6 Git + D7 Query expand
  → D8 Reason → D9 Rank → D10 Plan
  → D11 Route → D12 Validate → D13 Diff
  → D14 Budget → D15 Assemble → D16 Memory merge
  → LLM packet → LLM → Execution spine (Phase A)
```

## Verdict (research)

| Question | Answer |
|----------|--------|
| Is Sina behind industry agent OS? | **On runtime/governance: ahead.** On pre-LLM depth (L2/L3): **behind** best WTM agents. |
| Same architecture shape? | **Yes** — substrate / compiler / projection / gate matches ADK + ContextOS synthesis. |
| Copy external runtime? | **No** — broker + receipt + Eval-1b is the moat; borrow **retrieval + intent** patterns only. |
| Next build (not this sa) | D2 fusion close · D4 intent scaffold · deepen D5/D9 — ASF order only. |

**ACT shipped:** compare note only — no D-module diff.

**One-line:** Industry agent OS and Sina share the **packet-before-LLM** shape; Sina's edge is **governed factory + eval gate**, not another LangGraph clone.
