# sa-mkt-0896 — Portkey · Integrations & API

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-integrate
**Stack:** SourceA · **Competitor row:** 18 · **Phase:** phase-c18-portkey
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Portkey |
| Product | AI gateway |
| What they sell | LLM gateway with routing, caching, observability, governance |
| Who buys | Platform engineering |
| Pricing | Usage-tier SaaS |
| How it runs | Proxy all LLM calls; log, route, cache |
| Source links | https://portkey.ai |
| Portfolio lesson | Route models + log every call at dispatch |

## Task (Medium — hardening, validator, docs)

Document secrets path ~/.sourcea-secrets — never workspace .env

## Implementation extraction

`Portkey · Integrations & API` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0896`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Portkey` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
