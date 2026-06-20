# wb-mkt-0206 — Comp AI · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Add `Witness AI Flow install replay demo + 6 receipt types` mock row labeled mock_only until live — match Comp AI run/history metaphor not invented name

## Implementation extraction

`Comp AI · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0206`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Comp AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
