# sa-0837 — machine_hub_staleness_v1 auto-heal path T1 cross-ref (LOCKED v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **SA:** sa-0837 (T1) · **Canonical:** sa-0812 (T0)

## Contract

T1 dedup — no re-research. Proof chain:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0812 · `scripts/validate-machine-hub-staleness-auto-heal-v1.sh` |
| T1 echo | sa-0837 · `scripts/validate-machine-hub-staleness-auto-heal-t1-crossref-v1.sh` |
| Receipt | `receipts/sa-0812-receipt.json` DONE |
| Probe lib | `scripts/machine_hub_staleness_v1.py` |
| Heal path | `scripts/worker_anti_staleness_heal_v1.py` · `auto_heal_recommended` |

**Law:** tier dedup only — cites canonical sa-0812 · runs validate-machine-hub-staleness-auto-heal-v1.sh · no panel rebuild.
