# wb-mkt-0021 — LowerPlane · Run history & proof

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-run
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

## Task (Critical — smallest shippable slice with receipt)

From https://lowerplane.com · https://lowerplane.com/pricing document LowerPlane run/history UX: Integrations collect evidence; advisor helps pass audit — map to `Witness AI Flow install replay demo + 6 receipt types`

## Implementation extraction

`LowerPlane · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0021`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `LowerPlane` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
