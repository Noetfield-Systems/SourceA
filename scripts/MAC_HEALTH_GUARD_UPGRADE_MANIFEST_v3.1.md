# Mac Health Guard — Upgrade Manifest v3.1.0 (Icy Frost)

**Version:** 3.1.0 · Body · Heart · Brain · Icy Frost  
**Ship gate:** `bash scripts/run-mac-health-recipe-v1.sh [--build]`  
**Heart:** `http://127.0.0.1:13024/`  
**E2E receipt:** `~/.sina/mac-health/e2e-latest-v1.json`

---

## What shipped

| Layer | Change |
|-------|--------|
| **Version SSOT** | `mac_health_version_v1.py` — single source for server, guard, UI tag, cache buster |
| **UI** | Icy Frost glass system across all 4 tabs; poem + score ring; segmented nav |
| **CPU ladder** | `cpu_warn_state` in live pulse + report; `#cpu-ladder` strip in Overview |
| **Smart Chrome** | Default `when_mac_hot`; Cool Down receipts show skip vs close |
| **Auto guard** | Settings tab with explainer ladder, save toast, schema-driven form |
| **E2E ladder** | fast → full → recipe `--build`; disk receipt JSON |

---

## Validators

| Script | Time | Scope |
|--------|------|--------|
| `validate-mac-health-fast-v1.sh` | ~15s | health, HTML needles, settings API, UI theme |
| `validate-mac-health-e2e-v1.sh` | ~2min | all sub-validators + SASCIP + receipt |
| `validate-mac-health-ui-v1.sh` | ~5s | served HTML/CSS icy theme gate |
| `validate-mac-health-bundle-parity-v1.sh` | ~5s | SSOT hash parity vs bundles |
| `validate-mac-health-unattended-v1.sh` | ~5s | dry-run streak + Cursor auto-quit OFF |
| `run-mac-health-recipe-v1.sh --build` | ~3min | full E2E + Desktop `.app` rebuild |

---

## Founder manual taps (acceptance)

1. **Overview** — icy hero, poem, score 80+, CPU ladder strip calm when Mac is cool
2. **RAM truth** — hog rows load with glass cards
3. **Cool Down** — glass cards; Chrome skipped on calm Mac (`Chrome kept open — Mac OK`)
4. **Auto guard** — explainer ladder, save settings, Chrome dropdown `When Mac is hot`
5. **Recipe:** `cd ~/Desktop/SourceA && bash scripts/run-mac-health-recipe-v1.sh --build` → exit 0
6. **Receipt:** `~/.sina/mac-health/e2e-latest-v1.json` → `overall_ok: true`

---

## SSOT paths (edit only here)

- `SourceA/scripts/mac-health-standalone/` — `index.html`, `app.js`, `app.css?v=3.1.0`
- `SourceA/scripts/mac_health_*.py` — engine, settings, live, emergency stop
- `SourceA/scripts/mac_health_version_v1.py` — version string
- `~/.sina/config/mac-health-panic-v1.json` — runtime thresholds

---

## Agent law

- **RF-MHG-001** — never manual `cp` into bundles; use recipe sync
- **RF-MHG-002** — never declare done without recipe exit 0
- **RF-MHG-003** — never edit bundle without editing SSOT first

---

## Out of scope (v3.1)

- Playwright visual regression
- Hub `:13020` required for standalone ship (H1 bridge optional in E2E)
