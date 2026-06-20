# CALL_GRAPH.md

## Primary request path (GET tab data — light)

```
Browser tab open
  └─ app.js::showTab(tab)
       └─ [if tabNeedsFullLoad] ensureFullCommandData()
            └─ loadCommandDataFull()
                 └─ fetch GET /command-data.json
                      └─ SinaCommandHandler.do_GET
                           └─ command_data_response()
                                └─ get_hub_payload()
                                     ├─ [cache hit TTL 180s] return _HUB_CACHE
                                     └─ [miss] build_payload(run_refresh_scripts=False)
                                          └─ [50+ module payload calls]
                                               └─ return JSON → Browser
```

## Primary mutation path (POST — heavy)

```
Browser POST /api/{module}
  └─ SinaCommandHandler.do_POST
       └─ {module}.handle_action(body)
            └─ [writes module SSOT files]
            └─ [if success] hub_after_mutation()
                 ├─ invalidate_hub_cache()
                 ├─ get_hub_payload(force=True)
                 │    └─ build_payload(run_refresh_scripts=False)
                 ├─ sync_sa_queue_into_payload()
                 ├─ _apply_factory_freeze_from_lib()
                 ├─ write_panel_outputs()
                 │    ├─ build_shell_payload()
                 │    ├─ _write_text_atomic(command-data.json)
                 │    ├─ _write_text_atomic(command-data-shell.json)
                 │    └─ verify_command_data_atomic()
                 └─ subprocess validate-hub-p0-no-autorun-v1.sh
```

## POST /refresh path (expensive)

```
app.js::refreshFromApi()
  └─ fetch POST /refresh (120s client timeout)
       └─ hub_after_mutation(run_refresh_scripts=True, write_html=True)
            └─ build_payload(run_refresh_scripts=True)
                 └─ run_refresh_pipeline()
                      ├─ subprocess scan-cursor-agent-fleet.py
                      ├─ subprocess update-program-progress.py
                      ├─ subprocess build-sina-daily-bowl.py
                      └─ subprocess export-master-orders-json.py
            └─ write_panel_outputs(..., json_only=False)  # includes index.html
```

## Intelligence circle — Clear Session (L0 path)

```
app.js click "Clear session"
  └─ circleApi({ action: "clear_session", agent_id })
       └─ POST /api/intelligence-circle
            └─ handle_circle_action()
                 ├─ clear_agent_chat(agent_id)
                 │    ├─ _load_config()
                 │    ├─ _save_config()  → ~/.sina/intelligence-circle-config.json
                 │    └─ _clear_agent_session()
                 └─ circle_payload(hub_payload=get_hub_payload())
            └─ [L0] invalidate_hub_cache()  # NO hub_after_mutation
            └─ return JSON (circle fields in response body)
       └─ app.js merges json into D.intelligence_circle
```

## Intelligence circle — Chat (L2 path)

```
circleApi({ action: "chat", inject_cursor: false })
  └─ talk_to_live_agent() → session write, inject_skipped=true
  └─ [L0 if inject_skipped] invalidate_hub_cache()
  └─ OR [L2] hub_after_mutation() → full rebuild
```

## Strict CI build path

```
build-sina-command-panel.py::main()
  └─ _main_body()
       ├─ _run_audit(audit_agent_governance_e2e.py)
       ├─ _run_audit(audit_essentials_nav.py)
       ├─ _run_update_program_progress()
       ├─ build_payload()
       ├─ _write_panel() → write_panel_outputs()
       ├─ run_eval / run_eval_1b / graph executor
       ├─ _run_audit × 40 validators
       └─ validate-phase-s0-ssot-alignment-v1.sh
```

## find_critical_bugs path (no backend E2E as of 2026-06-10)

```
find_critical_bugs.py::main()
  ├─ _ensure_hub_via_serve()
  ├─ heal_command_data_shell_from_disk()
  ├─ audit_essentials_nav.py
  ├─ audit_hub_source_alignment.py
  ├─ audit_agent_governance_e2e.py
  ├─ [REMOVED] audit_backend_e2e.py
  ├─ SHELL_VALIDATORS × ~25 bash scripts
  └─ [if critical 0] append_repo_execution_log_v1.append_on_ci_pass()
```

## Recursive paths

| Cycle | Mitigation |
|-------|------------|
| refresh pipeline → update-progress → bowl → panel | `SINA_SKIP_NESTED_BOWL`, `SINA_SKIP_PANEL_BUILD` env |
| get_hub_payload during hub_after_mutation | `_HUB_LOCK` serializes |
| build_payload → healthy-drain subprocess → reads queue → may trigger truth rebuild | External scripts, not direct recursion |

## Circular paths (logical)

```
hub_after_mutation → write_panel_outputs → verify → heal_shell → read command-data.json
  → may call build_payload indirectly if heal fails badly

POST /refresh → E2E audit → POST /refresh  [BROKEN when E2E concurrent — E2E cancelled]
```

## Expensive path call depth

```
POST /refresh
  depth ~8, wall time ~230s
  fanout: 4 subprocesses + 50 Python imports + 2 JSON writes + 1 bash validator + HTML write
```

## Termination points

| Path | Terminates at |
|------|---------------|
| GET /api/* read-only | JSON response (no disk write) |
| L0 IC mutation | `invalidate_hub_cache` + HTTP 200 |
| L2 mutation | `write_panel_outputs` complete |
| /refresh | `write_panel_outputs` + HTML |
| Strict build | `sys.exit(0)` or validator failure |
