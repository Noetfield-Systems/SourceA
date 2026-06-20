# sa-0952 — Cursor agent vs Devin vs SWE-agent on SourceA verify gates

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research spike · **No code diff**

## Compare matrix (verify gates)

| Agent runtime | Autonomy | SourceA verify gate fit | Gap |
|---------------|----------|-------------------------|-----|
| **Cursor Worker** | Human-in-loop chat + broker CHECK→ACT→VERIFY | **Canonical** — `worker_verify_closeout_v1` · receipts · `worker_verify_fast_v1` | INCIDENT-030 class if YAML-only closeout |
| **Cognition Devin** | Autonomous SWE in repo | Partial — can run validators; **no** broker receipt SSOT without factory adapter | No `goal1_lane_broker` bind · no REGISTRY law |
| **SWE-agent (academic/OS)** | Issue→patch loops | Research only — no SourceA spine | No founder no-Terminal law · no dual_proof |

## SourceA verify stack (what they must match)

1. Task validators PASS  
2. `WORKER_ROUND_REPORT` → `goal1_lane_broker worker-submit`  
3. `receipts/sa-XXXX-receipt.json`  
4. `worker_verify_closeout_v1.sh`  
5. `worker_verify_fast_v1.sh` (registry-honest + broker-receipt)

## Verdict

**Cursor Worker is the only runtime wired to honest factory closeout today.** Devin/SWE-agent are ** references** (constellation L4) — integrate only behind broker + receipt adapter, never parallel REGISTRY writers.

**ACT shipped:** this spike doc only — no D-module.
