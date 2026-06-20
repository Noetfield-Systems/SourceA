# sa-mkt-0945 — Literal AI · Integrations & API

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-integrate
**Stack:** SourceA · ** row:** 19 · **Phase:** phase-c19-literal-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Literal AI |
| Product | Agent trace platform |
| What they sell | Tracing and eval UI for LLM apps and agents |
| Who buys | Agent startups |
| Pricing | Startup-friendly tiers |
| How it runs | Instrument app; view conversation traces and evals |
| Source links | https://www.literalai.com |
| Portfolio lesson | Conversation/run logging for agent sessions |

## Task (Medium — hardening, validator, docs)

Log every external call on run timeline (`Worker job run detail page (pass/fail/steps/logs/retry)`)

## Implementation extraction

`Literal AI · Integrations & API` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0945`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Literal AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
