# sa-mkt-0240 — Langfuse · Onboarding & PLG

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-onboard
**Stack:** SourceA · ** row:** 5 · **Phase:** phase-c05-langfuse
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Langfuse |
| Product | LLM engineering platform |
| What they sell | Observability, prompts, evals, and analytics for LLM apps and agents |
| Who buys | AI engineering teams |
| Pricing | Free 50k obs/mo; Core ~$29/mo; Pro ~$199/mo — https://langfuse.com/pricing |
| How it runs | SDK captures traces; dashboard filters by user, session, cost, latency |
| Source links | https://langfuse.com · https://langfuse.com/docs |
| Portfolio lesson | Hierarchical trace viewer per agent turn with cost/latency |

## Task (Low — research, defer note, or compare-only)

Close sa-mkt-0240 with onboarding evidence + verify PASS

## Implementation extraction

`Langfuse · Onboarding & PLG` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0240`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Langfuse` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
