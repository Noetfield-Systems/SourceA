# sa-mkt-0904 — Literal AI · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
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

## Task (High — next sprint parity with competitor)

E2E or glance check: founder can see `Buyer-visible UX` outcome without Terminal; receipt timestamp logged

## Implementation extraction

`Literal AI · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0904`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Literal AI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
