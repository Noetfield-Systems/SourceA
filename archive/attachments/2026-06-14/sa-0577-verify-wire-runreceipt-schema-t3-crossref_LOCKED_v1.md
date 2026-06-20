# sa-0577 — T3 cross-ref to canonical verify:wire RunReceipt schema (sa-0502)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T23:32Z · **Tier:** T3 · **canonical_sa:** sa-0502 · **Research spike — cite only**

## Dedup

| Key | Ref |
|-----|-----|
| **canonical_sa** | sa-0502 |
| **canonical_attachment** | `archive/attachments/2026-06-14/sa-0502-verify-wire-runreceipt-schema_LOCKED_v1.md` |
| **canonical_receipt** | `receipts/sa-0502-receipt.json` |
| **missing_receipt_hardening** | sa-0522 · `archive/attachments/2026-06-14/sa-0522-verify-wire-missing-receipt_LOCKED_v1.md` |
| **t1_echo** | sa-0527 · `verify_wire_t1_crossref` |
| **t2_echo** | sa-0552 · `verify_wire_t2_crossref` |
| **schema_law** | `product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md` |
| **this_sa** | sa-0577 (T3 research spike — cite only) |

## Machine proof (existing validators — no duplicate schema prose)

- `scripts/validate-verify-wire-v1.sh` — assert-only gate
- `scripts/validate-verify-wire-runreceipt-schema-v1.sh` — sa-0502 positive path
- `scripts/validate-verify-wire-missing-receipt-v1.sh` — sa-0522 negative probe

## Factory verdict (one line)

RunReceipt wire schema is T0-canonical at sa-0502; T3 research echo closes by cross-ref only.

*End sa-0577 cross-ref*
