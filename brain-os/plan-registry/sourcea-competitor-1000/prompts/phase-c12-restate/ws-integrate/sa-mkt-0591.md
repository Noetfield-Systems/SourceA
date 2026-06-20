# sa-mkt-0591 — Restate · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** SourceA · **Competitor row:** 12 · **Phase:** phase-c12-restate
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Restate |
| Product | Durable execution engine |
| What they sell | Durable async/await for long-running backend workflows |
| Who buys | Backend platform teams |
| Pricing | OSS free; cloud usage-based |
| How it runs | Developer writes durable functions; engine persists state |
| Source links | https://restate.dev |
| Portfolio lesson | Long-running worker without orchestrator ghost state |

## Task (Critical — smallest shippable slice with receipt)

List Restate integrations/APIs from https://restate.dev or docs — pick one we can wire this quarter

## Implementation extraction

`Restate · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0591`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Restate` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
