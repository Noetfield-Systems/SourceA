# Truth Log — Independent Verifier v1

Saved: 2026-06-22T22:15:00Z

## Purpose

Prove whether a cloud autonomy loop exists **without** Cursor, Mac, or agent-generated receipts.

**SSOT:** `data/truth-log-cloud-contract-v1.json`  
**Table:** `public.truth_log`  
**Migration:** `infra/supabase/portfolio-spine/migrations/002_truth_log_v1.sql`

## Who may write

| Source | Allowed | Event |
|--------|---------|-------|
| Cloudflare Cron | yes | `CRON_FIRED` |
| Cloudflare Worker | yes | (extensible) |
| Railway Runtime | yes | `JOB_STARTED`, `JOB_COMPLETED`, `JOB_FAILED`, `QUEUE_ADVANCED` |
| Cursor / Mac / local scripts | **no** | blocked by RLS + Python runtime guard |

## Pass test (60 minutes)

1. Apply migration to portfolio-spine Supabase.
2. Set `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` on Railway FBE and CF Worker secrets.
3. Note `SELECT count(*) FROM public.truth_log` and max `recorded_at`.
4. **Close Cursor. Sleep Mac. Wait 60 minutes.**
5. Re-query Supabase (dashboard or phone) — **not** from Mac terminal.

| Result | Verdict |
|--------|---------|
| New rows appear (especially `CRON_FIRED` ~every 10 min) | **Loop exists** |
| No new rows | **Loop does not exist** |

## Read endpoints (after deploy)

```bash
curl -sS https://sourcea-fbe-runner-production.up.railway.app/truth
curl -sS https://sourcea-fbe-runner-production.up.railway.app/truth/live
```

`/truth/live` returns `minutes_since_last_cron`, `minutes_since_last_job`, `minutes_since_last_queue_advance`.

## SQL (founder verification)

```sql
SELECT id, recorded_at, source, event, deployment_id, queue_head, old_queue_head, receipt_id
FROM public.truth_log
ORDER BY recorded_at DESC
LIMIT 50;
```

## Forbidden as proof

- Agent chat summaries
- `~/.sina/*` receipts
- Markdown status files
- Local JSON cycle files without matching Supabase row
