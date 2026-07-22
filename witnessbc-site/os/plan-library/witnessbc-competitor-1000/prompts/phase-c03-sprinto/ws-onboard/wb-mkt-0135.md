# wb-mkt-0135 — Sprinto · Onboarding & PLG

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-onboard
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

Pair onboarding step with `Witness AI Flow install replay demo + 6 receipt types` receipt so buyer sees proof immediately

## Implementation extraction

`Sprinto · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0135`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Sprinto` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
