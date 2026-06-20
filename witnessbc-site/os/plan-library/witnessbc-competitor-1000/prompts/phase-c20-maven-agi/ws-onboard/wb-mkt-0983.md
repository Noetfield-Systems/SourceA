# wb-mkt-0983 — Maven AGI · Onboarding & PLG

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-onboard
**Stack:** WitnessBC · **Competitor row:** 40 · **Phase:** phase-c20-maven-agi
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Maven AGI |
| Product | Enterprise support agents |
| What they sell | AI agents for customer support with escalation workflows |
| Who buys | Support leaders at mid-market+ |
| Pricing | Enterprise custom |
| How it runs | Agent resolves tickets; logs actions; escalates |
| Source links | https://www.mavenagi.com |
| Portfolio lesson | Escalation + action log per ticket pattern |

## Task (High — next sprint parity with competitor)

Add checklist or wizard step on `witnessbc.com pricing + toolkits hub` — no Terminal required

## Implementation extraction

`Maven AGI · Onboarding & PLG` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0983`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Maven AGI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
