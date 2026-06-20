# wb-mkt-0356 — Vanta · Buyer-visible UX

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-ux
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

## Task (Medium — hardening, validator, docs)

Add `Witness AI Flow install replay demo + 6 receipt types` mock row labeled mock_only until live — match Vanta run/history metaphor not invented name

## Implementation extraction

`Vanta · Buyer-visible UX` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0356`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Vanta` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
