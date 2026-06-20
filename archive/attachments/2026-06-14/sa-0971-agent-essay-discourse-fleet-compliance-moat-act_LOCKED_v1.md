# sa-0971 ACT — Essay discourse fleet compliance moat hardening

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T03:04Z · **Turn:** ACT · **Worker:** SourceA

## Shipped

| Piece | Change |
|-------|--------|
| `scripts/validate-essay-discourse-fleet-moat-v1.sh` | Quarterly moat crosswalk — chains essay-nudges + mark-best validators; asserts law doc, vault deposit markers, FR-008 threshold, fleet auto-green |
| CHECK doc | `sa-0971-agent-essay-discourse-fleet-compliance-moat_LOCKED_v1.md` (prior turn) |

## Moat signals enforced (machine)

| Signal | SSOT | Validator assert |
|--------|------|------------------|
| Participation gap | `nudge_count` == len(`essay_nudges`) | governance-fleet + moat crosswalk |
| Vault evidence | `deposit_document` + `essay_submitted` in `submit_essay` | moat crosswalk source scan |
| Mark-best authority | `mark_best_contract.actors` + attestation | validate-essay-mark-best-v1 |
| FR-008 fleet row | nudges ≤ 2 → shipped | moat crosswalk threshold check |
| Scoreboard coupling | `fleet_auto_green_count` / `agent_count` | moat crosswalk live read |

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-essay-discourse-fleet-moat-v1 | PASS |
| validate-essay-nudges-council-v1 | PASS (chained) |
| validate-essay-mark-best-v1 | PASS (chained) |
| validate-governance-fleet-v1 | PASS |

## OPEN (VERIFY turn)

- Append SOURCEA-PRIORITY evidence row (if not done here)
- Mark sa-0921 / sa-0946 / sa-0996 `consolidated` in REGISTRY on VERIFY closeout
- Register moat validator in `find_critical_bugs.py` optional T2 soak (deferred — not CRITICAL)

*End sa-0971 ACT*
