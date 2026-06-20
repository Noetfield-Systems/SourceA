# wb-mkt-0445 — Drata · Integrations & API

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-integrate
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

## Task (Medium — hardening, validator, docs)

Log every external call on run timeline (`Witness AI Flow install replay demo + 6 receipt types`)

## Implementation extraction

`Drata · Integrations & API` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0445`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Drata` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
