# sa-mkt-0589 — Restate · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
**Stack:** SourceA · ** row:** 12 · **Phase:** phase-c12-restate
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

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

## Task (Low — research, defer note, or compare-only)

Docs: onboarding section cites Restate as market analog with https://restate.dev

## Implementation extraction

`Restate · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0589`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Restate` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
