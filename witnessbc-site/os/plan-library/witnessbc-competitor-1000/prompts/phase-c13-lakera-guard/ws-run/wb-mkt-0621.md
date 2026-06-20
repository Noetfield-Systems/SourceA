# wb-mkt-0621 — Lakera Guard · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
**Stack:** WitnessBC · **Competitor row:** 33 · **Phase:** phase-c13-lakera-guard
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Lakera Guard |
| Product | GenAI security |
| What they sell | Runtime guardrails for LLM apps — block injections and policy violations |
| Who buys | AppSec and platform teams |
| Pricing | Enterprise custom |
| How it runs | API middleware scans prompts/responses; logs decisions |
| Source links | https://www.lakera.ai |
| Portfolio lesson | Policy at dispatch allow/block log |

## Task (Critical — smallest shippable slice with receipt)

From https://www.lakera.ai document Lakera Guard run/history UX: API middleware scans prompts/responses; logs decisions — map to `Witness AI Flow install replay demo + 6 receipt types`

## Implementation extraction

`Lakera Guard · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0621`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Lakera Guard` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
