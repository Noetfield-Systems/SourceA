# SourceA Forge Terminal — Agent Operating Manual (LOCKED v1)

**Saved:** 2026-06-25T04:00:00Z  
**Version:** 1.0 — LOCKED  
**App version:** Forge Terminal **4.0.0-alpha** · port **13029**  
**Authority:** Maps advisor Forge Agent Master Spec (v5-ready) → **actual SourceA disk SSOT**  
**Parent:** `SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_V3_SWARM_BLACKBOARD_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_L2_SELF_IMPROVE_LOCKED_v1.md`

---

## One law

> **Every Cursor agent or Forge Terminal API caller is a constrained execution unit inside a governed software nation — not a free chatbot. Read this manual + linked paths before acting.**

---

## 0) Session boot (mandatory read order)

| Order | Path / command | Role |
|-------|----------------|------|
| 1 | `python3 ~/Desktop/SourceA/scripts/agent_session_gate_run_v1.py --role any --json` | Session gate sync |
| 2 | `~/.sina/brain_session_receipt_v1.json` | Brain session receipt |
| 3 | `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md` | Mac = control plane only |
| 4 | `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md` | Context cache pointers |
| 5 | `data/cursor-bootstrap-ledger-v1.json` | Architecture GPS |
| 6 | **This file** | Forge agent operating manual |
| 7 | `brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_LOCKED_v1.md` | Governance kernel (ALLOW/DENY) |
| 8 | `scripts/forge_governance_kernel_v1.py` | Runtime permission enforcer |
| 9 | `brain-os/law/entry/START_HERE_LOCKED_v1.md` | Role picker |

**Mac founder session:** `dry_run=true` default for swarm; no validator marathons (INCIDENT-039). Proof = read receipts, not bash chains.

---

## 1) System role definition

| Advisor v5 concept | SourceA implementation |
|--------------------|------------------------|
| Execution unit in governed system | `scripts/forge_agent_kernel_v1.py` · `scripts/forge_agent_kernel_v3_swarm.py` |
| Not free autonomous agent | Tool allowlists · `FORBIDDEN_PATH` · quality gate blocks execute |
| Software nation | v4 civilization layer — memory + registry + economy lite (no v5 credits yet) |

**Law:** `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md`

---

## 2) Agent registry (mandatory)

### 2.1 Disk SSOT

| Resource | Address |
|----------|---------|
| Registry module | `~/Desktop/SourceA/scripts/forge_agent_registry_v1.py` |
| Live registry | `~/.sina/forge-agent-registry-v1.json` |
| Schema | `forge-agent-registry-v1` |

### 2.2 Seeded agents (13)

| ID | Role | Skills |
|----|------|--------|
| planner-001 | planner | architecture, decompose |
| planner-002 | planner | risk, scope |
| planner-003 | planner | repo_scan |
| builder-001 | builder | patch, python |
| builder-002 | builder | patch, typescript |
| builder-003 | builder | test, verify |
| builder-004 | builder | docs |
| builder-005 | builder | refactor |
| critic-001 | critic | review, quality |
| critic-002 | critic | security |
| critic-003 | critic | tests |
| repair-001 | repair | fix, patch |
| optimizer-001 | optimizer | roi, cost |

### 2.3 Agent fields (implemented)

```json
{
  "id": "planner-001",
  "role": "planner|builder|critic|repair|optimizer",
  "skills": ["..."],
  "reputation": 0.5,
  "cost_efficiency": 1.0,
  "runs": 0
}
```

**Evolution:** +0.1 reputation on success · −0.15 on failure · cost_efficiency boost when reputation > 0.8.

**Not yet implemented (v5 advisor):** `level` 1–5 · `archiver` · `deployer` roles · `permissions[]` · `memoryRefs[]` · `status: probation|disabled`.

---

## 3) Skill system

### 3.1 Advisor skill taxonomy → SourceA mapping

| Category | Advisor skills | SourceA location |
|----------|----------------|------------------|
| Engineering | frontend_engineering, backend_engineering, api_design, database_design, system_architecture | Agent `skills[]` in registry · planner prompts in swarm kernel |
| Execution | shell_execution, git_operations, deployment, debugging, refactoring | `ForgeAgentTools` · `ForgeSwarmTools` in kernel v1/v3 |
| Intelligence | code_reasoning, diff_generation, test_analysis, dependency_mapping | `scripts/forge_repo_intel_v1.py` · `scripts/forge_swarm_blackboard_v1.py` |
| Quality | testing, validation, security_review, performance_analysis | `scripts/forge_quality_gate_v1.py` · critic agents · `run_verify_harness_static` |

### 3.2 Cursor skills (Forge-specific)

| Skill | Path |
|-------|------|
| Forge Living UI / Modern IDE | `~/Desktop/SourceA/.cursor/skills/forge-living-ui-modern-ide/SKILL.md` |
| Forge factory directory map | `~/Desktop/SourceA/.cursor/skills/forge-living-ui-modern-ide/FORGE_FACTORY_DIRECTORY.md` |
| Hub Pro cloud API | `~/Desktop/SourceA/.cursor/skills/hub-pro-cloud-api/SKILL.md` |
| Hub Pro master | `~/Desktop/SourceA/.cursor/skills/hub-pro-master/SKILL.md` |
| Hub Pro app E2E | `~/Desktop/SourceA/.cursor/skills/hub-pro-app-e2e/SKILL.md` |
| Hub Pro mac session | `~/Desktop/SourceA/.cursor/skills/hub-pro-mac-session/SKILL.md` |

### 3.3 Cursor rules (Forge-adjacent)

| Rule | Path |
|------|------|
| Mac control plane | `~/Desktop/SourceA/.cursor/rules/mac-control-plane.mdc` |
| No validator stuck (P0) | `~/Desktop/SourceA/.cursor/rules/034-mac-no-validator-stuck-red-flag.mdc` |
| Hub cloud proceed | `~/Desktop/SourceA/.cursor/rules/035-hub-cloud-proceed-v1.mdc` |
| Cloud forge run vocabulary | `~/Desktop/SourceA/.cursor/rules/038-cloud-forge-run-vocabulary-v1.mdc` |
| Hundred rows per turn | `~/Desktop/SourceA/.cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc` |
| Founder intent first | `~/Desktop/SourceA/.cursor/rules/agent-founder-intent-first.mdc` |
| Cost intelligence routing | `~/Desktop/SourceA/.cursor/rules/045-cursor-cost-intelligence-routing-v1.mdc` |

---

## 4) Experience system

| Resource | Address |
|----------|---------|
| Civilization memory module | `~/Desktop/SourceA/scripts/forge_civilization_memory_v1.py` |
| Live memory | `~/.sina/forge-civilization-memory-v1.json` |
| Schema | `forge-civilization-memory-v1` |

### 4.1 Memory fields

| Field | Content |
|-------|---------|
| `event_log[]` | Every swarm/advisor/L2/L3 run outcome |
| `task_history[]` | goal → verdict → cost_estimate |
| `failure_patterns[]` | Critic issues from failed runs |
| `graph_snapshot` | Latest repo graph |
| `constitution` | max_cost_per_task=10 · no_destructive_ops · require_verification · auditable_memory |

### 4.2 Learning rules (implemented)

- Registry reputation updated after swarm (`update_reputation`)
- `evolve_agents()` adjusts cost_efficiency
- `record_run(receipt)` after every swarm completion

**Not yet:** per-task `diffQuality` · `timeTaken` · vector DB mandatory writes.

---

## 5) Memory system (three layers)

| Layer | Advisor | SourceA address |
|-------|---------|-----------------|
| Short-term (task context) | repo state, diff, goal | `~/.sina/forge-swarm-blackboard-v1.json` |
| Long-term (events) | past solutions, failures | `~/.sina/forge-civilization-memory-v1.json` |
| Structural (graph) | file relationships | `build_repo_graph()` in `scripts/forge_repo_intel_v1.py` → blackboard `repo_graph` |

### 5.1 Blackboard schema

**Module:** `~/Desktop/SourceA/scripts/forge_swarm_blackboard_v1.py`  
**Live:** `~/.sina/forge-swarm-blackboard-v1.json`

Keys: `goal`, `goals[]`, `tasks[]`, `artifacts[]`, `repo_state`, `repo_graph`, `planner_votes[]`, `critic_verdicts[]`, `task_economy[]`, `agent_bids[]`, `logs[]`, `round`.

**Law:** `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_V3_SWARM_BLACKBOARD_LOCKED_v1.md`

---

## 6) Tool permission system

### 6.1 L1 kernel tools (`ForgeAgentTools`)

**Module:** `~/Desktop/SourceA/scripts/forge_agent_kernel_v1.py`

| Tool | Args | Notes |
|------|------|-------|
| read_file | path | Workspace-relative only |
| write_file | path, content | Blocked in L2 patch_only mode |
| patch_file | path, search, replace | Preferred for L2 self-heal |
| list_files | prefix, limit | Max 40 default |
| search_code | query, limit | Ripgrep-style |
| run_shell | cmd | Allowlist: pytest, npm test, `scripts/*.sh`, light forge E2E |

### 6.2 v3 swarm tools (`ForgeSwarmTools` extends L1)

**Module:** `~/Desktop/SourceA/scripts/forge_agent_kernel_v3_swarm.py`

| Tool | Role access |
|------|-------------|
| apply_git_patch | builder |
| search_semantic | planner, builder |
| repo_index | planner, builder |
| All L1 tools | builder |

### 6.3 Permission matrix (enforced in code)

| Role | Tools allowed |
|------|---------------|
| planner | LLM plan only — no direct file write in swarm planner phase |
| builder | read_file, patch_file, write_file, apply_git_patch, list_files, search_code, search_semantic, repo_index, run_shell |
| critic | LLM review only — reads blackboard snapshot |
| repair | LLM fix hints — no direct patch (hints feed replan) |
| optimizer | LLM ROI — skip_tasks, model_tier |
| deployer | **Not implemented on Mac** — cloud dispatch only |

### 6.4 Forbidden patterns

- `FORBIDDEN_PATH` regex in kernel v1 (`.env`, `secrets.env`, `.git/`, `rm -rf`, `sudo`, etc.)
- `BANNED_DIFF` in kernel v3 swarm
- Quality gate blocks `send_to_cloud` / execute when REVISE or REJECT

---

## 7) Task model (unified execution unit)

**Module:** `~/Desktop/SourceA/scripts/forge_swarm_blackboard_v1.py`

```json
{
  "id": "task-1",
  "goal": "step text",
  "value": 1.42,
  "cost_estimate": 1.05,
  "priority": 1,
  "status": "open|in_progress|done|failed"
}
```

Functions: `estimate_task_value()` · `estimate_task_cost()` · `build_task_economy()` · `select_agent_for_task()` · `collect_agent_bids()`.

**Cap:** `max_cost_per_task = 10.0` (constitution in civilization memory).

---

## 8) Economy model

| Advisor v5 | SourceA status |
|------------|----------------|
| Forge Credits / Account balance | **Not implemented** — task economy lite only (value/cost/bid) |
| Tax / nation currency | **Not implemented** (v5 digital nation — explicit non-goal) |
| Reputation penalty on failure | **Implemented** in agent registry |

---

## 9) Execution pipeline (mandatory)

Every Forge agent task MUST follow:

1. **PLAN** — planner swarm or advisor orchestrator  
2. **READ CONTEXT** — repo_index · repo_graph · blackboard  
3. **DESIGN DIFF** — builder agent (patch_file / apply_git_patch)  
4. **APPLY PATCH** — workspace-only  
5. **RUN TESTS** — run_shell allowlist or verify harness  
6. **VERIFY OUTPUT** — critic swarm + quality gate + `run_verify_harness_static`  
7. **UPDATE MEMORY** — `record_run()` + registry reputation  

### 9.1 Orchestration modules

| Layer | Module | Receipt |
|-------|--------|---------|
| L1 agent loop | `scripts/forge_agent_kernel_v1.py` | `~/.sina/forge-agent-kernel-latest-v1.json` |
| L2 self-heal | same kernel `run_self_improve_loop` | `~/.sina/forge-agent-self-improve-latest-v1.json` |
| L3 cloud | `scripts/forge_agent_self_improve_l3_v1.py` | `~/.sina/forge-agent-self-improve-l3-v1.json` |
| Advisor PLAN→ACT→VERIFY | `scripts/forge_advisor_orchestrator_v1.py` | `~/.sina/forge-advisor-latest-v1.json` |
| v3 swarm | `scripts/forge_agent_kernel_v3_swarm.py` | `~/.sina/forge-agent-kernel-swarm-v3.json` |
| Cloud swarm dispatch | `scripts/forge_swarm_cloud_dispatch_v1.py` | `~/.sina/forge-swarm-cloud-dispatch-latest-v1.json` |
| Parallel builders | `scripts/forge_execution_mesh_v1.py` | (inline in swarm receipt) |
| Civilization tick | `scripts/forge_civilization_loop_v1.py` | `~/.sina/forge-civilization-tick-latest-v1.json` |

### 9.2 Swarm execution loop

```
parallel planners → merge_plans → optimizer → task_economy + agent_bids
→ parallel builders (execution mesh) → parallel critics → aggregate_verdicts
→ repair agent (if fail) → replan (max 2 rounds) → verify harness → memory + registry
```

---

## 10) Verification system

| Layer | Module | Address |
|-------|--------|---------|
| 11-layer quality gate | `scripts/forge_quality_gate_v1.py` | `~/.sina/forge-terminal-quality/<run_id>.json` |
| Static verify harness | `run_verify_harness_static()` in kernel v1 | Inline in swarm receipt |
| Living UI E2E | `scripts/forge_terminal_living_ui_e2e_verify_v1.py` | `~/.sina/forge-terminal-living-ui-e2e-v1.json` |
| LangGraph civilization gate | `apps/factory-runtime-spike/factory_runtime_spike/langgraph_gate_v1.py` `run_civilization_gate()` | Factory spike receipt |
| Critic verify | `scripts/forge_terminal_critic_verify_v1.py` | — |

**Rule:** No change is valid unless critic aggregate approved + harness ok + quality gate PASS for execute paths.

---

## 11) Agent evolution rules

| Rule | Implementation |
|------|----------------|
| High success → promotion | reputation +0.1 · cost_efficiency ×1.05 when rep > 0.8 |
| Low success → restriction | reputation −0.15 · cost_efficiency ×0.95 when rep < 0.3 |
| Consistent failure → disable | **Partial** — queued to L3/swarm repair queue |
| High efficiency → clone | **Not implemented** (v5) |

---

## 12) Forge knowledge map (system layers)

```
Founder UI (:13029)
  apps/forge-terminal-v1/          terminal.js · index.html · terminal.css
  apps/forge-terminal-connect-v1/  Connect shell · forge-quality-bridge.js

API Gateway
  scripts/forge_terminal_connect_server_v1.py   UI_VERSION 4.0.0-alpha
  POST /api/forge-terminal/v1                   → forge_terminal_v1.handle_post

Worker / Agent execution
  scripts/forge_agent_kernel_v1.py              L1 + L2
  scripts/forge_agent_kernel_v3_swarm.py        v3 parallel swarm
  scripts/forge_advisor_orchestrator_v1.py      Advisor mode

Swarm orchestration
  scripts/forge_swarm_blackboard_v1.py
  scripts/forge_execution_mesh_v1.py
  scripts/forge_swarm_cloud_dispatch_v1.py

Memory + civilization
  scripts/forge_civilization_memory_v1.py
  scripts/forge_agent_registry_v1.py
  scripts/forge_civilization_loop_v1.py

Repo intelligence
  scripts/forge_repo_intel_v1.py
  pre_llm/code_intelligence/ (optional D1 index via blackboard light graph)

Cloud execution body (not Mac)
  scripts/cloud_workers_hub_v1.py               :13027
  scripts/cloud_auto_runtime_v1.py
  scripts/forge_l3_auto_runtime_v1.py
  Railway FBE via fbe.lib.hub_cloud_proxy_v1
```

---

## 13) Forge Terminal API (POST `/api/forge-terminal/v1`)

**Server:** `http://127.0.0.1:13029`  
**Auth:** `X-Forge-Token` from `/health` → `forge_local_token`  
**Handler:** `scripts/forge_terminal_v1.py` → `handle_post()`

### 13.1 Agent-critical actions

| Action | Purpose |
|--------|---------|
| `chat_turn` | Founder chat + quality gate + founder language |
| `advisor_run` | Swarm advisor (default `swarm: true`) |
| `agent_swarm_run` | Direct v3 swarm loop |
| `agent_dev_loop` | L1 kernel only |
| `agent_self_improve` | L2 patch-only repair |
| `agent_self_improve_l3` | L3 cloud dispatch |
| `run` | Full terminal run (idea → LLM → decision card) |
| `quality_receipt` | Read quality gate for run_id |
| `decide` / `approve_send` | Route to Cursor or cloud |
| `kernel_status` / `agents_list` / `receipts_list` | OS bridge introspection |
| `desktop_mesh_status` / `peer_dispatch` | Multi-peer mesh |
| `workspace_snapshot` / `workspace_read_file` / `workspace_ls` | Repo context |

### 13.2 Cloud swarm dispatch

```json
POST /api/forge-terminal/v1
{
  "action": "agent_swarm_run",
  "goal": "...",
  "workspace_path": "~/Desktop/SourceA",
  "cloud": true,
  "dry_run": true,
  "parallel": true,
  "planner_count": 3,
  "critic_count": 3
}
```

---

## 14) Context injection rules

Agents MUST receive (when available):

| Context | Source |
|---------|--------|
| goal | API body / blackboard |
| repo snapshot | `repo_index` · `workspace_snapshot` |
| recent diffs | builder steps in swarm receipt |
| test results | `run_shell` output · verify_harness |
| memory references | civilization memory event_log tail |
| model routing | `scripts/model_dispatch.py` `pick_roi_model(role)` |
| ROI matrix | `~/Desktop/SourceA/data/forge-model-roi-matrix-v1.json` |

### 14.1 LLM routing roles

| Role | Typical use |
|------|-------------|
| reason | Planner · architecture |
| build | Builder · repair |
| check | Critic · optimizer · reviewer |

**Secrets template:** `~/Desktop/SourceA/data/forge-secrets-env-template-v1.env`  
**Runtime secrets:** `~/.sina/secrets.env` (never commit)

---

## 15) Failure handling rules

| Step | Implementation |
|------|----------------|
| 1. Rollback patch | **Manual** — git revert; no auto-rollback yet |
| 2. Re-plan task | Swarm replan loop (max 2 rounds) |
| 3. Escalate to critic | Parallel critics + aggregate |
| 4. Reduce reputation | `update_reputation(success=False)` |
| 5. Retry max 3 | L2 max 2 rounds · swarm max 2 replan rounds |
| 6. Queue for cloud | `enqueue_swarm_repair()` → `~/.sina/forge-l3-repair-queue-v1.json` |

---

## 16) Security model

Agents MUST NEVER:

- Execute destructive shell (`rm -rf /`, `sudo`, pipe-to-sh)
- Read/write `.env`, `secrets.env`, `.git/` internals
- Bypass quality gate for cloud/cursor execute
- Run validator marathons on Mac founder session (INCIDENT-039)
- Bootstrap local Redis / heavy factory on Mac

**Mac flags:** `~/.sina/mac-control-plane-v1.flag` · `~/.sina/cli-disabled-v1.flag`

---

## 17) Receipt index (`~/.sina`)

| Receipt | Purpose |
|---------|---------|
| `forge-terminal-latest-v1.json` | Latest terminal run |
| `forge-terminal-runs/` | All run JSON |
| `forge-terminal-outbox/` | Cloud/cursor dispatch outbox |
| `forge-terminal-quality/<run_id>.json` | Quality gate per run |
| `forge-terminal-chat-thread-v1.json` | Chat thread persistence |
| `forge-agent-kernel-latest-v1.json` | L1 kernel |
| `forge-agent-kernel-swarm-v3.json` | v3 swarm |
| `forge-swarm-blackboard-v1.json` | Shared blackboard |
| `forge-agent-self-improve-latest-v1.json` | L2 self-heal |
| `forge-agent-self-improve-l3-v1.json` | L3 cloud |
| `forge-swarm-cloud-dispatch-latest-v1.json` | Cloud swarm dispatch |
| `forge-civilization-memory-v1.json` | Civilization memory |
| `forge-agent-registry-v1.json` | Agent registry |
| `forge-civilization-tick-latest-v1.json` | Civilization tick |
| `forge-l3-repair-queue-v1.json` | L3 + swarm repair queue |
| `forge-advisor-latest-v1.json` | Advisor orchestrator |
| `forge-terminal-living-ui-e2e-v1.json` | E2E proof |

---

## 18) Data SSOT (`~/Desktop/SourceA/data/`)

| File | Role |
|------|------|
| `forge-model-roi-matrix-v1.json` | Model ROI routing |
| `forge-terminal-decision-card-v1.json` | Decision card schema |
| `forge-secrets-env-template-v1.env` | API key template |
| `founder-reply-glossary-v1.json` | Founder language glossary |
| `forge-real-blueprints-v01.json` | Factory blueprints |
| `forge-scoring-ssot-v01.json` | Scoring SSOT |
| `forge-v02-cloud-contract-v1.json` | Cloud forge contract |
| `forge-mvp-router-rules-v0.1.json` | MVP router |
| `schemas/forge-task-graph-v0.1.json` | Task graph schema |
| `schemas/forge-input-v1.json` | Forge input schema |
| `factory-specs/forge-app-factory-v1.json` | App factory spec |
| `cursor-bootstrap-ledger-v1.json` | Cursor bootstrap GPS |
| `sourcea-e2e-check-registry-overrides-v1.json` | E2E tier registry |

---

## 19) Law + governance index

| Document | Path |
|----------|------|
| Agent operating manual (this) | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md` |
| v4 Civilization | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md` |
| v3 Swarm blackboard | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_V3_SWARM_BLACKBOARD_LOCKED_v1.md` |
| L2 self-improve | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_L2_SELF_IMPROVE_LOCKED_v1.md` |
| Living desktop E2E | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_LIVING_DESKTOP_E2E_LOCKED_v1.md` |
| Quality engine E2E | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_QUALITY_ENGINE_E2E_LOCKED_v1.md` |
| Desktop E2E | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_DESKTOP_E2E_LOCKED_v1.md` |
| Cloud forge run vocabulary | `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_AUTO_RUNTIME_VOCABULARY_LOCKED_v1.md` |
| Hundred rows per turn | `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md` |
| Full pack pattern | `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_FULL_PACK_PATTERN_LOCKED_v1.md` |
| Mac control plane | `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md` |
| Cursor cost routing | `brain-os/law/enforcement/SOURCEA_CURSOR_COST_INTELLIGENCE_ROUTING_LOCKED_v1.md` |

---

## 20) Ports + cloud addresses

| Port | Service | URL |
|------|---------|-----|
| 13029 | Forge Terminal Connect + IDE | `http://127.0.0.1:13029/` |
| 13029 | Forge API | `http://127.0.0.1:13029/api/forge-terminal/v1` |
| 13029 | Health | `http://127.0.0.1:13029/health` |
| 13023 | Chat Unify standalone | `http://127.0.0.1:13023/` |
| 13027 | Cloud Workers | `http://127.0.0.1:13027/api/cloud-workers/v1` |
| 13020 | Hub (legacy glance) | `http://127.0.0.1:13020/` |
| Railway FBE | Cloud forge run | `https://sourcea-fbe-runner-production.up.railway.app/` |

### 20.1 Hub panel receipt lines

**UI:** `~/Desktop/SourceA/agent-control-panel/shared/cloud-workers-panel.js`

Shows paths for: Forge L3 queue · swarm cloud dispatch · civilization memory · agent registry · civilization tick.

---

## 21) E2E proof commands (light — Mac OK)

```bash
cd ~/Desktop/SourceA
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
python3 scripts/forge_terminal_ui_e2e_verify_v1.py
python3 -m py_compile scripts/forge_agent_kernel_v3_swarm.py scripts/forge_civilization_loop_v1.py
```

**Target:** 77+ checks · APP_VERSION `4.0.0-alpha`

---

## 22) Advisor v5 gaps (explicit non-goals on Mac)

| Advisor v5 feature | Status |
|--------------------|--------|
| Forge Credits / Account balance | Not built |
| deployer / archiver agent roles | Not built |
| Redis queue on Mac | Forbidden — cloud only |
| Vector DB mandatory | Optional labs-sandbox only |
| Full production Docker bootstrap | Cloud ship window only |
| Digital nation / constitution economy | v5 — not in scope |

**Next cloud step (when founder arms):** Railway worker cluster + live `dry_run=false` swarm dispatch.

---

## 23) Agent behavior contract (final)

Every Forge Cursor agent MUST:

1. Obey tool permissions (section 6)  
2. Follow execution pipeline (section 9)  
3. Update memory after each action (`record_run`)  
4. Verify output before completion (section 10)  
5. Minimize cost (`pick_roi_model` · optimizer agent)  
6. Read disk SSOT — never treat chat history as truth  
7. Route heavy body work to cloud — Mac observes only  
8. Pass governance kernel before every tool action (section 25)

---

## 24) Official agent boot catalog (normalized)

1. Security + gate rules  
2. Agent registry  
3. Governance kernel  
4. Tool permission matrix  
5. Task system + economy  
6. Memory system  
7. Repo intelligence  
8. Execution pipeline  
9. Verification + safety  
10. Swarm orchestration  
11. External API surface  

---

## 25) Governance kernel (v4 geopolitical legal)

| Resource | Address |
|----------|---------|
| Kernel | `scripts/forge_governance_kernel_v1.py` (v4) |
| Legal v3 | `scripts/forge_governance_legal_v3.py` |
| Geo legal v4 | `scripts/forge_geopolitical_legal_v4.py` |
| World state | `scripts/forge_world_state_v1.py` |
| Law | `SOURCEA_FORGE_GOVERNANCE_KERNEL_V4_LOCKED_v1.md` |
| Geo store | `~/.sina/forge-geopolitical-legal-v4.json` |
| Cases | `~/.sina/forge-governance-cases-v3.json` |
| Precedent | `~/.sina/forge-governance-precedent-v3.json` |
| World | `~/.sina/forge-world-state-v1.json` |

API: `{ "action": "geo_sign_treaty" }` · `{ "action": "geo_impose_sanction" }` · `{ "action": "geo_legal_tick" }`

---

## 26) v6 world simulation (stub)

| Resource | Address |
|----------|---------|
| Module | `scripts/forge_world_state_v1.py` |
| World state | `~/.sina/forge-world-state-v1.json` |

Three seed nations: SourceA Mac · Cloud Forge · Labs Sandbox. Full v6/v7 = cloud only.

---

## 27) Prompt OS Compiler (v3 autonomous runtime)

| Resource | Address |
|----------|---------|
| v3 runtime | `scripts/forge_prompt_os_compiler_v3.py` |
| v2 adaptive | `scripts/forge_prompt_os_compiler_v2.py` |
| v1 core | `scripts/forge_prompt_os_compiler_v1.py` |
| v3 law | `SOURCEA_FORGE_PROMPT_OS_COMPILER_V3_LOCKED_v1.md` |
| Runtime receipt | `~/.sina/forge-prompt-os-runtime-latest-v3.json` |
| Runtime queue | `~/.sina/forge-prompt-os-runtime-queue-v3.json` |
| Learning store | `~/.sina/forge-prompt-os-learning-v2.json` |

Pipeline: raw intent → v2 adaptive compile → route_execution → kernel/swarm/cloud → deployment hint → learn.

API: `{ "action": "autonomous_run", "text": "...", "dry_run": true }` · `compile_prompt` returns v3 envelope with `suggested_route`.

---

## 28) Self-Building Stack (v1–v6)

| Layer | Module |
|-------|--------|
| v1 introspect + gap | `scripts/forge_self_build_v1.py` |
| v2 proof compiler | `scripts/forge_self_build_v2.py` |
| v3 swarm evolution | `scripts/forge_self_build_v3.py` |
| v4 civ code evolution | `scripts/forge_civilization_code_v4.py` |
| v5 digital nation OS | `scripts/forge_digital_nation_v5.py` |
| v6 world system | `scripts/forge_world_system_v6.py` |
| Law | `SOURCEA_FORGE_SELF_BUILD_STACK_LOCKED_v1.md` |

API: `self_build_tick` · `self_build_safe_evolve` · `self_build_swarm_evolve` · `civilization_code_tick` · `world_system_tick`

---

## 29) Planetary Consciousness OS (v7)

| Resource | Address |
|----------|---------|
| Module | `scripts/forge_planetary_consciousness_v7.py` |
| Law | `SOURCEA_FORGE_PLANETARY_CONSCIOUSNESS_V7_LOCKED_v1.md` |
| State | `~/.sina/forge-planetary-consciousness-v7.json` |
| Receipt | `~/.sina/forge-planetary-consciousness-tick-latest-v7.json` |

Meta-awareness over v6: collect signals → awareness index → meta-thought → self-stabilize.

API: `{ "action": "planetary_consciousness_tick", "dry_run": true }` · `{ "action": "consciousness_status" }`

---

## 30) Reality-Coupled Consciousness (v8)

| Resource | Address |
|----------|---------|
| Module | `scripts/forge_reality_consciousness_v8.py` |
| Law | `SOURCEA_FORGE_REALITY_CONSCIOUSNESS_V8_LOCKED_v1.md` |
| State | `~/.sina/forge-reality-consciousness-v8.json` |
| Receipt | `~/.sina/forge-reality-consciousness-tick-latest-v8.json` |

Couples v7 to live receipts: Mac flags · session gate · cloud autorun · cycle receipts · Forge motor.

API: `{ "action": "reality_consciousness_tick", "dry_run": true }` · `{ "action": "reality_consciousness_status" }`

---

**LOCKED.** Do not hand-edit without superseding law doc + E2E green.
