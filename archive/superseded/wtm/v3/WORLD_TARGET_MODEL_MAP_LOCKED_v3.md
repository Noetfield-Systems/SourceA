# World Target Model Map (Locked)

**Saved:** 2026-06-05T11:43:19Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 3.0 — LOCKED  
**Supersedes:** `archive/superseded/wtm/v2/WORLD_TARGET_MODEL_MAP_LOCKED_v2.md`  
**Session:** 2026-06-05 — alignment law v3 sub-step insert  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  
**Payload:** `system_roadmap` v3.0 · `phase_order: ["A","B","C","D"]`  
**Separation law:** `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md`  
**Alignment law:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` (Orders 7–12 applied)  
**Architecture visual:** `WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md`  

**Companions:** `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md`, `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md`, `SINA_RUNTIME_STACK_LOCKED_v1.md`, `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md`

---

## Phase letters vs step IDs (read first)

| Hub phase | Title | Step ID prefix (stable) | Example |
|-----------|--------|-------------------------|---------|
| **A** | Execution Spine | `D` | D1–D4 ✅ |
| **B** | Execution Intelligence OS | `C` | C1–C6 ✅ frozen |
| **C** | Runtime Stack | `B` | B4 ● now |
| **D** | Pre-LLM World Model | `A` | A1.1 ● now |

Founder UI always shows phases **A → B → C → D**. Step IDs are artifact names — never rename casually.

---

## 1. Reality alignment

| System | Question | Status |
|--------|----------|--------|
| **Execution OS** (Phase A+B) | What happened? What worked? | ✅ Shipped + frozen |
| **Runtime Stack** (Phase C) | Safe plan → verify → route → repair? | 🔄 B4 active |
| **Pre-LLM World Model** (Phase D) | Repo meaning before LLM? | ❌ A1.1 next |

**Core gap:** Learning **after** action ✅ · Understanding **before** action ❌

---

## 2. L0–L16 gap table

(Same as v2 — hub renders live from `layer_comparison` in payload.)

---

## 3. Locked build order — 16 steps (Phase D)

Matches hub **Future** column and `STRATEGIC_BUILD_PHASES` in payload v3.0.

**Sub-steps** (alignment law §7.3) — convinced ChatGPT extras placed as children, not new top-level list.

| # | Step ID | Layer | Gate | Notes |
|---|---------|-------|------|-------|
| 1 | **A1.1** | Code Intelligence Layer v1 | `validate-code-intelligence-v1.sh` | **BUILD NOW** |
| 1.1 | A1.1.1 | Graph Fusion Layer v1 | `validate-graph-fusion-v1.sh` | After A1.1 |
| 2 | A1.2 | Dependency Graph Engine v1 | `validate-dependency-graph-v1.sh` | |
| 3 | A1.3 | Intent Inference Engine v1 | `validate-intent-engine-v1.sh` | |
| 4 | A2.1 | Vector Retrieval Engine v1 | retrieval smoke | |
| 4.1 | A2.1.1 | Memory + Logs + Git read bridge v1 | `validate-memory-git-bridge-v1.sh` | After A2.1 |
| 4b | A2.1b | Query Expansion Layer v1 | `validate-query-expansion-v1.sh` | Before A2.2 |
| 5 | A2.2 | Graph Reasoning Engine v1 | graph reasoning smoke | |
| 6 | A3.1 | Context Ranking System v1 | ranking smoke | |
| 7 | A3.2 | Planning Engine v1 (semantic) | plan graph smoke | |
| 8 | A4.1 | Tool Router v1 (upgrade) | router policy smoke | |
| 9 | A4.2 | Validation Layer v1 (full) | full validation smoke | |
| 10 | A5.1 | Diff Intelligence Engine v1 | diff smoke | |
| 11 | A5.2 | Context Compression Engine v1 | budget smoke | |
| 12 | A5.3 | Context Assembly Engine v1 | `llm_context_packet_v1.json` | |
| 12.1 | A5.3.1 | Memory merge into context packet v1 | `validate-packet-memory-merge-v1.sh` | After A5.3 |

**You are here:** Phase B frozen → Phase C step **B4** → Phase D step **A1.1**

**Then queue (Phase D):** A1.1.1 → A1.2 → A1.3 → A2.1 → A2.1.1 → A2.1b → A2.2 → …

---

## 4. Architecture pipeline vs build steps

The **◎ Live map** blueprint shows the full target pipeline (zones, state machine).  
Not every pipeline box is a separate gated build step — **v3 promotes four convinced extras to sub-steps.**

**Law:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` — complete rule order: compare → keep → attach → convince → place → sub-step → vN+1 upgrade.

| Pipeline zone (architecture) | Build step home (v3) |
|-----------------------------|----------------------|
| Graph Fusion Layer | **A1.1.1** (after A1.1) |
| Memory + Logs + Git | **A2.1.1** (retrieval feed) + **A5.3.1** (packet merge) |
| Query Expansion | **A2.1b** (before A2.2) |
| Retrieval Orchestrator | Inside **A2.1 + A2.1b + A2.2** |
| Context Budget Manager | Inside **A5.2** Compression |

**Worked example (not canonical):**  
`archive/attachments/examples/wtm/CHATGPT_13STEP_WTM_REVIEW_EXAMPLE_LOCKED_v1.md` — Orders 7–12 applied → this map v3.

---

## 5. Target architecture (summary)

See `WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md` for locked visual.

```text
USER → Intent → Workspace → Code Intelligence → Graph Fusion (A1.1.1)
  → Memory/Git (A2.1.1) → Vector Retrieval → Query Expansion (A2.1b)
  → Graph Reasoning → Ranking → Context Budget → Planning
  → Tool Router → Validation → Compression → Context Assembly
  → Memory merge (A5.3.1) → LLM CONTEXT PACKET → LLM
```

States: `INIT → INTENT_PARSED → CONTEXT_LOADED → GRAPH_BUILT → RETRIEVAL_DONE → RANKED → COMPRESSED → PACKET_READY`

---

## 6. Next move (non-negotiable)

### Strategic track (Phase D)

**A1.1 — Code Intelligence Layer v1** ← build this first

- AST parser · symbol index · import/export graph · query API  
- Output: `~/.sina/code_intelligence_v1.json`  
- Gate: `validate-code-intelligence-v1.sh`

**Immediately after A1.1 ships:** **A1.1.1 — Graph Fusion Layer v1**

### Runtime parallel (Phase C)

**B4 — Autonomous Repair Loop v1** (active alongside A1.1)

Detail: `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md` §10

---

## 7. Archive

Superseded v2: `archive/superseded/wtm/v2/` · manifest: `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md`
