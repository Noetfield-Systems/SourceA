# Autonomous loop fix — 2026-06-22

**UTC:** 2026-06-22T23:45:40Z

INCIDENT: Cloudflare cron fired every 10 minutes but Railway cloud-forge-run proceed stayed blocked (422 HALT / observer 500).

ROOT_CAUSE: Read-only `GET /api/cloud-forge-run/queue/v1` was gated by the single-cycle latch, so hub/observer polls consumed the cycle before cron `proceed`.

WHAT_FAILED:
- Railway observer returned 500 — `No module named 'cloud_forge_run_queue_path_v1'` (stale image; Dockerfile missing COPY lines).
- `deploy_fbe_railway_v1.py` staging omitted `cloud_auto_runtime_single_cycle_gate_v1.py` — deploy build FAILED until staged.
- Queue polls latched HALT (`second_request_within_cycle_window`); cron `POST /api/cloud-forge-run/proceed/v1` returned 422.

WHAT_FIXED_IT:
1. Added Dockerfile COPY lines for observer + cloud-forge-run modules (`c4a424a3`).
2. Staged `cloud_auto_runtime_single_cycle_gate_v1.py` in `scripts/deploy_fbe_railway_v1.py` (`79be9a5d`).
3. Deployed via `python3 scripts/deploy_fbe_railway_v1.py` → Railway deploy `e0c40033` SUCCESS; observer `"ok": true`.
4. Removed `/api/cloud-forge-run/queue/v1` from `GATED_PATHS` in `scripts/cloud_auto_runtime_single_cycle_gate_v1.py` and removed gate checks on queue GET/POST in `scripts/fbe_cloud_worker_http_v1.py` (`8de60862`).
5. Redeployed via `python3 scripts/deploy_fbe_railway_v1.py` → Railway deploy `3636acbc` SUCCESS.
6. Cleared latched gate on Railway volume: `ssh -i ~/.ssh/virlux_github railway-sourcea-fbe-runner "rm -f /app/receipts/cloud/cloud-auto-runtime-single-cycle-gate-v1.json"`.
7. Verified `POST https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/proceed/v1` → HTTP 200, `"ok": true`; queue head advanced CLOUD-SEC-106 → CLOUD-SEC-107.

NEVER_DO_AGAIN:
- Gate read-only `GET /api/cloud-forge-run/queue/v1` on the single-cycle latch.
- Use `railway redeploy` for missing-module fixes — it reuses the old image; always rebuild with `deploy_fbe_railway_v1.py`.
- Run `railway up` from repo root (broken symlinks / 413 payload) instead of staged `--path-as-root` deploy.
- Cloudflare Worker must be on main account (sina.kazemnezhad.ca@gmail.com). Never deploy Workers via witness.bc@gmail.com OAuth. Always run `wrangler whoami` before deploy — confirm correct account.

PROOF:
- Queue head: `CLOUD-SEC-108` · last completed: `CLOUD-SEC-107` · `at`: `2026-06-22T23:45:40Z`
- Last Cloudflare cron cycle: `2026-06-22T23:30:04Z` · `trigger_source`: `cloudflare_cron`
