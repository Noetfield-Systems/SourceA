# sa-0822 — scheduled_cadence UP-01..UP-06 excluded from pending_total

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Tier:** T0 · **Hub 2** `/machines/`

## Verdict (one line)

`UP-01` through `UP-06` machine-refinement rows belong in `scheduled_cadence[]` only — counted in `scheduled_total`, **never** in `pending_total` / `pending_open`.

## Bucket contract

| Field | Rule |
|-------|------|
| **Registry path** | `~/.sina/h2-pending-registry-v1.json` → `scheduled_cadence[]` |
| **Canonical ids** | `UP-01` … `UP-06` (from `machine_three_pipelines_lib_v1.UPGRADE_BOARD`) |
| **SSOT goals** | RAGAS CI · Demo film W1 · Kernel write path · Test ladder · Refine pipelines · Agentic layer v3 |
| **Required keys** | `id` · `title` · `cadence` · `status` (`scheduled`) |
| **Count rule** | `h2_pending_count_lib_v1._maintainer_open()` returns **False** for `UP-*` |
| **pending_total** | Sum of `form_open` + `next_phase` + `deferred` + `ops_blocker` + open `maintainer_ship` only |
| **scheduled_total** | `len(scheduled_cadence)` + maintainer rows with `cadence` + done status |
| **Forbidden buckets** | `deferred` · `next_phase` · open `maintainer_ship` must not contain `UP-*` |

## Row map (UPGRADE_BOARD)

| id | goal | cadence |
|----|------|---------|
| UP-01 | RAGAS CI vs Eval-1b | Quarterly |
| UP-02 | Demo film W1 | Weekly |
| UP-03 | Kernel single write path | Daily |
| UP-04 | Machine test ladder | Daily |
| UP-05 | Machine refine pipelines | Daily smoke |
| UP-06 | Agentic layer v3 | Weekly |

## Reconcile rule

`h2_pending_registry_reconcile_v1.py` seeds missing `UP-*` into `scheduled_cadence` and strips stray `UP-*` from `deferred` / `next_phase`.

## Machine proof

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-h2-scheduled-cadence-up-pending-total-v1.sh
python3 h2_pending_registry_reconcile_v1.py --json
```

## Law

`SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` slot **22** · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §2a · `h2_pending_count_lib_v1.py`

*End sa-0822*
