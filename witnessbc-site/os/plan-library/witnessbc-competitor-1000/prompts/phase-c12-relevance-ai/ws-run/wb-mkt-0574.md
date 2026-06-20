# wb-mkt-0574 — Relevance AI · Run history & proof

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-run
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

## Task (High — next sprint parity with competitor)

Wire orchestrator/factory receipt emit on run complete — no chat-only done

## Implementation extraction

`Relevance AI · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0574`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Relevance AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
