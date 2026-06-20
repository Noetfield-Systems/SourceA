# wb-mkt-0105 — Sprinto · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Diff our public copy vs Sprinto pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Sprinto · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0105`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Sprinto` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
