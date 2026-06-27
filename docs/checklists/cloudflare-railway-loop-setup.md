# Cloudflare + Railway autonomous loop setup

**UTC:** 2026-06-22T23:45:40Z

## Cloudflare Worker (`cloud/workers/cloud-auto-runtime-tick-v1`)

- [ ] `wrangler.toml` `account_id` = main SourceA account (`0d0b967b77e2e5535455d39ff3dae72c`).
- [ ] Cron trigger: `*/10 * * * *` in `wrangler.toml` `[triggers]`.
- [ ] Worker secrets set: `FBE_CLOUD_WORKER_URL`, `CLOUD_FORGE_RUN_AUTO_PROCEED=true`, `FBE_INTERNAL_SECRET`.
- [ ] `FBE_CLOUD_WORKER_URL` = `https://sourcea-fbe-runner-production.up.railway.app`.
- [ ] Deploy: `cd cloud/workers/cloud-auto-runtime-tick-v1 && npx wrangler deploy` (OAuth as main account, not witness).
- [ ] Health: `curl https://<worker-host>/health` → `"ok": true`, `"cron": "*/10 * * * *"`.
- [ ] Tail proof (optional): `wrangler tail --format json` → `"type": "cron"` every 10 min.

## Railway FBE runner

- [ ] Service: `sourcea-fbe-runner` · URL: `https://sourcea-fbe-runner-production.up.railway.app`.
- [ ] Env: `FBE_MODE=headless`, `FBE_INTERNAL_SECRET` matches CF worker, `CLOUD_FORGE_RUN_AUTO_PROCEED=true`.
- [ ] Deploy only via staging script (never bare `railway up` from repo root):

```bash
python3 scripts/deploy_fbe_railway_v1.py
```

- [ ] Confirm deploy SUCCESS in Railway dashboard (note deployment id).
- [ ] Do **not** use `railway redeploy` for code/module fixes — it does not rebuild the image.

## Dockerfile / staging (before every deploy)

- [ ] `cloud/Dockerfile.fbe-runner` COPY includes: observer modules, `cloud_forge_run_queue_path_v1.py`, `cloud_auto_runtime_single_cycle_gate_v1.py`, `hub_cloud_forge_run_proceed_v1.py`, receipts dirs.
- [ ] `scripts/deploy_fbe_railway_v1.py` stages all cloud-forge-run + observer scripts listed in its manifest.

## Post-deploy smoke (curl only)

- [ ] `GET /health` → 200.
- [ ] `GET /api/cloud-forge-run/observer/v1` → `"ok": true` (not `cloud_forge_run_queue_path_v1` missing).
- [ ] `GET /api/cloud-forge-run/queue/v1` → `"ok": true` + `cloud_forge_run_head`.
- [ ] `POST /api/cloud-forge-run/proceed/v1` with `Authorization: Bearer $FBE_INTERNAL_SECRET` and `{}` → HTTP 200, `"ok": true`.

## Single-cycle gate

- [ ] `GATED_PATHS` in `scripts/cloud_auto_runtime_single_cycle_gate_v1.py` includes only:
  - `/api/cloud-forge-run/proceed/v1`
  - `/api/cloud-forge-run/auto-tick/v1`
- [ ] **Not** gated: `GET /api/cloud-forge-run/queue/v1`, `GET /api/cloud-forge-run/observer/v1`.
- [ ] If latched HALT after bad deploy: `ssh -i ~/.ssh/virlux_github railway-sourcea-fbe-runner "rm -f /app/receipts/cloud/cloud-auto-runtime-single-cycle-gate-v1.json"`.
- [ ] Gate file path on volume: `/app/receipts/cloud/cloud-auto-runtime-single-cycle-gate-v1.json`.

## SSH to Railway (gate reset / debug)

- [ ] `railway ssh config -s sourcea-fbe-runner` → host `railway-sourcea-fbe-runner` in `~/.ssh/config`.
- [ ] Key: `~/.ssh/virlux_github`.

## Loop proof (production)

- [ ] Observer last cycle: `GET /api/cloud-forge-run/observer/v1` → latest `cycles[]` entry with `trigger_source: cloudflare_cron`.
- [ ] Queue advances: compare `cloud_forge_run_head` before/after cron window (expect one task per 10 min when armed).

## Known failures

| Symptom | Fix |
|--------|-----|
| Observer 500 `cloud_forge_run_queue_path_v1` | Rebuild via `deploy_fbe_railway_v1.py`; add missing COPY/staging lines |
| Proceed 422 `second_request_within_cycle_window` | Remove queue GET from gate; clear gate file on volume |
| Build FAILED missing script | Add file to `deploy_fbe_railway_v1.py` staging list |
| `railway up` 413 / symlink errors | Use staged deploy only |
