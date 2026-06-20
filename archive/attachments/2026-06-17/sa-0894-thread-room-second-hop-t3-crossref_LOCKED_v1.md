# sa-0894 — Thread Room second-hop law T3 cross-ref (LOCKED v1)

**Saved:** 2026-06-17T13:15:00Z · **Version:** 1.0.0 · **Authority:** Worker ACT sa-0894  
**Date:** 2026-06-17 · **SA:** sa-0894 (T3) · **Canonical:** sa-0819 (T0) · **T1 echo:** sa-0844 · **T2 echo:** sa-0869

## Contract

T3 research spike — no re-research. Proof chain:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0819 · `scripts/validate-thread-room-second-hop-v1.sh` |
| T1 echo | sa-0844 · `scripts/validate-thread-room-second-hop-t1-crossref-v1.sh` |
| T2 echo | sa-0869 · `scripts/validate-thread-room-second-hop-t2-crossref-v1.sh` |
| T3 echo | sa-0894 · `scripts/validate-thread-room-second-hop-t3-crossref-v1.sh` |
| Receipt | `receipts/sa-0819-receipt.json` DONE |
| Law | `SINA_THREAD_ROOM_LOCKED_v1.md` · H2 second hop |
| Registry | `~/.sina/h2-pending-registry-v1.json` · `thread_room` bucket |
| Curation | `~/.sina/thread-room/latest-curation-v1.json` |
| H1 pin | boot.json `thread_room` headline only · `one_line_alarm_only` |

## H2 second-hop law cross-check

```text
SINA_THREAD_ROOM_LOCKED_v1 + SOURCEA_SUPER_FAST_HUB_LOCKED_v1 → H2 second hop clauses
h2-pending-registry-v1.json thread_room: hub=H2 h1_allowed=one_line_alarm_only run_cadence=weekly
H1 boot thread_room pin: headline only (no full scout/cartographer inline)
machine_hub_v1.py wires thread_room bucket
```

**Law:** tier dedup only — cites canonical sa-0819 · runs validate-thread-room-second-hop-v1.sh · weekly cadence · no panel rebuild.
