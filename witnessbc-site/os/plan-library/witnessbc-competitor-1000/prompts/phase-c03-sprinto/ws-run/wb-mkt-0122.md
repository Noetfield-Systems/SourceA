# wb-mkt-0122 — Sprinto · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
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

## Task (Critical — smallest shippable slice with receipt)

Spec run detail fields: status · steps · failure class · retry · timestamp (from lesson: Policy pack → control checklist → export bundle)

## Implementation extraction

`Sprinto · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0122`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Sprinto` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
