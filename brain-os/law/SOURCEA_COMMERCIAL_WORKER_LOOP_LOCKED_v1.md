# SourceA — Commercial Worker Loop (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Authority:** ASF — production lane, not test harness  
**Router:** `SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md` · `WORKER_FAST_ANTI_STALENESS_AUTO_HEAL_LOCKED_v1.md`

---

## Law (one sentence)

**Worker ships sa with a thin hot path (~10s/turn) — broker transaction + ultra verify + fast propagation; full fleet is Safety/weekly only.**

---

## Commercial stack (default env)

| Env | Set by | Effect |
|-----|--------|--------|
| `SINA_COMMERCIAL_LOOP=1` | turn entry · verify · broker | Master fast lane |
| `SINA_WORKER_LOOP=1` | turn entry · verify | Redirect full FCB → ultra |
| `SINA_BROKER_FAST=1` | broker submit · orchestrator | Skip brain sync · pack validator · recovery |

---

## Hot path (every turn)

```text
worker_turn_entry_v1.sh     gate + AS heal (~1s)
ACT/CHECK/VERIFY            one sa · one role
worker_verify_ultra_v1.sh   VERIFY only (~1s)
goal1_lane_broker submit    fast broker (~1–5s)
  → validate YAML + receipt (VERIFY)
  → advance queue --fast
  → deliver INBOX --fast (no pack validator · no UI pop)
  → propagation cascade --fast (~300ms)
STOP
```

---

## What stays (commercial core)

| Component | Why |
|-----------|-----|
| **Broker** | Transaction: YAML → receipt → REGISTRY done → next INBOX |
| **Orchestrator** | CHECK→ACT→VERIFY state machine |
| **Ultra verify** | Honest closeout without 3 min shell |
| **AS auto-heal** | Kill hung shells · light sync |

---

## Cold path (not loop)

| Component | When |
|-----------|------|
| Full `find_critical_bugs` | Hub Safety · weekly |
| Anti-staleness bundle | Hub Safety |
| Brain sync full | Queue exhausted · Brain poll |
| Live pack validator | Safety · pack rebuild |
| `run_recovery` deep | Hub Unstick only |

---

## Machine proof

```bash
bash scripts/validate-commercial-worker-loop-v1.sh
bash scripts/validate-worker-anti-staleness-v1.sh
bash scripts/validate-fast-system-load-v1.sh
```

---

*End SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1*
