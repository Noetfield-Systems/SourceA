# wb-mkt-0439 — Drata · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
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

## Task (Low — research, defer note, or compare-only)

Docs: onboarding section cites Drata as market analog with https://drata.com

## Implementation extraction

`Drata · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0439`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Drata` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
