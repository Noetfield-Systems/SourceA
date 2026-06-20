# sa-0973 — validate-spine-bridge-founder proof types matrix (CHECK)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**SA:** sa-0973 · phase-s9-research-models · T2  
**Duplicates:** sa-0923 · sa-0948 · sa-0998 (same title — canonical here)  
**Law:** `brain-os/law/DISPATCH_POLICY_LOCKED_v1.md` · `runtime/graph_executor/spine_bridge.py` · sa-0416

## Thesis

`validate-spine-bridge-founder-v1.sh` is the **founder-safe proof gate** for graph-executor spine handoff. It asserts two parallel proof paths — **planner bridge** (C7 `pos-dispatch` chain) and **eval proof bridge** (`spine-smoke-echo`) — while **hard-locking** `dispatch_ready: false` (founder confirm always required).

## Proof types matrix

| Proof type | SSOT field | Action / trigger | Policy class | Gate required | `spine_bridge_ready` when |
|------------|-----------|------------------|--------------|---------------|---------------------------|
| **Planner bridge** | `planner_bridge_ready` | First `spine_sequence.action_ids[0]` (e.g. `pos-dispatch`) | `suggest` or `auto_low_risk` | `founder_spine_bridge_gate_ok` + plan `ready` + not `blocked` | `auto_low_risk` only → `planner_auto_bridge_ready` |
| **Eval proof bridge** | `eval_proof_bridge` | `spine-smoke-echo` (smoke echo) | `auto_low_risk` | `founder_spine_bridge_gate_ok` + Eval-1b eligibility | `eval_proof_ready` true |
| **Structural fallback** | `founder_spine_bridge_gate_ok` | Eval live blocked (402) · scaffold ≥80% | N/A — unlocks gate only | `eval_1b_ci_mode_v1.json` `structural_fallback` + report `mode=scaffold` | Gate open; **dispatch still false** |
| **Live Eval-1b** | `eval_1b_gate_ok` | `~/.sina/eval_packet_v1b_report.json` `mode=live` | Unlocks `auto_low_risk` tier | `live_pilot_win_pct` ≥ 80 · `live_ok` | Full live path |

## Policy class → instruction mapping

| `policy_class` | `instruction.action` | Founder UX | Auto dispatch |
|----------------|---------------------|------------|---------------|
| `observe` | `blocked_or_review` | Read-only validators | **Never** |
| `suggest` | `founder_confirm_required` | Hub confirm on planner chain | **Never** |
| `auto_low_risk` | `founder_confirm_then_enqueue_spine` | Confirm then enqueue smoke/validate | **Never** (`dispatch_ready` locked false) |

**Founder law invariant:** `dispatch_ready` and `auto_dispatch` must stay **false** — validator asserts this explicitly.

## Gate status tree

```text
eval_1b_gate_status()
  ├─ live_ok (mode=live, pct≥80) → founder_gate OPEN
  └─ live blocked
       └─ structural_fallback + scaffold≥80 → founder_gate OPEN (note: dispatch_ready stays false)
            └─ else → founder_gate CLOSED

founder_spine_bridge_gate_ok → eval_proof_bridge.spine_bridge_ready
planner_auto_bridge_ready → first_action auto_low_risk + gates + branch spec
spine_bridge_ready = planner_auto OR eval_proof_ready
```

## Validator contract (`validate-spine-bridge-founder-v1.sh`)

| Assert | Meaning |
|--------|---------|
| `build_spine_bridge().ok` | Planner snapshot exists |
| `founder_spine_bridge_gate_ok` | Gate open (live or structural) |
| `dispatch_ready is False` | Founder law — no silent auto-run |
| `eval_proof_bridge.spine_bridge_ready` | Smoke echo path eligible |
| `/api/graph-executor-v1` mirrors gate | Hub API SSOT alignment |

## Live snapshot (2026-06-14)

| Field | Value |
|-------|-------|
| `eval_1b_gate_ok` | false — scaffold only |
| `founder_spine_bridge_gate_ok` | false |
| `first_action_id` | `pos-dispatch` |
| `policy_class` | `suggest` |
| `instruction.action` | `founder_confirm_required` |
| `eval_proof.action_id` | `spine-smoke-echo` |
| `eval_proof.spine_bridge_ready` | false |
| `dispatch_ready` | false |

Validator **FAIL** expected until Eval-1b live pass or structural fallback enabled — honest scaffold state.

## Industry comparators

| Pattern | Vendor norm | SourceA delta |
|---------|-------------|---------------|
| Auto tool dispatch | Agent runs bash without confirm | `dispatch_ready` hard false |
| Risk tiers | Implicit in prompt | `observe` / `suggest` / `auto_low_risk` machine classes |
| Eval-gated automation | A/B before prod | Eval-1b live ≥80% unlocks low-risk tier only |
| Smoke proof | CI echo step | `spine-smoke-echo` via graph executor bridge |

## ACT backlog

| Item | Owner |
|------|-------|
| Document matrix in validator header comment | Worker ACT |
| Optional `validate-spine-bridge-proof-matrix-v1.sh` wrapper | Worker ACT |
| Live Eval-1b unlock | separate sa-0131 family · not this CHECK |

## WTM thread

- **Spine:** Pre-LLM eval-dispatch · C7 planner → graph executor  
- **Related:** sa-0416 founder bridge · sa-0403/0428 proof echo runs · `DISPATCH_POLICY_LOCKED_v1.md`  
- **Deferred:** OpenRouter behavioral proof tier (phase-s9 boundary)

## CHECK verdict

Proof types matrix is **documented and machine-mapped**: planner bridge vs eval smoke echo vs structural fallback, all under founder-confirm-only dispatch policy.
