# sa-mkt-0749 — Activepieces · Integrations & API

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-integrate
**Stack:** SourceA · **Competitor row:** 15 · **Phase:** phase-c15-activepieces
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Activepieces |
| Product | Open-source automation |
| What they sell | Self-hostable Zapier alternative with flow builder |
| Who buys | SMB and developers |
| Pricing | OSS free; cloud paid tiers |
| How it runs | Build flows; trigger on events; view run history |
| Source links | https://www.activepieces.com |
| Portfolio lesson | Self-hostable workflow runs for portfolio factories |

## Task (Low — research, defer note, or compare-only)

Update catalog/registry row for integration — Activepieces row 15

## Implementation extraction

`Activepieces · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0749`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Activepieces` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
