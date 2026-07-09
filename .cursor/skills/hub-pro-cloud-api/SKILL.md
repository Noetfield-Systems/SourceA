---
name: hub-pro-cloud-api
description: >-
  Hub Pro cloud proceed, API Station, and founder ops — H1/H2 wiring, Railway
  dispatch, founder-ops API, and Mac→Cloud Forge Run without local FORGE motor.
---

# Hub Pro — Cloud proceed + API Station

## Cloud Workers founder control plane (Jun 2026)

**Law:** Cloud Workers.app (:13027) is primary cockpit. Worker Hub :13020 is legacy optional glance.

```bash
GET  http://127.0.0.1:13027/api/cloud-workers/v1
POST http://127.0.0.1:13027/api/cloud-workers/v1
{"action":"probe"|"proceed"|"auto_tick"|"deploy_instructions"}
```

Machine: `scripts/cloud_workers_hub_v1.py`  
UI: **Cloud Workers.app** → Proceed next cloud task (full-pack)

**Founder deploy (you run — not agents):**
```bash
cd ~/Desktop/Noetfield-Systems/SourceA && python3 scripts/deploy_fbe_railway_v1.py
```

Stale cloud (`No module named hub_cloud_forge_run_proceed_v1`) → deploy command + amber banner.

## Cloud proceed (one law)

> **Proceed = Cloud Workers.app or CF cron → Railway full-pack.** Batch 2 complete at CLOUD-SEC-200.

```bash
POST http://127.0.0.1:13027/api/cloud-workers/v1
{"action":"proceed","full_pack":true,"max_advance":100,"llm_provider":"openrouter","full_motor":true}
```

Receipt: `~/.sina/hub-cloud-forge-run-proceed-receipt-v1.json`  
Log: `~/.sina/cloud-workers-proceed-log-v1.jsonl`  
UI: Cloud Workers.app → **Proceed next cloud task**

**Rule:** `.cursor/rules/035-hub-cloud-proceed-v1.mdc`

## Founder ops API

```bash
GET  http://127.0.0.1:13020/api/founder-ops/v1
POST http://127.0.0.1:13020/api/founder-ops/v1
{"op": "dual_heal"}
```

Machine: `scripts/founder_ops_v1.py` — cloud category: `cloud_workers_status`, `cloud_workers_probe`, `cloud_workers_dry_run`, `cloud_deploy_instructions`, `cloud_proceed_dry`

## API Station

- UI: View → **API Station** tab
- Script: `scripts/api_station_v1.py`
- Tasks per app: worker-hub (27), machine-hub (13), founder-ops (33)

## Jun 2026 fixes

| Issue | Fix |
|-------|-----|
| Railway deploy FAIL | `brain-os/` excluded in `.dockerignore` — moved registry to `data/` |
| Missing GET cloud-workers | Route was in `do_POST` only — moved to `do_GET` |
| Proceed UI separate card | Moved under `#health-card` Auto-heal |
| Missing import on proceed | `invalidate_worker_hub_cache` import in server |
| Deploy health green but queue still old | Railway volume pointer can override image pointer — POST `/api/cloud-forge-run/queue/v1` with `{"action":"sync_pointer_from_image","reason":"..."}` |

## Queue Proof After Deploy

Do not treat Railway `/health` as Cloud Forge Run proof. `/health` only proves the service is alive. The proof is:

```bash
curl -s https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1
```

Expected fields: `cloud_forge_run_head`, `observed.batch_id`, `queue_batch_complete`.

If the new image built successfully but the queue still shows the old batch, the persistent Railway volume pointer is stale. Use the built-in repair:

```bash
curl -s -X POST https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1 \
  -H "Content-Type: application/json" \
  -d '{"action":"sync_pointer_from_image","reason":"post_deploy_queue_pointer_repair"}'
```

Then re-read the queue endpoint. Do not redeploy again unless the queue file is missing from the image.

## Hub restart after server edits

```bash
launchctl kickstart -k "gui/$(id -u)/com.sourcea.hub"
```

## Mac Health cloud glance (read-only)

- Strip: `#cloud-glance-strip` on :13024
- API: `/api/mac-health/cloud-glance/v1`
- Tap → Worker Hub URL from API (no local factory)

## Forbidden on Mac founder session

- Full motor FORGE on Mac for Cloud Forge Run rows
- Chat-only "proceed" without hub receipt
- Validator marathon to prove cloud state
