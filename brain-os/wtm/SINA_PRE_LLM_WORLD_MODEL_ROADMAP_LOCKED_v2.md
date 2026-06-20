# Pre-LLM World Model — Reality Alignment & Locked Roadmap

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0 — LOCKED  
**Supersedes:** `archive/superseded/wtm/v1/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v1.md`  
**sequence_id:** SA-2026-06-05-PRE-LLM-ROADMAP-v2  
**Hub phase:** **D** (Pre-LLM World Model) · steps **A1.1–A5.3**  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  
**Master map:** `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`  
**Big picture:** `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md`  
**Companions:** `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` (Phase B · done) · `SINA_RUNTIME_STACK_LOCKED_v1.md` (Phase C · B4 active)  

**Phase law:** Hub phase **D** = this doc. Step IDs keep **A** prefix (A1.1, not renamed to D1.1).


---

## 1. Reality alignment (read this first)

Two different systems are often conflated. They are **not** the same product.

### What you built — Target System A: **Execution OS (post-action learning)**

```text
Execution Spine
  → Memory Writeback (execution_memory.jsonl)
  → Pattern Engine v1
  → Decision Memory v1
  → Feedback Loop v1
  → Planner Upgrade v1
  → Context Intelligence v1
  → Self-Optimization v1 (suggestions only — no auto-execute)
```

**Plus Runtime Stack (Phase 2 — in progress):**

```text
Tool Graph Engine v1        ✅ DONE
Tool Graph Verification v1  ✅ DONE
Execution Router v1         ✅ DONE
Autonomous Repair Loop v1   ⬜ NEXT
Semantic Context Fabric     ⬜ NOT STARTED
Multi-Step Execution Planner⬜ NOT STARTED
Runtime Orchestrator        ⬜ NOT STARTED
```

This stack answers: **“What happened? What worked? What should we prefer next time?”**

### What the target blueprint is — Target System B: **Pre-LLM world model (pre-action understanding)**

```text
User signals → Intent → Workspace state → Code intelligence (AST)
  → Dependency graph → Memory + Git → Vector retrieval
  → Graph reasoning → Ranking → Planning → Tool routing
  → Validation → Compression → Context assembly → LLM packet → LLM
```

This stack answers: **“What does the repo mean? What is the user trying to do? What context should the LLM see before it reasons?”**

---

## 2. Core gap (single truth)

| Dimension | Built today | Target system |
|-----------|-------------|---------------|
| **When learning happens** | After execution | Before execution |
| **Primary substrate** | Run receipts, patterns, decisions | AST, symbols, graphs, embeddings |
| **Planning basis** | Historical outcomes + influence signals | Repo understanding + intent + semantic retrieval |
| **LLM role** | Adjacent planner consumer | Final reasoning step on a pre-built world model |

**Single truth:**

> You have built a **learning system after action**.  
> The target is an **understanding system before action**.

Neither replaces the other. The Execution OS is real and shippable. The Pre-LLM world model is the missing foundation for repo-native, intent-first intelligence.

---

## 3. Full comparison: target layers vs current state

| Layer | Target pre-LLM system | Current state | Gap severity |
|-------|-------------------------|---------------|--------------|
| **L0** User signals | Keystrokes, CLI, editor events | 🔄 Partial (hub touch SSOT — L0-full editor telemetry open) | High |
| **L1** Workspace state | Active buffers, session state | 🔄 Partial (hub snapshot, bowl) | Medium |
| **L2** Intent engine | Classify goal **before** execution | ❌ Missing | **Critical** |
| **L3** Code intelligence | AST, symbol graph, cross-file index | ❌ Missing | **Critical** |
| **L4** Dependency graph | File graph, call graph, module graph, impact | 🔄 Partial (tool graph only — execution tools, not code) | **Critical** |
| **L5** Change history | Git diff lineage, change impact | ❌ Missing | High |
| **L6** Execution signals | Logs, errors, tests | 🔄 Done backend-only (`execution_memory.jsonl`) | Medium — not wired pre-LLM |
| **L7** Memory system | Unified long/short memory | 🔄 Fragmented JSONL/JSON SSOT files | High |
| **L8** Vector retrieval | Embeddings, semantic search, AST-aware chunking | ❌ Missing (pgvector deferred) | **Critical** |
| **L9** Graph reasoning | Impact tracing, root-cause graph | ❌ Missing | High |
| **L10** Ranking system | Relevance scoring **pre-LLM** | 🔄 Partial (`planner_upgrade` — post-exec bias) | High |
| **L11** Planning engine | Task decomposition **before** execution | 🔄 Partial (`tool_graph` — tool order, not semantic plan) | High |
| **L12** Tool router | Capability-based selection, policy | 🔄 Partial (hub actions + spine routing) | Medium |
| **L13** Validation layer | Dry-run, compile sim, safety gates | 🔄 Partial (`tool_graph_verification` — graph only) | Medium |
| **L14** Diff intelligence | Semantic diff, change impact | ❌ Missing | High |
| **L15** Compression engine | Token budget, summarization hierarchy | ❌ Missing | Medium |
| **L16** Context assembly | Final LLM packet builder | ❌ Missing | **Critical** |

**Legend:** ✅ Done · 🔄 Partial · ❌ Missing

**L0-full gap note (sa-0625):** `user_signals_v1.json` hub-touch MVP is shipped (`pre_llm/user_signals/`). Full editor open_files / keystroke telemetry (`L0-full`) remains **partial** — hub workspace POST only; Cursor editor extension not wired.

---

## 4. Honest score — where you actually are

### Built and validated (Execution + Runtime substrate)

| System | Status | SSOT / code |
|--------|--------|-------------|
| Execution Spine | ✅ DONE | `scripts/execution_spine/` · `~/.sina/execution-queue.db` |
| Post-execution intelligence (Steps 1–6) | ✅ DONE | `scripts/execution_intelligence/` |
| Context snapshot | ✅ DONE | `~/.sina/context_intelligence_v1.json` |
| Self-optimization (observe only) | ✅ DONE | `~/.sina/self_optimization_v1.json` |
| Tool graph (execution path) | ✅ DONE | `scripts/runtime/tool_graph/` · `~/.sina/tool_graph_v1.json` |
| Tool graph verification | ✅ DONE | `scripts/runtime/tool_graph_verification/` · `~/.sina/tool_graph_verified_v1.json` |

### Not built (Pre-LLM world model)

| System | Status |
|--------|--------|
| Pre-LLM intelligence pipeline (L0–L16) | ❌ NOT BUILT |
| Code understanding engine (AST / symbols) | ❌ NOT BUILT |
| Semantic retrieval (embeddings) | ❌ NOT BUILT |
| Intent inference before execution | ❌ NOT BUILT |
| LLM context packet assembly | ❌ NOT BUILT |

**You are here:**

```text
Execution OS (post-LLM world)     ✅ SHIPPED
  Memory → Patterns → Decisions → Feedback → Planner → Context → Self-optimization

Pre-LLM intelligence system       ❌ NOT STARTED (except weak partials in L1, L6, L11–L13)
  Repo understanding BEFORE decision
  Intent BEFORE execution
  Graph BEFORE reasoning
```

---

## 5. Strategic conclusion

### Key insight

The Execution Intelligence Stack is a **closed, auditable post-action brain**. It improves strategy from receipts. It does **not** understand the codebase before the first tool runs.

The target system treats the **LLM as the last step**, not the brain:

```text
World model (code + graph + memory + retrieval + ranking + plan)
  → compressed, ranked context packet
  → LLM (final reasoning only)
```

### What not to do

- Do **not** add more post-execution intelligence modules — stack is **complete and locked**.
- Do **not** pretend tool graph = code dependency graph — they solve different problems.
- Do **not** bypass the spine for execution state.
- Do **not** auto-execute optimization recommendations or verified graphs without founder confirm (law).

### What to do next

Build **upward from code understanding**, not outward from more execution analytics.

---

## 6. Locked build order — Pre-LLM world model

Build **sequentially**. Do not skip phases. Do not parallel-jump across foundations.

---

### Phase 1 — Core missing foundation (CRITICAL)

| Step | Layer | Goal | Gate |
|------|-------|------|------|
| **1** | **Code Intelligence v1** | AST parse, symbol index, function/class registry, import/export graph, repo map | `validate-code-intelligence-v1.sh` PASS |
| **2** | **Dependency Graph Engine v1** | File graph, call graph, module relationships, change-impact edges (code-native, not tool-only) | `validate-dependency-graph-v1.sh` PASS |
| **3** | **Intent Inference Engine v1** | Classify user goal before execution; ambiguity detection; goal decomposition tree | `validate-intent-engine-v1.sh` PASS |

**Rule:** Without Code Intelligence (Step 1), nothing above L3 can be correct.

---

### Phase 2 — Semantic understanding

| Step | Layer | Goal | Gate |
|------|-------|------|------|
| **4** | **Vector Retrieval Engine v1** | Embeddings (code + logs + text); similarity search; AST-aware chunking | Retrieval smoke PASS |
| **5** | **Graph Reasoning Engine v1** | Dependency traversal; root-cause tracing; impact simulation | Graph reasoning smoke PASS |

**Infra note:** pgvector / paid embedding APIs deferred per no-credit-card rule — local embeddings or file-backed index first.

**Embedding API deferral (sa-0620):** Real OpenRouter-paid / cloud embeddings are **out of scope** for `phase-s6-wtm-pre-llm`. They are deferred exclusively to **`phase-s9-research-models`** (`REGISTRY.json` id `phase-s9-research-models`). Pre-s6 L8 uses hash-local / file-backed index only (`scripts/pre_llm/vector_retrieval/embedding_provider.py`); no live OpenRouter calls on healthy Worker packs.

---

### Phase 3 — Pre-LLM decision system

| Step | Layer | Goal | Gate |
|------|-------|------|------|
| **6** | **Context Ranking System v1** | Relevance scoring, intent alignment, noise filtering (**pre-LLM**, not post-exec planner) | Ranking smoke PASS |
| **7** | **Planning Engine v1 (semantic)** | Task decomposition before execution; execution plan graph; fallback plans | Plan graph smoke PASS |

---

### Phase 4 — Execution preparation

| Step | Layer | Goal | Gate |
|------|-------|------|------|
| **8** | **Tool Router v1 (upgrade)** | Capability-based selection; permission constraints; cost estimation | Router policy smoke PASS |
| **9** | **Validation Layer v1 (full)** | Dry-run execution; compile simulation; full safety constraints | Extends `tool_graph_verification` + code checks |

**Relationship to Runtime Stack:** Steps 8–9 **upgrade** existing runtime verification; they do not replace Execution Spine.

---

### Phase 5 — Final context system

| Step | Layer | Goal | Gate |
|------|-------|------|------|
| **10** | **Diff Intelligence Engine v1** | Semantic diff; change impact estimation | Diff smoke PASS |
| **11** | **Context Compression Engine v1** | Token budget manager; summarization hierarchy | Budget smoke PASS |
| **12** | **Context Assembly Engine v1** | Build LLM packet; merge + rank + prune; structured prompt output | End-to-end context packet PASS |

**Final output artifact (target):** `~/.sina/llm_context_packet_v1.json` (name TBD at implementation lock).

---

## 7. Target architecture (full system)

```text
USER
  ↓
L0  User signals (editor, CLI, hub actions)
  ↓
L2  Intent Engine                    ← classify goal BEFORE execution
  ↓
L1  Workspace State                  ← buffers, session, active task
  ↓
L3  Code Intelligence (AST)         ← symbols, imports, repo map
  ↓
L4  Dependency Graph                ← file / call / module / impact
  ↓
L5  Change History (git)            ← diff lineage
  ↓
L6  Execution Signals               ← execution_memory (read-only bridge)
  ↓
L7  Unified Memory                  ← long + short; single brain SSOT
  ↓
L8  Vector Retrieval                ← embeddings + semantic search
  ↓
L9  Graph Reasoning                 ← impact + root cause
  ↓
L10 Ranking System                  ← pre-LLM relevance
  ↓
L11 Planning Engine                 ← decomposition BEFORE run
  ↓
L12 Tool Router                     ← capability + policy
  ↓
L13 Validation Layer              ← dry-run + safety (graph + code)
  ↓
L14 Diff Intelligence
  ↓
L15 Compression Engine
  ↓
L16 Context Assembly                ← LLM CONTEXT PACKET
  ↓
LLM (final reasoning step only)
  ↓
Execution Spine                     ← existing OS (unchanged foundation)
  ↓
Post-execution Intelligence Stack   ← existing learning loop (read-only upstream for L6/L7)
```

**Critical truth:**

> The LLM is **not** the intelligence.  
> The LLM is the **final reasoning step on a pre-built world model**.

---

## 8. Two-stack coexistence (how they fit)

```text
┌─────────────────────────────────────────────────────────────┐
│  PRE-LLM WORLD MODEL (this roadmap — NOT BUILT)             │
│  Understand repo + intent → build context packet            │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
                            LLM
                               ↓
┌──────────────────────────────┴──────────────────────────────┐
│  EXECUTION OS (BUILT — LOCKED)                              │
│  Spine → memory → patterns → decisions → feedback →         │
│  planner → context snapshot → self-optimization             │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌──────────────────────────────┴──────────────────────────────┐
│  RUNTIME STACK (PARTIAL)                                    │
│  Tool graph ✅ · Verification ✅ · Router ✅ · Repair ⬜         │
└─────────────────────────────────────────────────────────────┘
```

**Integration rule:** Pre-LLM layers may **read** Execution OS SSOT (memory, patterns, context snapshot). They must **not** duplicate intelligence logic or modify spine/queue/worker.

---

## 9. Status dashboard

| System | Status |
|--------|--------|
| Execution Intelligence OS | ✅ **DONE** (locked) |
| Self-optimization loop v1 | ✅ **DONE** (suggestions only) |
| Context snapshot system v1 | ✅ **DONE** |
| Tool graph system v1 | ✅ **DONE** |
| Tool graph verification v1 | ✅ **DONE** |
| Runtime execution router v1 | ✅ **DONE** |
| Runtime repair loop v1 | ⬜ **NEXT** (runtime phase) |
| Pre-LLM world model (L0–L16) | ❌ **NOT BUILT** |
| Code understanding engine | ❌ **NOT BUILT** |
| Semantic retrieval system | ❌ **NOT BUILT** |
| LLM context packet assembly | ❌ **NOT BUILT** |

---

## 10. Next build (non-negotiable) — Pre-LLM track

### Priority 1 — Code Intelligence Layer v1

**Why first:** Every higher layer (dependency graph, intent, retrieval, ranking, planning, diff) depends on structured code facts — not on post-execution patterns. Without this, everything above is guess-based.

**Position in full system:**

```text
Code Intelligence Layer  ← BUILD THIS (Pre-LLM Phase 1 Step 1)
        ↓
Context Engine (future)
        ↓
Intent Engine (future)
        ↓
Planning Engine (semantic)
        ↓
Execution Router (runtime — separate locked doc)
        ↓
Tool Graph System (done)
        ↓
Execution Spine (done)
```

### v1 responsibilities

| # | Component | Deliverable |
|---|-----------|-------------|
| 1 | **Repo understanding core** | Full file tree index; module discovery; folder structure graph |
| 2 | **AST engine** | Parse code; extract functions, classes, exports, imports |
| 3 | **Symbol system** | Global symbol table; cross-file references; definition → usage map |
| 4 | **Import / dependency graph** | File-level + module-level graphs; circular dependency detection |
| 5 | **Code relation map** | Who calls what; who depends on what; change impact map |
| 6 | **Query layer** | “Where is this function used?” · “What breaks if I change this?” · “What depends on this module?” · “What is the system entry point?” |

### SSOT output schema (target)

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

**Minimum v1 deliverables:**

```text
SourceA/scripts/pre_llm/code_intelligence/
├── __init__.py
├── repo_indexer.py         # file tree + module discovery
├── ast_parser.py           # Python AST first
├── symbol_index.py         # functions, classes, cross-file refs
├── import_graph.py         # import/export + cycle detection
├── relation_map.py         # call/dependency/impact edges
├── query_layer.py          # structured queries over indexes
├── store.py                # SSOT writer
└── api.py                  # GET /api/code-intelligence-v1

~/.sina/code_intelligence_v1.json
validate-code-intelligence-v1.sh
```

**v1 scope constraints:**

- Read-only over repo filesystem — no execution spine writes
- Python AST first (SourceA + mono roots); extend later
- No LLM calls inside this layer
- No auto-edit / auto-commit

---

## 11. Forbidden until Phase 1 Step 1 is green

| Forbidden | Why |
|-----------|-----|
| New hub tabs for pre-LLM features | Surface before substrate |
| Vector DB / pgvector production dependency | Deferred; local index first |
| “Smarter planner” tweaks in post-exec stack | Wrong stack; planner upgrade is locked |
| Treating tool graph as code dependency graph | Category error |
| Autonomous execution without founder confirm | Incident law |

---

## 12. Validation commands (existing — keep green)

```bash
bash SourceA/scripts/validate-execution-spine.sh
bash SourceA/scripts/validate-execution-intelligence.sh
bash SourceA/scripts/validate-feedback-loop-v1.sh
bash SourceA/scripts/validate-planner-upgrade-v1.sh
bash SourceA/scripts/validate-context-intelligence-v1.sh
bash SourceA/scripts/validate-self-optimization-v1.sh
bash SourceA/scripts/validate-tool-graph-v1.sh
bash SourceA/scripts/validate-tool-graph-verify-v1.sh
bash SourceA/scripts/validate-execution-router-v1.sh
```

---

## 13. Document authority

| Question | Answer here |
|----------|-------------|
| What did we build? | Execution OS + partial Runtime Stack (§1, §4) |
| What is the gap? | Post-action learning vs pre-action understanding (§2) |
| What is locked and done? | `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` |
| What do we build next? | Code Intelligence v1 (§10) |
| What is the full target? | L0–L16 pre-LLM pipeline (§6, §7) |

## 14. Status check confirmation (2026-06-05)

**Verdict:** VALID · CONSISTENT · READY

| Check | Result |
|-------|--------|
| Locked strategic roadmap created | ✅ |
| Execution OS vs Pre-LLM separation | ✅ No merge |
| Dependency identification | ✅ Code Intelligence unlocks L4–L16 |
| Post-exec intelligence frozen | ✅ No new intelligence modules |
| Tool Graph Verification v1 | ✅ COMPLETE AND STABLE |
| Next-step constraints | ✅ Enforced |

### System gap (final form)

| Domain | Status |
|--------|--------|
| Execution intelligence | ✅ DONE |
| Runtime graph system | ✅ DONE |
| Verification layer | ✅ DONE |
| Learning loop | ✅ DONE |
| Pre-LLM world model | ❌ NOT BUILT |
| Code understanding (AST/symbols) | ❌ NOT BUILT |
| Semantic retrieval | ❌ NOT BUILT |
| Context assembly engine | ❌ NOT BUILT |

### Dual-track next steps (no conflict)

| Track | Doc | Next step |
|-------|-----|-----------|
| **Runtime Stack** | `SINA_RUNTIME_STACK_LOCKED_v1.md` | **Step 4: Autonomous Repair Loop v1** — recovery suggestions (no auto-execute) |
| **Pre-LLM World Model** | this file §10 | **Phase 1 Step 1: Code Intelligence v1** — AST, symbols, repo graph (foundation) |

**Strategic priority for repo-native intelligence:** Code Intelligence v1 first.  
**Runtime continuity:** Execution Router v1 can proceed in parallel only if it remains read-only and does not block Code Intelligence staffing.

---

**This file is LOCKED.** Changes require maintainer review and version bump (`v1.2+`).
