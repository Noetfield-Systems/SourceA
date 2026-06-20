# wb-mkt-0996 — Maven AGI · Integrations & API

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-integrate
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

## Task (Medium — hardening, validator, docs)

Document secrets path ~/.sourcea-secrets — never workspace .env

## Implementation extraction

`Maven AGI · Integrations & API` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0996`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Maven AGI` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
