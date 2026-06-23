---
name: hub-pro-app-e2e
description: >-
  Hub Pro app e2e wiring — health probes, port map, API routes, link checks,
  hub restart, and founder-session-safe smoke tests for all Hub apps.
---

# Hub Pro — App e2e wire

## Port + health matrix

| Service | Port | Health | Primary API |
|---------|------|--------|-------------|
| Worker Hub | 13020 | `GET /health` | `GET /api/worker-hub/v1` |
| Machine Hub UI | 13020 | same hub | `POST /api/founder-ops/v1` |
| Official Form | 13020 | hub health | `GET/POST /api/live-founder-decision-form-v1` |
| Mac Health | 13024 | `GET /health` | `GET /api/mac-health/live` |
| Chat Unify | 13023 | `GET /health` | app-specific |
| n8n Integration | 13026 | `GET /health` | glue runner APIs |
| Mac Law | 8781 | `GET /health` | surfaces API |
| Routing | 8780 | `GET /` | registry |

## E2e sequence (light — founder Mac session)

```bash
# Hub alive
curl -sf http://127.0.0.1:13020/health

# Worker hub payload (disk cache — should be <2s)
curl -sf --max-time 5 http://127.0.0.1:13020/api/worker-hub/v1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('ok'), len(str(d))<500000)"

# Form schema
curl -sf http://127.0.0.1:13020/api/live-founder-decision-form-v1 | python3 -c "import sys,json; d=json.load(sys.stdin); q=d['open_questions'][0]; print(len(q.get('option_slots',[])))"

# Mac Health live
curl -sf http://127.0.0.1:13024/api/mac-health/live | python3 -c "import sys,json; print(json.load(sys.stdin).get('live_status'))"
```

## After code change — restart hub

```bash
launchctl kickstart -k "gui/$(id -u)/com.sourcea.hub"
```

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
- `~/.sina/hub-cloud-drain-proceed-receipt-v1.json`
- `~/.sina/agent-live-surfaces-v1.json` → `factory_now_line`
