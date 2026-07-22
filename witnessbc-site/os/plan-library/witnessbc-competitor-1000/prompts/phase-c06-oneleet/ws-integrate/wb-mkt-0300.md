# wb-mkt-0300 — Oneleet · Integrations & API

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-integrate
**Stack:** WitnessBC · **Competitor row:** 26 · **Phase:** phase-c06-oneleet
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Oneleet |
| Product | Security + compliance |
| What they sell | Security monitoring and compliance for startups |
| Who buys | Startups |
| Pricing | Custom pricing |
| How it runs | Security controls + compliance evidence in one platform |
| Source links | https://oneleet.com |
| Portfolio lesson | Proof call + deposit SOW before signature |

## Task (Low — research, defer note, or compare-only)

Close wb-mkt-0300: integration receipt + verify PASS + https://oneleet.com

## Implementation extraction

`Oneleet · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0300`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Oneleet` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
