> **SUPERSEDED** — archived 2026-06-05. Canonical: v2 at SourceA root. See `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md`.

# World Target Model Map (Locked)

**Saved:** 2026-06-05T11:03:12Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**Session:** 2026-06-05 — after *we have major upgrade today*  
**Authority:** Founder blueprint — English canonical map for hub UI  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  
**Separation law:** `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md` — roadmap after major upgrade = WTM only; not Roadmaps & goals tab, factory, or products.  
**UI spec (locked):** `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` — Map / Blueprint / Live Pipeline cockpit.

**Companion chapters (same WTM upgrade, not other roadmaps):** `SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md`, `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md`, `SINA_RUNTIME_STACK_LOCKED_v1.md`, `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v1.md`

---

## 1. Reality alignment

Two systems — do not merge.

### Built (what you have)

- Execution Spine
- Post-execution Intelligence
- Patterns / Decisions / Feedback / Context snapshot
- Tool Graph + Verification (+ Router)

### Target (what the system must become)

- Pre-LLM world model
- Repo understanding **before** execution
- Intent → structured plan **before** runtime
- Semantic + graph + retrieval **before** LLM

---

## Core gap (single truth)

You have a **learning system after action**.  
The target is an **understanding system before action**.

---

## 2. Full comparison — L0–L16

| Layer | Target pre-LLM system | Your status | Gap |
|-------|----------------------|-------------|-----|
| L0 User Signals | keystrokes, CLI, editor events | missing | missing |
| L1 Workspace State | active buffers + session state | partial | weak |
| L2 Intent Engine | classify goal BEFORE execution | missing | missing |
| L3 Code Intelligence | AST + symbol graph | missing | critical missing |
| L4 Dependency Graph | call graph + module graph | partial (tool graph only) | incomplete |
| L5 Change History | git diff lineage | missing | missing |
| L6 Execution Signals | logs / errors / tests | partial (execution_memory) | backend-only |
| L7 Memory System | unified long/short memory | partial (fragmented jsonl) | no unified brain |
| L8 Vector Retrieval | embeddings + semantic search | missing | missing |
| L9 Graph Reasoning | impact / root cause graph | missing | missing |
| L10 Ranking System | relevance scoring pre-LLM | partial (planner upgrade) | post-exec bias |
| L11 Planning Engine | task decomposition BEFORE execution | partial (tool graph) | not semantic |
| L12 Tool Router | capability-based selection | partial | weak policy layer |
| L13 Validation Layer | dry-run + safety gates | partial | not full |
| L14 Diff Intelligence | semantic diff engine | missing | missing |
| L15 Compression Engine | token optimization | missing | missing |
| L16 Context Assembly | final LLM packet builder | missing | missing |

---

## 3. Honest score — where you are

**You are HERE:**

```text
Execution OS (post-action world)
  → Memory → Patterns → Decisions → Feedback → Planner → Context snapshot
```

**NOT HERE:**

```text
Pre-LLM intelligence system
  → Repo understanding BEFORE decision
  → Intent BEFORE execution
  → Graph BEFORE reasoning
```

---

## 4. Strategic conclusion

You built a **brain that learns from execution** — not a **brain that understands before execution**.

---

## 5. Correct roadmap — professional build order

### Phase 1 — Core missing foundation (CRITICAL)

1. **Code Intelligence Layer** — AST parser, symbol index, function/class registry, import/export graph  
2. **Dependency Graph Engine** — file graph, call graph, module relationships, change impact graph  
3. **Intent Inference Engine** — classify goal before execution, ambiguity detection, goal decomposition tree  

### Phase 2 — Semantic understanding

4. **Vector Retrieval Engine** — embeddings (code + logs + text), similarity search, AST-aware chunking  
5. **Graph Reasoning Engine** — dependency traversal, root cause tracing, impact simulation  

### Phase 3 — Pre-LLM decision system

6. **Context Ranking System** — relevance scoring, intent alignment, noise filtering  
7. **Planning Engine (real version)** — task decomposition before execution, execution plan graph, fallback plans  

### Phase 4 — Execution preparation

8. **Tool Router (upgrade)** — capability-based selection, permission constraints, cost estimation  
9. **Validation Layer (full)** — dry-run execution, compile simulation, safety constraints  

### Phase 5 — Final context system

10. **Diff Intelligence Engine** — semantic diff, change impact estimation  
11. **Context Compression Engine** — token budget manager, summarization hierarchy  
12. **Context Assembly Engine** — build LLM packet, merge + rank + prune, structured prompt output  

---

## 6. Final architecture (target system)

**Canonical visual (locked):** `WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md`  
**Hub render:** five zones · human descriptions · state machine · `architecture_blueprint` payload v1.0

```text
USER
  ↓
Intent Engine
  ↓
Workspace State
  ↓
Code Intelligence (AST + Symbols)
  ↓
Graph Fusion Layer          ← unified AST + call + import + execution + error graph
  ↓
Memory + Logs + Git
  ↓
Vector Retrieval
  ↓
Retrieval Orchestrator      ← hybrid symbol + semantic + graph retrieval
  ↓
Graph Reasoning
  ↓
Ranking System
  ↓
Context Budget Manager      ← token allocation per subsystem
  ↓
Planning Engine
  ↓
Tool Router
  ↓
Validation Layer
  ↓
Compression Engine
  ↓
Context Assembly Engine
  ↓
LLM CONTEXT PACKET
  ↓
LLM
```

Pipeline states: `INIT → INTENT_PARSED → CONTEXT_LOADED → GRAPH_BUILT → RETRIEVAL_DONE → RANKED → COMPRESSED → PACKET_READY`

Next build after A1.1 foundation: **Graph Fusion Layer v1**.

---

## 7. Critical truth

**The LLM is NOT the intelligence.**  
The LLM is the **final reasoning step on a pre-built world model**.

---

## 8. System status

| System | Status |
|--------|--------|
| Execution Intelligence OS | DONE |
| Tool Graph System | DONE |
| Self-optimization loop | DONE |
| Context snapshot system | DONE |
| Pre-LLM intelligence system | NOT BUILT |
| Code understanding engine | NOT BUILT |
| Semantic retrieval system | NOT BUILT |

---

## 9. Next move (non-negotiable)

**Code Intelligence Layer v1** — foundation for everything above.

- AST parsing  
- Symbol graph  
- Repo map  
- Cross-file reference index  

Roadmap step: **A1.1**
