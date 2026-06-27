# INCIDENT-044 — Cloud Forge Run NO SKIP · mandatory 100 shipped per turn

**Locked:** 2026-06-24T22:00:00Z  
**Pairs:** INCIDENT-043 · `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json` · `data/cloud-auto-runtime-v1.json`

## One law (ASF)

> **Every Auto Runtime turn (~10 min) MUST ship 100 rows. Skipped rows are forbidden. Motor fail HALTS the turn — head does not advance via skip_head.**

## Pass criteria (observer)

| Field | Required |
|-------|----------|
| `pack.shipped` / `pack.advanced` | **100** (or batch tail: all remaining, still zero skips) |
| `pack.skipped` | **0** |
| `pack.processed` | equals shipped (not shipped+skipped) |

## Forbidden

- `self_heal_any_motor_fail: true`
- `skip_head` on motor fail inside `run_auto_runtime_pack`
- Founder phrase “high skipped still PASS”

## Fix shipped

- `scripts/cloud_worker_dispatch_v1.py` — parse URLs from `cloud_action`
- `scripts/cloud_auto_runtime_v1.py` — `no_skip_law`, halt on motor fail
- `data/cloud-auto-runtime-v1.json` — self-heal off, `mandatory_shipped_per_turn: 100`
