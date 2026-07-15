# Execution Intelligence Stack — locked plan & next goals

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-EXEC-INTEL-STACK  
**Locked:** 2026-06-05  
**Authority:** ASF / Sina Command maintainer  
**Hub:** `http://127.0.0.1:13020/`  
**Supersedes:** ad-hoc “add more agents/UI” expansion before spine exists  
**Master roadmap:** `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md`  
**Next stack (pre-LLM):** `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md`  
**Runtime stack (Phase 2):** `SINA_RUNTIME_STACK_LOCKED_v1.md`  

---

## 1. Stack (bottom → top)

```text
Brain / UI          — Sina Command hub, laws, agent loop packs, governance rooms
        ↓
Execution Spine     — queue → worker → runner → RunReceipt → execution_memory.jsonl
        ↓
Memory Writeback    — every run appends SSOT record + artifacts (~/.sina/)
        ↓
Pattern Engine      — success/failure/repeated-error extraction → execution_patterns.json
        ↓
Decision Memory     — why pass/fail + fix mapping → execution_decisions_v1.jsonl
        ↓
Feedback Loop v1    — patterns + decisions → influence signals → execution_feedback_signals.jsonl
        ↓
Memory-Aware Planner v1 — history + signals → ranked recommendations → planner_context_v1.json
        ↓
Self-Optimization v1 — observe → measure → compare → suggest → self_optimization_v1.json
```

**Principle:** Each layer reads only from layers below. **Never** bypass the spine for execution state.

---

## 2. Status (what is logged today)

| Layer | Status | Code / artifact |
|-------|--------|-----------------|
| Brain / UI | **DONE** (control plane) | `agent-control-panel/`, `sina_command_lib.py` |
| Execution Spine | **DONE** | `scripts/execution_spine/` · `~/.sina/execution-queue.db` |
| Memory Writeback | **DONE** | `~/.sina/execution_memory.jsonl` · `execution-artifacts/` |
| Pattern Engine (v1) | **DONE** | `scripts/execution_intelligence/processor.py` |
| Decision Memory v1 (WHY layer) | **DONE** | `decision_memory/` · `execution_decisions_v1.jsonl` |
| Feedback Loop v1 | **DONE** | `feedback_loop/` · `execution_feedback_signals.jsonl` |
| Memory-Aware Planner v1 | **DONE** | `planner_upgrade/` · `planner_context_v1.json` → `agent_loop.py`, `prompt_direction.py` |
| Predictive layer (v2) | **DONE** (read-only) | `scripts/execution_intelligence_v2/` |
| Context Intelligence v1 | **DONE** | `context_intelligence/` · `context_intelligence_v1.json` |
| Self-Optimization v1 | **DONE** | `self_optimization/` · `self_optimization_v1.json` (suggestions only) |
| Tool Graph v1 | **DONE** | `scripts/runtime/tool_graph/` · `tool_graph_v1.json` |
| Tool Graph Verification v1 | **DONE** | `scripts/runtime/tool_graph_verification/` · `tool_graph_verified_v1.json` |

---

## 3. Locked work order (do not reorder)

Build and stabilize **top-down only after the layer below is green.**

| Step | Layer | Goal | Gate |
|------|-------|------|------|
| 1 | **Pattern Extraction Engine** | Deterministic patterns from `execution_memory.jsonl` | `validate-execution-intelligence.sh` PASS |
| 2 | **Decision Memory v1** | Why-based reasoning; cause/fix mappings | `execution_decisions_v1.jsonl` grows per new runs |
| 3 | **Feedback Loop v1** | Patterns + decisions → influence signals | `validate-feedback-loop-v1.sh` PASS |
| 4 | **Planner upgrade v1** | History + signals → ranked recommendations | `validate-planner-upgrade-v1.sh` PASS |
| 5 | **Context Intelligence v1** | Unified snapshot: state + repo + behavior + planner | `validate-context-intelligence-v1.sh` PASS |
| 6 | **Self-Optimization v1** | Evidence-based optimization memory; no auto-execute | `validate-self-optimization-v1.sh` PASS |

**Forbidden while Steps 1–4 are incomplete:** new hub tabs, new agent types, new rule files, Redis/Docker spine, auto-paste into Cursor.

---

## 4. Next goals (immediate)

### P0 — Close the intelligence loop (no new surfaces)

1. Run `validate-execution-spine.sh` + `validate-execution-intelligence.sh` + `validate-execution-intelligence-v2.sh` on every hub refresh.
2. Wire **Actions** tab to show `best_next_action` from v2 before founder taps dispatch.
3. Append RunReceipt (`P0-RUNRECEIPT`) on every spine success — already mirrored; raise `progress_pct` only from receipts.

### P1 — Context intelligence (Step 5) — SHIPPED

1. `GET /api/execution-context` — unified context object + `matters_now` subset.
2. Planners receive `execution_context` via `planner_context_block()`.
3. **Next:** semantic Layer A retrieval (pgvector deferred per no-credit-card rule).

### P2 — Self-optimization (Step 6)

1. Background worker drains queue; v2 `strategy_optimizer` re-runs after each new memory line.
2. Auto-suggest (not auto-execute) next engine in hub; founder one-tap confirm only.
3. Weekly digest: top failure signatures + resolution strategies → Incident Room optional paste.

---

## 5. Module map (SSOT paths)

```text
execution_spine/              # DO NOT MODIFY without maintainer + stack review
execution_intelligence/       # v1 — patterns, decisions, feedback, planner influence
execution_intelligence_v2/      # v2 — prediction, risk, causal, recommender, strategy

~/.sina/execution_memory.jsonl
~/.sina/execution_patterns.json
~/.sina/execution_decisions_v1.jsonl
~/.sina/execution_feedback_signals.jsonl
~/.sina/planner_context_v1.json
~/.sina/context_intelligence_v1.json
~/.sina/self_optimization_v1.json
~/.sina/execution-strategy-v2.json
~/.sina/execution-intelligence-state.json
```

**APIs (read-only intelligence):**

- `GET /api/execution-spine`
- `GET /api/execution-intelligence`
- `GET /api/execution-feedback-v1`
- `GET /api/planner-upgrade-v1`
- `GET /api/context-intelligence-v1`
- `GET /api/self-optimization-v1`
- `GET /api/execution-context` (legacy task-scoped)
- `GET /api/execution-intelligence-v2`

---

## 6. What this stack is NOT

| Not now | Why |
|---------|-----|
| Full autonomous agent OS | Auto-paste blocked; founder in loop by law |
| Vector memory fabric | Step 5; infra deferred |
| Economic / participation layer | Separate thread; not intelligence stack |
| Replacement for Cursor IDE execution | Spine orchestrates; IDE still runs code |

---

## 7. Success criteria (stack “green”)

- [ ] Every `one_click` / `shell` action produces a spine record.
- [ ] `execution_patterns.json` updates when memory line count changes.
- [ ] Planners log shows `execution_intelligence_v2.best_next_action` in context.
- [ ] `PROGRAM_PROGRESS.json` `signals_auto.execution_spine` present after refresh.
- [ ] No new intelligence silo outside `~/.sina/` + Layer A promotion path.

---

## 8. References

- RunReceipt P0: `product/PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md` · `SinaaiDataBase/runreceipt/RUNRECEIPT_SCHEMA.md`
- Prompt-fast loop: `SINA_PROMPT_FAST_LOOP_LOCKED_v1.md`
- Phase 1 freeze: `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` (stability > new architecture)
- Hub essentials: add tab `essentials` → read chain includes this doc when ASF pins it

**Maintainer rule:** Intelligence upgrades extend `execution_intelligence*` only. Spine changes require separate locked amendment.
