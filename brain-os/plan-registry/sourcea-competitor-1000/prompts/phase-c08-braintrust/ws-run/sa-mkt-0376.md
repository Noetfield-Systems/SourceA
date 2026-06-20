# sa-mkt-0376 — Braintrust · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
**Stack:** SourceA · **Competitor row:** 8 · **Phase:** phase-c08-braintrust
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Braintrust |
| Product | Eval + logging platform |
| What they sell | Experiment tracking, eval scores, and production logs for AI products |
| Who buys | AI product and eng teams |
| Pricing | From ~$249/mo (market); free tier for evals |
| How it runs | Log spans; run eval suites; compare prompt versions |
| Source links | https://www.braintrust.dev |
| Portfolio lesson | PASS/FAIL eval score on shipped agent runs |

## Task (Medium — hardening, validator, docs)

Surface run id + link in Hub/factory glance for founder audit

## Implementation extraction

`Braintrust · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0376`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Braintrust` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
