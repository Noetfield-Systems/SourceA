# sa-0963 — Eval live pilot expansion beyond 5 tasks — tasks.json design spike

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research spike only · **No OpenRouter · No tasks.json edit · No D-modules**

## One-line verdict

> **10 tasks exist; 5 are live pilots today.** Expansion beyond 5 = promote scaffold tasks or add new rows with `live_pilot: true` — validator already allows `>= 5`. This spike defines **tiering + promotion rules** — implement only after ASF order + live CI budget.

---

## Current tasks.json (disk truth)

**Path:** `scripts/eval_packet_v1b/tasks.json` · schema `eval-packet-tasks-v1b` v2

| Tier | Count | Task IDs | `live_pilot` |
|------|-------|----------|--------------|
| **Live core** | 5 | bugfix-gate · plan-eval-1b · retrieve-dispatch · governance-rules · factory-runreceipt | `true` |
| **Scaffold / probe** | 5 | gov-probe-portfolio-ssot · gov-probe-fake-green · gov-probe-receipt-tamper · event-bus · l8-hybrid | `false` |

**Report SSOT:** `~/.sina/eval_packet_v1b_report.json` — last run scaffold mode · 10/10 scaffold wins · `live_pilot_count: 0` until live validator runs.

---

## Live gate (shipped — sa-0101 spine)

`validate-eval-packet-v1b-live.sh`:

| Assert | Value |
|--------|-------|
| `live_pilot_count` | **>= 5** (not capped at 5) |
| `live_pilot_win_pct` | **>= 80%** |
| Retries | 3 attempts |
| Fallback | structural-only on OpenRouter HTTP 402 |

**Implication:** Promoting task #6–#10 to `live_pilot: true` **does not require validator amend** — only raises OpenRouter cost (2 arms × N pilots per strict build).

---

## Proposed tasks.json schema extensions (design only)

| Field | Purpose | Example |
|-------|---------|---------|
| `live_pilot` | Run in live A/B arm | existing |
| `pilot_tier` | `core` \| `extended` \| `probe` | core = always live; extended = promoted; probe = weekly |
| `probe_week` | Rotate governance probes | existing on gov-probe-* |
| `forbidden_paths` | Anti-hallucination guard | existing on gov-probe-portfolio-ssot |
| `cost_weight` | Budget planner (1–3) | l8-hybrid = 3 (long context) |
| `promotion_criteria` | Scaffold win streak before live flip | e.g. 3× scaffold packet_wins |

**Do not add** until maintainer ships schema v3 + `validate-eval-packet-tasks-v1.sh`.

---

## Expansion options (6+ pilots)

| # | Option | Pilots | Cost | Risk |
|---|--------|--------|------|------|
| **E1** | Promote **factory-runreceipt** neighbors only — keep 5 core | 5 | Baseline | Low — current law |
| **E2** | Promote **gov-probe-*** trio (week-8 probes) | 8 | +3× live calls | Med — probe prompts are adversarial |
| **E3** | Promote **event-bus** + **l8-hybrid** | 7–10 | High | High — retrieval tasks need stable paths |
| **E4** | **Rotating probe pool** — max 5 live at once, `probe_week` selects 2 + 3 core | 5 live / 10 catalog | Bounded | Low — best cost/coverage trade |
| **E5** | Add **new** portfolio lane tasks (trustfield, mono) | 10+ | High | Needs new `expected_paths` per repo |

**Recommended (research):** **E4 rotating pool** — keeps 5-live gate semantics, expands catalog honesty without 10× OpenRouter per build.

---

## Promotion workflow (when ASF orders implement)

```text
1. Scaffold PASS on candidate (packet_wins in report row)
2. Maintainer sets live_pilot: true OR pilot_tier: extended
3. Run validate-eval-packet-v1b-live.sh (not in RUN INBOX — feasibility blocks)
4. eval_report_capture → synthesis + dispatch policy eval_1b_gate_ok
5. PRIORITY evidence row with pilot count
```

**RUN INBOX law:** `prompt_feasibility_gate` blocks OpenRouter in inbox ACT — expansion **design doc only** in this sa.

---

## Relation to sa-0953 (RAGAS vs Eval-1b)

sa-0953: Eval-1b is the **enforced behavioral gate** — pilot expansion widens **factory task coverage**, not RAGAS metrics. Any RAGAS layer stays parallel/deferred.

---

## Duplicate sa titles

Same task at **sa-0913**, **sa-0938**, **sa-0988**, **sa-0963**. This doc is canonical for sa-0963 VERIFY closeout.

---

## Verdict

**Expansion beyond 5 is a catalog + tiering problem, not a validator blocker.** Ship **E4 rotating probe pool** design first; defer `tasks.json` v3 edits until ASF orders live CI budget increase.

**One-line:** 10 tasks on disk, 5 live — expand via tier/rotation design, not inbox live run.
