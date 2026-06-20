# sa-0974 ACT — PROGRAM_PROGRESS factory divergence hardening

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T03:32Z · **Turn:** ACT · **Worker:** SourceA

## Shipped

| Piece | Change |
|-------|-------|
| `scripts/validate-program-progress-factory-divergence-v1.sh` | Two-speed clock crosswalk — machine `updated_by`, `synced_at`, REGISTRY unproven=0, factory honest count |
| CHECK doc | `sa-0974-program-progress-machine-sync-vs-manual-asf-edit-incidents_LOCKED_v1.md` |

## Signals enforced

| Signal | Assert |
|--------|--------|
| Machine sync | `updated_by == update-program-progress.py` |
| Build chain | `validate-program-progress-build-sync-v1` chained PASS |
| No manual fake done | `audit_registry_done.unproven_done == 0` |
| Factory clock | `honest_done/1000` printed alongside parallel ≥90% rows |
| Incident law | INCIDENT-016 file present |

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-program-progress-factory-divergence-v1 | PASS |
| validate-program-progress-build-sync-v1 | PASS (chained) |

*End sa-0974 ACT*
