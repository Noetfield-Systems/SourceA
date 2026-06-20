# sa-0891 — THREE_ZONE_HUB_SPINE H2 not nested under H1 T3 cross-ref (LOCKED v1)

**Saved:** 2026-06-17T12:00:05Z · **Version:** 1.0.0 · **Authority:** Worker ACT sa-0891  
**Date:** 2026-06-17 · **SA:** sa-0891 (T3) · **Canonical:** sa-0816 (T0) · **T1 echo:** sa-0841 · **T2 echo:** sa-0866

## Contract

T3 research spike — no re-research. Proof chain:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0816 · `scripts/validate-three-zone-hub-spine-v1.sh` |
| T1 echo | sa-0841 · `scripts/validate-three-zone-hub-spine-t1-crossref-v1.sh` |
| T2 echo | sa-0866 · `scripts/validate-three-zone-hub-spine-t2-crossref-v1.sh` |
| T3 echo | sa-0891 · `scripts/validate-three-zone-hub-spine-t3-crossref-v1.sh` |
| Receipt | `receipts/sa-0816-receipt.json` DONE |
| Law | `SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md` |

## Three-zone navigation (H2 sibling — not nested)

| Zone | Surface | Rule |
|------|---------|------|
| **A H1** | `/` · Worker Hub | Daily · links `/machines/` as **sibling** |
| **B H2** | `/machines/` · Machine Hub | Heavy · declares sibling hub · not sub-page |
| **C legacy** | `/legacy/` | Museum quarantine · `legacy_url` separate on H2 API |

**ACT fix:** `machine_hub_v1.py` exposes `legacy_url: /legacy/` (was `null`) so validator proves legacy is separate from H1/H2 sibling law.

**Law:** tier dedup only — cites canonical sa-0816 · runs validate-three-zone-hub-spine-v1.sh · no panel rebuild.
