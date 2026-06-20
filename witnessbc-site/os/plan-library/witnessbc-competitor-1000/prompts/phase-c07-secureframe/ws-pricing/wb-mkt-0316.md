# wb-mkt-0316 — Secureframe · Pricing & packaging

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-pricing
**Stack:** WitnessBC · **Competitor row:** 27 · **Phase:** phase-c07-secureframe
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | Secureframe |
| Product | Automated compliance |
| What they sell | Automate evidence for SOC 2, ISO 27001, and more |
| Who buys | Mid-market SaaS |
| Pricing | Custom; typically $10k+ (market) |
| How it runs | Integrations → continuous monitoring → audit export |
| Source links | https://secureframe.com |
| Portfolio lesson | Export bundle buyer can hand to auditor |

## Task (Medium — hardening, validator, docs)

Document why buyers pay per Secureframe: Audit prep without full-time compliance hire — tie to our offer in plain English

## Implementation extraction

`Secureframe · Pricing & packaging` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0316`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Secureframe` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
