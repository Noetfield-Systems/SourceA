# sa-0817 — Hub 2 light refresh does not trigger build-sina-command-panel

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Tier:** T0 · **Hub 2** `/machines/` · **Sina Command quarantine**

## Verdict (one line)

Hub 2 heal and light-refresh paths use **disk align + registry sync + cache invalidate** only — **never** `build-sina-command-panel.py` on founder or dual-heal taps.

## Chain audited

| Layer | Path | Panel build? |
|-------|------|----------------|
| Hub 1 light refresh | `sina_command_lib.hub_light_refresh` · `run_refresh_scripts=False` | **No** |
| Dual heal | `hub_dual_heal_v1.py` → `worker_hub_heal_v1` + `h2_pending_registry_sync` | **No** |
| H2 payload | `machine_hub_v1.py` · actions `light_refresh` mode `light` | **No** |
| Weekly bundle | `machine_hub_bundle_v1.py` · `forbidden_on: h1-light-refresh` | **No** |
| Sina Command archive | `/legacy/` · monthly strict only | **Quarantine** |

## Machine proof

- `scripts/validate-h2-light-refresh-no-panel-build-v1.sh`
- Receipt: `~/.sina/two-hub-heal-receipt-v1.json` after `hub_dual_heal_v1.py`

## Law

`SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` slot 17

*End sa-0817*
