# E2E Executor Checklist — SourceA (LOCKED v1)

**Saved:** 2026-06-23T12:00:00Z  
**Runtime SSOT:** `~/.sina/brain/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md`  
**Law:** `brain-os/law/enforcement/SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md`  
**Incident:** `brain-os/incidents/SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md`  
**Idle gate:** `scripts/factory_idle_gate_v1.py` · `validate-e2e-fast-ladder-v1.sh --require-idle`

---

## Steps (every E2E run)

| # | Action |
|---|--------|
| 1 | **Read last report** — `python3 scripts/sourcea_e2e_run_v1.py --read-last --json` |
| 2 | **Factory idle** — `python3 scripts/factory_idle_gate_v1.py --json` |
| 3 | **Pick bundle** by cadence — not raw marathon (`--bundle` or `--cadence weekly`) |
| 4 | **Run** — one bundle; Mac founder session = `mac_daily_smoke` only |
| 5 | **Write report** — `--write-report` or ingest from standard/ladder runners |
| 6 | **On FAIL** — playbook rule + log path in reply (`SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md`) |

---

## Bundles (quick)

| Cadence | Bundle |
|---------|--------|
| Daily (Mac OK) | `mac_daily_smoke` |
| Weekly | `--cadence weekly` |
| Ship window | `sourcea_standard` |
| Monthly cloud | `--cadence monthly --all` |

---

## Proof paths

- Last: `~/.sina/sourcea-e2e-last-report-v1.json`
- Weekly: `~/.sina/sourcea-e2e-weekly-checklist-receipt-v1.json`
- Logs: `~/.sina/e2e-logs/`
- Mirror: `docs/system-audits/E2E_REPORT_YYYY-MM-DD.md`

```bash
test -f ~/.sina/sourcea-e2e-last-report-v1.json
python3 ~/Desktop/SourceA/scripts/factory_idle_gate_v1.py --json
```

*End E2E_EXECUTOR_CHECKLIST v1*
