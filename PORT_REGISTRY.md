# Port Registry (live — do not edit by hand)

**Updated:** 2026-06-12T16:59:07Z  
**Agent:** `SinaPromptOS/port_registry_agent`  
**Law:** `SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md`  

> **Mandatory:** Every agent reads this file **before** binding or documenting any port.

**Summary:** 3 busy · 44 free · **2 violations**

## Violations (fix before new binds)

- **:13020** — Port 13020 is bound by unknown_python but catalog owner is sina_command; no other product may listen here.
- **:13030** — Port 13030 is bound by unknown_python but catalog owner is hub_rebuild_worker; no other product may listen here.

## Live table

| Port | Status | Declared owner | Purpose | Listener |
|------|--------|----------------|---------|----------|
| **3000** | free | `mono_ui` | Mono ui/ observation dashboard; Noetfield dev-port-redirect  | — |
| **3001** | free | `virlux_dashboard` | VIRLUX product dashboard (Delivery repo); not DevBridge | — |
| **3002** | free | `virlux_api` | VIRLUX API — DevBridge desk must NOT bind here | — |
| **3003** | free | `asf_reserved` | ASF reserved — not for DevBridge desk (locked with 3000–3002 | — |
| **3004** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3005** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3006** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3007** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3008** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3009** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3010** | free | `devbridge_desk` | DevBridge Safari desk (npm start auto-pick) | — |
| **3100** | free | `virlux_marketing` | VIRLUX marketing site | — |
| **8000** | free | `sinaai_runtime` | SinaaiRuntime primary execution spine (Telegram PAIOS, fleet | — |
| **8001** | free | `golden_edge` | Golden Edge optional scoring; Noetfield platform/governance  | — |
| **8010** | free | `mono_legacy_backend` | Legacy backend — frozen | — |
| **8020** | free | `mono_legacy_cacos` | Legacy cacos — deprecated | — |
| **8082** | free | `expo_dev` | Expo / React Native dev server (typical) | — |
| **8765** | free | `sinapromptos_streamlit` | SinaPromptOS Streamlit UI (run-ui.sh) | — |
| **8766** | busy | `devbridge_agent` | DevBridge WebSocket agent (wire lane); Prompt OS FastAPI ske | `devbridge_agent` pid 60110 |
| **8767** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8768** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8769** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8770** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8771** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8772** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8773** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8774** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8775** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8776** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8777** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8778** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8779** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8780** | free | `devbridge_relay` | DevBridge relay server (npm run relay:dev) | — |
| **8781** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8782** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8783** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8784** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8785** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **8786** | free | `devbridge_agent_fallback` | DevBridge agent fallback range if 8766 busy | — |
| **9473** | free | `cursor_os_pro` | Cursor OS Pro bridge / link server | — |
| **13000** | free | `noetfield_dev` | Noetfield Next cognitive dashboard (internal) | — |
| **13020** | busy | `sina_command` | Sina Command hub UI + API (browser entry, tier router) | `unknown_python` pid 58469 |
| **13030** | busy | `hub_rebuild_worker` | Hub rebuild queue consumer (external worker, Phase N1) | `unknown_python` pid 58542 |
| **13031** | free | `hub_state_service` | Hub State API scaffold (N2 — optional until ASF approves) | — |
| **13032** | free | `hub_agent_runtime` | Hub Agent runtime scaffold (N3 — optional until ASF approves | — |
| **13080** | free | `noetfield_dev` | Noetfield unified public proxy (www) | — |
| **18002** | free | `noetfield_dev` | Noetfield governance-console dev API | — |

## Suggested (agents)

- **DevBridge desk → port 3004** (`npm start`)
- **DevBridge agent → port 8766**
- **Never desk on 3000–3003**

## Refresh

```bash
cd ~/Desktop/SinaPromptOS && source .venv/bin/activate
python main.py --port-registry
```

Runs automatically at start of `./scripts/run-full-cycle.sh`.
