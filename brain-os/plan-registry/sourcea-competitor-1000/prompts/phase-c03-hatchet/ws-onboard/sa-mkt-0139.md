# sa-mkt-0139 — Hatchet · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
**Stack:** SourceA · ** row:** 3 · **Phase:** phase-c03-hatchet
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Hatchet |
| Product | Task orchestration for AI pipelines |
| What they sell | Low-latency orchestration for agentic AI workflows with automatic retries |
| Who buys | AI pipeline and data engineering teams |
| Pricing | Free tier; Starter ~$180/mo; Production ~$425/mo (market reviews) |
| How it runs | Postgres-backed task DAG; workers execute with priority lanes |
| Source links | https://hatchet.run |
| Portfolio lesson | Priority lanes + durable steps for agent orchestration |

## Task (Low — research, defer note, or compare-only)

Docs: onboarding section cites Hatchet as market analog with https://hatchet.run

## Implementation extraction

`Hatchet · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0139`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Hatchet` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
