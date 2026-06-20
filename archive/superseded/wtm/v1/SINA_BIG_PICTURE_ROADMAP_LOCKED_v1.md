> **SUPERSEDED** — archived 2026-06-05. Canonical: v2 at SourceA root. See `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md`.

# Sina System — Big Picture Roadmap (Locked)

**Saved:** 2026-06-05T11:03:12Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-BIG-PICTURE-ROADMAP  
**Locked:** 2026-06-05  
**Authority:** ASF / Sina Command maintainer  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  

**World Target Model companion** — phase overview for the major upgrade session. Master map: `WORLD_TARGET_MODEL_MAP_LOCKED_v1.md`. Law: `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md`. **Not** the Roadmaps & goals tab (factory / investor / products).

**Detail docs (WTM companions, not separate roadmaps):**
- `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` — post-execution intelligence (**DONE**)
- `SINA_RUNTIME_STACK_LOCKED_v1.md` — runtime graph → verify → route (**Steps 1–3 DONE**)
- `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v1.md` — pre-LLM L0–L16 (**NOT BUILT**)

---

## 0. One-page truth

You are building **two systems**. They must **never merge**.

| System | Question it answers | Status |
|--------|---------------------|--------|
| **Execution OS** | What happened? What worked? What should we prefer next time? | ✅ **SHIPPED** |
| **Runtime Stack** | How do we turn a plan into a safe, ordered execution stream? | 🔄 **PARTIAL** (Steps 1–3 done) |
| **Pre-LLM World Model** | What does the repo mean? What is the goal? What context does the LLM need **before** reasoning? | ❌ **NOT BUILT** |

**Core gap (single truth):**

> You have a **learning system after action**.  
> You do **not** yet have an **understanding system before action**.

**Critical truth:**

> The LLM is **not** the intelligence.  
> The LLM is the **final reasoning step on a pre-built world model**.

---

## 0.5 Major system upgrade (World Target Model) — origin & boundaries

**Trigger:** Founder declared **major upgrade today** (2026-06-05 session), then pasted ChatGPT's analysis. **Everything in that message — including Layer 1 Execution Runtime / spine — is this system roadmap.** It is **not** RunReceipt.

**ChatGPT alignment:**
- **Diagnosis accepted:** Brain+UI+Rules without living execution + memory fabric + closed loop.
- **Layer 1–3 = this upgrade:** Runtime (Phase D) → Memory/learning (Phase C) → Closed loop (Phase B) → Pre-LLM world model (Phase A).
- **"RunReceipt system" in ChatGPT Layer 1:** Echoed a **partial assistant mistake** — not founder intent. Spine = `execution_spine` + artifact store only.

**This upgrade track (Phases D→C→B→A):**

| Built in session (chronology) | Locked phase |
|-------------------------------|--------------|
| Execution Spine (SQLite queue — not Redis/Docker) | Phase D |
| Pattern → Decision → Feedback → Planner → Context → Self-Optimization | Phase C (frozen) |
| Intelligence v2 (predictive, read-only) | Supplemental — not a locked C step |
| Tool Graph → Verification → Router | Phase B (B4 Repair next) |
| Locked Pre-LLM roadmap docs | Phase A (not started) |

**NOT part of this upgrade:**

| Lane | Where it lives |
|------|----------------|
| **RunReceipt** product ship | Factory P0 · `today` tab · THREAD-FACTORY |
| **MergePack** product ship | Evidence Factory · parallel product lane |
| **Personal DB / Layer A** | Constitution + knowledge ingest — separate |
| **ChatGPT Redis/NATS/Docker spine** | Rejected prescription — we built SQLite spine |

**D4 clarification:** Execution **artifact store** (`~/.sina/execution-artifacts/`) is spine infrastructure — **not** the RunReceipt product SKU.

**Hub live map:** `http://127.0.0.1:13020/?tab=system-roadmap`

---

## 1. Full system architecture (target end state)

```text
USER
  ↓
┌─────────────────────────────────────────────────────────────┐
│  PRE-LLM WORLD MODEL (NOT BUILT — Phases A1–A5 below)       │
│  Intent → Workspace → Code Intel → Dep Graph → Git/Memory   │
│  → Vector Retrieval → Graph Reasoning → Ranking → Planning  │
│  → Tool Router → Validation → Diff → Compression            │
│  → CONTEXT ASSEMBLY → LLM CONTEXT PACKET                    │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
                         LLM (reasoning only)
                               ↓
┌──────────────────────────────┴──────────────────────────────┐
│  RUNTIME STACK (PARTIAL — Phase B below)                    │
│  Tool Graph → Verification → Router → Repair → Orchestrator │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
                    (founder confirm — no auto-execute)
                               ↓
┌──────────────────────────────┴──────────────────────────────┐
│  EXECUTION SPINE (DONE — DO NOT MODIFY)                     │
│  queue → worker → runner → artifact store → execution_memory │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌──────────────────────────────┴──────────────────────────────┐
│  EXECUTION INTELLIGENCE OS (DONE — FROZEN)                  │
│  Patterns → Decisions → Feedback → Planner → Context      │
│  → Self-Optimization (suggestions only)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Phase map — all tracks

```text
PHASE A — PRE-LLM WORLD MODEL     ❌ NOT STARTED (strategic foundation)
PHASE B — RUNTIME STACK           🔄 IN PROGRESS (Steps 1–3 ✅)
PHASE C — EXECUTION INTELLIGENCE  ✅ COMPLETE (frozen)
PHASE D — EXECUTION SPINE         ✅ COMPLETE (foundation)
```

---

# PHASE D — EXECUTION SPINE ✅ DONE

**Purpose:** Runtime execution substrate. Single source of execution truth.

| Component | Status | Artifact |
|-----------|--------|----------|
| Execution queue | ✅ | `~/.sina/execution-queue.db` |
| Worker | ✅ | `scripts/execution_spine/` |
| Memory writeback | ✅ | `~/.sina/execution_memory.jsonl` |
| Execution artifact store | ✅ | `~/.sina/execution-artifacts/` (spine — not RunReceipt product) |

**Rule:** Nothing above may bypass the spine for execution state.

---

# PHASE C — EXECUTION INTELLIGENCE OS ✅ DONE (FROZEN)

**Purpose:** Post-execution learning — patterns, why, signals, planner influence, context snapshot, optimization suggestions.

**Locked sequence (do not reorder, do not extend):**

| Step | Layer | Status | SSOT |
|------|-------|--------|------|
| C1 | Pattern Extraction Engine v1 | ✅ | `execution_patterns_v1.json` |
| C2 | Decision Memory v1 | ✅ | `execution_decisions_v1.jsonl` |
| C3 | Feedback Loop v1 | ✅ | `execution_feedback_signals.jsonl` |
| C4 | Planner Upgrade v1 | ✅ | `planner_context_v1.json` |
| C5 | Context Intelligence v1 | ✅ | `context_intelligence_v1.json` |
| C6 | Self-Optimization v1 | ✅ | `self_optimization_v1.json` |

**Forbidden:** New post-execution intelligence modules. Read-only consumption by upper layers only.

---

# PHASE B — RUNTIME STACK 🔄 IN PROGRESS

**Purpose:** Transform `brain → recommendation` into `brain → action → verification → dispatch instruction → (confirm) → execution → repair`.

**Does NOT:** Plan semantically, execute autonomously, or duplicate intelligence logic.

| Step | Layer | Status | SSOT / API |
|------|-------|--------|------------|
| B1 | Tool Graph Engine v1 | ✅ **DONE** | `tool_graph_v1.json` · `/api/tool-graph-v1` |
| B2 | Tool Graph Verification v1 | ✅ **DONE** | `tool_graph_verified_v1.json` · `/api/tool-graph-verify-v1` |
| B3 | Execution Router v1 | ✅ **DONE** | `execution_router_v1.json` · `/api/execution-router-v1` |
| B4 | Autonomous Repair Loop v1 | ⬜ **NEXT** | Failure → recovery suggestions (no auto-execute) |
| B5 | Semantic Context Fabric v1 | ⬜ NOT STARTED | Bridge runtime ↔ pre-LLM context |
| B6 | Multi-Step Execution Planner v1 | ⬜ NOT STARTED | Multi-step runtime plans |
| B7 | Runtime Orchestrator v1 | ⬜ NOT STARTED | Coordinated runtime control |

**B1→B3 flow:**

```text
task + goal
  → dependency mapper → graph builder → execution path
  → tool_graph_v1.json
  → cycle/dependency/context/safety scoring
  → tool_graph_verified_v1.json
  → policy + priority → next_step instruction only
  → execution_router_v1.json
  → founder confirm → Execution Spine
```

---

# PHASE A — PRE-LLM WORLD MODEL ❌ NOT BUILT

**Purpose:** Repo understanding **before** execution. Build world model → LLM packet → then LLM.

**Observe → measure → compare → improve strategy** lives in Phase C (post-exec).  
**Understand → rank → plan → validate → assemble context** lives in Phase A (pre-exec).

## A — Layer gap table (target L0–L16 vs today)

| Layer | Target capability | Today | Gap |
|-------|-------------------|-------|-----|
| **L0** | User signals (keystrokes, CLI, editor) | ❌ | Missing |
| **L1** | Workspace state (buffers, session) | 🔄 Partial | Weak |
| **L2** | Intent engine (goal **before** run) | ❌ | **Critical** |
| **L3** | Code intelligence (AST, symbols) | ❌ | **Critical** |
| **L4** | Dependency graph (file/call/module) | 🔄 Tool graph only | **Critical** |
| **L5** | Change history (git lineage) | ❌ | High |
| **L6** | Execution signals (logs/errors/tests) | 🔄 `execution_memory` backend | Not wired pre-LLM |
| **L7** | Unified memory (long + short) | 🔄 Fragmented JSONL | High |
| **L8** | Vector retrieval (embeddings) | ❌ | **Critical** |
| **L9** | Graph reasoning (impact/root cause) | ❌ | High |
| **L10** | Ranking (pre-LLM relevance) | 🔄 Post-exec planner bias | High |
| **L11** | Planning (decomposition **before** run) | 🔄 Tool order only | High |
| **L12** | Tool router (capability + policy) | 🔄 Hub + spine partial | Medium |
| **L13** | Validation (dry-run, safety) | 🔄 Graph verify partial | Medium |
| **L14** | Diff intelligence | ❌ | High |
| **L15** | Compression (token budget) | ❌ | Medium |
| **L16** | Context assembly (LLM packet) | ❌ | **Critical** |

---

## A — Locked build order (12 steps, 5 sub-phases)

Build **sequentially**. No skipping. No parallel jumps across foundations.

### Sub-phase A1 — Core foundation (CRITICAL)

| Step | Build | Deliverable | Gate |
|------|-------|-------------|------|
| **A1.1** | **Code Intelligence Layer v1** | AST, symbol index, import graph, repo map, query layer | `validate-code-intelligence-v1.sh` |
| **A1.2** | **Dependency Graph Engine v1** | File graph, call graph, module graph, impact edges | `validate-dependency-graph-v1.sh` |
| **A1.3** | **Intent Inference Engine v1** | Goal classification, ambiguity, decomposition tree | `validate-intent-engine-v1.sh` |

**Rule:** A1.1 is non-negotiable first. Without AST/symbols, everything above is guess-based.

**A1.1 output schema:**

```json
{
  "repo_graph": {},
  "symbol_index": {},
  "ast_index": {},
  "dependency_graph": {},
  "call_graph": {},
  "impact_map": {}
}
```

**A1.1 must answer:**
- Where is this function used?
- What breaks if I change this?
- What depends on this module?
- What is the system entry point?

---

### Sub-phase A2 — Semantic understanding

| Step | Build | Deliverable | Gate |
|------|-------|-------------|------|
| **A2.1** | **Vector Retrieval Engine v1** | Embeddings, similarity search, AST-aware chunking | Retrieval smoke PASS |
| **A2.2** | **Graph Reasoning Engine v1** | Traversal, root-cause trace, impact simulation | Graph reasoning smoke PASS |

*Infra: local/file-backed index first; pgvector deferred (no-credit-card rule).*

---

### Sub-phase A3 — Pre-LLM decision system

| Step | Build | Deliverable | Gate |
|------|-------|-------------|------|
| **A3.1** | **Context Ranking System v1** | Relevance, intent alignment, noise filter (**pre-LLM**) | Ranking smoke PASS |
| **A3.2** | **Planning Engine v1 (semantic)** | Task decomposition before execution; plan graph; fallbacks | Plan graph smoke PASS |

---

### Sub-phase A4 — Execution preparation (upgrades Runtime)

| Step | Build | Deliverable | Gate |
|------|-------|-------------|------|
| **A4.1** | **Tool Router v1 (upgrade)** | Capability selection, permissions, cost estimate | Router policy smoke PASS |
| **A4.2** | **Validation Layer v1 (full)** | Dry-run, compile sim, code + graph safety | Full validation smoke PASS |

*Extends Phase B verification — does not replace spine.*

---

### Sub-phase A5 — Final context system

| Step | Build | Deliverable | Gate |
|------|-------|-------------|------|
| **A5.1** | **Diff Intelligence Engine v1** | Semantic diff, change impact | Diff smoke PASS |
| **A5.2** | **Context Compression Engine v1** | Token budget, summarization hierarchy | Budget smoke PASS |
| **A5.3** | **Context Assembly Engine v1** | Merge + rank + prune → structured LLM packet | E2E packet PASS |

**Final artifact:** `~/.sina/llm_context_packet_v1.json`

---

# 3. Status dashboard (current truth — 2026-06-05)

| Domain | Status |
|--------|--------|
| Execution Spine | ✅ DONE |
| Execution intelligence (C1–C6) | ✅ DONE |
| Learning / self-optimization loop | ✅ DONE (suggestions only) |
| Context snapshot | ✅ DONE |
| Runtime tool graph | ✅ DONE |
| Runtime verification | ✅ DONE |
| Runtime execution router | ✅ DONE |
| Pre-LLM world model (A1–A5) | ❌ NOT BUILT |
| Code understanding (AST/symbols) | ❌ NOT BUILT |
| Semantic retrieval | ❌ NOT BUILT |
| Context assembly / LLM packet | ❌ NOT BUILT |

---

# 4. Next steps (dual track — both locked)

| Priority | Track | Step | Build |
|----------|-------|------|-------|
| **Strategic (repo intelligence)** | Phase A | **A1.1** | **Code Intelligence Layer v1** |
| **Runtime continuity** | Phase B | **B4** | **Autonomous Repair Loop v1** |

**How to choose:**
- Need **understanding before execution** → start **A1.1 Code Intelligence**
- Need **complete runtime chain before spine dispatch wiring** → start **B4 Repair Loop**

Both tracks are valid. They must not merge or duplicate logic.

---

# 5. Forbidden (all phases)

| Forbidden | Why |
|-----------|-----|
| New post-execution intelligence modules | Phase C frozen |
| Auto-execute router/optimizer/verified graph | Incident law |
| Modify spine / queue / worker from upper layers | Spine is foundation |
| Tool graph = code dependency graph | Category error |
| Hub tabs before substrate (A1.1) | Surface before understanding |
| pgvector / paid embeddings before local index | Infra rule |

---

# 6. Validation commands (keep green)

```bash
# Phase C — Intelligence
bash SourceA/scripts/validate-execution-spine.sh
bash SourceA/scripts/validate-execution-intelligence.sh
bash SourceA/scripts/validate-feedback-loop-v1.sh
bash SourceA/scripts/validate-planner-upgrade-v1.sh
bash SourceA/scripts/validate-context-intelligence-v1.sh
bash SourceA/scripts/validate-self-optimization-v1.sh

# Phase B — Runtime
bash SourceA/scripts/validate-tool-graph-v1.sh
bash SourceA/scripts/validate-tool-graph-verify-v1.sh
bash SourceA/scripts/validate-execution-router-v1.sh

# Phase A — (future)
# validate-code-intelligence-v1.sh
```

---

# 7. Document authority

| Question | Answer |
|----------|--------|
| What is the big picture? | This file |
| What is built? | Phase D + C complete; Phase B steps 1–3 complete |
| What is missing? | Phase A (pre-LLM L0–L16) |
| What is the core gap? | Learning after action vs understanding before action |
| What next (strategic)? | **A1.1 Code Intelligence v1** |
| What next (runtime)? | **B4 Autonomous Repair Loop v1** |

**This file is the master locked roadmap.** Changes require maintainer review and version bump.
