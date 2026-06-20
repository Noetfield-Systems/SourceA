# Brain rule collision matrix (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-BRAIN-COLLISION  
**Authority:** ASF · **system bug** behind INCIDENT-026 marathon  
**Resolver:** `scripts/brain_intent_gate_v1.py` · `scripts/brain_session_guard_v1.py`

---

## 0. One sentence

> Brain got stuck because **conflicting machine rules** all fired at once with **no intent router** for “check e2e” — not because Brain lacks narrative.

---

## 1. The collision (why 31 minutes)

| Rule source | What it told Brain |
|-------------|-------------------|
| ASF order | “check everything e2e” → sounds like **full audit** |
| `agent-loop.mdc` | **Executor** runs shell · builds · proves |
| `agent-smart-judgment.mdc` | **Self-heal** · remediate drift · verify |
| `AGENT_MISS_DISK_FIRST` | Fix disk before reply → **brain_sync · heal · rebuild** |
| INCIDENT-014 | `dual_proof` lag → **repair loop** |
| `brain_session_guard` (old) | **Allowed** `validate-e2e-fast-ladder-v1.sh` |
| `BRAIN_UNIFIED` §4 | “Normal Brain” — **no e2e branch** |
| `brain_intent_gate` (old) | “check e2e” → **OTHER** (no allowed/forbidden list) |

**Result:** Brain became a **healer-executor hybrid** — ran 90–150s ladders repeatedly while also required to reply <30s and route only.

---

## 2. Resolution order (machine — not narrative)

```text
1. brain_intent_gate_v1.py  → classify founder message
2. brain_session_guard_v1.py → allowed/forbidden shells + idle
3. factory_idle_gate_v1.py   → block ladder if mid-slice
4. BRAIN_UNIFIED §0.5        → AUDIT_CHEAP_E2E branch
5. Worker chat               → idle ladder (--require-idle) only
```

---

## 3. Intent → behavior

| Intent | Brain may run | Brain must NOT | Delegate to |
|--------|---------------|----------------|-------------|
| `AUDIT_CHEAP_E2E` | preflight · fcb FAST · guard | fast/standard/full ladder | Worker if ladder needed |
| `RUN_TRACE` | brain_run_loop_trace | E2E validators | Worker for sa |
| `NARRATE_ONLY` | brain_narrate_loop | spawn | — |
| `OTHER` | session-start · guard | E2E ladder | Worker for build |

---

## 4. Related incidents

| ID | Class |
|----|-------|
| INCIDENT-026 (2026-06-10) | Validator recursion in Brain |
| INCIDENT-026 (2026-06-11) | E2E retry storm · 6× ladder |
| INCIDENT-016 | Plan todo ghost → false “done” |
| INCIDENT-014 | dual_proof / queue drift repair loop |
| INCIDENT-003 | Brain/Worker lane cross |

---

## 5. Proof

```bash
python3 scripts/brain_intent_gate_v1.py --message "check everything e2e" --json
bash scripts/validate-brain-intent-e2e-v1.sh
bash scripts/validate-brain-e2e-discipline-v1.sh
```

---

*End BRAIN_RULE_COLLISION_MATRIX*
