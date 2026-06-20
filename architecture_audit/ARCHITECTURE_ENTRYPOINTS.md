# ARCHITECTURE_ENTRYPOINTS.md

## Production hub (SSOT)

| Entry | Path | Role |
|-------|------|------|
| **Server** | `scripts/sina-command-server.py` | Unified HTTP server: static UI + ~150 API routes on `:13020` |
| **Startup shell** | `scripts/serve-sina-command.sh` | Health check, optional panel build, `nohup` server, PID `~/.sina/command-server.pid` |
| **UI HTML** | `agent-control-panel/index.html` | Shell layout; preloads `/command-data-shell.json` |
| **UI JS** | `agent-control-panel/assets/app.js` | ~9k lines: routing, fetch, render, polling |
| **UI CSS** | `agent-control-panel/assets/app.css`, `theme-duo.css` | Styling |
| **Lazy pages** | `assets/pages-detail.js`, `journey-ui.js` | Supplemental UI modules |

## Legacy / alternate entrypoints

| Entry | Path | Status |
|-------|------|--------|
| Legacy API | `scripts/sina-command-api.py` | Superseded; direct `build_payload`+`write_panel_outputs` (no cache layer) |
| Strict CI build | `scripts/build-sina-command-panel.py` | Offline panel generation + 40+ validators when `SINA_AUDIT_STRICT=1` |
| Agent hub refresh | `scripts/hub_self_refresh_v1.py` | `GET /api/hub-sync` (light) or `POST /refresh` (full) |
| Align UI | `scripts/align_command_data_ui_v1.py` | Re-pull panels after hub-sync-only refresh |
| Heal shell | `scripts/heal_command_data_shell_v1.py` | Re-strip heavy keys into shell JSON |
| Live agent reply | `scripts/live-agent-cursor-reply.sh` | `build_payload` + `write_panel_outputs` on maintainer reply |

## Server boot sequence

```
serve-sina-command.sh
  ├─ health_ok? → exit 0 (unless SINA_FORCE_RESTART=1)
  ├─ optional background: build-sina-command-panel.py (SINA_PANEL_BUILD_ON_START=1)
  └─ nohup python3 sina-command-server.py → ~/.sina/command-server.log

sina-command-server.py::main()
  ├─ _bootstrap_vault_env()
  ├─ warm_hub_cache_from_disk()  ← reads command-data.json into _HUB_CACHE
  ├─ if missing command-data.json → hub_after_mutation(write_html=True)  [COLD START FULL REBUILD]
  ├─ ThreadingHTTPServer(("127.0.0.1", 13020), SinaCommandHandler)
  ├─ _kick_autorun_on_hub_start()  [background thread]
  └─ serve_forever()
```

## UI boot sequence

```
index.html loads
  └─ app.js IIFE
       ├─ loadCommandData()
       │    ├─ loadCommandDataShell() → GET /command-data-shell.json
       │    └─ loadCommandDataFull() [background] → GET /command-data.json
       ├─ buildNav() + render()
       └─ tab switch → ensureFullCommandData() if HEAVY_TAB_KEYS[tab] missing
```

## Payload builders

| Function | File | Trigger |
|----------|------|---------|
| `build_payload()` | `sina_command_lib.py:3503` | Cache miss, hub-sync, CI build, refresh |
| `build_shell_payload()` | `sina_command_lib.py:4184` | Strips `HEAVY_PAYLOAD_KEYS` |
| `get_hub_payload()` | `sina_command_lib.py:4167` | 180s TTL cache wrapper |
| `hub_after_mutation()` | `sina_command_lib.py:4199` | POST mutations, `/refresh` |
| `write_panel_outputs()` | `sina_command_lib.py:4289` | Atomic JSON + optional index.html |
| `run_refresh_pipeline()` | `sina_command_lib.py:2867` | Only when `run_refresh_scripts=True` |

## Refresh scripts (pipeline subprocesses)

When `run_refresh_scripts=True`:

1. `python3 scripts/scan-cursor-agent-fleet.py` (180s timeout)
2. `python3 scripts/update-program-progress.py` (300s)
3. `python3 scripts/build-sina-daily-bowl.py` (300s)
4. `python3 scripts/export-master-orders-json.py` (300s)
5. Log-only step: "Panel + KPI scan"

Env on children: `SINA_SKIP_NESTED_BOWL=1`, `SINA_SKIP_PANEL_BUILD=1`, `SINA_SKIP_FLEET_SCAN=1`

## Static JSON generation outputs

| File | Writer | Reader |
|------|--------|--------|
| `agent-control-panel/command-data.json` | `write_panel_outputs` | UI full load, `warm_hub_cache_from_disk` |
| `agent-control-panel/command-data-shell.json` | `write_panel_outputs` | UI first paint, shell cap 500KB |
| `agent-control-panel/index.html` | `write_panel_outputs` (from `assets/shell.html` template) | Browser |
| `~/.sina/fleet_build_snapshot_v1.json` | `build-sina-command-panel._log_fleet_build_snapshot` | Fleet validators |

## API registration

- **No framework router** — `BaseHTTPRequestHandler.do_GET` / `do_POST` with `if path ==` chains in `sina-command-server.py`
- **CORS:** `do_OPTIONS` → 204
- **Static fallback:** unmatched GET → `_serve_static` → `agent-control-panel/**`

## Middleware (implicit)

| Concern | Implementation |
|---------|----------------|
| Cache | `_HUB_CACHE` + `_HUB_LOCK` in `sina_command_lib` |
| Threading | `ThreadingHTTPServer` — concurrent requests |
| Auth | None on localhost (founder machine trust model) |
| Atomic writes | `_write_text_atomic` temp+replace |
| Factory lock | `factory_validation_lock_v1.py` (strict build / E2E) |

## Mutation handlers (hub_after_mutation fanout)

~30 POST paths in `sina-command-server.py` call `hub_after_mutation()` on success. See `REBUILD_TRIGGER_MAP.md`.

**Intelligence circle tiering (2026-06-10 partial):**
- L0: `clear_session`, `select_agent`, dry `chat` → `invalidate_hub_cache()` only
- L2: real `chat`, `talk`, etc. → full `hub_after_mutation()`

## Polling (no WebSocket)

| Interval | Location | Endpoint |
|----------|----------|----------|
| 5s | `app.js` advisor track | `GET /api/founder-advisor-discussion` |
| 25s | Goal1 auto-refresh copy | implied hub-sync |
| On tab | `refreshIntelligenceStatus`, `refreshAgentLoopStatus` | per-tab GET/POST |
| Silent | `hubAutoSync()` | `GET /api/hub-sync` |

**WebSocket:** None. All real-time behavior is HTTP polling.

## Command panel generation (strict CI path)

```
build-sina-command-panel.py::main()
  ├─ factory_validation_lock acquire (if strict)
  ├─ pre-build audits (governance, nav, personal_db)
  ├─ update-program-progress.py
  ├─ build_payload(run_refresh_scripts=False)
  ├─ write_panel_outputs (full HTML)
  ├─ eval/graph seed subprocesses
  ├─ 40+ validator scripts (bash/python)
  └─ phase-s0 SSOT alignment (retry loop)
```

## Cache layers

| Layer | TTL | Invalidation |
|-------|-----|--------------|
| `_HUB_CACHE` | 180s | `invalidate_hub_cache()`, `write_panel_outputs`, `force=True` |
| `warm_hub_cache_from_disk` | Until invalidate | Reads stale `command-data.json` at boot |
| Factory `_now_cache` | 5s | `factory_control_v1` |
| Factory `_gate_cache` | 2s | `factory_control_v1` |
| Browser `COMMAND_DATA` | Session | `applyPayload()` on fetch |

## Related enforcement docs

- `SINA_HUB_E2E_CANCELLED_LOCKED_v1.md` — E2E gate off
- `brain-os/law/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` — no full E2E in brain chat
- Founder law: hub Refresh/Actions only — no Terminal
