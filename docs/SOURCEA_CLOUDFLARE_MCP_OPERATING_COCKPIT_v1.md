# SourceA Cloudflare MCP Operating Cockpit v1

**Saved at:** 2026-06-28T16:16:02Z  
**Purpose:** make Cloudflare MCP + Browser Automation a repeatable SourceA product-ops cockpit, not an ad hoc debugging toy.  
**Scope:** `sourcea.app` public APIs, Site Pulse, Brain Chat, Auto Runtime, Hook Relay, Cloudflare Worker deploy proof.

## One Line

Use Browser Automation to prove product behavior, Observability to prove Worker runtime behavior, Builds to prove deployment behavior, and Bindings to prove Cloudflare state.

## Product API Smoke

Run the light branded route smoke after deploying `sourcea-app-proxy-v1`:

```bash
python3 scripts/sourcea_public_api_smoke_v1.py
```

Required contract: every `/api/*` route returns JSON. No `/api/*` path may fall through to the Pages landing HTML.

## Browser Automation Recipes

1. **Landing console check**
   - Open `https://sourcea.app/`.
   - Check console and network errors.
   - Confirm CTA clicks do not create red requests.

2. **Public API JSON check**
   - Open `https://sourcea.app/api/sourcea/routes/v1`.
   - Confirm JSON schema `sourcea-public-api-routes-v1`.
   - Check `Content-Type` includes JSON.

3. **Site Pulse check**
   - POST one pageview to `/api/site/event/v1`.
   - Open `/api/site/stats/v1`.
   - Confirm pageviews or event counters move.

4. **Brain Chat check**
   - GET `/api/brain/status/v1`.
   - POST a safe public SourceA question to `/api/brain/chat/v1`.
   - Confirm reply, citations, retrieval, and trace fields exist.

5. **Auto Runtime proof check**
   - Open `/api/cloud-forge-run/status/v1`.
   - Confirm queue and observer objects return JSON.
   - Confirm health shows cron `*/10 * * * *`.

## Observability Recipes

Use Cloudflare Observability when the question is “what happened at runtime?”

- Auto Runtime scheduled invocations:
  - service: `sourcea-cloud-auto-runtime-tick-v1`
  - filters: scheduled trigger, errors, upstream status.

- Site Pulse failures:
  - service: `sourcea-site-pulse-v1`
  - filters: errors, POST `/api/site/event/v1`, POST `/api/site/feedback/v1`.

- Brain Chat failures:
  - service: `sourcea-brain-chat-v1`
  - filters: OpenRouter errors, 429/5xx, request exceptions.

- Hook Relay failures:
  - service: `sourcea-hook-relay-v1`
  - filters: non-2xx responses, relay exceptions.

## Builds Recipes

Use Cloudflare Builds when the question is “what code is live?”

- List latest Worker builds before blaming runtime.
- Pull failed build logs for syntax/config errors.
- Compare active Worker code against local `cloud/workers/*/src/index.js` when live behavior disagrees with disk.

## Bindings Recipes

Use Cloudflare Bindings when the question is “what Cloudflare state exists?”

- `sourcea-site-pulse-v1`
  - KV binding: `PULSE_KV`
  - namespace id on disk: `a07c528436c84691be51ebc936184304`
  - used for stats, feedback inbox, dashboard rollups.

- `sourcea-brain-chat-v1`
  - optional trace KV: `BRAIN_CHAT_LOGS`
  - enable when durable public chat traces become required.

## SourceA Priority Order

1. Public route correctness: `/api/*` must return JSON.
2. Site Pulse proof: stats and feedback are real KV-backed product signals.
3. Brain Chat proof: status, retrieval metadata, live tools, and traces are visible.
4. Auto Runtime proof: status, queue, observer, and cron health are visible.
5. Deploy proof: Cloudflare Builds confirm the code that is actually live.
6. Runtime proof: Cloudflare Observability confirms what actually happened.

## Do Not Use MCP For

- Heavy local validator marathons on Mac.
- Guessing secrets or printing secret values.
- Replacing Railway proof for the factory body.
- Treating Cloudflare Queues or D1 as live until bindings exist on disk.
- Making destructive Cloudflare changes without explicit founder approval.

## Proof Endpoints

- `https://sourcea.app/health`
- `https://sourcea.app/api/sourcea/routes/v1`
- `https://sourcea.app/api/site/status/v1`
- `https://sourcea.app/api/site/stats/v1`
- `https://sourcea.app/api/brain/status/v1`
- `https://sourcea.app/api/brain/chat/v1`
- `https://sourcea.app/api/cloud-forge-run/health/v1`
- `https://sourcea.app/api/cloud-forge-run/status/v1`
- `https://sourcea.app/api/cloud-forge-run/queue/v1`

## Ship Rule

Every Cloudflare MCP finding should become one of four artifacts: code fix, route smoke result, observability evidence, or deploy rollback instruction.
