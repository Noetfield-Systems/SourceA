# NOOS loop executor (Fly)

Bounded Python runtime for 24/7 NOOS — **one tick per `POST /loop`**, no daemon.

## Architecture

Law: `data/noos-runtime-architecture-v1.json`

| Platform | Role |
|----------|------|
| **Cloudflare Workers Paid** | Scheduler · dispatcher · heartbeat — no Python |
| **Fly `noos-loop-executor`** | `GET /health` · `POST /loop` · gates · receipts |
| **GitHub Actions** | CI / manual / emergency only |

**Current gate:** CF NOOS fleet cron stays **off** until Fly health + authenticated `/loop` pass `scripts/validate-noos-loop-executor-v1.sh`.

## Local

```bash
export NOOS_LOOP_SECRET=dev-secret
export NOOS_EXECUTOR_ROOT="$(pwd)"
export PYTHONPATH=apps/noos-loop-executor
python3 apps/noos-loop-executor/noos_loop_executor/server.py --port 8080
```

## Validate

```bash
bash scripts/validate-noos-loop-executor-v1.sh
```

## Deploy Fly

```bash
fly secrets set NOOS_LOOP_SECRET=<long-random> -a noos-loop-executor
bash scripts/deploy_noos_loop_executor_fly_v1.sh
NOOS_LOOP_EXECUTOR_URL=https://noos-loop-executor.fly.dev \
  NOOS_LOOP_SECRET=<secret> \
  bash scripts/validate-noos-loop-executor-v1.sh
```

## Auth

Header: `X-NOOS-Loop-Secret` (env `NOOS_LOOP_SECRET` on Fly).

## Next (after Fly green)

1. CF worker `noos-loop-dispatch-v1` POSTs to Fly `/loop` (replaces `noos-loop-fleet-tick-v1` GHA dispatch).
2. Re-enable CF cron on dispatch worker only.
