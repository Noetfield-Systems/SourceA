# Truth Layer Autonomy Test Procedure v1

Saved: 2026-06-22T19:45:00Z

## Pass criteria

AUTONOMY NOT PROVEN unless all steps below produce independent evidence.

## Steps

1. Apply Supabase migration `001_truth_layer_cycle_receipts_v1.sql` to portfolio-spine.
2. Set on Railway `sourcea-fbe-runner`: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `CLOUD_DRAIN_AUTO_PROCEED=true`.
3. Redeploy FBE runner after migration + env.
4. Record Mac power-off time (UTC).
5. Shut down Mac completely (not sleep).
6. Wait minimum 30 minutes (≥2 CF cron intervals at `*/10 * * * *`).
7. Power Mac on. Do not trigger proceed manually.

## Evidence collection

### A — Supabase (SOURCE 1)

```sql
SELECT id, cycle_id, execution_id, queue_head_before, queue_head_after,
       started_at, finished_at, duration_ms, trigger_source, verdict, created_at
FROM public.cycle_receipts
WHERE created_at > '<mac_off_at_utc>'
ORDER BY created_at ASC;
```

Required: minimum 3 rows where `created_at` is while Mac was off.

Each row must have all contract fields non-null:

- cycle_id
- execution_id
- queue_head_before
- queue_head_after
- started_at
- finished_at
- duration_ms

Missing any field → VERDICT = FAIL.

### B — Cloudflare (SOURCE 3)

Cloudflare dashboard → Workers → `sourcea-cloud-drain-tick-v1` → Logs.

Filter cron executions between Mac off and Mac on.

Export timestamps showing `scheduled` events every ~10 minutes.

Each cron must correspond to one Supabase receipt within ±2 minutes.

### C — Railway (SOURCE 2)

```bash
railway logs -s sourcea-fbe-runner -e production --since 2h --json
```

Find `[FBE KERNEL] "POST /api/cloud-drain/proceed/v1` lines matching Supabase `started_at` windows.

Record `RAILWAY_DEPLOYMENT_INSTANCE_ID` from runtime env; must match Supabase `execution_id` for GREEN rows.

### D — Truth status (observer)

```bash
curl -sS https://sourcea-fbe-runner-production.up.railway.app/truth/status
```

`display` must be `GREEN` only if:

- Supabase has a new receipt
- `execution_id` matches live Railway instance
- `last_verdict` is `GREEN`

Otherwise: RED.

## Autonomy verdict

| Check | Required |
|-------|----------|
| Mac offline ≥30 min | yes |
| ≥3 Supabase receipts while Mac offline | yes |
| CF cron timestamps align | yes |
| Railway proceed logs align | yes |
| execution_id match on GREEN rows | yes |
| No manual proceed during window | yes |

If any check fails: **AUTONOMY NOT PROVEN**.

## Forbidden as proof

- Agent chat summaries
- Markdown status reports
- Disk-only cycle JSON without Supabase row
- Inferred or simulated receipts
- Claims without `receipt_row_id` + `execution_id` + timestamp
