# sa-0956 — pos-dispatch policy promotion criteria (founder council vote)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules · No dispatch_ready flip**

## Factory today (disk truth)

| Field | SourceA state |
|-------|----------------|
| **pos-dispatch** | L1 class **`suggest`** · L2 `packet-assemble` · SAFE_AUTO* (`DISPATCH_POLICY_LOCKED_v1`) |
| **Auto-dispatch** | **false** — founder confirm required at spine bridge |
| **Orchestrator** | `dispatch_ready: false` — founder law until Phase 3 council brief |
| **Eval gate** | `eval_1b_gate_ok` from live report — enables low-risk **eligibility**, not silent auto |
| **Planner gate** | `gate_mode: shadow` default — ENFORCE is separate founder decision |

## What “promotion” means (internal)

Promotion is **not** flipping `orchestrator.dispatch_ready` in code without council. It is amending **policy class** for `pos-dispatch` (and related `pos-*` / `plan-*`) from **`suggest` → eligible auto_low_risk enqueue** with founder confirm retained until Phase 3 brief explicitly says otherwise.

| Stage | Class | Founder confirm | Machine proof |
|-------|-------|-----------------|---------------|
| **Now** | `suggest` | Required every enqueue | `validate-graph-executor-pos-dispatch-v1` · alignment OK |
| **Eligible** | `auto_low_risk` enqueue | One-tap Action, not silent | `eval_1b_gate_ok: true` + spine bridge green |
| **Phase 3** | Council brief may define `dispatch_ready` | ASF + council vote | New LOCKED doc supersedes v1 §Forbidden |

## Promotion criteria matrix (council vote inputs)

| # | Criterion | PASS signal | FAIL / defer |
|---|-----------|-------------|--------------|
| 1 | **Eval-1b live** | `eval_1b_gate_ok: true` · ≥80% on ≥5 pilots | Scaffold-only CI — no promotion vote |
| 2 | **Alignment** | `alignment.mapping_ok: true` on `/api/dispatch-policy-v1` | Classifier/registry drift |
| 3 | **pos-dispatch guard** | sa-0109 class validators PASS — suggest not global auto | Any auto-dispatch without confirm |
| 4 | **ENFORCE shadow soak** | `gate_shadow_v1.jsonl` reviewed · bypass map published | Flip ENFORCE before shadow review |
| 5 | **Bypass map** | `ENFORCE_BYPASS_MAP_LOCKED_v1.md` — Cursor IDE / maintainer paths documented | Unknown bypass lanes |
| 6 | **Founder council vote** | ASF explicit yes + council brief row filed | ChatGPT paste alone (EXTERNAL_CRITIC) |
| 7 | **Law amend** | New `DISPATCH_POLICY_LOCKED_vN` or council brief clause — not chat | Code-only class flip |

## Council vote procedure (research — not automated)

1. **Advisor / council room** presents this criteria table + disk snapshot (`dispatch-policy-v1`, eval report, gate receipts).
2. **Founder** votes in hub (one tap) — no Terminal.
3. **If PASS:** maintainer ships law amend (`pos-dispatch` promotion clause) — Worker broker receipt chain.
4. **If DEFER:** `pos-dispatch` stays **`suggest`** — no regression; queue continues research rail.

## Verdict

**pos-dispatch promotion requires founder council vote against criteria 1–7.** Factory law already blocks silent promotion; this note is the **vote checklist** for Phase 3 / policy amend — not an implementation ticket.

**One-line:** `suggest` is correct today; promotion = **law + council**, not code flip alone.
