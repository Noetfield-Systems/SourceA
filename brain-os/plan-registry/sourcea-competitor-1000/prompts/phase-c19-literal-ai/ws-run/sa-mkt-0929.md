# sa-mkt-0929 — Literal AI · Run history & proof

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-run
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

## Task (Low — research, defer note, or compare-only)

Regression: rerun verify after run UI change

## Implementation extraction

`Literal AI · Run history & proof` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0929`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Literal AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
