# Pure Flow Pool & Spa — Landing Page (E2E)

**Primary URL:** https://pureflow.sourcea.app

Public contact: `hello@pureflow.sourcea.app` · bookings notify privately via Worker env (not on site).

The `*.workers.dev` URL is disabled (`workers_dev = false`) so your personal Cloudflare account name is not the public address.

Full-stack Cloudflare Worker: static site + `/api/quote` intake + KV leads + email notifications.

## Architecture

```
Browser → Pure Flow Worker
            ├── GET /*        → static assets (HTML/CSS/JS)
            ├── GET /api/health
            └── POST /api/quote → validate → KV store → email founder + customer
```

| Component | Detail |
|-----------|--------|
| Worker | `pureflow-pool` |
| KV | `PUREFLOW_LEADS` — every form submission stored with lead ID |
| Email | Cloudflare `send_email` → private notify inbox (Worker secret) |
| From address | `hello@pureflow.sourcea.app` |
| Custom domain | `pureflow.sourcea.app` (auto-DNS via `custom_domain = true`) |

## Deploy (full e2e)

```bash
cd ~/Desktop/SourceA
python3 scripts/publish_pureflow_landing_v1.py
```

Or:

```bash
cd labs/pure-flow-pool-landing
wrangler deploy
```

Receipt: `~/.sina/pureflow-landing-publish-receipt-v1.json`

## Edit contact info

`config.js` — phone, email (client-side display)  
`wrangler.toml` `[vars]` — NOTIFY_EMAIL, NOTIFY_FROM (server-side)

Then redeploy.

## Test form API

```bash
curl -s https://pureflow.sourcea.app/api/health

curl -s -X POST https://pureflow.sourcea.app/api/quote \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"you@email.com","phone":"6045551234","postal":"V6K1A1","property":"pool","interest":"weekly","message":"hello"}'
```

## Email setup (one-time)

If `emailSent: false` in API response, enable Cloudflare Email Sending on `sourcea.app`:

1. Cloudflare Dashboard → Email → Email Sending → enable `sourcea.app`
2. Redeploy worker

Leads are **always saved to KV** even if email fails.

## Deep links

- `?interest=weekly&quote=1`
- `?interest=opening&property=pool&quote=1`

## Files

| File | Purpose |
|------|---------|
| `index.html` | Landing page |
| `styles.css` / `script.js` | UI + form → `/api/quote` |
| `config.js` | Client config |
| `worker/index.js` | API + asset router |
| `wrangler.toml` | Worker bindings + custom domain |
