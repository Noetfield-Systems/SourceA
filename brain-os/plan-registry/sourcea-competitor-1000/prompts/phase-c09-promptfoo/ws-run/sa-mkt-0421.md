# sa-mkt-0421 — Promptfoo · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
**Stack:** SourceA · **Competitor row:** 9 · **Phase:** phase-c09-promptfoo
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Promptfoo |
| Product | LLM eval & red-team CLI |
| What they sell | Test prompts, agents, RAG — red teaming for jailbreaks and PII leaks |
| Who buys | Developers and security teams |
| Pricing | Community free 10k probes/mo; enterprise contact sales |
| How it runs | CLI/CI runs matrix evals locally or in cloud |
| Source links | https://www.promptfoo.dev |
| Portfolio lesson | Pre-ship eval gate on worker output |

## Task (Critical — smallest shippable slice with receipt)

From https://www.promptfoo.dev document Promptfoo run/history UX: CLI/CI runs matrix evals locally or in cloud — map to `Worker job run detail page (pass/fail/steps/logs/retry)`

## Implementation extraction

`Promptfoo · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0421`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Promptfoo` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
