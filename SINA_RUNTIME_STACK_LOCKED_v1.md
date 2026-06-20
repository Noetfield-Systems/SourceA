# Runtime Stack — Locked Plan (Phase 2)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-RUNTIME-STACK  
**Locked:** 2026-06-05  
**Authority:** ASF / Sina Command maintainer  
**Master roadmap:** `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md` (all phases — **read first**)  
**Companion:** `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` (intelligence — **DONE**, read-only)  
**Companion:** `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md` (Phase D pre-LLM — **separate track**)  

---

## 1. Purpose

Transform the system from:

```text
brain → recommendation
```

toward:

```text
brain → action → verification → dispatch instruction → (founder/spine) execution → repair
```

**This stack builds execution capability — not intelligence logic.**

Execution Spine remains the foundation. Intelligence SSOT is read-only input.

---

## 2. Locked work order (do not reorder)

| Step | Layer | Status | SSOT / code |
|------|-------|--------|-------------|
| 1 | **Tool Graph Engine v1** | ✅ **DONE** | `scripts/runtime/tool_graph/` · `~/.sina/tool_graph_v1.json` |
| 2 | **Tool Graph Verification v1** | ✅ **DONE** | `scripts/runtime/tool_graph_verification/` · `~/.sina/tool_graph_verified_v1.json` |
| 3 | **Execution Router v1** | ✅ **DONE** | `scripts/runtime/execution_router/` · `~/.sina/execution_router_v1.json` |
| 4 | Autonomous Repair Loop v1 | ⬜ **NEXT** | — |
| 5 | Semantic Context Fabric v1 | ⬜ NOT STARTED | — |
| 6 | Multi-Step Execution Planner v1 | ⬜ NOT STARTED | — |
| 7 | Runtime Orchestrator v1 | ⬜ NOT STARTED | — |

**Gate for Step 2 (verified 2026-06-05):** `validate-tool-graph-verify-v1.sh` PASS — cycle check, dependency validation, scoring, API.

---

## 3. Step 3 — Execution Router v1 (shipped)

### Goal

Build a **controlled execution dispatcher** that:

- Takes **verified tool graph** (`tool_graph_verified_v1.json`)
- Applies **policy + safety + priority rules** (read-only from planner/context)
- Selects **next executable step** only
- Outputs **execution-ready instruction**
- Does **NOT** execute anything itself
- Does **NOT** modify spine, queue, or worker

### Inputs (read-only)

```text
~/.sina/tool_graph_verified_v1.json
~/.sina/tool_graph_v1.json
~/.sina/planner_context_v1.json
~/.sina/context_intelligence_v1.json
```

### Output contract (target)

```json
{
  "task_id": "",
  "goal_tool_id": "",
  "recommendation": "approve",
  "next_step": {
    "step": 1,
    "tool_id": "",
    "instruction": "",
    "dispatch_ready": false
  },
  "remaining_steps": [],
  "policy": {}
}
```

### Rules

- Reject routing if verification `recommendation` is `reject`
- `needs_fix` → dispatch_ready false; emit fix hints only
- `approve` → may emit next step instruction; founder confirm before spine enqueue
- No auto-execute (incident law)

### API (target)

`GET /api/execution-router-v1?task_id=&goal=`

### Validation

`bash SourceA/scripts/validate-execution-router-v1.sh` — PASS

---

## 4. Data flow (runtime slice)

```text
tool_graph_v1.json
        ↓
tool_graph_verified_v1.json
        ↓
execution_router_v1          ← Step 3 (instruction only)
        ↓
(founder confirm)
        ↓
execution_spine              ← unchanged substrate
```

---

## 5. APIs (runtime)

- `GET /api/tool-graph-v1`
- `GET /api/tool-graph-verify-v1`
- `GET /api/execution-router-v1`

---

## 6. Validation commands (keep green)

```bash
bash SourceA/scripts/validate-tool-graph-v1.sh
bash SourceA/scripts/validate-tool-graph-verify-v1.sh
bash SourceA/scripts/validate-execution-router-v1.sh
```

---

## 7. Forbidden

| Forbidden | Why |
|-----------|-----|
| Duplicate intelligence extraction | Read SSOT only |
| Auto-enqueue to spine without founder confirm | Incident law |
| Modify execution_spine/queue/worker from router | Spine is foundation |
| Merge with Pre-LLM Code Intelligence track | Separate locked sequences |

---

**This file is LOCKED.** Step 3 begins only after Step 2 validation remains green.
