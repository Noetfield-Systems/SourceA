# sa-mkt-0535 — Mastra · Onboarding & PLG

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-onboard
**Stack:** SourceA · ** row:** 11 · **Phase:** phase-c11-mastra
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Mastra |
| Product | TypeScript agent framework |
| What they sell | Agent framework with built-in observability and workflow primitives |
| Who buys | TypeScript agent developers |
| Pricing | OSS free; cloud tiers (market) |
| How it runs | Define agents in TS; deploy with tracing hooks |
| Source links | https://mastra.ai |
| Portfolio lesson | Standard agent harness hooks in SourceA motor |

## Task (Medium — hardening, validator, docs)

Pair onboarding step with `Worker job run detail page (pass/fail/steps/logs/retry)` receipt so buyer sees proof immediately

## Implementation extraction

`Mastra · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0535`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Mastra` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
