# sa-mkt-0255 — Helicone · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
**Stack:** SourceA · ** row:** 6 · **Phase:** phase-c06-helicone
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Helicone |
| Product | LLM gateway & observability |
| What they sell | Proxy layer for LLM requests — caching, analytics, monitoring |
| Who buys | LLM app developers |
| Pricing | Free hobby ~10k req; Pro from ~$79/mo (market) |
| How it runs | One-line proxy integration; logs every request |
| Source links | https://helicone.ai |
| Portfolio lesson | Per-model cost and latency dashboard on dispatch |

## Task (Medium — hardening, validator, docs)

Diff our public copy vs Helicone pricing/product page — list 3 concrete gaps; fix highest P0 gap only

## Implementation extraction

`Helicone · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0255`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Helicone` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
