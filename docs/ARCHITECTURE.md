# SourceA / Sina Command — Architecture

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Path:** `~/Desktop/SourceA/`  
**Hub:** `http://127.0.0.1:13020/`  
**Updated:** 2026-06-06  
**Canonical laws:** `SINA_OS_SSOT_LOCKED.md` · `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md`

---

## 1. What this system is

SourceA is the **governance + hub implementation** for the Sina MonoRepo ecosystem. It is not the data lake (that lives in `SinaaiMonoRepo/SinaaiDataBase/`) and it is not the execution runtime (`SinaaiRuntime` on `:8000`).

**Sina Command** is a single-origin app: Python HTTP server + static SPA that serves UI and ~120 JSON API routes on port **13020**.

```
Founder / agents
       ↓
Sina Command UI (:13020)     agent-control-panel/
       ↓ reads
The Bowl (generated)         sina-bowl/state.json · DAILY_BOWL.md
       ↓ aggregates
SSOT sources                 PROGRAM_PROGRESS.json · ~/.sina/*.json · fleet · lanes
```

---

## 2. Four planes (big picture)

| Plane | Role | Key paths |
|-------|------|-----------|
| **Governance** | Council, rules-in-charge, 8-agent fleet, Track, Scoreboard | `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` · `scripts/agent_rules_in_charge.py` |
| **Hub control** | Founder Refresh/Actions only; WTM panels; no Terminal law | `scripts/sina-command-server.py` · `agent-control-panel/` |
| **Pre-LLM + runtime** | D1–D16 packet, ENFORCE gate, C1–C7 pipeline, dispatch policy | `scripts/runtime/` · `DISPATCH_POLICY_LOCKED_v1.md` |
| **Portfolio lanes** | TrustField, AI Dev Bridge, MergePack, Factory P0 | `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` |

**Current bottleneck (by design):**

```
Context → Plan → Runtime → STOP (dispatch_ready: false)
```

Behavioral proof (Eval-1b live) and dispatch closure are the gate before auto-execution — not new D-modules.

---

## 3. Hub stack

| Layer | Technology | Entry |
|-------|------------|-------|
| Server | Python 3 stdlib `HTTPServer` | `scripts/sina-command-server.py` |
| Panel data | Generated JSON | `agent-control-panel/command-data.json` |
| Build | Validators + merge | `scripts/build-sina-command-panel.py` |
| Start | Background daemon | `scripts/serve-sina-command.sh` |
| Health | GET | `/health` |

**Founder law:** interact via **Refresh**, **Actions**, and hub tabs — never Terminal for ops the maintainer can run.

---

## 4. Runtime pipeline (C1–C7)

Orchestrator coordinates read/plan stages; it does **not** auto-execute spine.

| Stage | Module | SSOT |
|-------|--------|------|
| C1 | `runtime/tool_graph/` | `~/.sina/tool_graph_v1.json` |
| C2 | `runtime/tool_graph_verification/` | `~/.sina/tool_graph_verified_v1.json` |
| C3 | `runtime/execution_router/` | `~/.sina/execution_router_v1.json` |
| C4 | `runtime/repair_loop/` | `~/.sina/repair_loop_v1.json` |
| C5 | `runtime/context_fabric/` | `~/.sina/semantic_context_fabric_v1.json` |
| C6 | `runtime/multi_step_planner/` | `~/.sina/multi_step_planner_v1.json` |
| C7 handoff | `runtime/graph_executor/spine_bridge.py` | `~/.sina/graph_executor_v1.json` |

**Orchestrator:** `runtime/orchestrator/orchestrator_engine.py`  
- `dispatch_ready` always **false** at hub layer  
- Shadow `dispatch_decision` attached (`dry_run: true`) for task-class simulation  

**API:** `/api/runtime-orchestrator-v1` · `/api/graph-executor-v1`

---

## 5. Dispatch policy (dual-layer)

| Layer | Module | Classes |
|-------|--------|---------|
| Spine bridge | `runtime/dispatch_policy/classifier.py` | `observe` · `suggest` · `auto_low_risk` |
| Task dispatch | `runtime/dispatch_policy/allowlist.py` | `SAFE_AUTO` · `BEHAVIORAL` · `CONFIRM` |

`policy_engine.evaluate()` combines C2 graph + C3 router + `eval_tier` + `task_class`.  
Law: `DISPATCH_POLICY_LOCKED_v1.md` · Errata vs Claude spec: `docs/DISPATCH_POLICY_INTERFACE_ERRATA_v1.md`  
API: `/api/dispatch-policy-v1` — top-level `dispatch_ready` always false; read `decision.dispatch_ready` for simulation

---

## 6. Eval + gates

| Gate | Report | Validator |
|------|--------|-----------|
| Eval-1 (structural) | `~/.sina/eval_packet_v1_report.json` | `validate-eval-packet-v1.sh` |
| Eval-1b (behavioral) | `~/.sina/eval_packet_v1b_report.json` | `validate-eval-packet-v1b-live.sh` |
| CI mode | `~/.sina/eval_1b_ci_mode_v1.json` | structural fallback when OpenRouter 402 |
| Dispatch policy | `~/.sina/dispatch_policy_v1.json` | `validate-dispatch-policy-v1.sh` |
| Founder lock | — | `dispatch_ready_lock.py` |

---

## 7. Workspace layout

```
~/Desktop/SourceA/
├── agent-control-panel/     # Hub UI (HTML + JS)
├── scripts/                 # Server, validators, runtime, build
│   └── runtime/             # C1–C7 + dispatch_policy + event_bus
├── sina-bowl/               # Generated bowl state
├── os/plan-library/         # sourcea-1000 prompts + SOURCEA-PRIORITY.md
├── product/ investor/ founder/   # Lane and product canon
├── docs/                    # This file + RUNBOOK + ONBOARDING
└── *_LOCKED_v1.md           # Governance law (read chain, not duplicated here)

~/.sina/                     # Machine SSOT (reports, policy, executor snapshots)
```

**HQ shell:** `~/Desktop/SinaaiDataBase/` — Cursor bridge, agent-loop prompts; not the full data tree.

---

## 8. Related diagrams

- World Target Model: `WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md`  
- Hub live diagram tab: `/?tab=system-roadmap&view=diagram`  
- 10× automation: `SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md`

---

## 9. What not to treat as architecture authority

- Chat transcripts (disk wins)  
- Generated `RUNTIME/` artifacts  
- Stale README narrative without validator proof  
- Parallel `.mdc` rules without supersession via rules-in-charge loop
