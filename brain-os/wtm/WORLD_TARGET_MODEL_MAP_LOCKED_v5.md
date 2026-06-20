# World Target Model Map — FINAL (Locked)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 5.2 — LOCKED · **FINAL ROADMAP** (governance unification — contracts in authority index)  
**Supersedes:** `archive/superseded/wtm/v4/WORLD_TARGET_MODEL_MAP_LOCKED_v4.md`  
**Authority law:** `WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md` (v1.1)  
**Hub payload:** `system_roadmap` v5.2  
**Hub URL:** `http://127.0.0.1:13020/?tab=system-roadmap`  

**Naming law:** Step ID prefix = phase letter · **33 steps** · phases **A→B→C→D**

---

## Executive summary

| | |
|--|--|
| **Built** | Learning-after-action (A+B) + runtime stack (C1–C7) + D1 code intelligence |
| **Active** | D2 graph fusion (strategic) · runtime stack frozen at C7 |
| **Target** | Pre-LLM world model (D1–D16) → `llm_context_packet_v1.json` → LLM |
| **Focus** | Understanding before action — LLM is last reasoning step only |

### Governance contracts

**Canonical (do not duplicate here):** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` → `WTM_AUTHORITY` · `WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md` · payload `system_roadmap.authorities`.

---

## Phase overview

| Phase | Name | Steps | Status | Question |
|-------|------|-------|--------|----------|
| **A** | Execution Spine | A1–A4 | ✅ DONE | What ran? What was recorded? |
| **B** | Intelligence OS | B1–B6 | ✅ FROZEN | What happened? What to prefer next? |
| **C** | Runtime Stack | C1–C7 | ✅ DONE | Safe plan → verify → route → repair → orchestrate? |
| **D** | Pre-LLM World Model | D1–D16 | 🔄 D2 | What does repo mean before LLM? |

---

# PHASE A — Execution Spine ✅

| ID | Title | Concrete deliverable | Gate |
|----|--------|----------------------|------|
| A1 | Execution queue | `~/.sina/execution-queue.db` | spine validate |
| A2 | Worker + executor | `scripts/execution_spine/` | `validate-execution-spine.sh` |
| A3 | Memory writeback | `execution_memory.jsonl` | spine validate |
| A4 | Artifact store | `~/.sina/execution-artifacts/` | spine validate |

---

# PHASE B — Intelligence OS ✅ FROZEN

| ID | Title | Concrete deliverable | Memory/plan class |
|----|--------|----------------------|-------------------|
| B1 | Pattern Extraction | `execution_patterns_v1.json` | patterns |
| B2 | Decision Memory | `execution_decisions_v1.jsonl` | **causal memory** |
| B3 | Feedback Loop | `execution_feedback_signals.jsonl` | signals |
| B4 | Planner Upgrade | `planner_context_v1.json` | **learned ranking** (not pre-exec SSOT) |
| B5 | Context Intelligence | `context_intelligence_v1.json` | **snapshot** |
| B6 | Self-Optimization | `self_optimization_v1.json` | suggestions only |

**Law:** B is frozen. Read-only for C/D. Never pre-LLM authority.

---

# PHASE C — Runtime Stack 🔄

| ID | Title | Concrete deliverable | Graph type |
|----|--------|----------------------|------------|
| C1 | Tool Graph Engine | `tool_graph_v1.json` | **execution tool graph** |
| C2 | Graph Verification | `tool_graph_verified_v1.json` | safety score |
| C3 | Execution Router | `execution_router_v1.json` | instruction only |
| **C4** | **Autonomous Repair** | `repair_loop_v1.json` | **recovery graph** ● NOW |
| C5 | Context Fabric | bridge contract only | **handles to D** — no semantics |
| C6 | Multi-Step Planner | runtime plan chains | **runtime planner** |
| C7 | Orchestrator | full C-stack control | orchestration |

**C5 law:** Transport only — pointers to D1/D5. No AST, no retrieval, no ranking.

---

# PHASE D — Pre-LLM World Model ❌

**Gate artifact:** `llm_context_packet_v1.json` (D15 + D16)

### Block 1 — Core foundation (D1–D4)

| ID | Title | Delivers | Gate |
|----|--------|----------|------|
| D1 | Code Intelligence | AST, symbols, import graph | `validate-code-intelligence-v1.sh` ✅ |
| **D2** | Graph Fusion | unified code graph SSOT | `validate-graph-fusion-v1.sh` ● |
| D3 | Dependency Graph | call/module/impact edges | `validate-dependency-graph-v1.sh` |
| D4 | Intent Engine | goal class + ambiguity tree | `validate-intent-engine-v1.sh` |

### Block 2 — Semantic understanding (D5–D8)

| ID | Title | Delivers | Gate |
|----|--------|----------|------|
| D5 | Vector Retrieval | local embedding index | retrieval smoke |
| D6 | Memory+Git bridge | read-only history feed | `validate-memory-git-bridge-v1.sh` |
| D7 | Query expansion | Intent→QuerySet + source router | `validate-query-expansion-v1.sh` |
| D8 | Graph Reasoning | root-cause + impact paths | graph smoke |

**Retrieval pipeline:** D4 → **D7** (query formulation + router) → D5/D6/D3 sources → D8

### Block 3 — Decision (D9–D10)

| ID | Title | Delivers | Gate |
|----|--------|----------|------|
| D9 | Context Ranking | relevance + intent align | ranking smoke |
| D10 | Semantic Planning | pre-exec plan graph SSOT | plan smoke |

### Block 4 — Execution prep (D11–D12)

| ID | Title | Delivers | Gate |
|----|--------|----------|------|
| D11 | Tool Router upgrade | policy + cost routing | router smoke |
| D12 | Validation full | dry-run + safety | validation smoke |

### Block 5 — Packet (D13–D16)

| ID | Title | Delivers | Gate |
|----|--------|----------|------|
| D13 | Diff Intelligence | semantic change impact | diff smoke |
| D14 | Compression | token slots per field | budget smoke |
| D15 | Context Assembly | structured packet | `validate-llm-context-packet-v1.sh` |
| D16 | Memory merge | budget-aware memory in packet | `validate-packet-memory-merge-v1.sh` |

---

## Target pipeline (technical)

```text
USER → D4 Intent → D1 Code → D2 Fusion → D3 Deps
  → D7 Query router ← D5 Vector + D6 Memory/Git
  → D8 Reason → D9 Rank → D10 Plan
  → D11 Route → D12 Validate → D13 Diff
  → D14 Budget → D15 Assemble → D16 Memory merge
  → LLM PACKET → LLM
```

Runtime (parallel): C1→C2→C3→**C4**→C5→C6→C7 → spine (founder confirm)

---

## LLM packet schema (D15 output)

`intent` · `files` · `symbols` · `errors` · `dependencies` · `plan` · `constraints` · `tools` · `compressed_context`

Validated by **`validate-llm-context-packet-v1.sh`** before LLM call.

---

## What is NOT this roadmap

RunReceipt/MergePack · factory/investor roadmaps · Personal DB Layer A

---

## Archive

v4: `archive/superseded/wtm/v4/` · Step ID migration: `WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md`
