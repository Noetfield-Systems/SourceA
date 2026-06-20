# sa-mkt-0753 — Relay.app · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
**Stack:** SourceA · **Competitor row:** 16 · **Phase:** phase-c16-relay-app
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Relay.app |
| Product | Human-in-the-loop automation |
| What they sell | Collaborative automations with approval steps |
| Who buys | Ops and rev teams |
| Pricing | From ~$19/mo (market) |
| How it runs | Workflow pauses for human approval; then continues |
| Source links | https://www.relay.app |
| Portfolio lesson | Approval step before ACT/implement in worker loop |

## Task (High — next sprint parity with competitor)

Add `Worker Hub Next steps + factory-now line` UI field or copy block implementing smallest slice of `Approval step before ACT/implement in worker loop`; preserve honest tier label

## Implementation extraction

`Relay.app · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0753`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `Relay.app` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
