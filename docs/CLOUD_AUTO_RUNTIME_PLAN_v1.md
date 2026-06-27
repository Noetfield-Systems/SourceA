# Cloud Forge Run Auto-Runtime v1 — Full Plan (LOCKED draft)

**Saved:** 2026-06-22T09:00:00Z  
**SSOT:** `data/cloud-auto-runtime-v1.json`  
**Machine:** `scripts/cloud_auto_runtime_v1.py`

---

## Problem

- Queue has 110 CLOUD-SEC rows but **no scheduler** — founder must click Proceed every row.
- **mock_only** scaffold rows (006, 043, 056) block sequential drain when FORGE motor fails.
- **Skip button** failed: WKWebView `confirm()` dead + standalone app could not write `~/.sina` (proxied to Hub now).

---

## Shipped in this build

| # | Deliverable | Path |
|---|-------------|------|
| 1 | **Skip fix** — `skip_to_next_real` action, no confirm, Hub proxy from :13027 | `cloud-workers-panel.js`, `cloud-workers-server.py` |
| 2 | **Queue intelligence** — `is_mock_plan`, `auto_pass` on drain rows | `cloud_workers_hub_v1.py`, `secondary-cloud-forge-run-next-100-v1.json` |
| 3 | **Auto tick** — mock skip · self-heal on motor fail · optional proceed | `cloud_auto_runtime_v1.py` |
| 4 | **SSOT** | `data/cloud-auto-runtime-v1.json` |
| 5 | **CF Worker cron** (deploy pending) | `cloud/workers/cloud-auto-runtime-tick-v1/` |
| 6 | **N8N workflow** | `wf-cloud-auto-runtime-v1` via `n8n_workflow_factory_v1.py` + glue `cloud-auto-runtime-tick` |
| 7 | **UI** — Auto tick · Auto status pills | Cloud Workers Command Center |

---

## Founder opt-in (arm auto proceed)

```bash
python3 scripts/cloud_auto_runtime_v1.py --enable
# or: touch ~/.sina/cloud-forge-run-auto-proceed-v1.flag
# or on Cloudflare: CLOUD_FORGE_RUN_AUTO_PROCEED=true
```

**Default:** auto_skip_mock ON · auto_proceed OFF (safe).

---

## Deploy checklist

1. **Restart Hub** — `launchctl kickstart -k "gui/$(id -u)/com.sourcea.hub"`
2. **Rebuild Cloud Workers.app** — `bash scripts/build-cloud-workers-standalone-app-v1.sh`
3. **N8N** — `python3 scripts/n8n_workflow_factory_v1.py` then import `n8n/workflows/wf-cloud-auto-runtime-v1.json`
4. **Cloudflare** — `cd cloud/workers/cloud-auto-runtime-tick-v1 && npx wrangler deploy` + set secrets
5. **Arm** — `--enable` or CF secret when ready for unattended Proceed

---

## Guardrails (INCIDENT-023)

- Factory STOP receipt blocks auto tick.
- Rate limit: 15 min between ticks (configurable in SSOT).
- Mac stays glance-only; cron runs on cloud/N8N.

---

## Next rows after skip

Head advances to next non-mock CLOUD-SEC row (e.g. 007 evidence, 008 copy) — Proceed should run real FORGE motor.

**END PLAN**
