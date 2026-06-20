# wb-mkt-0562 — Relevance AI · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 32 · **Phase:** phase-c12-relevance-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Relevance AI |
| Product | AI workforce platform |
| What they sell | Build and deploy AI agents for GTM and operations |
| Who buys | GTM and ops teams |
| Pricing | Pro $19/mo; Team $234/mo — https://relevanceai.com/docs/get-started/pricing |
| How it runs | Agent builder; actions + vendor credits; workforce dashboard |
| Source links | https://relevanceai.com/docs/get-started/pricing |
| Portfolio lesson | Packaged agent install SKUs like Witness AI Flow |

## Task (Critical — smallest shippable slice with receipt)

Map Relevance AI revenue model (Actions + credits SaaS) to our `Free toolkits → Pro packs → Flow install → Ops retainer` tier names — no hidden fees theater

## Implementation extraction

`Relevance AI · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0562`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Relevance AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
