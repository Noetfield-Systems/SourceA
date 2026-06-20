# sa-0824 — H2 machine hub evidence row after weekly SHIP pass (LOCKED v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **SA:** sa-0824 · **Law:** `SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` slot 24

## Contract

After `machine_hub_bundle_v1.py` weekly SHIP pass (`core_ok`):

1. Receipt `~/.sina/h2-machine-weekly-bundle-receipt-v1.json` · `schema=h2-machine-weekly-bundle-v1` · `ok=true`
2. `scripts/h2_machine_hub_evidence_v1.py::append_priority_h2_weekly_ship_evidence` appends idempotent row to `brain-os/plan-registry/SOURCEA-PRIORITY.md` Evidence log
3. Validator `scripts/validate-h2-weekly-ship-evidence-row-v1.sh` proves bundle + evidence row + H2 plan slot 24 pointer

**Forbidden:** append on failed bundle · duplicate sa-0824 rows · Sina Command panel rebuild on weekly path
