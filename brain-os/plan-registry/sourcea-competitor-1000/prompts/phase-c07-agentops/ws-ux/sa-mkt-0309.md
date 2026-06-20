# sa-mkt-0309 — AgentOps · Buyer-visible UX

**Version:** 2 · **Tier:** T3 · **Workstream:** ws-ux
**Stack:** SourceA · ** row:** 7 · **Phase:** phase-c07-agentops
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

##  evidence

| Field | Value |
|-------|-------|
| Company | AgentOps |
| Product | Agent observability |
| What they sell | Session replay and monitoring for autonomous AI agents |
| Who buys | Agent builders and AI startups |
| Pricing | Free tier ~5k events; Pro ~$40/mo (market) |
| How it runs | SDK records agent steps, tools, costs; time-travel debugging UI |
| Source links | https://www.agentops.ai |
| Portfolio lesson | Time-travel replay for worker/agent debugging |

## Task (Low — research, defer note, or compare-only)

Ship summary in PRIORITY: preserved · changed · achieved vs AgentOps Buyer-visible UX

## Implementation extraction

`AgentOps · Buyer-visible UX` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `sa-mkt-0309`
2. Evidence row in `AGENT-AUTO-SOURCEA` PRIORITY/AUDIT with `AgentOps` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: generate_portfolio__1000_plans_v1.py v2
