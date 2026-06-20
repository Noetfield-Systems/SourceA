# sa-0893 — h2 pending honest count after registry sync T3 cross-ref (LOCKED v1)

**Saved:** 2026-06-17T12:46:30Z · **Version:** 1.0.0 · **Authority:** Worker ACT sa-0893  
**Date:** 2026-06-17 · **SA:** sa-0893 (T3) · **Canonical:** sa-0818 (T0) · **T1 echo:** sa-0843 · **T2 echo:** sa-0868

## Contract

T3 research spike — no re-research. Verification:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0818 · `scripts/validate-h2-pending-honest-count-v1.sh` |
| T1 echo | sa-0843 · `scripts/validate-h2-pending-honest-count-t1-crossref-v1.sh` |
| T2 echo | sa-0868 · `scripts/validate-h2-pending-honest-count-t2-crossref-v1.sh` |
| T3 echo | sa-0893 · `scripts/validate-h2-pending-honest-count-t3-crossref-v1.sh` |
| Receipt | `receipts/sa-0818-receipt.json` DONE |
| Registry | `~/.sina/h2-pending-registry-v1.json` |
| Count lib | `scripts/h2_pending_count_lib_v1.py` · `machine_hub_v1.py` · `pending_total` honest |

## Honest count after registry sync

```text
h2_pending_registry_sync_v1.py → refresh registry from live Form + disk truth
count_h2_pending(reg) → pending_total honest buckets
machine_hub_payload(skip_cache=True) → hub pending_total matches lib
No shipped/wired rows in maintainer_ship · pending_total ≤ 15 · scheduled bucket counted
```

**Law:** tier dedup only — cites canonical sa-0818 · runs validate-h2-pending-honest-count-v1.sh after registry sync · no panel rebuild.
