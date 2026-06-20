# API_MAP.md

Complete HTTP surface for `scripts/sina-command-server.py` on `127.0.0.1:13020`.

**Router:** No framework — `SinaCommandHandler.do_GET` / `do_POST` path equality checks.  
**Middleware:** None (stdlib `ThreadingHTTPServer`).  
**Auth:** Localhost-only binding; founder actions gated in UI + branch handlers.

## Summary counts

| Method | Routes | hub_after_mutation on success | build_payload in GET |
|--------|--------|------------------------------|----------------------|
| GET | ~105 | — | 3 heavy paths |
| POST | ~52 | ~28 conditional | 2 goal1 paths |
| Static | `/*` fallback | — | — |

## Payload size reference

| Endpoint | Typical size | Notes |
|----------|--------------|-------|
| `/command-data.json` | ~2.7 MB | Full panel |
| `/command-data-shell.json` | ~200–400 KB | Stripped `HEAVY_PAYLOAD_KEYS` |
| `/api/hub-sync` | ~2.7 MB | Full in-memory build |
| Module GET `/api/*` | 1–50 KB | Per-module |
| pre_llm v1 GETs | 10–500 KB | May scan repo on `force=1` |

---

## Tier A — Hub core (highest traffic)

### GET `/health`
- **Handler:** inline `_json`
- **Files:** `sina-command-server.py`
- **Calls:** none
- **Disk:** none
- **Validators:** none
- **Complexity:** O(1)

### GET `/status`
- **Handler:** inline + `live_eval_available()`
- **Files:** `healthy_queue_blocker_lib.py`
- **Disk:** read eval gate state
- **Complexity:** low

### GET `/command-data.json` | `/api/state`
- **Handler:** `command_data_response()` → `get_hub_payload()`
- **Files:** `sina_command_lib.py`
- **Calls:** cache hit OR `build_payload(False)`
- **Disk:** read cache from disk on boot only; no write
- **Complexity:** medium–heavy on miss

### GET `/command-data-shell.json`
- **Handler:** `command_data_shell_response()` → `build_shell_payload(get_hub_payload())`
- **Disk:** none on read
- **Complexity:** medium on miss

### GET `/api/hub-sync`
- **Handler:** read `command-data-shell.json` from disk (no build on request thread)
- **Files:** `sina-command-server.py` only
- **Disk:** read shell JSON
- **Validators:** none
- **Complexity:** **light** — O(1) file read
- **Payload:** slim shell slice (~50–400 KB) + `generation_id`

### POST `/refresh`
- **Handler:** `enqueue_rebuild(source="POST /refresh", run_refresh=True)` → **202 queued**
- **Files:** `hub_queue_lib_v1.py` + external worker on `:13030`
- **Disk writes:** none on request thread (worker rebuilds async)
- **Complexity:** **light** on request thread; heavy work in worker
- **Payload:** `{"ok": true, "status": "queued", ...}`

### POST `/api/action`
- **Handler:** `run_branch_action(action_id)`
- **Files:** `sina_command_lib.py` (branch dispatch ~2197–2733)
- **On success:** `hub_after_mutation()` if no `data` in result
- **Disk:** branch-dependent + panel rebuild
- **Complexity:** medium–heavy

### POST `/api/intelligence-circle`
- **Handler:** `handle_circle_action()` in `intelligence_circle.py`
- **L0 (T0):** `clear_session`, `select_agent`, dry `chat` → `invalidate_hub_cache()` only
- **L2 (T2):** real chat/inject → `hub_after_mutation()`
- **Disk:** `~/.sina/intelligence-circle-config.json`, session JSON

---

## Tier B — Founder mutations (hub_after_mutation on success)

| Route | POST handler module | Trigger actions | Tier |
|-------|---------------------|-----------------|------|
| `/api/rule` | `write_rule` | any write | T3 (+refresh scripts) |
| `/todo/done` | `mark_todo_done` | todo close | T3 |
| `/api/ai/advisory` | `sina_ai_advisory.run_advisory` | success | T2 |
| `/api/prompt-queue` | `prompt_queue_action` | success | T2 |
| `/api/prompt-direction` | `prompt_direction_action` | success | T2 |
| `/api/agent-loop` | `agent_loop_action` | start/response/select_workspace | T2 |
| `/api/advisor/chat` | `handle_advisor_action` | action=chat | T2 |
| `/api/semej` | `handle_semej_action` | start/response/capture | T2 |
| `/api/commitments` | `handle_commitments_action` | add/done/pin | T2 |
| `/api/audit-backlog` | `handle_audit_action` | set_status | T2 |
| `/api/agent-review` | `handle_review_action` | submit/set_status | T2 |
| `/api/agent-workspaces` | `handle_workspace_action` | ensure | T2 |
| `/api/workspace-vault` | `handle_vault_action` | deposit/log/ensure | T2 |
| `/api/agent-scoreboard` | `handle_scoreboard_action` | submit/verify | T2 |
| `/api/essay-discourse` | `handle_essay_action` | submit/mark_best | T2 |
| `/api/agent-research` | `research_action` | submit/promote | T2 |
| `/api/incident-room` | `handle_incident_room_action` | non-list | T2 |
| `/api/conflict-room` | `handle_conflict_room_action` | non-list | T2 |
| `/api/founder-requests` | `handle_action` | register/update | T2 |
| `/api/founder-advisor-discussion` | `handle_action` | update_decision | T2 |
| `/api/order-guardian` | `handle_action` | register/refresh_advisory | T2 |
| `/api/founder-agent-guide` | `handle_action` | want/done | T2 |
| `/api/governance-drift` | `handle_drift_action` | run/refresh | T2 |
| `/api/council-room` | `handle_post` / unified | add_directive | T2 |

---

## Tier C — POST without full rebuild

| Route | Handler | Notes |
|-------|---------|-------|
| `/open` | subprocess `open` | No rebuild |
| `/api/apps/launch` | `launch_mini_app` | No rebuild |
| `/api/apps/open` | `open_mini_app` | No rebuild |
| `/api/dispatch-policy-v1` | `dispatch_policy_v1_post` | Autonomy stack |
| `/api/user-workspace-signals-v1` | `user_workspace_signals_v1_payload` | |
| `/api/execution-state-v1` | `execution_state_v1_post` | |
| `/api/goal1-autorun-*` | `run_branch_action` | Branch may rebuild internally |
| `/api/run-goal1-*` | subprocess + `build_payload(False)` | T1 in-memory only |
| `/api/notes` | `add_founder_note` | No hub rebuild |
| `/api/notes/done` | `set_note_status` | No hub rebuild |
| `/api/founder-cursor-send` | `handle_founder_cursor_send` | |
| `/api/site-guide` | `answer_site_question` | Read-only LLM |
| `/api/workspace-mirror` | `handle_mirror_action` | No rebuild |
| `/api/governance-unify` | `handle_unification_action` | No rebuild |
| `/api/apple-health` | `handle_action` | |
| `/api/mac-health` | `handle_action` | |
| `/api/personal-db` | `handle_action` | |
| `/api/n8n/intelligence` | `handle_intelligence_action` | |
| `/shutdown` | `run_emergency_stop` | SIGTERM hub |

---

## Tier D — GET module APIs (read-only)

Each returns module-specific JSON. Most call `get_hub_payload()` or dedicated `*_payload()`.

| Route | Handler function | Uses hub cache |
|-------|------------------|----------------|
| `/api/branches` | `branches_registry()` | no |
| `/api/founder/actions` | `founder_actions_grouped()` | no |
| `/api/goal1-auto-run-status` | `goal1_auto_run_payload()` | no |
| `/api/apps` | `mini_apps_registry()` | no |
| `/api/notes` | `list_notes()` | no |
| `/api/ai/advisory` | `load_cached_advisory()` | no |
| `/api/prompt-queue` | `queue_payload()` | no |
| `/api/prompt-direction` | `direction_payload()` | no |
| `/api/agent-loop` | `loop_payload(hub_payload)` | yes |
| `/api/advisor/chat` | `advisor_payload()` | no |
| `/api/intelligence-circle` | `circle_payload(hub_payload)` | yes |
| `/api/semej` | `semej_payload()` | no |
| `/api/site-guide` | `search_site(q, payload)` | yes |
| `/api/commitments` | `commitments_payload(**ctx)` | yes |
| `/api/audit-backlog` | `audit_backlog_payload()` | no |
| `/api/agent-review` | `reviews_payload()` | no |
| `/api/agent-workspaces` | `workspaces_payload()` | no |
| `/api/workspace-vault` | `handle_vault_action list` | no |
| `/api/workspace-mirror` | `handle_mirror_action get` | no |
| `/api/agent-scoreboard` | `handle_scoreboard_action list` | no |
| `/api/essay-discourse` | `handle_essay_action list` | no |
| `/api/incident-room` | `incident_room_payload` | no |
| `/api/conflict-room` | `conflict_room_payload` | no |
| `/api/founder-requests` | `handle_action list` | no |
| `/api/founder-advisor-discussion` | `handle_action list` | no |
| `/api/agent-truth-bundle-v1` | `build_agent_truth_bundle()` | no |
| `/api/order-guardian` | `handle_action list` | yes |
| `/api/founder-agent-guide` | `handle_action list` | yes |
| `/api/governance-drift` | `handle_drift_action get` | no |
| `/api/governance-unify` | `handle_unification_action list` | no |
| `/api/council-room` | `council_room_payload` | no |
| `/api/important-docs` | `important_docs_payload()` | no |
| `/api/roadmaps-goals` | `roadmaps_goals_payload()` | no |
| `/api/system-roadmap` | `system_roadmap_payload()` | no |
| `/api/meta-reasoning-policy` | `handle_action get` | yes |
| `/api/agent-research` | `research_action list` | no |
| `/api/execution-spine` | `spine_payload` / `read_memory` | no |
| `/api/hub-essentials` | `hub_essentials_payload()` | no |
| `/api/personal-db` | `personal_db_payload()` | no |
| `/api/apple-health` | `apple_health_payload()` | no |
| `/api/mac-health` | `build_report(rescan=False)` | no |
| `/api/n8n` | `automation_payload()` | no |
| `/api/n8n/intelligence` | `handle_intelligence_action` | no |
| `/api/rule` | `read_rule(rel)` | no |

---

## Tier E — Autonomy / pre_llm / runtime v1 APIs (~40 GET routes)

Query-param driven; optional `force_refresh=1` triggers disk scan/cache rebuild per module.

| Prefix | Example handler | Avg complexity |
|--------|-----------------|----------------|
| `/api/execution-intelligence*` | `intelligence_payload` | medium |
| `/api/execution-patterns-v1` | `patterns_v1_payload` | medium |
| `/api/context-intelligence-v1` | `context_intelligence_v1_payload` | medium |
| `/api/execution-context` | `execution_context_payload` | medium |
| `/api/execution-decisions-v1` | `decisions_v1_payload` | low |
| `/api/execution-feedback-v1` | `feedback_v1_payload` | low |
| `/api/planner-upgrade-v1` | `planner_upgrade_v1_payload` | medium |
| `/api/self-optimization-v1` | `self_optimization_v1_payload` | medium |
| `/api/tool-graph-v1` | `tool_graph_v1_payload` | medium |
| `/api/execution-router-v1` | `execution_router_v1_payload` | medium |
| `/api/prompt-router-v1` | `prompt_router_v1_payload` | medium |
| `/api/execution-kernel-v1` | `execution_kernel_v1_payload` | medium |
| `/api/execution-state-v1` | `execution_state_v1_payload` | low |
| `/api/execution-scheduler-v1` | `execution_scheduler_v1_payload` | medium |
| `/api/repair-loop-v1` | `repair_loop_v1_payload` | medium |
| `/api/code-intelligence-v1` | `code_intelligence_v1_payload` | **heavy** on force |
| `/api/graph-fusion-v1` | `graph_fusion_v1_payload` | **heavy** on force |
| `/api/vector-retrieval-v1` | `vector_retrieval_v1_payload` | **heavy** |
| `/api/memory-git-bridge-v1` | `memory_git_bridge_v1_payload` | **heavy** |
| `/api/query-expansion-v1` | `query_expansion_v1_payload` | medium |
| `/api/graph-reasoning-v1` | `graph_reasoning_v1_payload` | **heavy** |
| `/api/context-ranking-v1` | `context_ranking_v1_payload` | medium |
| `/api/planning-engine-v1` | `planning_engine_v1_payload` | medium |
| `/api/tool-router-v1` | `tool_router_v1_payload` | medium |
| `/api/validation-layer-v1` | `validation_layer_v1_payload` | medium |
| `/api/diff-intelligence-v1` | `diff_intelligence_v1_payload` | medium |
| `/api/context-compression-v1` | `context_compression_v1_payload` | medium |
| `/api/context-assembly-v1` | `context_assembly_v1_payload` | medium |
| `/api/model-dispatch-gate-v1` | `gate_status_payload` | low |
| `/api/eval-packet-v1` | `eval_packet_payload` | medium |
| `/api/dispatch-policy-v1` | `dispatch_policy_v1_get` | low |
| `/api/graph-executor-v1` | `graph_executor_v1_payload` | medium |
| `/api/gate-receipts-v1` | `gate_receipts_hub_payload` | low |
| `/api/strategic-synthesis-v1` | `strategic_synthesis_payload` | medium |
| `/api/packet-readiness-v1` | `packet_readiness_hub_payload` | medium |
| `/api/packet-memory-merge-v1` | `packet_memory_merge_v1_payload` | medium |
| `/api/intent-engine-v1` | `intent_engine_v1_payload` | medium |
| `/api/dependency-graph-v1` | `dependency_graph_v1_payload` | **heavy** |
| `/api/semantic-context-fabric-v1` | `semantic_context_fabric_v1_payload` | medium |
| `/api/multi-step-planner-v1` | `multi_step_planner_v1_payload` | medium |
| `/api/runtime-orchestrator-v1` | `runtime_orchestrator_v1_payload` | medium |

---

## Known routing anomalies

Three routes check `self.command == "POST"` inside `do_GET` — **POST to these paths returns 404**:

| Route | Intended POST handler | Status |
|-------|----------------------|--------|
| `/api/eval-packet-v1b` | `eval_1b_run()` | Broken via POST |
| `/api/event-bus-v1` | `publish()` | Broken via POST |
| `/api/agent-rules-in-charge-v1` | `rules_loop_api()` | Broken via POST |

Workaround: use GET with query params where supported, or fix routing (out of scope for audit).

---

## DELETE / PATCH

**None registered.** All mutations are POST with `action` field in JSON body.

---

## Static assets

| Pattern | Handler |
|---------|---------|
| `/`, `/index.html` | `agent-control-panel/index.html` |
| `/assets/*` | `app.js`, `app.css`, etc. |
| Unmatched GET | `_serve_static` with path traversal guard |

---

## API registration model (rebuild note)

To rebuild the hub API surface:

1. Instantiate `ThreadingHTTPServer` on port 13020.
2. Implement `SinaCommandHandler(BaseHTTPRequestHandler)` with `do_GET`/`do_POST`.
3. Import `sina_command_lib` hub functions at module level.
4. Add path branches in order (specific before static fallback).
5. On POST success for founder modules, call `hub_after_mutation()` unless L0 tier.
6. Serve `PANEL_DIR` static files for all non-API paths.
