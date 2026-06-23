---
name: hub-pro-cloud-api
description: >-
  Hub Pro cloud proceed, API Station, and founder ops — H1/H2 wiring, Railway
  dispatch, founder-ops API, and Mac→cloud drain without local FORGE motor.
---

# Hub Pro — Cloud proceed + API Station

## Cloud Workers founder control plane (Jun 2026)

**Law:** Founder runs Railway deploy — agents wire Hub only.

```bash
GET  http://127.0.0.1:13020/api/cloud-workers/v1
POST http://127.0.0.1:13020/api/cloud-workers/v1
{"action":"probe"|"dry_run"|"dispatch"|"deploy_instructions"}
```

Machine: `scripts/cloud_workers_hub_v1.py`  
UI: Worker Hub → Live health → **Cloud Workers** (status · dry run · proceed · deploy command)

**Founder deploy (you run — not agents):**
```bash
cd ~/Desktop/SourceA && python3 scripts/deploy_fbe_railway_v1.py
```

Stale cloud (`No module named hub_cloud_drain_proceed_v1`) → Hub shows deploy command + amber banner.

## Cloud proceed (one law)

> **Proceed = Hub button or POST only.** Mac proxies one tap to Railway — no `portfolio__forge_dispatch` on Mac.

```bash
POST http://127.0.0.1:13020/api/cloud-drain/proceed/v1
{"llm_provider":"openrouter","full_motor":true}
```

Receipt: `~/.sina/hub-cloud-drain-proceed-receipt-v1.json`  
UI: Worker Hub → Auto-heal card → Cloud Proceed

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

## Hub restart after server edits

```bash
launchctl kickstart -k "gui/$(id -u)/com.sourcea.hub"
```

## Mac Health cloud glance (read-only)

- Strip: `#cloud-glance-strip` on :13024
- API: `/api/mac-health/cloud-glance/v1`
- Tap → Worker Hub URL from API (no local factory)

## Forbidden on Mac founder session

- Full motor FORGE on Mac for cloud drain rows
- Chat-only "proceed" without hub receipt
- Validator marathon to prove cloud state
