# noetfield-nerve-probe-v1 — SETUP

**Cron:** `*/15 * * * *`  
**Probes:** `nf_intake_e2e` · `greeting` · `drift` · `uptime`

## Deploy

```bash
cd cloud/workers/noetfield-nerve-probe-v1
npx wrangler deploy
```

## Secrets (Cloudflare dashboard)

| Secret | Purpose |
|--------|---------|
| `SUPABASE_URL` | portfolio-spine REST |
| `SUPABASE_SERVICE_ROLE_KEY` | insert probe + intake rows |
| `TELEGRAM_BOT_TOKEN` | alert on probe FAIL |
| `TELEGRAM_ALERT_CHAT_ID` | founder chat id |
| `NERVE_PROBE_HEALTH_URL` | optional self health override |

## Apply migration 013 (founder/CI)

```bash
bash scripts/apply_portfolio_spine_migrations_v1.sh
```

## nf_intake_e2e PASS (Telegram+DB)

1. `POST /api/noetfield/intake/v1` with `probe:true`
2. Row in `nf_intake_submissions` read-back
3. `telegram_notified=true` on row

```bash
python3 scripts/nf_intake_e2e_v1.py --json
```

## Manual tick

```bash
curl -X POST https://noetfield-nerve-probe-v1.sina-kazemnezhad-ca.workers.dev/run
```
