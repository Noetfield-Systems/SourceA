# wb-mkt-0862 — Dust.tt · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 38 · **Phase:** phase-c18-dust-tt
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Dust.tt |
| Product | Enterprise AI assistants |
| What they sell | Build internal AI assistants connected to company data |
| Who buys | Enterprise ops teams |
| Pricing | Team tiers custom |
| How it runs | Template assistants; team workspaces; usage controls |
| Source links | https://dust.tt |
| Portfolio lesson | Packaged team templates for first install |

## Task (Critical — smallest shippable slice with receipt)

Map Dust.tt revenue model (Seat + usage SaaS) to our `Free toolkits → Pro packs → Flow install → Ops retainer` tier names — no hidden fees theater

## Implementation extraction

`Dust.tt · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0862`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Dust.tt` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
