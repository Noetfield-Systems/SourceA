# sa-0836 — hub_dual_heal_v1 H2 sync after H1 light refresh T1 cross-ref (LOCKED v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **SA:** sa-0836 (T1) · **Canonical:** sa-0811 (T0)

## Contract

T1 dedup — no re-research. Verification:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0811 · `scripts/validate-hub-dual-heal-h2-sync-v1.sh` |
| T1 echo | sa-0836 · `scripts/validate-hub-dual-heal-h2-sync-t1-crossref-v1.sh` |
| Receipt | `receipts/sa-0811-receipt.json` DONE |
| Heal receipt | `~/.sina/two-hub-heal-receipt-v1.json` (steps: h2_registry_sync, h2_payload_refresh) |
| Script | `scripts/hub_dual_heal_v1.py` |

**Trigger:** H1 light refresh → hub_dual_heal_v1 → H2 registry sync.

**Law:** tier dedup only — cites canonical sa-0811 · runs validate-hub-dual-heal-h2-sync-v1.sh · H2 sync after H1 light refresh · no panel rebuild.
