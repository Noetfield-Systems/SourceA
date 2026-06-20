# wb-mkt-0452 — Gumloop · Buyer-visible UX

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-ux
**Stack:** WitnessBC · **Competitor row:** 30 · **Phase:** phase-c10-gumloop
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Gumloop |
| Product | No-code AI automation |
| What they sell | Build AI workflows with guardrails, MCP hosting, team analytics |
| Who buys | Business and ops teams |
| Pricing | Free 5k credits/mo; Pro $37/mo — https://www.gumloop.com/pricing |
| How it runs | Visual canvas; agent interactions; policy guardrails |
| Source links | https://www.gumloop.com/pricing |
| Portfolio lesson | App policies + guardrails UI on agent dispatch |

## Task (Critical — smallest shippable slice with receipt)

Write one-line UX spec: `Gumloop Buyer-visible UX` → buyer sees X → we show on `witnessbc.com pricing + toolkits hub` (lesson: App policies + guardrails UI on agent dispatch)

## Implementation extraction

`Gumloop · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0452`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Gumloop` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
