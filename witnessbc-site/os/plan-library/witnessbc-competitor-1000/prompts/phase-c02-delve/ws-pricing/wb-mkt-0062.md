# wb-mkt-0062 — Delve · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 22 · **Phase:** phase-c02-delve
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Delve |
| Product | AI compliance automation |
| What they sell | AI agents auto-collect evidence for SOC 2, HIPAA, GDPR, ISO |
| Who buys | AI startups needing fast SOC 2 |
| Pricing | ~$18,000–30,000+/yr (market); contact sales — note Mar 2026 audit controversy |
| How it runs | AI agents integrate tools; collect screenshots and logs |
| Source links | https://delve.co |
| Portfolio lesson | Fast install motion — always verify independent auditor (lesson from 2026 controversy) |

## Task (Critical — smallest shippable slice with receipt)

Map Delve revenue model (High-touch annual SaaS) to our `Free toolkits → Pro packs → Flow install → Ops retainer` tier names — no hidden fees theater

## Implementation extraction

`Delve · Pricing & packaging` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0062`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Delve` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
