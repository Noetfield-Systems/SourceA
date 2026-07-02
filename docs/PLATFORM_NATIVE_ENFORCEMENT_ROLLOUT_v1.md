# Platform-native enforcement rollout v1

**Status:** IN PROGRESS (one item per cycle)  
**Saved at (UTC):** 2026-07-02T22:00:00Z  
**Law base:** governed-autorun v3 · NOETFIELD coherent system spec §4

## Order

| ID | Item | Status | Owner |
|---|---|---|---|
| PN-001 | `workflow_run` chain: deploy → external-verify | **SHIPPED** (`3240ac7aa`) | both |
| PN-002 | GHA `concurrency` groups (D2) + 15-recipe matrix fan-out | **SHIPPED** (reconciled from `aeb457c89`) | both |
| PN-003 | `environment: production` on deploy jobs (founder enables reviewer) | **PREP SHIPPED** (`efb141cec` + deploy job) | both |

## PN-001 — retired hand-rolled code

| Retired | Replaced by |
|---|---|
| `publish_sourcea_landing_v1.py` `run_founder_proof_verify(min_seconds=60)` inline sleep after deploy | `workflow_run` on successful `deploy-sourcea-buyer-surfaces-v1` |
| Manual “wait 60s then curl” timing guess in ship scripts | GitHub platform guarantee: verify starts only after deploy workflow `conclusion=success` |
| `--min-seconds-after-deploy 60` as primary deploy→verify gate in CI | `--min-seconds-after-deploy 0` when `VERIFY_TRIGGER_SOURCE=deploy_workflow_run_chain` |

## Artifacts

- Deploy workflow: `.github/workflows/deploy-sourcea-buyer-surfaces-v1.yml`
- Verify chain: `.github/workflows/external-verify.yml` (`workflow_run` trigger)
- Proof receipt: `receipts/proof/platform-native-001-workflow-run-chain-v1.json`

## SourceA design-only (founder_gated — no code)

- `docs/design/SOURCEA_CF_DO_QUEUE_MIGRATION_PLAN_FOUNDER_GATED_v1.md`

## NOOS prep (founder_gated — no code)

- `docs/design/NOOS_SUPABASE_REALTIME_PGCRON_T8_PREP_v1.md`
