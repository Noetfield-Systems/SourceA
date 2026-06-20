# sa-mkt-0669 — Pipedream · Pricing & packaging

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-pricing
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

## Task (Low — research, defer note, or compare-only)

Write competitor row evidence: Pipedream pricing → our SKU → defer/shipped with path

## Implementation extraction

`Pipedream · Pricing & packaging` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0669`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Pipedream` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
