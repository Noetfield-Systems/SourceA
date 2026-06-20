# sa-0799 ACT — Harden essay mark-best POST without ASF as sole actor

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T21:30Z · **Turn:** ACT · **Worker:** SourceA

## Shipped (scripts only — Worker Hub law; legacy hub archived)

| Piece | Change |
|-------|--------|
| `scripts/agent_essay_discourse.py` | `mark_best` requires `actor` (`founder`\|`maintainer`) + attestation token |
| Attestation SSOT | `~/.sina/essay-mark-best-attestation-v1.json` (auto-created) |
| Audit trail | `~/.sina/essay-discourse/mark-best-receipts.jsonl` |
| Deny event | `essay_best_mark_denied` governance log on failed auth |
| Payload contract | `mark_best_contract` in `essay_discourse_payload()` — not fleet verify |
| Validator | `scripts/validate-essay-mark-best-v1.sh` |

## Authority preserved

- **ASF qualitative:** founder still picks winner (law §0 unchanged)
- **Machine verify:** fleet `auto_pass` — **not** mark_best
- **Co-actor:** `maintainer` may mark_best with same attestation token

## OPEN (Maintainer — legacy `/legacy/` only)

Hub `app.js` Mark best button must pass `actor: "founder"` + attestation from disk token until Worker Hub wires essay UI.

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-essay-mark-best-v1 | PASS |
| validate-governance-fleet-v1 | PASS |
| validate-dispatch-policy-v1 | PASS |

*End sa-0799 ACT*
