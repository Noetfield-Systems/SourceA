# wb-mkt-0354 — Vanta · Buyer-visible UX

**Version:** 2 · **Tier:** T1 · **Workstream:** ws-ux
**Stack:** WitnessBC · **Competitor row:** 28 · **Phase:** phase-c08-vanta
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Vanta |
| Product | Trust management |
| What they sell | Automate compliance for SOC 2, ISO 27001, HIPAA, and more |
| Who buys | Startups to mid-market |
| Pricing | Custom; often $10k–50k/yr (market) |
| How it runs | Connect stack; continuous monitoring; trust center |
| Source links | https://www.vanta.com |
| Portfolio lesson | Control → linked proof artifact (pattern only) |

## Task (High — next sprint parity with competitor)

E2E or glance check: founder can see `Buyer-visible UX` outcome without Terminal; receipt timestamp on disk

## Implementation extraction

`Vanta · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0354`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Vanta` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
