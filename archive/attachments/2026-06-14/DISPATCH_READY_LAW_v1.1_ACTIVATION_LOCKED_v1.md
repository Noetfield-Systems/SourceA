# Dispatch ready law v1.1 — activation (LOCKED)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**ASF order:** orchestrator `dispatch_ready` must not be hard-false by law  
**Authority:** `brain-os/law/DISPATCH_POLICY_LOCKED_v1.md` v1.1

## New law

`dispatch_ready = orchestrator_dispatch_ready()` on hub, orchestrator, graph_executor when **all** pass:

1. `eval_1b_gate_ok` (live ≥80%)
2. `gate_mode = enforce`
3. `eval_tier = behavioral_pass`
4. `founder_spine_bridge_gate_ok`
5. `critical_count = 0`

## Machine SSOT

- `scripts/runtime/dispatch_policy/policy_engine.py` → `orchestrator_dispatch_ready()`
- `scripts/dispatch_ready_lock.py` → hub sync validator
- `~/.sina/dispatch_policy_v1.json` · `graph_executor_v1.json` · runtime orchestrator snapshot

## Still forbidden

- Silent auto-dispatch on CONFIRM-tier (deploy/migrate/delete)
- `auto_dispatch=true` on hub surfaces
- `dispatch_ready=true` while `critical_count > 0`

## Founder action when true

Hub → **Spine bridge Action** → enqueue eval proof / planner chain (founder confirm on high-risk).

*End DISPATCH_READY_LAW_v1.1_ACTIVATION_LOCKED_v1*
