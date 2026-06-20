# sa-0883 — deferred excludes scheduled_cadence T3 cross-ref (LOCKED v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **SA:** sa-0883 (T3) · **Canonical:** sa-0808 (T0)

## Contract

T3 research dedup — no re-research. Verification:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0808 · `scripts/validate-deferred-excludes-scheduled-v1.sh` |
| T1 echo | sa-0833 · `scripts/validate-deferred-excludes-scheduled-t1-crossref-v1.sh` |
| T2 echo | sa-0858 · `scripts/validate-deferred-excludes-scheduled-t2-crossref-v1.sh` |
| T3 echo | sa-0883 · `scripts/validate-deferred-excludes-scheduled-t3-crossref-v1.sh` |
| Receipt | `receipts/sa-0808-receipt.json` DONE |
| Registry | `~/.sina/h2-pending-registry-v1.json` · `deferred` · `scheduled_cadence` |
| Count lib | `scripts/h2_pending_count_lib_v1.py` · `pending_total` |

**Law:** tier dedup only — cites canonical sa-0808 · deferred bucket excludes scheduled_cadence from pending_total · no panel rebuild.
