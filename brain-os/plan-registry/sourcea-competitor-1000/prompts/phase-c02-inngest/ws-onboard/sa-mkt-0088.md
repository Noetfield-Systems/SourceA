# sa-mkt-0088 — Inngest · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
**Stack:** SourceA · ** row:** 2 · **Phase:** phase-c02-inngest
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Inngest |
| Product | Durable serverless functions |
| What they sell | Reliable workflows with invisible infra — step functions for serverless apps |
| Who buys | Serverless product teams on Vercel/Netlify |
| Pricing | Hobby $0 (50k executions); Pro $75/mo — https://www.inngest.com/pricing |
| How it runs | Event triggers functions; each step durable with trace retention |
| Source links | https://www.inngest.com · https://www.inngest.com/pricing |
| Portfolio lesson | Step timeline + trace retention tiers on every factory job |

## Task (Low — research, defer note, or compare-only)

Integrate `scripts/ queue + cloud dispatch APIs` hook needed for onboarding (API key, MCP, connector)

## Implementation extraction

`Inngest · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0088`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Inngest` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
