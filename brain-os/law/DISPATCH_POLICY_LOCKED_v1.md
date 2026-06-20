# Dispatch policy (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 — ASF activation 2026-06-14  
**Date:** 2026-06-06 (§Gate v1.1 2026-06-14)  
**Authority:** Maintainer · ASF order · gated on Eval-1b live pass + ENFORCE  
**Parent:** `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` Phase 2  
**Hub:** `/api/dispatch-policy-v1` · WTM dispatch policy panel

---

## Purpose

Assign **auto-execution classes** to spine actions after behavioral proof — without breaking founder confirm on high-risk paths.

---

## Classes

| Class | auto_dispatch | When |
|-------|---------------|------|
| `observe` | false | Read-only validators, hub refresh, audits |
| `suggest` | false | Planner chains, repair suggestions, C7 instruct-only |
| `auto_low_risk` | false* | spine-smoke-echo, validate-only — *eligible after Eval-1b live |

\* `auto_low_risk` becomes **eligible** (not auto) when Eval-1b live passes; founder confirm still required at orchestrator layer until Phase 2b.

---

## Gate (v1.1 — orchestrator dispatch_ready)

```
Eval-1b live A/B ≥ 80% pilot wins → dispatch_policy.eval_1b_gate_ok
→ gate_mode = enforce (~/.sina/gate_mode_v1.txt)
→ eval_tier = behavioral_pass
→ founder_spine_bridge_gate_ok
→ critical_count = 0 (find_critical_bugs)
→ orchestrator dispatch_ready = TRUE (machine SSOT: orchestrator_dispatch_ready())
```

When any gate fails → `dispatch_ready=false` with `dispatch_ready_blockers[]` on hub/API.

**CONFIRM-tier** tasks still require founder confirm even when `dispatch_ready=true`.  
**auto_dispatch** for high-risk writes stays **false** — no silent deploy/migrate/delete.

---

## Model gate modes — SHADOW vs ENFORCE (`model_dispatch.py`)

Separate from orchestrator **shadow dry_run** (below): **planner ingress** is gated by `scripts/model_dispatch.py`.

| Mode | Blocks OpenRouter planner? | Receipt log | Founder SSOT |
|------|------------------------------|-------------|--------------|
| **off** | No — observe only | — | `~/.sina/gate_mode_v1.txt` or `SINA_GATE_MODE` |
| **SHADOW** | No — logs **would-block** | `~/.sina/gate_shadow_v1.jsonl` | default when unset |
| **ENFORCE** | **Yes** when `gate_eligible` is false | `~/.sina/gate_enforce_v1.jsonl` | founder sets mode explicitly |

Rules:

- **SHADOW** = honest telemetry; packets still dispatch; use before flipping ENFORCE.
- **ENFORCE** = primary choke on `agent_loop` planner path when packet readiness fails (see `ENFORCE_BYPASS_MAP_LOCKED_v1.md` for bypass lanes).
- Hub panel: `/api/gate-receipts-v1` · `gate_receipts_hub.py` — mode + recent receipts.
- Orchestrator **task simulation** (`dispatch_decision.dry_run: true`) is separate from top-level `dispatch_ready` — simulation may differ per task_class; hub top-level follows `orchestrator_dispatch_ready()`.

---

## SSOT

- Policy: `~/.sina/dispatch_policy_v1.json`
- Eval-1b: `~/.sina/eval_packet_v1b_report.json`
- Bridge: `~/.sina/graph_executor_v1.json`

---

## Phase 2a — Task-class registry (dual-layer model)

Two layers work together; top-level `dispatch_ready` reflects activation gates (v1.1).

| Layer | Module | Unit | Classes |
|-------|--------|------|---------|
| **1 — Spine bridge** | `runtime.dispatch_policy.classifier` | `action_id` | `observe` · `suggest` · `auto_low_risk` |
| **2 — Task dispatch** | `runtime.dispatch_policy.allowlist` | `task_class` | `SAFE_AUTO` · `BEHAVIORAL` · `CONFIRM` |

`policy_engine.evaluate()` runs Layer 2 against C2 verified graph + C3 router + `eval_tier`.  
Orchestrator attaches `dispatch_decision` with `dry_run: true` for per-task simulation; **top-level** `dispatch_ready` from `orchestrator_dispatch_ready()`.

**Claude spec errata:** compare-only `~/Downloads/dispatch_policy_interface_1.md` — full delta in [`docs/DISPATCH_POLICY_INTERFACE_ERRATA_v1.md`](docs/DISPATCH_POLICY_INTERFACE_ERRATA_v1.md). Event bus `spine.bridge` on successful enqueue when `dispatch_ready=true`.

### Action ↔ task_class mapping (canonical)

| action_id | classifier (L1) | task_class (L2) | tier |
|-----------|-----------------|-----------------|------|
| `spine-smoke-echo` | `auto_low_risk` | `validate-only` | SAFE_AUTO |
| `validate-*` / `audit-*` | `observe` | `validate-only` | SAFE_AUTO |
| `pos-dispatch` | `suggest` | `packet-assemble` | SAFE_AUTO* |
| `pos-*` / `plan-*` | `suggest` | `packet-assemble` | SAFE_AUTO* |
| file writes / shell | — | `file-write` / `shell-script` | BEHAVIORAL |
| deploy / migrate / delete | — | `deploy` / `database-migrate` | CONFIRM |

\* SAFE_AUTO task_class does **not** imply auto-dispatch for `suggest` actions — founder confirm required at spine bridge.

### Hub alignment

- API: `GET/POST /api/dispatch-policy-v1` — hub `dispatch_ready` = `orchestrator_dispatch_ready()`; task simulation under `decision`
- SSOT: `~/.sina/dispatch_policy_v1.json` — `alignment.mapping_ok` from cross-check
- Validator: `validate-dispatch-policy-alignment-v1.sh`

---

## Phase 2b — Founder spine Action (eligible, not auto)

After Eval-1b live pass (`eval_1b_gate_ok: true`):

| Bridge | Ready when | Founder action |
|--------|------------|----------------|
| `eval_proof_bridge` | `spine-smoke-echo` class = `auto_low_risk` | **Enqueue eval spine bridge** |
| `planner_bridge` | C7 `spine_sequence` first action mapped via `branches_registry` | Same Action — `pos-dispatch` stays `suggest` until council amends |

Rules:

- `auto_low_risk` may **enqueue** via founder Action — not silent auto
- `suggest` class (`pos-*`) maps to branch spec but requires explicit confirm
- `dispatch_ready` in orchestrator **true** when activation gates pass — `validate-runtime-orchestrator-v1.sh` enforces honesty

Event bus publishes `spine.bridge` topic on successful enqueue.

---

## Forbidden

- Auto-dispatch high-risk writes without Eval-1b live pass
- `dispatch_ready=true` while `gate_mode` is shadow or eval live failed
- `dispatch_ready=true` while `critical_count > 0`
- Lane agents editing SourceA policy modules
