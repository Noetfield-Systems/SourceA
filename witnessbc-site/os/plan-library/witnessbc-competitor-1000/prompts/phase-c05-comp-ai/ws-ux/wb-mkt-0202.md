# wb-mkt-0202 — Comp AI · Buyer-visible UX

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-ux
**Stack:** WitnessBC · **Competitor row:** 25 · **Phase:** phase-c05-comp-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Comp AI |
| Product | SOC 2 in a box |
| What they sell | Get SOC 2 compliant quickly with AI-assisted automation |
| Who buys | Early-stage SaaS |
| Pricing | Startup tiers (market) |
| How it runs | Guided setup; automated evidence; auditor handoff |
| Source links | https://comp.ai |
| Portfolio lesson | ≤30-day install promise on Witness AI Flow SOW |

## Task (Critical — smallest shippable slice with receipt)

Write one-line UX spec: `Comp AI Buyer-visible UX` → buyer sees X → we show on `witnessbc.com pricing + toolkits hub` (lesson: ≤30-day install promise on Witness AI Flow SOW)

## Implementation extraction

`Comp AI · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0202`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Comp AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
