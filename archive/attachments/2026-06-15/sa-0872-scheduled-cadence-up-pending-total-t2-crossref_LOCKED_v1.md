# sa-0872 — scheduled_cadence UP-01..UP-06 pending_total exclusion T2 cross-ref (LOCKED v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **SA:** sa-0872 (T2) · **Canonical:** sa-0822 (T0)

## Contract

T2 dedup — no re-research. Proof chain:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0822 · `scripts/validate-h2-scheduled-cadence-up-pending-total-v1.sh` |
| T1 echo | sa-0847 · `scripts/validate-h2-scheduled-cadence-up-pending-total-t1-crossref-v1.sh` |
| T2 echo | sa-0872 · `scripts/validate-h2-scheduled-cadence-up-pending-total-t2-crossref-v1.sh` |
| Receipt | `receipts/sa-0822-receipt.json` DONE |
| LOCKED doc | `archive/attachments/2026-06-15/sa-0822-scheduled-cadence-up-pending-total_LOCKED_v1.md` |
| Registry | `~/.sina/h2-pending-registry-v1.json` · `scheduled_cadence[]` |
| Count lib | `scripts/h2_pending_count_lib_v1.py` · `pending_total` vs `scheduled_total` |

**Law:** tier dedup only — cites canonical sa-0822 · UP-01 through UP-06 excluded from pending_total · runs validate-h2-scheduled-cadence-up-pending-total-v1.sh · no panel rebuild.
