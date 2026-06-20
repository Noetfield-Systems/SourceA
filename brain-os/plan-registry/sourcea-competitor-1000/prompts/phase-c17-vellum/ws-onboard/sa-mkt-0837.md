# sa-mkt-0837 — Vellum · Onboarding & PLG

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-onboard
**Stack:** SourceA · ** row:** 17 · **Phase:** phase-c17-vellum
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

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

## Task (Medium — hardening, validator, docs)

Measure drop-off: list one friction point vs Vellum and fix

## Implementation extraction

`Vellum · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0837`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Vellum` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
