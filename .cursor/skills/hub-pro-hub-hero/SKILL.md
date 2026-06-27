---
name: hub-pro-hub-hero
description: >-
  Hub Hero — field playbook for Worker Hub (H1), Machine Hub (H2), Mac Health,
  Form, API Station, Cloud Workers, and founder session ops. Read when wiring
  Hub features, debugging LIVE vs OFFLINE UI, or onboarding the next agent.
---

# Hub Pro — Hub Hero (field playbook)

**Manifest:** `data/hub-pro-skills-index-v1.json`  
**In-app:** View → **Hub Pro** on every portfolio app (technical UP-0..UP-7 + per-app UI checklist)  
**Experience log:** `data/hub-pro-app-experience-log-v1.json`

## One law

> Hub pipe can be LIVE while the page shows OFFLINE — always split **server health** from **JS/DOM errors**. Fix the surface the founder sees, then prove with receipts.

## Port map

| App | Port | Health |
|-----|------|--------|
| Worker Hub H1 | 13020 | `curl -sf http://127.0.0.1:13020/health` |
| Machine Hub H2 | 13020/machines/ | `GET /api/founder-ops/v1` |
| Official Form | 13020/form/ | `POST /api/live-founder-decision-form-v1` |
| Mac Health Guard | 13024 | `curl -sf http://127.0.0.1:13024/health` |
| Chat Unify | 13023 | `curl -sf http://127.0.0.1:13023/health` |
| n8n Integration | 13026 | `curl -sf http://127.0.0.1:13026/health` |

## Hub restart (after `sina-command-server.py` or shared JS edits)

```bash
launchctl kickstart -k "gui/$(id -u)/com.sourcea.hub"
```

Hard refresh browser / WKWebView after shared tab JS changes (`api-station-tab.js`, `hub-pro-skills-tab.js`).

## Cloud Workers command center (P1)

- **API:** `GET /api/cloud-workers/v1` — situation, plans, inbox, events, CLI
- **Proceed:** Hub `POST /api/cloud-forge-run/proceed/v1` only — not Mac FORGE motor
- **Receipt:** `~/.sina/hub-cloud-forge-run-proceed-receipt-v1.json`
- **Events:** `~/.sina/cloud-workers-event-log-v1.json`
- **Motor FAIL vs pipe LIVE:** Railway image/stale motor — not missing Hub route

```bash
python3 scripts/cloud_workers_hub_v1.py --action situation --json
```

## API Station (H1 + H2 full catalog)

- **Shared JS:** `agent-control-panel/shared/api-station-tab.js` — syntax error = blank panel
- **Tasks:** `founder_ops_v1.py` `station_tasks()` — machine-hub must expose full ops (44+), not 2-button subset
- **Open:** View → API Station or `?station=1` on Machine Hub
- **Proof:** `GET /api/api-station/v1?app=machine-hub`

## Official form (founder-only submit)

- Button text must be **SUBMIT** (not “pick at least one”)
- Fixed headers must not overlap Q1 radios — z-index + padding
- Partial batch OK: 1+ explicit picks
- **INCIDENT-037:** agents do not submit form rows

## Mac Health Guard — full relief

- **Relieve pressure** (`heal` / `full_relief`): CPU cool down · pipeline zombies · ghost carts · RAM inactive purge when RAM ≥75% · firewall · rescan
- **Quick:** Clear pipeline · Reset inactive RAM (password dialog for `purge`)
- **Backend:** `scripts/mac_health_guard.py` → `run_full_relief()`
- **UI source:** `scripts/mac-health-standalone/` — sync to `.app` bundle after edits
- **References:** More → References & skills (`sources-grid` from `knowledge` API)
- **Law:** `brain-os/law/enforcement/SINA_MAC_HEALTH_GUARD_LOCKED_v1.md`

```bash
curl -sf http://127.0.0.1:13024/health
# action test (founder session — one call only):
curl -s -X POST http://127.0.0.1:13024/api/mac-health/v1 -H 'Content-Type: application/json' -d '{"action":"report"}' | head
```

## Mac founder session (INCIDENT-039)

- Reply <30s · one light shell ≤90s · proof = receipts
- No validator marathons · no `validate-all-e2e` on Mac body
- ASF uses Hub + Terminal — different lane from Cursor agents

## Mandatory agent loop (every app ship)

1. View → Hub Pro → read UP-0..UP-7 + this app's UI checklist
2. Read last experience entries for this `app_id`
3. Light health curl (≤90s total)
4. Ship bounded diff
5. Append experience log + ledger if UI

```bash
python3 scripts/hub_pro_skills_v1.py --app worker_hub --json
python3 scripts/hub_pro_skills_v1.py --append --app mac_health --agent <id> \
  --summary "..." --tips "one golden tip" --json
```

## Golden tips (Jun 2026)

1. **GET route missing in do_GET** — Cloud Workers 404 while POST worked; add GET mirror in `sina-command-server.py`
2. **Never block HTTP response with background subprocess** — form submit dropped connection
3. **founder_glance removes DOM ids** — null-guard every `$("id")` in `app.js`
4. **Desktop .app bundle stale** — copy `mac-health-standalone` → `Mac Health Guard.app/.../mac-health-bundle/app/`
5. **Proceed FAIL** — read classification: `pipe_live` / `stale_image` / `motor_failed`

## Related skills

| Skill | When |
|-------|------|
| `hub-pro-master` | First read — index |
| `hub-pro-ui-upgrade` | Any HTML/CSS/JS |
| `hub-pro-cloud-api` | Proceed + founder ops |
| `hub-pro-mac-session` | Mac founder session law |
| `hub-pro-standalone-apps` | WKWebView .app shells |
| `hub-pro-change-log` | After every ship |
