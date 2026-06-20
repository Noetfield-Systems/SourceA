# sa-mkt-0841 — Vellum · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** SourceA · **Competitor row:** 17 · **Phase:** phase-c17-vellum
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Vellum |
| Product | LLM ops platform |
| What they sell | Prompt deployment, eval, and monitoring for production LLM apps |
| Who buys | LLM product teams |
| Pricing | Team/enterprise custom tiers |
| How it runs | Version prompts; run evals; monitor production |
| Source links | https://www.vellum.ai |
| Portfolio lesson | Versioned prompt + eval on every dispatch |

## Task (Critical — smallest shippable slice with receipt)

List Vellum integrations/APIs from https://www.vellum.ai or docs — pick one we can wire this quarter

## Implementation extraction

`Vellum · Integrations & API` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0841`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Vellum` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
