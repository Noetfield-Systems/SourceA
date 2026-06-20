# sa-mkt-0462 — Giskard · Pricing & packaging

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-pricing
**Stack:** SourceA · ** row:** 10 · **Phase:** phase-c10-giskard
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

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

Map Giskard revenue model (OSS + enterprise Hub) to our `SourceA agency + Buyer-1 pricing narrative` tier names — no hidden fees theater

## Implementation extraction

`Giskard · Pricing & packaging` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0462`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Giskard` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
