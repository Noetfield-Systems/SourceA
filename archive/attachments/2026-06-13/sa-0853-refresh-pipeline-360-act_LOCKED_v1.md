# sa-0853 ACT — Fix refresh pipeline total time under 360s for audit E2E

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T22:30Z · **Turn:** ACT · **Worker:** SourceA

## Shipped

| Piece | Change |
|-------|--------|
| `audit_backend_e2e.py` | `REFRESH_E2E_BUDGET_SEC=360` · light `POST /refresh` · timed poll ≤360s |
| `audit_backend_e2e_light_v1.py` | `refresh-light` expects **200** · `mode: light` |
| `validate-refresh-pipeline-360-v1.sh` | **NEW** — budget marker + live light timing |

## Proof (ACT)

| Check | Result |
|-------|--------|
| Live light refresh | **0.67s** ≤ 360s · HTTP **200** |
| `audit_backend_e2e_light_v1.py` | **PASS** all checks |
| generation_id | increments on light refresh |

## Hub law preserved

- **Worker Hub daily** = light refresh only (not full rebuild in E2E default)
- Full async `mode:full` still accepted if server returns **202** (poll within 360s budget)

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-refresh-pipeline-360-v1 | PASS |
| audit_backend_e2e_light_v1 | PASS |

*End sa-0853 ACT*
