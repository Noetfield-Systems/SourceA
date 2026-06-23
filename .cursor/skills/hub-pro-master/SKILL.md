---
name: hub-pro-master
description: >-
  Hub Pro master index — read FIRST before building, upgrading, e2e-testing, or
  fixing any SourceA Hub app (Worker Hub, Mac Health, Form, Chat Unify, n8n,
  Machine Hub). Points to checklists, Mac security guard, experience log.
---

# Hub Pro — Master (read first)

**SSOT manifest:** `data/hub-pro-skills-index-v1.json`  
**Experience log:** `data/hub-pro-app-experience-log-v1.json`  
**In-app panel:** Hub → View → **Hub Pro** tab (every H1/H2 app)

## One law

> Before you touch any Hub app: read this index → read that app's skill + ledger → run light e2e → ship → **append change log**.

## Hub app map

| App | Port | URL | surface_id |
|-----|------|-----|------------|
| Worker Hub (H1) | 13020 | http://127.0.0.1:13020/ | `worker_hub` |
| Machine Hub (H2) | 13020 | http://127.0.0.1:13020/machines/ | `worker_hub` |
| Official Form | 13020 | http://127.0.0.1:13020/form/ | `hub_form` |
| Mac Health Guard | 13024 | http://127.0.0.1:13024/ | `mac_health` |
| Chat Unify | 13023 | http://127.0.0.1:13023/ | `chat_unify` |
| n8n Integration | 13026 | http://127.0.0.1:13026/ | `n8n_integration` |
| Portfolio Mail | 13020 | http://127.0.0.1:13020/mail-hub/ | `portfolio_mail` |

## Skill batch (load the one you need)

| Skill | Use when |
|-------|----------|
| `hub-pro-ui-upgrade` | Any HTML/CSS/JS UI edit |
| `hub-pro-app-e2e` | Wire links, health, API, smoke |
| `hub-pro-mac-security` | .app build, Gatekeeper blocks, Console crashes |
| `hub-pro-standalone-apps` | Desktop .app shell + embedded server |
| `hub-pro-form-official` | FORM_OFFICIAL 5-slot + submit |
| `hub-pro-cloud-api` | Cloud proceed, API Station, founder ops |
| `hub-pro-hub-hero` | Hub Hero field playbook — read for H1/H2 wiring |
| `hub-pro-mac-session` | Founder session on Mac (INCIDENT-039) |
| `hub-pro-change-log` | After every ship — append entry |

## Mandatory pre-flight (every app)

```bash
# 1 — classify path + UI first-check (if UI)
python3 scripts/ui_upgrade_path_classifier_v1.py --path "<file>" --json
python3 scripts/ui_upgrade_first_check_v1.py --surface <surface_id> --ack --json

# 2 — read last experience for this app
python3 scripts/hub_pro_skills_v1.py --app <app_id> --json

# 3 — light health (≤90s total on Mac founder session)
curl -sf http://127.0.0.1:<port>/health
```

## Mandatory post-ship

```bash
python3 scripts/hub_pro_skills_v1.py --append --app <app_id> --agent <your_id> \
  --summary "what changed" --obstacles "what blocked" --fixes "what fixed" --json
python3 scripts/ui_upgrade_ledger_v1.py --surface <surface_id> --append ...  # if UI
```

## Golden rules from Jun 2026 field work

1. **API can be LIVE while UI shows OFFLINE** — always separate server health from JS errors.
2. **Never start background subprocess before HTTP response** — macOS threaded servers drop the connection (form submit lesson).
3. **founder_glance UI removes DOM ids** — grep `getElementById` / `$("id")` and null-guard every legacy panel.
4. **Desktop .app ≠ live server code** — rebuild or sync bundle after `scripts/*-standalone/` edits.
5. **Console crash ≠ active failure** — read process name + stack; old crashes stay in DiagnosticReports.
6. **Mac founder session** — one light check ≤90s; proof = receipts not validator marathons.

## Related law

- UI upgrade: `.cursor/rules/024-ui-upgrade-mandatory-checklist.mdc`
- Mac control plane: `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`
- Form founder-only: INCIDENT-037 · `form-agent-submit-forbidden-v1.flag`
