# World Target Model — Architecture Diagram (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** LOCKED — founder-facing target system architecture.  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap&view=diagram`  
**Payload field:** `world_target_map.architecture_blueprint`  
**Updated:** 2026-06-05

---

## 1. One-line summary (human)

> **User intent → unified world model → guided retrieval → budgeted context → structured packet → LLM.**

The LLM is the **last** step. Everything before it is the real intelligence.

---

## 2. Five zones (how to read the diagram)

| Zone | Name | Plain English |
|------|------|----------------|
| **1** | Input | What you want — intent and live workspace |
| **2** | World Model | What the system knows about the repo + runtime |
| **3** | Retrieve & Reason | Find and score the right evidence |
| **4** | Decide & Validate | Plan, route tools, check safety — under a token budget |
| **5** | Output | Compress, assemble, packet — then LLM |

Flow is **left → right** on desktop, **top → bottom** on mobile. Arrows mean: *output of this stage feeds the next*.

---

## 3. Full pipeline (canonical order)

```text
USER
  ↓
Intent Engine
  ↓
Workspace State
  ↓
Code Intelligence (AST + Symbols)
  ↓
Graph Fusion Layer          ★ unified AST + call + import + execution + error graph
  ↓
Memory + Logs + Git
  ↓
Vector Retrieval
  ↓
Retrieval Orchestrator      ★ hybrid symbol + semantic + graph retrieval
  ↓
Graph Reasoning
  ↓
Ranking System
  ↓
Context Budget Manager      ★ token allocation per subsystem
  ↓
Planning Engine
  ↓
Tool Router
  ↓
Validation Layer
  ↓
Compression Engine
  ↓
Context Assembly Engine     ★ merge + rank + prune → structured packet
  ↓
LLM CONTEXT PACKET
  ↓
LLM
```

★ = **critical gap layer** (not optional for a real pre-LLM brain)

---

## 4. Pipeline state machine (runtime)

Not a linear script — the system moves through states:

```text
INIT
  → INTENT_PARSED
  → CONTEXT_LOADED
  → GRAPH_BUILT
  → RETRIEVAL_DONE
  → RANKED
  → COMPRESSED
  → PACKET_READY
```

---

## 5. Four design laws

1. **Graph-first** — not file-first  
2. **Multi-source retrieval** — not vector-only  
3. **Budget-controlled context** — not compress-only  
4. **State-driven pipeline** — not a dumb linear script  

---

## 6. Critical truth

**The LLM is NOT the intelligence.**  
The LLM is the **final reasoning step on a pre-built world model.**

---

## 7. Next architecture build

After **A1.1 Code Intelligence** ships:

**Graph Fusion Layer v1** — single source of truth for AST + call + import + execution + error relationships.

---

## 8. Lock rules

1. Hub **◎ Live map** must render this blueprint from payload — not hard-coded drift.  
2. UI may polish visuals only; **zone order, node order, and names** must match this doc.  
3. Do not remove critical (★) layers from the founder diagram.  
4. Agent commentary (ChatGPT reviews, misconception tables) **never** replaces this diagram in the hub.

---

*End of locked architecture diagram v1.*
