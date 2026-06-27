---
name: hub-pro-app-e2e
description: >-
  Hub Pro app e2e wiring — health probes, port map, API routes, link checks,
  hub restart, and founder-session-safe smoke tests for all Hub apps.
---

# Hub Pro — App e2e wire

## Port + health matrix

| Service | Port | Health | Primary API | Status |
|---------|------|--------|-------------|--------|
| **Cloud Workers** (primary cockpit) | 13027 | `GET /health` | `GET /api/cloud-workers/v1` | **daily** |
| Chat Unify + Official Form | 13023 | `GET /health` | `GET/POST /api/live-founder-decision-form-v1` · `/form/` | **daily** |
| Mac Health | 13024 | `GET /health` | `GET /api/mac-health/live` | daily |
| n8n Integration | 13026 | `GET /health` | glue runner APIs | optional |
| Mac Law | 8781 | `GET /health` | surfaces API | daily |
| Routing | 8780 | `GET /` | registry | optional |
| Worker Hub (legacy) | 13020 | — | — | **archived** — `asf_hub_legacy_trash_v1.sh` |

## E2e sequence (light — founder Mac session)

```bash
# Primary cockpit — Cloud Workers
curl -sf http://127.0.0.1:13027/health

# Chat Unify + form
curl -sf http://127.0.0.1:13023/health
curl -sf http://127.0.0.1:13023/form/

# Mac Health live
curl -sf http://127.0.0.1:13024/api/mac-health/live | python3 -c "import sys,json; print(json.load(sys.stdin).get('live_status'))"

# Full founder-desktop smoke (boots apps if down)
bash scripts/verify-founder-desktop-apps-v1.sh
```

**Do not** probe `:13020` — Worker Hub is legacy archived.

## API Station (founder ops from UI)

- Tab: **View → API Station** on H1, H2, Chat Unify, n8n
- Machine: `scripts/api_station_v1.py`
- Founder ops: `scripts/founder_ops_v1.py` (33 ops)

## Link wire checklist

- [ ] Official links bar loads (`/shared/official-links-bar.js`)
- [ ] API Station tab mounts (`api-station-tab.js`)
- [ ] Hub Pro tab mounts (`hub-pro-skills-tab.js`)
- [ ] Cross-app URLs use `127.0.0.1` not `localhost` drift
- [ ] `meta name="sina-app-id"` set for station routing

## Obstacles we hit (Jun 2026)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hub "Load failed" 37s | Validator marathon in worker_hub | Disk receipts + cache TTL |
| Form POST empty reply | subprocess before HTTP response | Defer background wire |
| Mac Health OFFLINE | JS null on removed grid | Null guards in app.js |
| n8n links dead | Wrong port or server down | stack-boot + health |

## Proof = receipts (not green chat)

- `~/.sina/hub-form-submit-receipt-v1.json`
- `~/.sina/hub-cloud-forge-run-proceed-receipt-v1.json`
- `~/.sina/agent-live-surfaces-v1.json` → `factory_now_line`
