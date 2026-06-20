# sa-mkt-0610 — Windmill · Buyer-visible UX

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-ux
**Stack:** SourceA · **Competitor row:** 13 · **Phase:** phase-c13-windmill
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Windmill |
| Product | Developer workflow platform |
| What they sell | Scripts, flows, schedules with run history and permissions |
| Who buys | Ops and platform teams |
| Pricing | OSS free; cloud team tiers |
| How it runs | Write scripts/flows; schedule; audit run log |
| Source links | https://windmill.dev |
| Portfolio lesson | Internal ops job dashboard with run history |

## Task (Low — research, defer note, or compare-only)

Mark sa-mkt-0610 done in REGISTRY with evidence path + https://windmill.dev after verify PASS

## Implementation extraction

`Windmill · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0610`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Windmill` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
