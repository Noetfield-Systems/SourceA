# Two-Hub check + fix 2026-06-14

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority:** ASF — CHECK Super Fast Hub + Machine Hub (H2)

## Status after fix

| Hub | URL | Health | Validator |
|-----|-----|--------|-------------|
| **H1** Super Fast | `http://127.0.0.1:13020/` | fresh | `validate-super-fast-hub-v1.sh` |
| **H2** Machine | `http://127.0.0.1:13020/machines/` | fresh | `validate-machine-hub-v1.sh` |
| **Both** | dual heal | PASS | `validate-two-hub-v1.sh` |

## Scripts shipped

| Script | Purpose |
|--------|---------|
| `h2_pending_registry_sync_v1.py` | Refresh H2 registry from live Form + queue |
| `machine_hub_staleness_v1.py` | H2 health probe (fixed `form_open=0` bug) |
| `hub_dual_heal_v1.py` | Heal H1 + H2 in one command |
| `validate-two-hub-v1.sh` | Master two-hub gate |

## API upgrades (H2)

`/api/machine-hub/v1` now includes:
- `health` block (`machine-hub-staleness-v1`)
- Auto registry sync when stale
- `built_at` from live registry

## Hub restart

Server restart required to load `machine_hub_v1.py` health field:
`SINA_FORCE_RESTART=1 bash scripts/serve-sina-command.sh`

## UI follow-up (Maintainer)

Agent-review filed: H2 HTML needs health pill + light refresh + poll (parity with H1). API ready; `agent-control-panel/machines/index.html` is edit-locked for this agent.

## One command

```bash
python3 scripts/hub_dual_heal_v1.py --json
bash scripts/validate-two-hub-v1.sh
```
