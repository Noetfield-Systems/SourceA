# Worker — Fast Anti-Staleness Auto-Heal (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Authority:** ASF — fast Worker loop with self-healing  
**Router:** `SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md` · `WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md`  
**Index:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` row `WORKER_AS_HEAL`

---

## Law (one sentence)

**Every Worker loop turn runs fast anti-staleness probe + auto-heal (~1–8s) — kill hung shells, sync inbox, light hub heal — never full fleet on the loop path.**

---

## Machine (one command)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
python3 worker_anti_staleness_heal_v1.py --json
```

| Flag | Use |
|------|-----|
| `--probe` | Disk probe only (~ms) |
| `--force` | Bypass heal cooldown |
| `--deep` | Full `worker_stuck_recovery` (founder Unstick class) |

**Receipt:** `~/.sina/worker-as-heal-receipt-v1.json`

---

## Wired into loop

| Step | Script |
|------|--------|
| **Turn entry** | `worker_turn_entry_v1.sh` → AS heal `--force` |
| **VERIFY** | `worker_verify_ultra_v1.sh` → probe + heal if stale |
| **Hub** | `/api/worker-hub/heal` · auto-heal on stale poll |
| **Unstick** | `--deep` or `founder-unstick-worker` action |

---

## Fast heal steps (not full fleet)

1. `staleness_probe` — AS latches · age · dual-pick  
2. `kill_hung_processes` — stop 3 min `find_critical_bugs` / strict build  
3. `sync_orchestrator_from_inbox` — queue/inbox align  
4. `hub_heal` light — if stale + cooldown ok  
5. Re-probe → receipt  

**Forbidden on loop:** `validate-anti-staleness-bundle` · full `find_critical_bugs` · strict build · **post-VERIFY hub refresh** (hub polls ms · Safety only)

---

## Commercial rule (not kid-project)

| After VERIFY | Required? |
|--------------|-----------|
| `worker_verify_ultra_v1.sh` | **Yes** (~1s) |
| Broker `--fast` propagation | **Yes** (~ms) |
| Light/full hub refresh | **No** — Super Fast Hub auto-heals on poll |
| Full `find_critical_bugs` | **No** — redirects to ultra when `SINA_WORKER_LOOP=1` |

*End WORKER_FAST_ANTI_STALENESS_AUTO_HEAL_LOCKED_v1*
