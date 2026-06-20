# sa-0821 — ops_blocker bucket row contracts (MP-SHIP · WIRE-G3 · B-001)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Tier:** T0 · **Hub 2** `/machines/` · **Sina Command quarantine**

## Verdict (one line)

`ops_blocker` in `~/.sina/h2-pending-registry-v1.json` is the **machine pending SSOT** for three canonical ship blockers; Hub 1 `sina_command_lib.ops_blockers()` is the **live projection** with richer fields — both must agree on `id`, `severity`, and `action` semantics.

## Bucket contract

| Field | Rule |
|-------|------|
| **Registry path** | `~/.sina/h2-pending-registry-v1.json` → `ops_blocker[]` |
| **Allowed ids** | `MP-SHIP`, `WIRE-G3`, `B-001` only (fixed set until ASF extends plan slot 21) |
| **Required keys (H2 minimal)** | `id` (string) · `severity` (`high` \| `medium` \| `critical`) · `action` (string, founder-readable one line) |
| **Optional keys (hub projection)** | `title` · `status` · `founder_actions[]` with `{id, label}` — emitted by `scripts/sina_command_lib.py` `ops_blockers()` |
| **Count in pending_total** | Each open row counts toward `h2_pending_count_lib_v1.count_h2_pending` |
| **Ship order** | MP-SHIP first · WIRE-G3 second · B-001 parallel infra review |
| **H1 surface** | One-line alarm only (`SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §2a) |
| **H2 surface** | Full table via `machine_hub_v1.py` → `ops_blocker` passthrough |

## Row contracts

### MP-SHIP

| Key | Contract |
|-----|----------|
| **id** | `MP-SHIP` |
| **severity** | `high` |
| **title (projection)** | MergePack public ship |
| **action** | Disable Vercel Deployment Protection · verify `/health` |
| **status source** | `mp_prog.milestones.MP-SHIP` — row present while `!= pass` |
| **thread** | `THREAD-MERGEPACK` · `GOAL-MP-SHIP` |
| **founder_actions** | `founder-open-form-pdf` · `founder-verify-mp-health` · `founder-refresh` |
| **close when** | MergePack milestone `MP-SHIP: pass` and `/health` 200 public |

### WIRE-G3

| Key | Contract |
|-----|----------|
| **id** | `WIRE-G3` |
| **severity** | `medium` |
| **title (projection)** | Wire G3 Tailscale |
| **action** | Run g3 proof · record `WIRE_LANE_PROGRESS.md` |
| **status source** | `wire.g3_tailscale == pending` |
| **deferred link** | `deferred[]` id `Q-WIRE-G3` pick `RECONCILE` — closes when proof recorded |
| **founder_actions** | `founder-wire-preflight` · `founder-open-wire-progress` |
| **close when** | `g3_tailscale` not `pending` and `WIRE_LANE_PROGRESS.md` receipt on disk |

### B-001

| Key | Contract |
|-----|----------|
| **id** | `B-001` |
| **severity** | `medium` in H2 registry · `critical` in hub when law collision active |
| **title (projection)** | Active law collision — infra |
| **action** | Review `ARCHITECT_REPORT.yaml` · ingest pipeline · resolve per `GLOBAL_BLOCKERS.json` |
| **status source** | `progress.signals_auto.architect_blockers` contains `B-001` or `law collision`, or `BOWL_STATE.blockers` id `B-001` |
| **founder_actions** | `founder-open-global-blockers` · `founder-open-architect-report` |
| **close when** | No B-001 row in architect signals and bowl blockers cleared |

## Schema drift (documented — not a failure)

| Layer | Shape |
|-------|-------|
| **H2 registry** | Minimal `{id, severity, action}` — machine reconcile target |
| **Hub projection** | Rich `{id, severity, title, action, status, founder_actions}` — runtime from `ops_blockers()` |
| **Sync rule** | Reconcile script must preserve the three ids; projection may add fields not stored in registry |

## Machine proof

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-h2-ops-blocker-row-contracts-v1.sh
```

## Law

`SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` slot **21** · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §2a bucket taxonomy

*End sa-0821*
