# SourceA E2E Weekly Checklist (LOCKED v1)

**Saved:** 2026-06-23T12:00:00Z  
**Authority ID:** `E2E_WEEKLY_CHECKLIST`  
**Registry doc (triplicate):** `brain-os/system/SOURCEA_E2E_CHECK_REGISTRY_LOCKED_v1.md` · Desktop · MacLaw  
**Registry JSON:** `data/sourcea-e2e-check-registry-v1.json`  
**Overrides:** `data/sourcea-e2e-check-registry-overrides-v1.json`  
**Runner:** `scripts/sourcea_e2e_run_v1.py`  
**Last report:** `~/.sina/sourcea-e2e-last-report-v1.json`  
**Playbook:** `brain-os/law/SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md`  
**Mac law:** INCIDENT-039 — heavy E2E ship window / cloud CI only

---

## One law

> **No agent runs E2E without reading the last report. No agent finishes E2E without writing the report.**

---

## Agent protocol

### Before E2E

```bash
python3 scripts/sourcea_e2e_run_v1.py --read-last --json
```

Read `~/.sina/sourcea-e2e-last-report-v1.json` — note `stale_checks`, `blockers`, `summary`.

### Run (one bundle per cadence — not validator chains)

```bash
# Daily Mac-safe smoke
python3 scripts/sourcea_e2e_run_v1.py --bundle mac_daily_smoke --write-report --json

# Weekly checklist (ship window or cloud CI)
python3 scripts/sourcea_e2e_run_v1.py --cadence weekly --write-report --json

# Ship window standard (founder: RUN STANDARD E2E ONCE)
python3 scripts/sourcea_e2e_run_v1.py --bundle sourcea_standard --write-report --json

# Monthly full catalog (cloud CI only)
python3 scripts/sourcea_e2e_run_v1.py --cadence monthly --all --write-report --json
```

### After E2E

Report written to:

| Artifact | Path |
|----------|------|
| Last report | `~/.sina/sourcea-e2e-last-report-v1.json` |
| Weekly receipt | `~/.sina/sourcea-e2e-weekly-checklist-receipt-v1.json` |
| Archive | `receipts/e2e-reports/E2E-*.json` |
| Human mirror | `docs/system-audits/E2E_REPORT_YYYY-MM-DD.md` |
| Per-check logs | `~/.sina/e2e-logs/*.log` |

On FAIL: cite playbook rule in `blockers[]` + log path in founder reply.

---

## Unified tiers

| Tier | Meaning | Mac founder session | Cadence |
|------|---------|---------------------|---------|
| **T0_probe** | HTTP health &lt;5s | Allowed | Daily |
| **T1_fast** | Disk grep / &lt;30s | Allowed (one shell) | Daily |
| **T2_medium** | Chain slice / &lt;120s | Ship window only | Weekly |
| **T3_heavy** | Named E2E / 2–10 min | Ship window only | Weekly |
| **T4_marathon** | Full standard / all-e2e | Cloud CI only | Monthly |

---

## Weekly bundles

| Bundle ID | Tier | Cadence | Est time | Entry |
|-----------|------|---------|----------|-------|
| `mac_daily_smoke` | T0–T1 | Daily | &lt;2 min | `--bundle mac_daily_smoke` |
| `machine_ladder_weekly` | T2 | Weekly | ~30 min | `machine_test_ladder_run_v1.py --tier weekly` |
| `hub_e2e_core` | T3 | Weekly | ~15 min | `--bundle hub_e2e_core` |
| `disk_truth_matrix` | T2 | Weekly | ~3 min | `--bundle disk_truth_matrix` |
| `h2_weekly` | T2 | Weekly | ~5 min | `--bundle h2_weekly` |
| `sourcea_standard` | T3 | Ship window | ~6–8 min | `--bundle sourcea_standard` |
| `brain_live_production` | T1 | Weekly / post-landing-ship | ~90s | `bash scripts/validate-sourcea-brain-live-v1.sh` |
| `cloud_runtime_ci` | T4 | Cloud CI | ~10 min | `--bundle cloud_runtime_ci` |
| `full_marathon` | T4 | Monthly | 60+ min | `--bundle full_marathon` |

**Full catalog (~800 checks):** Registry tracks every validator. Weekly runs **bundles** only. Monthly `--cadence monthly --all` runs parallel batches on cloud CI.

---

## Sunday rhythm

1. Read last report (`--read-last`)
2. Ship window or dispatch cloud CI
3. `python3 scripts/sourcea_e2e_run_v1.py --cadence weekly --write-report --json`
4. Founder glance: `e2e_last_report_line` on `~/.sina/agent-live-surfaces-v1.json`

Cross-ref: `founder/ASF_WEEKLY_SUNDAY.md` · `ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md`

---

## Regenerate registry

```bash
python3 scripts/sourcea_e2e_registry_generate_v1.py --json
bash scripts/validate-sourcea-e2e-registry-v1.sh
```

---

*End E2E_WEEKLY_CHECKLIST v1*
