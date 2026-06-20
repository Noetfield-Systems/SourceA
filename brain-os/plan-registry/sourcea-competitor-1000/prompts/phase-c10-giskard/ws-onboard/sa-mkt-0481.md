# sa-mkt-0481 — Giskard · Onboarding & PLG

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-onboard
**Stack:** SourceA · **Competitor row:** 10 · **Phase:** phase-c10-giskard
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Giskard |
| Product | LLM agent testing library |
| What they sell | Open-source evaluation and testing for LLM agents before production |
| Who buys | ML/AI QA teams |
| Pricing | OSS free; Hub subscription contact sales |
| How it runs | Run test suites on agents; Hub adds collaboration and continuous red-team |
| Source links | https://www.giskard.ai |
| Portfolio lesson | Pre-prod agent regression test library |

## Task (Critical — smallest shippable slice with receipt)

Document Giskard onboarding path (Paris OSS 2021 → enterprise Hub): who runs (OSS library + Giskard Hub enterprise) → first value moment

## Implementation extraction

`Giskard · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0481`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Giskard` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
