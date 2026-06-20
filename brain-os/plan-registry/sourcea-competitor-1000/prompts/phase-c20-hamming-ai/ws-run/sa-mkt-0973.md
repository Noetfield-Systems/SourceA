# sa-mkt-0973 — Hamming AI · Run history & proof

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-run
**Stack:** SourceA · **Competitor row:** 20 · **Phase:** phase-c20-hamming-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Hamming AI |
| Product | Voice/agent QA |
| What they sell | Scenario test suites for voice and conversational agents |
| Who buys | Voice AI and agent QA teams |
| Pricing | Custom (young startup) |
| How it runs | Define scenarios; run regression; score outcomes |
| Source links | https://www.hamming.ai |
| Portfolio lesson | Regression scenario suite before agent release |

## Task (High — next sprint parity with competitor)

Implement smallest `Worker job run detail page (pass/fail/steps/logs/retry)` slice — PASS/FAIL + one step log; mock_only ok with label

## Implementation extraction

`Hamming AI · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0973`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Hamming AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
