# wb-mkt-0471 — Gumloop · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
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

From https://www.gumloop.com/pricing document Gumloop run/history UX: Visual canvas; agent interactions; policy guardrails — map to `Witness AI Flow install replay demo + 6 receipt types`

## Implementation extraction

`Gumloop · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0471`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Gumloop` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
