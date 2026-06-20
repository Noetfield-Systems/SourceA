# SourceA — Fast System Load Budget (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Authority:** ASF — cut unnecessary loop tax  
**Router:** `WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md` · `AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md` · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md`

---

## Law (one sentence)

**Every lane has a wall-time budget — Worker loop ~10s/turn, hub poll ~ms, full fleet ~weekly on Safety only.**

---

## Load tiers

| Tier | Wall time | When | Commands |
|------|-----------|------|----------|
| **L0 Ultra** | **&lt;8s** | Worker VERIFY closeout · turn entry | `worker_verify_ultra_v1.sh` · `worker_anti_staleness_heal_v1.py` |
| **L1 Fast** | **&lt;15s** | Worker CHECK · agent status | `worker_verify_fast_v1.sh` · `SINA_FCB_FAST=1` |
| **L2 Hub** | **&lt;30s** | Founder Safety · weekly | `founder-ecosystem-safety` action |
| **L3 Fleet** | **60–180s** | Maintainer · explicit sa | full `find_critical_bugs.py` |
| **L4 Museum** | **5–50 min** | M2 legacy UI only | strict build · `--full` refresh |

---

## Removed from Worker loop (pain list)

| Unnecessary load | Was | Now |
|------------------|-----|-----|
| Full `find_critical_bugs` every VERIFY | 3+ min | **Ultra verify ~2s** |
| Strict build every VERIFY | 5–50 min | **Banned** — M2 only |
| 44-step anti-staleness every turn | 2+ min | **Safety only** |
| `session-start` + spine every INBOX turn | 30–90s | **`worker_turn_entry_v1.sh`** — gate only if fresh |
| `run_inbox` sync_disk every prompt build | 5–30s | **`sync=False`** read cache |
| `hub_self_refresh` align+wire+brain | ~40s | **`--quick`** skips |
| `program-1000 --write` on hub poll | ~1s | **Removed** from worker_hub_v1 |
| Duplicate fleet validators in autodrain | 2+ min | **`worker_verify_ultra_v1.sh`** |
| Full propagation cascade every VERIFY | 30–90s | **`governance_propagation_cascade --fast`** (~ms) |
| Agent runs `find_critical_bugs` from stale sa .md | 3+ min | **`SINA_WORKER_LOOP=1` redirect** → ultra |

---

## Worker loop (optimized)

```text
INBOX turn → worker_turn_entry_v1.sh (gate + AS auto-heal, skip stale session-start)
CHECK      → ultra or fast verify + gap only
ACT        → diff only · no verify
VERIFY     → worker_verify_ultra_v1.sh (AS heal + hub) + sa-specific · STOP
```

Full hygiene: Hub **Safety check** · not loop.

---

## Machine proof

```bash
bash scripts/validate-fast-system-load-v1.sh
bash scripts/validate-worker-loop-minimal-v1.sh
bash scripts/validate-worker-anti-staleness-v1.sh
time bash scripts/worker_verify_ultra_v1.sh
```

---

*End SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1*
