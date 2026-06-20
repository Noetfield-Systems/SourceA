# wb-mkt-0148 — Sprinto · Integrations & API

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-integrate
**Stack:** WitnessBC · **Competitor row:** 23 · **Phase:** phase-c03-sprinto
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Sprinto |
| Product | Continuous compliance |
| What they sell | Automate SOC 2, ISO, GDPR evidence collection and monitoring |
| Who buys | SaaS startups |
| Pricing | From ~$6,000/yr (market); custom enterprise |
| How it runs | Connect infra; continuous control monitoring; audit export |
| Source links | https://sprinto.com |
| Portfolio lesson | Policy pack → control checklist → export bundle |

## Task (Low — research, defer note, or compare-only)

Validate adapter with one fixture test or validator script

## Implementation extraction

`Sprinto · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0148`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Sprinto` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
