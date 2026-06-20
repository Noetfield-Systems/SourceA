# sa-mkt-0419 — Promptfoo · Pricing & packaging

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-pricing
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

## Task (Low — research, defer note, or compare-only)

Write competitor row evidence: Promptfoo pricing → our SKU → defer/shipped with path

## Implementation extraction

`Promptfoo · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0419`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Promptfoo` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
