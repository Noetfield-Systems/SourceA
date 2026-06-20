# sa-mkt-0025 — Trigger.dev · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
**Stack:** SourceA · ** row:** 1 · **Phase:** phase-c01-trigger-dev
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Trigger.dev |
| Product | Durable background jobs & AI workflows |
| What they sell | Open-source AI agent and workflow platform — run long tasks with retries and a visual run dashboard |
| Who buys | Backend and platform engineers at SaaS startups |
| Pricing | Free $0 + Hobby $10/mo + Pro $50/mo; $0.25 per 10,000 run invocations + compute seconds — https://trigger.dev/pricing |
| How it runs | Developer writes tasks in TypeScript; platform executes, logs steps, retries failures |
| Source links | https://trigger.dev · https://trigger.dev/pricing |
| Portfolio lesson | Run detail page with pass/fail, steps, logs, retry — copy for Worker Hub job dashboard |

## Task (Medium — hardening, validator, docs)

Add retention note: how long run history kept vs Trigger.dev (Free $0 + Hobby $10/mo + Pro $50/mo; $0.25 per 10,000 run invocations + compute seconds — https://trigger.dev/pricing tier hints)

## Implementation extraction

`Trigger.dev · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0025`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Trigger.dev` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
