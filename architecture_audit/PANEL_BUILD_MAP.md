# PANEL_BUILD_MAP.md

## Output artifacts

| Artifact | Path | Size (typical) | Cap |
|----------|------|----------------|-----|
| Full payload | `agent-control-panel/command-data.json` | ~2.7MB | None |
| Shell payload | `agent-control-panel/command-data-shell.json` | <500KB | `SHELL_MAX_BYTES` |
| HTML | `agent-control-panel/index.html` | ~KB | Injected from `assets/shell.html` |

## build_payload() dependency graph

```
build_payload(run_refresh_scripts: bool)
│
├─ [if run_refresh_scripts] run_refresh_pipeline()
│    ├─ scan-cursor-agent-fleet.py
│    ├─ update-program-progress.py → PROGRAM_PROGRESS.json
│    ├─ build-sina-daily-bowl.py → sina-bowl/state.json, DAILY_BOWL.md
│    └─ export-master-orders-json.py → MASTER_ORDERS.json
│
├─ _maybe_export_master_orders() [if not refresh path]
├─ load_json: BOWL_STATE, FLEET, MASTER_ORDERS, PROGRAM_PROGRESS, MERGEPACK
├─ fetch_mergepack_kpi()
├─ command_center_payload()
├─ ecosystem_subjects.ecosystem_payload() OR founder_threads fallback
├─ subprocess healthy-drain-orchestrator-v1.py status
├─ goal1_auto_run_payload() → subprocess broker poll
├─ hub_home_founder_payload()
├─ strategic_synthesis_payload()
├─ loop_payload()
├─ semej_payload()
├─ commitments_payload()
├─ audit_backlog_payload()
├─ reviews_payload()
├─ workspaces_payload()
├─ incident_room_payload()
├─ conflict_room_payload()
├─ council_room_payload()
├─ scoreboard_payload()
├─ essay_discourse, knowledge_library, execution_spine, …
├─ intelligence_circle.circle_payload()
├─ system_roadmap_payload()
├─ important_docs_index
├─ governance_drift, governance_unification
├─ sourcea_sa_queue_payload() → sync_sa_queue_into_payload
├─ prompt_queue.queue_payload()
├─ prompt_direction.direction_payload()
├─ ai_advisory, founder_notes, n8n, agent_skills, …
└─ returns dict schema_version=5, built_at=ISO
```

## HEAVY_PAYLOAD_KEYS (shell exclusion list)

40 keys deferred from shell including:
`fleet`, `ecosystem`, `council_room`, `agent_loop`, `intelligence_circle`, `agent_scoreboard`, `prompt_queue`, `semej`, `execution_spine`, `governance_drift`, `commitments`, `founder_notes`, …

Full list: `sina_command_lib.py:4091–4140`

## build_shell_payload()

```python
{k: v for k, v in full.items() if k not in HEAVY_PAYLOAD_KEYS}
```

## write_panel_outputs()

```
write_panel_outputs(payload, json_only=False)
├─ build_shell_payload(payload)
├─ _write_text_atomic(command-data.json)
├─ _write_text_atomic(command-data-shell.json)
├─ verify_command_data_atomic()
│    └─ on fail: heal_command_data_shell_from_disk(force=True)
├─ _HUB_CACHE = payload (in-memory update)
└─ [if not json_only and shell.html exists]
     └─ inject __COMMAND_DATA_LAZY + __BUILD_STAMP__ → index.html
```

## hub_after_mutation() (runtime refresh)

```
hub_after_mutation(run_refresh_scripts=False, write_html=False)
├─ invalidate_hub_cache()
├─ get_hub_payload(force=True, run_refresh_scripts=...)
│    └─ build_payload(...)
├─ sync_sa_queue_into_payload(payload)
├─ _apply_factory_freeze_from_lib(payload)  # imports build panel module
├─ write_panel_outputs(payload, json_only=not write_html)
└─ subprocess validate-hub-p0-no-autorun-v1.sh (90s timeout)
```

## Strict CI build path (offline)

```
build-sina-command-panel.py
├─ Does NOT call run_refresh_pipeline by default
├─ update-program-progress.py (SINA_SKIP_NESTED_BOWL, SINA_SKIP_FLEET_SCAN)
├─ build_payload(run_refresh_scripts=False)
├─ write_panel_outputs (full HTML first time)
├─ run_eval + run_eval_1b + graph executor seed
├─ 40+ validators
└─ phase-s0 SSOT alignment (up to 3 retries)
```

## Tab builders (lazy API pattern)

UI `HEAVY_TAB_KEYS` in `app.js` maps tabs → payload keys. When shell lacks key, tab fetch uses dedicated `/api/*`:

| Tab | Payload key | API |
|-----|-------------|-----|
| intelligence | intelligence_circle | POST/GET `/api/intelligence-circle` |
| agent-loop | agent_loop | GET/POST `/api/agent-loop` |
| council-room | council_room | GET `/api/council-room` |
| agent-scoreboard | agent_scoreboard | GET/POST `/api/agent-scoreboard` |
| prompt-feed | prompt_queue | GET `/api/prompt-queue` |

## Payload mergers (client)

`app.js`:
- `mergeCommandPayload(payload)` — shallow merge into `D`
- `applyPayload(json.data)` — used after `/refresh`, hub-sync, circleApi when `json.data` present

## JSON generators (per-module)

Each `*_payload()` function in `scripts/` is effectively a mini JSON generator. `build_payload` orchestrates ~50 of them synchronously in one thread.

## Refresh vs strict build

| Path | `run_refresh_scripts` | Writes disk SSOT | Writes panel |
|------|----------------------|------------------|--------------|
| `POST /refresh` | True | Yes (pipeline) | Yes |
| `hub_after_mutation()` default | False | No | Yes |
| `GET /api/hub-sync` | False | No | No (in-memory only) |
| `build-sina-command-panel.py` | False | via update-progress only | Yes |
