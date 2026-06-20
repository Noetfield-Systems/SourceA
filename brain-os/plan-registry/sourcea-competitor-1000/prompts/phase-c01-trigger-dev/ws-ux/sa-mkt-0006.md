# sa-mkt-0006 — Trigger.dev · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** SourceA · **Competitor row:** 1 · **Phase:** phase-c01-trigger-dev
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

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

Add `Worker job run detail page (pass/fail/steps/logs/retry)` mock row labeled mock_only until live — match Trigger.dev run/history metaphor not invented name

## Implementation extraction

`Trigger.dev · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0006`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Trigger.dev` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
