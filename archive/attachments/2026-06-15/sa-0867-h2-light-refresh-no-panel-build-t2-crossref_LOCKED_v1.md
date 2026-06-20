# sa-0867 — H2 light refresh no panel build T2 cross-ref (LOCKED v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **SA:** sa-0867 (T2) · **Canonical:** sa-0817 (T0) · **T1 echo:** sa-0842

## Contract

T2 quarterly dedup — no re-research. Verification:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0817 · `scripts/validate-h2-light-refresh-no-panel-build-v1.sh` |
| T1 echo | sa-0842 · `scripts/validate-h2-light-refresh-no-panel-build-t1-crossref-v1.sh` |
| T2 echo | sa-0867 · `scripts/validate-h2-light-refresh-no-panel-build-t2-crossref-v1.sh` |
| Receipt | `receipts/sa-0817-receipt.json` DONE |
| Heal chain | `scripts/hub_dual_heal_v1.py` · `scripts/machine_hub_v1.py` |
| Law | `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` — light refresh never invokes `build-sina-command-panel` |

**Law:** tier dedup only — cites canonical sa-0817 · runs validate-h2-light-refresh-no-panel-build-v1.sh · no panel rebuild.
