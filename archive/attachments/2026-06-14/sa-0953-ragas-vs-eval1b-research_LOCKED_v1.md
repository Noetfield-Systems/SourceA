# sa-0953 — RAGAS eval CI vs Eval-1b live packet (internal note)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No OpenRouter spend · No new D-modules**

## Factory today (disk truth)

| Layer | SourceA Eval-1b | Industry RAGAS-style CI |
|-------|-------------------|-------------------------|
| Purpose | Prove **packet beats raw** on controlled tasks | Prove **RAG pipeline quality** on datasets |
| Live arm | OpenRouter A/B · 5 pilot tasks · **80% threshold** | LLM-as-judge metrics on fixed Q/A sets |
| Scaffold arm | Composite proxy (keywords + grounding + actionability) · **70%** | N/A — RAGAS is metric-native, not dual-arm |
| Report SSOT | `~/.sina/eval_packet_v1b_report.json` | External harness / CI artifact (not in factory) |
| Dispatch gate | `eval_1b_gate_ok` via `policy_engine.eval_1b_gate_status()` | Not wired — no `ragas_gate_ok` |
| CI fallback | `eval_1b_ci_mode_v1.json` · structural-only on HTTP 402 | Typical: skip live or mock judge |

## Compare matrix

| Dimension | **RAGAS-style CI** | **Eval-1b live packet** | Gap / alignment |
|-----------|-------------------|-------------------------|-----------------|
| **What it measures** | Faithfulness, answer relevancy, context precision/recall | Task outcome: packet context vs raw prompt win rate | RAGAS = retrieval QA quality · Eval-1b = **controlled context assembly** uplift |
| **Judge** | Reference + LLM judge on dataset rows | OpenRouter completion + factory composite on pilots | Eval-1b is **factory-specific** tasks (`tasks.json`), not generic RAG bench |
| **CI posture** | Batch dataset in pipeline; gate on metric thresholds | `validate-eval-packet-v1b-live.sh` in strict build; scaffold survives live pass | SourceA already has **two-arm CI** (scaffold + live) — RAGAS would be a **third metric layer** |
| **Cost model** | Dataset-sized judge calls | 5 pilots × 2 arms per strict build | Eval-1b is **bounded spend**; RAGAS at scale can exceed pilot budget |
| **Honest closeout** | External report file | Receipt chain + `eval_1b_gate_ok` + broker VERIFY | RAGAS has no `receipts/sa-XXXX` bind today |
| **Dispatch coupling** | Usually informational / product QA | **Blocks** low-risk dispatch when `eval_1b_gate_ok: false` | Only Eval-1b is **enforcement-linked** |

## Eval-1b CI stack (what RAGAS would have to match)

1. **Scaffold** — `validate-eval-packet-v1b.sh` · no LLM · proves packet wiring  
2. **Grounding** — `validate-eval-packet-v1b-grounding.sh`  
3. **Live** — `validate-eval-packet-v1b-live.sh` · OpenRouter A/B · ≥80% on ≥5 pilots  
4. **Structural fallback** — `eval_1b_ci_mode.py` when HTTP 402 · scaffold refresh only  
5. **Capture** — `validate-eval-report-capture-v1.sh` → `~/.sina`  
6. **Policy** — `validate-dispatch-policy-v1.sh` · `eval_1b_gate_ok`  

RAGAS metrics (faithfulness, relevancy) overlap **conceptually** with Eval-1b scaffold `grounding` + `actionability` — but are **not interchangeable**: Eval-1b wins are **A/B on factory prompts**, not RAGAS dataset rows.

## Verdict (internal)

| Question | Answer |
|----------|--------|
| Replace Eval-1b with RAGAS? | **No** — dispatch gate is bound to Eval-1b live packet proof |
| Add RAGAS as parallel CI? | **Deferred** — phase-s9 research only; needs ASF order + broker adapter |
| Nearest factory hook today? | WTM line: “future live LLM A/B with RAGAS-style CI” — Eval-1b **is** the live A/B layer; RAGAS would supplement **retrieval** slices (L8/D9), not replace behavioral gate |

**ACT shipped:** this internal compare note only — no D-module, no RAGAS dependency, no OpenRouter.

**One-line:** Eval-1b is the **enforced behavioral gate**; RAGAS is a **reference metric family** for future retrieval QA CI — complementary research debt, not a substitute.
