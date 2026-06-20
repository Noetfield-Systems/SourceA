# sa-0798 ACT — Order guardian judgments vs pendings statuses

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T21:05Z · **Worker:** SourceA · **Turn:** ACT  
**Task:** Cross-check order guardian judgments vs pendings statuses

## Verdict

| Check | Result |
|-------|--------|
| Judgment × status contract | **0 mismatches** (24 orders) |
| Pendings ↔ orders cross-SSOT | **6 drift warns** (informational — no auto-sync) |
| Fleet signals | essay_gap **0** · scoreboard_verified **8/8** · drift **100** |

**Internal consistency:** PASS — every `orders.jsonl` row matches `STATUS_JUDGMENT_CONTRACT`.

**Cross-SSOT drift (unchanged):**

| Pending | Pend | Order | Order status · judgment | Note |
|---------|------|-------|-------------------------|------|
| P2 | partial | TO-DRIFT | partial · partial | **Aligned** |
| P8 | done | TO-008 | needs_activation · needs_activation | Drift + fleet_green stale |
| P9 | done | TO-009 | needs_activation · needs_activation | Drift + fleet_green stale |
| P10 | in_progress | TO-SKU | deferred · different_goal | Different scope |
| P11 | done | TO-WIRE | open · missed | Drift |

## Shipped (ACT)

| Artifact | Path |
|----------|------|
| Contract SSOT | `scripts/task_orders_guardian.py` `STATUS_JUDGMENT_CONTRACT` |
| Crosswalk reporter | `scripts/order_guardian_pendings_crosswalk_v1.py` |
| Validator | `scripts/validate-order-guardian-judgment-sync-v1.sh` |

## Validators (ACT)

- `validate-order-guardian-judgment-sync-v1.sh` — PASS (drift WARN only)
- `validate-dispatch-policy-v1.sh` — PASS
- `validate-governance-fleet-v1.sh` — PASS

## Next (VERIFY turn)

- `find_critical_bugs.py` · REGISTRY closeout · `SOURCEA-PRIORITY` evidence row

## Maintainer OPEN (no Worker scope)

- Reconcile TO-008/TO-009 → `shipped` when fleet 8/8 (hub Order Guardian action)
- Show `judgment` in Order Guardian UI row

*End sa-0798 ACT crosswalk LOCKED v1*
