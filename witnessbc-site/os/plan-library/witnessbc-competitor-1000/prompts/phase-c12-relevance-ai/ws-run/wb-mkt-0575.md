# wb-mkt-0575 — Relevance AI · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
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

## Task (Medium — hardening, validator, docs)

Add retention note: how long run history kept vs Relevance AI (Pro $19/mo; Team $234/mo — https://relevanceai.com/docs/get-started/pricing tier hints)

## Implementation extraction

`Relevance AI · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0575`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Relevance AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
