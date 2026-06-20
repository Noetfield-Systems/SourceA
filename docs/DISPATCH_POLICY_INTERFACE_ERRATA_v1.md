# Dispatch policy interface spec — errata (v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Compare-only source:** `~/Downloads/dispatch_policy_interface_1.md` (Claude interface spec)  
**Authority:** [`DISPATCH_POLICY_LOCKED_v1.md`](../DISPATCH_POLICY_LOCKED_v1.md) wins for wiring and founder law  
**Updated:** 2026-06-06  
**Status:** Phase 2a shipped · Phase 2b shadow · Phase 3 orchestrator auto deferred

---

## 1. What the Claude spec got right (~90%)

| Area | Spec | Code | Status |
|------|------|------|--------|
| `evaluate()` signature | 6 kwargs | `policy_engine.py` | ✅ |
| `TASK_CLASS_REGISTRY` | 17 classes, 3 tiers | `allowlist.py` | ✅ |
| Output schema | `dispatch-policy-v1` + 8 fields | `_block` / `_allow` | ✅ |
| Hard blocks | reject graph, block router, `behavioral_fail` | L194–221 | ✅ |
| SAFE_AUTO | approve + allow → dispatch | L233–241 | ✅ |
| BEHAVIORAL | needs `behavioral_pass` or `founder_override` | L255–278 | ✅ |
| CONFIRM | `requires_founder_confirm=True` | L280–287 | ✅ |
| Store | `~/.sina/dispatch_policy_v1.json` | `store.py` | ✅ |
| API | GET/POST `/api/dispatch-policy-v1` | `api.py` + hub :13020 | ✅ |
| V-dispatch-01–04 | Safe auto, behavioral block, graph reject, API | `validate-dispatch-policy-v1.sh` | ✅ |

**Use the Claude doc as Layer 2 interface reference** for `evaluate()` + allowlist + validators.

---

## 2. Critical divergences — do not implement spec “After” as written

### Orchestrator wiring (spec §Wiring → After)

**Spec says (unsafe / not law):**

```python
result["dispatch_ready"] = decision["dispatch_ready"]
event_bus.publish("dispatch.approved", ...)
graph_executor.run_primary_chain(...)
```

**Shipped (`orchestrator_engine.py`):**

- `dispatch_decision = evaluate(..., dry_run=True)`
- `dispatch_ready: False` always at orchestrator + hub top-level
- No silent `event_bus.publish("dispatch.approved")`
- No `graph_executor.run_primary_chain()` auto call

**Deferred to Phase 3:** Eval-1b `behavioral_pass` + `DISPATCH_POLICY_LOCKED_v2` + council brief.

### API response shape

| Spec | Shipped |
|------|---------|
| GET returns `dispatch_decision` JSON directly | Wrapper `dispatch-policy-api-v1` |
| Top-level `dispatch_ready` = evaluate result | Top-level `dispatch_ready` **always false** |
| — | Real simulation under `decision` key |

**Clients:** read `decision.dispatch_ready`, not top-level `dispatch_ready`.

---

## 3. Extra layers not in Claude doc (shipped)

| Module | Role |
|--------|------|
| `classifier.py` | Layer 1: `observe` / `suggest` / `auto_low_risk` |
| `evaluate_action()` | Spine bridge gate (Eval-1b live) |
| `infer_task_class()` | `action_id` → `task_class` |
| `eval_1b_gate_status()` | Live ≥80% gate |
| `founder_spine_bridge_gate_status()` | Structural CI bridge when OpenRouter 402 |
| `current_eval_tier()` | Report + `eval_1b_ci_mode_v1.json` |
| `spine_bridge.py` | Founder confirm enqueue path |
| `validate-dispatch-policy-alignment-v1.sh` | L1↔L2 mapping cross-check |

Claude doc = **Layer 2 only**. Locked law = **dual-layer**.

---

## 4. Smaller nuances

| Item | Behavior |
|------|----------|
| `recommendation: review` / `needs_fix` | Not hard block; SAFE_AUTO fails via `blocking_conditions` |
| `router == "wait"` | Not explicit hard block; treated as non-allow for SAFE_AUTO |
| `dry_run=True` | Reason → `dry_run_simulated`; `auto_dispatch_allowed=False` |
| BEHAVIORAL pass reason | `"behavioral_proof_required"` (matches spec pseudo-code) |
| Import path | `runtime.dispatch_policy` from `scripts/` cwd |
| SSOT schema | Merged payload uses `dispatch-policy-v1` + `ssot_schema` |
| `eval_1b_gate_ok` | Hub payload field, not inside `dispatch_decision` |

---

## 5. Current runtime state (honest)

| Field | Value |
|-------|-------|
| `eval_tier` | `structural` (scaffold + CI structural fallback) |
| `eval_1b_gate_ok` | `false` (live not passed; OpenRouter 402) |
| `evaluate(validate-only)` | `dispatch_ready: true` in **simulation** only |
| `evaluate(file-write)` | `dispatch_ready: false` ✅ |
| Hub / orchestrator `dispatch_ready` | always `false` ✅ |

---

## 6. Extended validator receipt (V-dispatch-05–08)

| id | name | proves |
|----|------|--------|
| V-dispatch-05 | `hub_dispatch_ready_always_false` | Hub + API wrapper top-level false |
| V-dispatch-06 | `orchestrator_shadow_dry_run` | `dispatch_decision.dry_run=true`, orchestrator false |
| V-dispatch-07 | `dual_layer_classifier_alignment` | `alignment.mapping_ok=true` |
| V-dispatch-08 | `eval_1b_gate_honest` | `gate_ok=false` in structural CI mode |

Run: `bash scripts/validate-dispatch-policy-v1.sh`

---

## 7. Who wins

| Document | Role |
|----------|------|
| `dispatch_policy_interface_1.md` | Interface + **aspirational** Phase 3 orchestrator |
| `DISPATCH_POLICY_LOCKED_v1.md` | **Law** — founder confirm, shadow mode, no orchestrator flip |
| This errata | Bridge between compare-only spec and disk truth |

**Next blocker:** Eval-1b live `behavioral_pass` (OpenRouter credits) before BEHAVIORAL tier opens + spine auto beyond founder Action.
