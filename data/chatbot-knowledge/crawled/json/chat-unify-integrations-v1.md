---
updated: 2026-06-27T06:08:27Z
lane: developer
source_path: sites/SourceA-landing/green-unified/data/chat-unify-integrations-v1.json
public: true
kind: json
---

# Chat Unify Integrations V1

- **schema**: chat-unify-integrations-v1
- **version**: 1.0.0
- **saved_at**: 2026-06-23T23:55:00Z
- **product**: Chat Unify Connect
- **tagline**: Agent control bridge — Cursor · cloud · automation · proof
- **base_url**: http://127.0.0.1:13023
## api
- **integrations**: /api/integrations/v1
- **hook**: /api/integrations/v1/hook
- **manifest**: /api/integrations/v1/manifest
- **chat_unify**: /api/chat-unify
- **health**: /health
## lanes
## cursor_local
- **id**: cursor_local
- **label**: Cursor IDE (local)
- **category**: ide
- **description**: Send forged missions and close orders into your local Cursor Worker chat — inbox-first, receipt logged.
#### actions
- send_mission
- send_close_order
- copy_hook
- **docs**: Paste from Prompt Forge → Connect → Send to Cursor
## cursor_cloud
- **id**: cursor_cloud
- **label**: Cursor Cloud / API
- **category**: ide
- **description**: Cloud agents and API pool — dispatch through controlled gates, not raw bypass.
#### actions
- status
- dispatch_via_hub
#### env
- CURSOR_API_KEY
- [REDACTED]
## n8n
- **id**: n8n
- **label**: n8n Automation
- **category**: automation
- **description**: Webhook triggers · transcript ingest · scheduled proof exports.
- **port**: 13026
- **url**: http://127.0.0.1:13026/
#### actions
- wire
- trigger_webhook
## cloud_workers
- **id**: cloud_workers
- **label**: Cloud Workers
- **category**: cloud
- **description**: Railway factory body — Cloud Forge Run + Auto Runtime. Mac observes; cloud executes.
- **port**: 13027
- **url**: http://127.0.0.1:13027/
- **dispatch**: POST /api/cloud-worker/dispatch/v1
## webhook_inbound
- **id**: webhook_inbound
- **label**: Inbound webhooks
- **category**: automation
- **description**: Any client (Zapier · Make · custom CI) POSTs events — Chat Unify routes to the right machine.
- **hook_url**: http://127.0.0.1:13023/api/integrations/v1/hook
#### actions
- forge_and_queue
- verify_paste
- proof_pack
## mcp_ready
- **id**: mcp_ready
- **label**: MCP / plugin manifest
- **category**: extensibility
- **description**: Machine-readable manifest for Cursor MCP servers and partner integrations.
- **manifest**: /api/integrations/v1/manifest
- **file**: data/chat-unify-cursor-plugin-v1.json
## machines
## prompt_forge
- **id**: prompt_forge
- **tab**: forge
- **pipeline**: 3
## founder_loop
- **id**: founder_loop
- **tab**: founder
- **pipeline**: verify
## ord_loop
- **id**: ord_loop
- **tab**: ord
- **pipeline**: audit
## proof_pack
- **id**: proof_pack
- **tab**: proofpack
- **pipeline**: seal
## official_form
- **id**: official_form
- **tab**: form
- **pipeline**: decide
## api_station
- **id**: api_station
- **tab**: api
- **pipeline**: dispatch
## hub_pro
- **id**: hub_pro
- **tab**: hubpro
- **pipeline**: ops
