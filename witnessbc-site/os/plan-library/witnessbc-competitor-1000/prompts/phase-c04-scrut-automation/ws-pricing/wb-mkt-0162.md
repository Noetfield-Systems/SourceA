# wb-mkt-0162 — Scrut Automation · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 24 · **Phase:** phase-c04-scrut-automation
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Scrut Automation |
| Product | GRC automation |
| What they sell | Compliance automation for SOC 2, ISO, and risk management |
| Who buys | Mid-market compliance leads |
| Pricing | Custom mid-market pricing |
| How it runs | Control monitoring; evidence vault; audit readiness |
| Source links | https://scrut.io |
| Portfolio lesson | Shadow-mode parallel install narrative for Witness AI Flow |

## Task (Critical — smallest shippable slice with receipt)

Map Scrut Automation revenue model (Annual enterprise SaaS) to our `Free toolkits → Pro packs → Flow install → Ops retainer` tier names — no hidden fees theater

## Implementation extraction

`Scrut Automation · Pricing & packaging` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0162`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Scrut Automation` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
