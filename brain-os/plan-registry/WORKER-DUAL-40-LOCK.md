# Worker 1 unified pack (LOCKED v1.3)

**trace_tag:** `AUTO-TRACE-WORKER-W1-PACK-LOCK-v1.3`  
**agent:** `Auto`  
**Locked:** 2026-06-08 · **One worker only**

## Pack

| Block | IDs | Count |
|-------|-----|-------|
| **REGISTRY sa** | `w1-01`…`w1-20` | sa-0131→sa-0150 |
| **Loop A autoloop** | `w1-21`…`w1-40` | broker · AUTO-RUN · hygiene |

**Paste queue:** `.sina-loop/WORKER-1-PASTE-QUEUE.md`  
**Closeout:** `brain-os/plan-registry/worker-dual-40/WORKER1_UNIFIED_CLOSEOUT_LOCKED_v1.md`

## Default rail

**Rail A:** Hub ▶ AUTO-RUN — LIVE_PICK only. Manual `w1-*` = fallback only.

## Regenerate

```bash
python3 scripts/generate-worker-dual-40.py
```

## Finish (all 40)

```bash
bash scripts/finish-worker-1-unified-v1.sh
```
