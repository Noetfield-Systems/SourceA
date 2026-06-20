# wb-mkt-0742 — Arthur AI · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** WitnessBC · **Competitor row:** 35 · **Phase:** phase-c15-arthur-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Arthur AI |
| Product | Model monitoring |
| What they sell | Monitor ML and LLM performance, drift, and quality |
| Who buys | ML platform owners |
| Pricing | Enterprise custom |
| How it runs | Ingest predictions; detect drift; alert |
| Source links | https://www.arthur.ai |
| Portfolio lesson | Drift/quality alerts on Witness AI Ops |

## Task (Critical — smallest shippable slice with receipt)

Spec `Policy packs mapped to agent receipt gates` contract: input → policy gate → output + receipt

## Implementation extraction

`Arthur AI · Integrations & API` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0742`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Arthur AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
