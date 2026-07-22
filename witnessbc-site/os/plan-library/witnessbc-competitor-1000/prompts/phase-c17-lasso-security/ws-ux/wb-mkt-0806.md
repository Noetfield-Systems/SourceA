# wb-mkt-0806 — Lasso Security · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** WitnessBC · **Competitor row:** 37 · **Phase:** phase-c17-lasso-security
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Lasso Security |
| Product | GenAI security platform |
| What they sell | Discover shadow AI; protect GenAI apps |
| Who buys | CISO teams |
| Pricing | Startup and enterprise tiers |
| How it runs | Scan for shadow AI; enforce policies |
| Source links | https://www.lasso.security |
| Portfolio lesson | Shadow AI discovery in policy starter kits |

## Task (Medium — hardening, validator, docs)

Add `Witness AI Flow install replay demo + 6 receipt types` mock row labeled mock_only until live — match Lasso Security run/history metaphor not invented name

## Implementation extraction

`Lasso Security · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0806`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Lasso Security` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
