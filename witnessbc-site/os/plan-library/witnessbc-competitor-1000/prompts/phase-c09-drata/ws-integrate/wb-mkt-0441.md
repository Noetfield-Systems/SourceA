# wb-mkt-0441 — Drata · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** WitnessBC · **Competitor row:** 29 · **Phase:** phase-c09-drata
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Drata |
| Product | Compliance automation |
| What they sell | Continuous compliance monitoring and audit readiness |
| Who buys | SaaS companies |
| Pricing | Custom annual contracts |
| How it runs | Automated evidence; policy templates; auditor portal |
| Source links | https://drata.com |
| Portfolio lesson | Live control status page pattern |

## Task (Critical — smallest shippable slice with receipt)

List Drata integrations/APIs from https://drata.com or docs — pick one we can wire this quarter

## Implementation extraction

`Drata · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0441`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Drata` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
