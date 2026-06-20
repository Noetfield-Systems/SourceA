# sa-0890 — hub_surface_v1 tab slices without command-data hero T3 cross-ref (LOCKED v1)

**Saved:** 2026-06-17T11:51:54Z · **Version:** 1.0.0 · **Authority:** Worker ACT sa-0890  
**Date:** 2026-06-17 · **SA:** sa-0890 (T3) · **Canonical:** sa-0815 (T0) · **T1 echo:** sa-0840 · **T2 echo:** sa-0865

## Contract

T3 research spike — no re-research. Proof chain:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0815 · `scripts/validate-hub-surface-no-hero-v1.sh` |
| T1 echo | sa-0840 · `scripts/validate-hub-surface-no-hero-t1-crossref-v1.sh` |
| T2 echo | sa-0865 · `scripts/validate-hub-surface-no-hero-t2-crossref-v1.sh` |
| T3 echo | sa-0890 · `scripts/validate-hub-surface-no-hero-t3-crossref-v1.sh` |
| Receipt | `receipts/sa-0815-receipt.json` DONE |
| Surface | `scripts/hub_surface_v1.py` · `GET /api/surface/v1` |
| Shell SSOT | `agent-control-panel/command-data-shell.json` (not `command-data.json` hero) |

## hub_surface_v1 tab slices (no hero)

```text
hub_surface_v1.py
  → reads command-data-shell.json (slim boot)
  → never reads command-data.json hero (~9MB monolith)
  → nav[] tab slices are /api/* endpoints only
  → validate-hub-surface-no-hero-v1.sh loads each slice under hero/10 byte cap
```

**Law:** tier dedup only — cites canonical sa-0815 · runs validate-hub-surface-no-hero-v1.sh · no panel rebuild · H1 light refresh only.
