# Sina World Target Model — Full Blueprint (for external review)

**Purpose:** Paste this into ChatGPT to review alignment, gaps, and build order.  
**Source:** Canonical hub payload `system_roadmap` **v4.0** · `scripts/system_roadmap.py`  
**Map:** `WORLD_TARGET_MODEL_MAP_LOCKED_v4.md`  
**Date:** 2026-06-05  
**Hub:** World Target Model tab · phases **A → B → C → D**

---

## Instructions for ChatGPT

Please review this blueprint and answer:

1. Is the **phase order** logical (spine → post-exec intel → runtime → pre-LLM)?
2. Are any **critical layers missing** before LLM?
3. Is **parallel build** (C4 runtime + D1 strategic) sensible?
4. Any **duplicate work** between Phase B/C and Phase D?
5. Suggest improvements **without replacing step IDs** — we use phase-aligned IDs (A1, B1, C1, D1).

---

## Naming law (v4 — locked)

**Step ID prefix = Hub phase letter. Never mixed.**

| Phase | Title | Step IDs | Count |
|-------|--------|----------|-------|
| **A** | Execution Spine | A1–A4 | 4 |
| **B** | Execution Intelligence OS | B1–B6 | 6 |
| **C** | Runtime Stack | C1–C7 | 7 |
| **D** | Pre-LLM World Model | D1–D16 | 16 |
| | **TOTAL** | | **33 steps** |

---

## Big picture (one sentence)

We built a **learning-after-action** system (Phases A–B); we are finishing **safe runtime** (Phase C); we are building an **understanding-before-action** world model (Phase D) that outputs a structured **LLM context packet** — the LLM is the last reasoning step only.

---

## Core gap

| Have today | Missing (target) |
|------------|------------------|
| Execute → observe → store → learn → improve | Understand repo + intent + semantics **before** execution |
| Post-exec patterns, decisions, feedback | Pre-exec code graph, retrieval, ranking, planning |
| Tool graph + verify + route (runtime) | Full pre-LLM packet (`llm_context_packet_v1.json`) |

**Current nature:** reactive learning · **Target nature:** proactive understanding

---

## Target pipeline (architecture)

```text
USER
  → Intent (D4)
  → Workspace state
  → Code intelligence (D1) → Graph fusion (D2)
  → Memory/Git bridge (D6) + Vector retrieval (D5) + Query expansion (D7)
  → Graph reasoning (D8)
  → Context ranking (D9) → Planning (D10)
  → Tool router (D11) → Validation (D12)
  → Diff (D13) → Compression (D14) → Assembly (D15) → Memory merge (D16)
  → LLM CONTEXT PACKET
  → LLM (reasoning only)
```

**Runtime track (parallel, Phase C):** verified tool graph → route → repair → fabric → planner → orchestrator → spine dispatch (founder confirm, no auto-execute).

---

## Where we are NOW

| Track | Step | Title | Phase |
|-------|------|-------|-------|
| **Runtime (primary)** | **C4** | Autonomous Repair Loop v1 | C |
| **Strategic (parallel)** | **D1** | Code Intelligence Layer v1 | D |

**Then queue (Phase D):** D2 → D3 → D4 → D5 → D6 → D7 → D8 → … → D16  
**Runtime ahead:** C5 → C6 → C7

---

# PHASE A — Execution Spine ✅ DONE

**Question answered:** *What ran? What was recorded?*  
**Status:** Shipped · **Steps:** A1–A4

| ID | Title | Short detail | Gate / artifact |
|----|--------|--------------|-----------------|
| **A1** | Execution queue | Single durable SQLite queue — all spine tasks, no lost runs | `~/.sina/execution-queue.db` |
| **A2** | Worker + executor | Worker loop runs queued tasks, PASS/FAIL, artifact paths | `scripts/execution_spine/` · `validate-execution-spine.sh` |
| **A3** | Memory writeback | Append-only `execution_memory.jsonl` — every run recorded | `execution_memory.jsonl` |
| **A4** | Execution artifact store | Per-run folders for logs/outputs under `~/.sina/execution-artifacts/` | `execution-artifacts/` |

**Unlocks:** Foundation for all intelligence + runtime layers.

---

# PHASE B — Execution Intelligence OS ✅ FROZEN

**Question answered:** *What happened? What worked? What should we prefer next?*  
**Status:** Complete, frozen — no new post-exec intel modules  
**Steps:** B1–B6 (the original “6 intelligence steps”)

| ID | Title | Short detail | Gate / artifact |
|----|--------|--------------|-----------------|
| **B1** | Pattern Extraction Engine v1 | Success/failure/repeat-error patterns from execution history | `execution_patterns_v1.json` |
| **B2** | Decision Memory v1 | WHY layer — cause → effect → fix mapping | `execution_decisions_v1.jsonl` |
| **B3** | Feedback Loop v1 | Patterns + decisions → influence signals for planning | `execution_feedback_signals.jsonl` |
| **B4** | Planner Upgrade v1 | History-aware ranked next-action recommendations | `planner_context_v1.json` |
| **B5** | Context Intelligence v1 | Unified `matters_now` snapshot for agents | `context_intelligence_v1.json` · `/api/execution-context` |
| **B6** | Self-Optimization v1 | Observe → suggest optimizations — never auto-execute | `self_optimization_v1.json` |

**Unlocks:** Runtime stack reads this SSOT; Phase D pre-LLM track opens.

---

# PHASE C — Runtime Stack 🔄 IN PROGRESS

**Question answered:** *How do we safely plan, verify, route, and repair before spine dispatch?*  
**Status:** C1–C3 done · **C4 active** · C5–C7 ahead  
**Steps:** C1–C7

| ID | Title | Short detail | Status | Gate / artifact |
|----|--------|--------------|--------|-----------------|
| **C1** | Tool Graph Engine v1 | Task + goal → ordered tool dependency graph | ✅ done | `tool_graph_v1.json` · `/api/tool-graph-v1` |
| **C2** | Tool Graph Verification v1 | Cycle/deps/safety scoring — block unsafe graphs | ✅ done | `tool_graph_verified_v1.json` |
| **C3** | Execution Router v1 | Verified graph → next_step instruction only (no auto-exec) | ✅ done | `execution_router_v1.json` |
| **C4** | Autonomous Repair Loop v1 | Failure → recovery suggestions, links patterns/decisions | **● NOW** | `repair_loop_v1.json` |
| **C5** | Semantic Context Fabric v1 | Bridge runtime ↔ pre-LLM context without merging tracks | ahead | — |
| **C6** | Multi-Step Execution Planner v1 | Multi-step runtime plans from verified graphs | ahead | — |
| **C7** | Runtime Orchestrator v1 | Full orchestration: graph → verify → route → repair → spine | ahead | — |

**Unlocks:** End-to-end safe dispatch chain; feeds Phase D but does not replace it.

---

# PHASE D — Pre-LLM World Model ❌ NOT BUILT

**Question answered:** *What does the repo mean? What is the goal? What context does the LLM need?*  
**Status:** Not started · **D1 next** (parallel with C4)  
**Steps:** D1–D16 · **Output gate:** `llm_context_packet_v1.json`

### D-group 1 — Core foundation (D1–D4)

| ID | Title | Short detail | Gate |
|----|--------|--------------|------|
| **D1** | Code Intelligence Layer v1 | AST, symbols, import graph — repo map before LLM | `validate-code-intelligence-v1.sh` · `code_intelligence_v1.json` |
| **D2** | Graph Fusion Layer v1 | Fuse AST + call + import + error edges into one code graph | `validate-graph-fusion-v1.sh` |
| **D3** | Dependency Graph Engine v1 | File/call/module graphs + impact simulation (not tool graph) | `validate-dependency-graph-v1.sh` |
| **D4** | Intent Inference Engine v1 | Classify user goal BEFORE execution — ambiguity + goal tree | `validate-intent-engine-v1.sh` |

### D-group 2 — Semantic understanding (D5–D8)

| ID | Title | Short detail | Gate |
|----|--------|--------------|------|
| **D5** | Vector Retrieval Engine v1 | Embeddings + AST-aware chunking, local index first | retrieval smoke |
| **D6** | Memory + Logs + Git bridge v1 | Read-only: execution_memory + git lineage into retrieval | `validate-memory-git-bridge-v1.sh` |
| **D7** | Query Expansion Layer v1 | Intent→queries, symbol expansion, multi-query generation | `validate-query-expansion-v1.sh` |
| **D8** | Graph Reasoning Engine v1 | Root-cause tracing, dependency traversal, impact simulation | graph reasoning smoke |

### D-group 3 — Pre-LLM decision system (D9–D10)

| ID | Title | Short detail | Gate |
|----|--------|--------------|------|
| **D9** | Context Ranking System v1 | Relevance + intent alignment + noise filter before LLM | ranking smoke |
| **D10** | Planning Engine v1 (semantic) | Task decomposition BEFORE execution — plan graph | plan graph smoke |

### D-group 4 — Execution preparation (D11–D12)

| ID | Title | Short detail | Gate |
|----|--------|--------------|------|
| **D11** | Tool Router v1 (upgrade) | Capability routing, permissions, cost estimation | router policy smoke |
| **D12** | Validation Layer v1 (full) | Dry-run, compile sim, full code+graph safety | full validation smoke |

### D-group 5 — Final context system (D13–D16)

| ID | Title | Short detail | Gate |
|----|--------|--------------|------|
| **D13** | Diff Intelligence Engine v1 | Semantic diff + change impact before LLM sees code | diff smoke |
| **D14** | Context Compression Engine v1 | Token budget manager + summarization hierarchy | budget smoke |
| **D15** | Context Assembly Engine v1 | Merge + rank + prune → structured LLM packet | `llm_context_packet_v1.json` |
| **D16** | Memory merge into packet v1 | Merge long/short memory + git + logs into final packet | `validate-packet-memory-merge-v1.sh` |

---

## LLM packet schema (final output)

| Field | Meaning |
|-------|---------|
| intent | Classified user goal |
| files | Relevant file set |
| symbols | Functions/classes in scope |
| errors | Active errors + traces |
| dependencies | Impact + call edges |
| plan | Pre-execution step graph |
| constraints | Safety + policy limits |
| tools | Selected capabilities |
| compressed_context | Token-budgeted narrative |

---

## What is NOT this roadmap

| Track | Where |
|-------|--------|
| RunReceipt / MergePack products | Today tab · THREAD-FACTORY |
| Factory / investor roadmaps | Roadmaps & goals tab |
| Personal DB Layer A | personal-db tab |

---

## Status summary

| Domain | Status |
|--------|--------|
| Phase A — Spine | ✅ 4/4 |
| Phase B — Intelligence | ✅ 6/6 frozen |
| Phase C — Runtime | 🔄 3/7 done · **C4 now** |
| Phase D — Pre-LLM | ❌ 0/16 · **D1 next** |
| Code understanding engine | ❌ start **D1** |
| LLM context packet | ❌ end state **D15–D16** |

---

## Historical note (for reviewers)

Older docs used mismatched step IDs (e.g. spine as `D1`, pre-LLM as `A1.1`). **v4 aligned all IDs to phase letters.** Migration table: `WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md`.

---

**END OF BLUEPRINT — ready for ChatGPT review**
