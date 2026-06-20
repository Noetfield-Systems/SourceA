# sa-mkt-0192 — Upstash QStash · Integrations & API

**Version:** 2 · **Tier:** T0 · **Workstream:** ws-integrate
**Stack:** SourceA · ** row:** 4 · **Phase:** phase-c04-upstash-qstash
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | Upstash QStash |
| Product | HTTP message queue & scheduler |
| What they sell | Serverless message queue — schedule and retry HTTP calls without infra |
| Who buys | Serverless developers |
| Pricing | ~$1 per 100k messages pay-as-you-go; tiers from ~$180/mo |
| How it runs | Publish HTTP message; QStash delivers with retries and DLQ |
| Source links | https://upstash.com/qstash · https://upstash.com/pricing |
| Portfolio lesson | Lightweight dispatch layer for hub Actions → cloud workers |

## Task (Critical — smallest shippable slice with receipt)

Spec `scripts/ queue + cloud dispatch APIs` contract: input → policy gate → output + receipt

## Implementation extraction

`Upstash QStash · Integrations & API` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0192`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Upstash QStash` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
