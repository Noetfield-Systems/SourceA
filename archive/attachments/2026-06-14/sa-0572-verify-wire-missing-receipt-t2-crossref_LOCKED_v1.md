# sa-0572 — T2 cross-ref to canonical verify:wire missing-receipt hardening (sa-0522)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T23:17Z · **Tier:** T2 · **canonical_sa:** sa-0522 · **No re-implement assert gate prose**

## Dedup

| Key | Ref |
|-----|-----|
| **canonical_sa** | sa-0522 |
| **canonical_attachment** | `archive/attachments/2026-06-14/sa-0522-verify-wire-missing-receipt_LOCKED_v1.md` |
| **canonical_receipt** | `receipts/sa-0522-receipt.json` |
| **assert_fn** | `scripts/runreceipt/pack_v1.py::assert_runreceipt_artifacts` |
| **t1_echo** | sa-0547 · `verify_wire_missing_receipt_t1_crossref` |
| **this_sa** | sa-0572 (T2 quarterly hardening — cite only) |

## Machine proof (existing validators — no duplicate hardening table)

- `scripts/validate-verify-wire-missing-receipt-program-progress-v1.sh` — sa-0522 PROGRAM_PROGRESS hook + negative probe
- `scripts/validate-verify-wire-missing-receipt-v1.sh` — negative probe PASS when artifacts removed
- `scripts/validate-verify-wire-v1.sh` — assert-only gate (no auto-build)

## Factory verdict (one line)

verify:wire missing-receipt hardening is T0-canonical at sa-0522; T2 quarterly echo closes by cross-ref only.

*End sa-0572 cross-ref*
