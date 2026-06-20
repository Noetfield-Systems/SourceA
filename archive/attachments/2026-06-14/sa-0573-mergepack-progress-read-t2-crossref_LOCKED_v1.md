# sa-0573 — T2 cross-ref to canonical mergepack progress nonblocking read (sa-0523)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T23:24Z · **Tier:** T2 · **canonical_sa:** sa-0523 · **No re-implement safe-read table prose**

## Dedup

| Key | Ref |
|-----|-----|
| **canonical_sa** | sa-0523 |
| **canonical_attachment** | `archive/attachments/2026-06-14/sa-0523-mergepack-progress-nonblocking-read_LOCKED_v1.md` |
| **canonical_receipt** | `receipts/sa-0523-receipt.json` |
| **read_fn** | `scripts/mergepack_progress_read_v1.py::read_mergepack_progress_safe` |
| **t1_echo** | sa-0548 · `mergepack_progress_read_t1_crossref` |
| **this_sa** | sa-0573 (T2 quarterly hardening — cite only) |

## Machine proof (existing validators — no duplicate nonblocking table)

- `scripts/validate-mergepack-progress-read-program-progress-v1.sh` — sa-0523 PROGRAM_PROGRESS hook + safe read wired
- `scripts/validate-mergepack-progress-nonblocking-v1.sh` — negative probe when mergepack file missing

## Factory verdict (one line)

Mergepack progress json nonblocking read is T0-canonical at sa-0523; T2 quarterly echo closes by cross-ref only.

*End sa-0573 cross-ref*
