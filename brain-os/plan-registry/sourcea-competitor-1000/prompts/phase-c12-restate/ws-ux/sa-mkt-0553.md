# sa-mkt-0553 — Restate · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
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

## Task (High — next sprint parity with competitor)

Add `Worker Hub Next steps + factory-now line` UI field or copy block implementing smallest slice of `Long-running worker without orchestrator ghost state`; preserve honest tier label

## Implementation extraction

`Restate · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0553`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Restate` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
