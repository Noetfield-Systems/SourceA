# sa-0799 VERIFY receipt

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Turn:** VERIFY · **Status:** **done**  
**Date:** 2026-06-13T21:30Z

## Shipped proof

| Piece | Proof |
|-------|-------|
| `mark_best` auth | `actor` ∈ {founder, maintainer} + attestation token required |
| Deny path | Anonymous POST → `mark_best_actor_required` |
| Validator | `validate-essay-mark-best-v1.sh` PASS |
| Fleet verify | Unchanged — `not_fleet_verify` in `mark_best_contract` |

## Validators

| Validator | Result |
|-----------|--------|
| validate-essay-mark-best-v1 | PASS |
| validate-governance-fleet-v1 | PASS |
| validate-dispatch-policy-v1 | PASS |
| validate-incident-028-fast-v1 | PASS |
| worker_verify_fast_v1 | PASS (Worker Hub · FCB fast) |

## Closeout

- REGISTRY `sa-0799` → **done**
- `SOURCEA-PRIORITY.md` evidence row added
- Authority index: `WORKER_VERIFY_FAST` row wired (orphan fix)

## OPEN (Maintainer)

Legacy `/legacy/` essay UI must pass `actor` + `attestation` on Mark best click.

## Next queue

**sa-0800** — Append council governance evidence row after fleet essay wave

*End VERIFY*
