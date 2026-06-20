# Mac Health Guard — Upgrade Manifest v3.2.0 (Log Shield)

**Version:** 3.2.0 · Body · Heart · Brain · Log Shield  
**Ship gate:** `bash scripts/run-mac-health-recipe-v1.sh [--build]`  
**Heart:** `http://127.0.0.1:13024/`  
**E2E receipt:** `~/.sina/mac-health/e2e-latest-v1.json`

---

## What shipped (incident hardening)

| Layer | Change |
|-------|--------|
| **Log Shield** | `mac_health_log_shield_v1.py` — stat/tail only · no full log reads |
| **Runaway logs** | warn ≥100 MB · critical ≥1 GB on `command-server.log` |
| **Hub truth** | `hub_health_ok` requires JSON `ok:true` — not port-only |
| **Rebuild worker** | `:13030` health probe · `hub_rebuild_ok` |
| **Stuck readers** | detect `cat`/`wc` on huge logs · safe kill |
| **Factory storm** | auto-freeze when hub sick + ≥5 motor delegates |
| **find_critical_bugs** | tail-only log scan · runaway size finding |
| **UI** | Log Shield strip · hub truth badge · Relieve disk actions |
| **serve-sina-command** | debug instrumentation removed · rotate/snippet kept |

---

## Validators

| Script | Scope |
|--------|--------|
| `validate-mac-health-log-shield-v1.sh` | Log Shield probe + hub truth schema |
| `validate-mac-health-founder-upgrade-v1.sh` | Founder 10-step + v3.2 checks |
| `validate-mac-health-e2e-v1.sh` | Full recipe gate |

---

## SSOT paths

- `scripts/mac_health_log_shield_v1.py` — Log Shield engine
- `scripts/mac-health-standalone/` — UI
- `scripts/mac_health_version_v1.py` — version string

---

| v3.2.0 | 2026-06-17 | Incident hardening after 699 GB command-server.log |
