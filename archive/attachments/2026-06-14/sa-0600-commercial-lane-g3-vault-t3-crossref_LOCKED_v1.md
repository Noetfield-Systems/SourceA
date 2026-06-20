# sa-0600 — T3 cross-ref to canonical commercial lane G3 vault evidence (sa-0525)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15T01:12Z · **Tier:** T3 · **canonical_sa:** sa-0525 · **Research spike — cite only**

## Dedup

| Key | Ref |
|-----|-----|
| **canonical_sa** | sa-0525 |
| **canonical_attachment** | `archive/attachments/2026-06-14/sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md` |
| **canonical_receipt** | `receipts/sa-0525-receipt.json` |
| **probe_fn** | `scripts/commercial_lane_g3_vault_v1.py::probe_g3_vault_visibility` |
| **append_fn** | `scripts/commercial_lane_g3_vault_v1.py::append_priority_g3_evidence_if_visible` |
| **t1_echo** | sa-0550 · `commercial_lane_g3_vault_t1_crossref` |
| **t2_echo** | sa-0575 · `commercial_lane_g3_vault_t2_crossref` |
| **this_sa** | sa-0600 (T3 research spike — cite only) |

## Machine proof (existing validators — no duplicate G3 table)

- `scripts/validate-commercial-lane-g3-vault-program-progress-v1.sh` — sa-0525 PROGRAM_PROGRESS hook wired
- `scripts/validate-commercial-lane-g3-vault-evidence-v1.sh` — conditional PRIORITY append only when G3 visible

## Factory verdict (one line)

Commercial lane G3 vault conditional evidence is T0-canonical at sa-0525; T3 research echo closes by cross-ref only. G3 pending logged is deferred by design.

*End sa-0600 cross-ref*
