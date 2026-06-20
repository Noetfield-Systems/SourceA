# sa-mkt-0123 — Hatchet · Run history & proof

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-run
**Stack:** SourceA · **Competitor row:** 3 · **Phase:** phase-c03-hatchet
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

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

## Task (High — next sprint parity with competitor)

Implement smallest `Worker job run detail page (pass/fail/steps/logs/retry)` slice — PASS/FAIL + one step log; mock_only ok with label

## Implementation extraction

`Hatchet · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0123`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Hatchet` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
