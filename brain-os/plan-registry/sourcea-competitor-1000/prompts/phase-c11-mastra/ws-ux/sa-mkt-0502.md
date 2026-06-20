# sa-mkt-0502 — Mastra · Buyer-visible UX

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-ux
**Stack:** SourceA · **Competitor row:** 11 · **Phase:** phase-c11-mastra
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Mastra |
| Product | TypeScript agent framework |
| What they sell | Agent framework with built-in observability and workflow primitives |
| Who buys | TypeScript agent developers |
| Pricing | OSS free; cloud tiers (market) |
| How it runs | Define agents in TS; deploy with tracing hooks |
| Source links | https://mastra.ai |
| Portfolio lesson | Standard agent harness hooks in SourceA motor |

## Task (Critical — smallest shippable slice with receipt)

Write one-line UX spec: `Mastra Buyer-visible UX` → buyer sees X → we show on `Worker Hub Next steps + factory-now line` (lesson: Standard agent harness hooks in SourceA motor)

## Implementation extraction

`Mastra · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0502`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Mastra` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
