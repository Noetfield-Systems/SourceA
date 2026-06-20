# Worker — No Slow VERIFY Shell (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Authority:** ASF — Worker stuck 2–3 min on shell blocks W1/W3 ship  
**Router:** `AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md` · `WORKER_FAST_ANTI_STALENESS_AUTO_HEAL_LOCKED_v1.md` · `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md`  
**Index:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` row `WORKER_VERIFY_FAST`

---

## Law (one sentence)

**Worker VERIFY closes the sa with the fast lane (~10s) — never default full `find_critical_bugs.py` or anti-staleness bundle; full fleet rollup = Hub Safety only.**

---

## Why Worker stuck 3 min on shell

| Cause | Time | Where |
|-------|------|--------|
| `find_critical_bugs.py` **full** | **60–180s+** | Runs 44-step anti-staleness bundle |
| sa-XXXX verify line says only `find_critical_bugs.py` | Every VERIFY | 297 prompts |
| Old DEFAULT VERIFY | Worker skill + mandatory chat | Still listed full FCB |

**Not the hub:** `#p0-next` text is disk truth · ms API · unrelated to Cursor shell wait.

---

## Default Worker VERIFY (every sa closeout)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash worker_verify_ultra_v1.sh
```

Runs **anti-staleness auto-heal** then hub check (~1–8s). For CHECK-only with optional FCB fast: `worker_verify_fast_v1.sh`.

**Forbidden as default VERIFY:**

```bash
python3 find_critical_bugs.py                    # FULL — 60–180s+
bash validate-anti-staleness-bundle-v1.sh        # Safety / weekly only
SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py
```

---

## When full `find_critical_bugs` is allowed

| Who | When |
|-----|------|
| **Founder** | Hub → **Safety check** (one tap) |
| **Worker** | sa prompt **explicitly** says `full fleet` or `anti-staleness bundle` |
| **Maintainer** | Weekly hygiene · gate sa |

**Fast Worker CHECK turn only:**

```bash
SINA_FCB_FAST=1 python3 find_critical_bugs.py   # ~6s — not VERIFY closeout default
```

---

## sa-XXXX verify line interpretation

If prompt says `find_critical_bugs.py` alone → run **`worker_verify_fast_v1.sh`** instead.  
Honest closeout cites fast gate PASS + task validator. Full FCB is **not** implied.

---

## Machine proof

```bash
bash scripts/worker_verify_ultra_v1.sh
time bash scripts/worker_verify_ultra_v1.sh   # expect < 8s (full FCB = 60–180s)
bash scripts/validate-worker-anti-staleness-v1.sh
```

---

## Worker loop (CHECK → ACT → VERIFY)

**One sa · one role per turn.** No fleet hygiene in the loop.

| Turn | Run | Never |
|------|-----|-------|
| CHECK | preflight + gap | implement · full FCB |
| ACT | minimal diff | closeout · batch |
| VERIFY | **`worker_verify_ultra_v1.sh`** + sa-specific | full `find_critical_bugs` · strict build |

**Injection:** `healthy_prompt_turn_v1.py` rewrites stale sa verify via `worker_verify_normalize_v1.py`.

**Full fleet:** Hub Safety only · weekly · not every loop turn.

---

## VERIFY closeout (permanent — INCIDENT-006/007)

**Forbidden:** editing `REGISTRY.json` or `sa-XXXX.md` status directly.

**Required order:**

1. Task validator(s) PASS  
2. `WORKER_ROUND_REPORT` + `goal1_lane_broker.py worker-submit --stdin`  
3. `receipts/sa-XXXX-receipt.json` logged  
4. **Canonical closeout:**

```bash
bash scripts/worker_verify_closeout_v1.sh --sa sa-XXXX \
  --evidence "per-sa proof string" \
  --task-validator validate-your-task-v1.sh   # optional
```

5. `bash scripts/worker_verify_fast_v1.sh` (includes auto-revert if receipt missing)

**Auto-heal:** `validate-registry-honest-gate-v1.sh` reverts any `done` without receipt on every fast verify.

---
