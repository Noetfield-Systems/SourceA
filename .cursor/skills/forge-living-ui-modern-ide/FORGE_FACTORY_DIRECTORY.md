# SourceA Forge Factory — Full Directory Map

**Saved:** 2026-06-25T14:00:00Z

## Apps (product surfaces)

```
apps/
├── forge-terminal-v1/          # Forge IDE living chat (v2.7) — terminal.js, terminal.css
├── forge-terminal-connect-v1/  # Connect shell + Chat Unify machine (:13029)
│   ├── app.js                  # Tab router (must include forge-ide)
│   ├── forge-connect.css       # IDE iframe sizing
│   ├── forge-quality-bridge.js # Token + quality receipt lookup
│   └── terminal/               # Legacy v1.3.1 fallback (avoid)
├── factory-runtime-spike/      # Temporal/LangGraph factory spike
├── video-ad-factory/           # Video ad forge v02 contract
├── apple-store-api/
├── analytics-intelligence/
└── newmatch/
```

## Scripts — Forge Terminal plane

```
scripts/
├── forge-terminal-server.py              # Entry delegate
├── forge_terminal_connect_server_v1.py   # Connect + API :13029
├── forge_terminal_v1.py                  # run_terminal, chat_turn, execute
├── forge_quality_gate_v1.py              # 11-layer quality engine
├── forge_quality_gate_unit_v1.py         # Unit fixtures
├── forge_terminal_quality_e2e_verify_v1.py
├── forge_terminal_quality_matrix_v1.py
├── forge_terminal_ui_e2e_verify_v1.py
├── forge_terminal_e2e_verify_v1.py
├── forge_terminal_critic_verify_v1.py
├── forge_terminal_execution_matrix_v1.py
├── forge_terminal_desktop_mesh_v1.py     # Chat thread persistence
├── forge_terminal_local_auth_v1.py       # X-Forge-Token
├── forge_terminal_telemetry_v1.py
├── forge_workspace_open_v1.py
├── forge_workspace_catalog_v2.py
├── forge_workspace_v1.py
├── forge_terminal_os_bridge_v1.py
├── validate-forge-terminal-quality-desktop-e2e-v1.sh
├── validate-forge-terminal-desktop-e2e-v1.sh
└── build-forge-terminal-standalone-app-v1.sh
```

## Scripts — Founder language + Chat Unify

```
scripts/
├── chat_founder_language_v1.py           # translate_for_founder (4 sections)
├── founder_reply_translator_v1.py        # Glossary replacements
├── chat-unify-server.py                  # Chat Unify :13023
└── chat-unify-standalone/                # Chat Unify UI (sync with connect-v1)
```

## Scripts — Cloud Forge Factory (drain / v02)

```
scripts/
├── forge_v01_engine_v1.py
├── forge_v02_implement_v1.py
├── forge_v02_drain_v1.py
├── forge_v02_status_v1.py
├── forge_v02_github_v1.py
├── forge_factory_era_transition_v1.py
├── forge_cloud_env_load_v1.py
├── forge__run_v1.py
├── forge__closeout_v1.py
├── forge_critic_loop_v01.py
├── forge_mvp_lib_v1.py
├── forge_router_execute_v01.py
└── forge_task_graph_emit_v01.py
```

## Data — Forge SSOT

```
data/
├── forge-terminal-decision-card-v1.json
├── forge-real-blueprints-v01.json
├── forge-factory-queue-cycle2-v1.json
├── forge-scoring-ssot-v01.json
├── forge-factory-unified-brand-v1.json
├── forge-v02-cloud-contract-v1.json
├── forge-mvp-router-rules-v0.1.json
├── forge-github-source-v02.json
├── founder-reply-glossary-v1.json
├── factory-specs/forge-app-factory-v1.json
├── schemas/forge-task-graph-v0.1.json
├── schemas/forge-input-v1.json
└── icp-compile/forge-product-v1.json
```

## Law + governance

```
brain-os/law/enforcement/
├── SOURCEA_FORGE_TERMINAL_DESKTOP_E2E_LOCKED_v1.md
├── SOURCEA_FORGE_TERMINAL_QUALITY_ENGINE_E2E_LOCKED_v1.md
├── SOURCEA_CLOUD_FORGE_RUN_AUTO_RUNTIME_VOCABULARY_LOCKED_v1.md
├── SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md
└── SOURCEA_CLOUD_FORGE_RUN_FULL_PACK_PATTERN_LOCKED_v1.md
```

## Docs + labs

```
docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md
labs/forge-v0.1/
brand/macos-apps/ForgeTerminalShell.swift
```

## Ports

| Port | Service |
|------|---------|
| 13029 | Forge Terminal Connect (IDE iframe + APIs) |
| 13023 | Chat Unify standalone |
| 13027 | Cloud Workers |

## Receipts (~/.sina)

```
~/.sina/forge-terminal-quality/<run_id>.json
~/.sina/forge-terminal-quality-desktop-e2e-v1.json
~/.sina/forge-terminal-chat-thread-v1.json
~/.sina/forge-terminal-outbox/
```
