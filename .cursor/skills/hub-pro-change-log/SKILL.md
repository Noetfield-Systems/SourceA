---
name: hub-pro-change-log
description: >-
  Hub Pro app experience change log — mandatory append after every app
  build/upgrade/fix. Shared report log so all agents see last obstacles and
  golden tips per app.
---

# Hub Pro — App change log protocol

**Log file:** `data/hub-pro-app-experience-log-v1.json`  
**Script:** `scripts/hub_pro_skills_v1.py`  
**In-app:** Hub Pro tab → Recent experience

## When to append

After **every** app touch that ships to disk:
- UI upgrade
- API route change
- .app rebuild
- e2e fix
- Incident resolution

## Append command

```bash
python3 scripts/hub_pro_skills_v1.py --append \
  --app worker_hub \
  --agent "your-agent-id" \
  --summary "One sentence what changed" \
  --obstacles "comma,separated,blockers" \
  --fixes "comma,separated,fixes" \
  --paths "path/one,path/two" \
  --json
```

## Entry schema

| Field | Required | Purpose |
|-------|----------|---------|
| `app_id` | yes | `worker_hub` · `mac_health` · `hub_form` · … |
| `agent` | yes | Who shipped |
| `summary` | yes | Founder-readable one-liner |
| `obstacles` | recommended | What blocked you |
| `fixes` | recommended | What fixed it |
| `golden_tips` | recommended | Advice for next agent |
| `paths` | recommended | Files touched |

## Read before edit

```bash
python3 scripts/hub_pro_skills_v1.py --app mac_health --json
python3 scripts/hub_pro_skills_v1.py --list-apps --json
```

## Also append UI ledger (if UI changed)

```bash
python3 scripts/ui_upgrade_ledger_v1.py --surface mac_health --append ...
```

## Comment template for agents

```text
## [app_id] — [date] — [agent]
**Summary:** …
**Obstacles:** …
**Fix:** …
**Golden tip:** …
**Paths:** …
**Proof:** ~/.sina/… or curl …
```

## Do not

- Chat-only "done" without log entry
- Duplicate entry without new facts
- Put secrets in log
