# wb-mkt-0014 — LowerPlane · Pricing & packaging

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 21 · **Phase:** phase-c01-lowerplane
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | LowerPlane |
| Product | Compliance automation |
| What they sell | AI-powered SOC 2, ISO 27001, HIPAA compliance with public pricing |
| Who buys | Startups needing first SOC 2 |
| Pricing | From $4,995/yr SOC2; bundles up to $15,995 — https://lowerplane.com/pricing |
| How it runs | Integrations collect evidence; advisor helps pass audit |
| Source links | https://lowerplane.com · https://lowerplane.com/pricing |
| Portfolio lesson | Public pricing ladder like WitnessBC toolkits → install tiers |

## Task (High — next sprint parity with competitor)

Label free vs paid honestly (AI policy + first agentic install — site independence law); never claim production without receipt

## Implementation extraction

`LowerPlane · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0014`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `LowerPlane` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
