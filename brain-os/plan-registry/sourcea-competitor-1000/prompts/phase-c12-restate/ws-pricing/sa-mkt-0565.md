# sa-mkt-0565 — Restate · Pricing & packaging

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-pricing
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

## Task (Medium — hardening, validator, docs)

Compare Restate PLG motion (Infrastructure OSS → cloud) vs our onboarding — one adoption fix on `Hub Actions + RUN INBOX first-run path`

## Implementation extraction

`Restate · Pricing & packaging` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0565`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Restate` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
