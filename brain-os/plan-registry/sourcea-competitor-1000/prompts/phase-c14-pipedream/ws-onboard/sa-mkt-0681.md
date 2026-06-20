# sa-mkt-0681 — Pipedream · Onboarding & PLG

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-onboard
**Stack:** SourceA · **Competitor row:** 14 · **Phase:** phase-c14-pipedream
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Pipedream |
| Product | Integration workflows |
| What they sell | Connect APIs and run code workflows with event triggers |
| Who buys | Developers and ops |
| Pricing | Free tier + usage paid plans |
| How it runs | Visual + code workflows; each run logged |
| Source links | https://pipedream.com |
| Portfolio lesson | Connector-based automation run log pattern |

## Task (Critical — smallest shippable slice with receipt)

Document Pipedream onboarding path (Developer integrations marketplace): who runs (Managed cloud) → first value moment

## Implementation extraction

`Pipedream · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0681`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Pipedream` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
