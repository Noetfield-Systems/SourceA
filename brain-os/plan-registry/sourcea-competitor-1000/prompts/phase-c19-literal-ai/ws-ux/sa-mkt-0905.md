# sa-mkt-0905 — Literal AI · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** SourceA · **Competitor row:** 19 · **Phase:** phase-c19-literal-ai
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

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

Diff our public copy vs Literal AI pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Literal AI · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0905`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Literal AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
