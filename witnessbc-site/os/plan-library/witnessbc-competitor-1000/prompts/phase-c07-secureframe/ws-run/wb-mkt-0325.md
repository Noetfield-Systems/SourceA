# wb-mkt-0325 — Secureframe · Run history & proof

**Version:** 2 · **Tier:** T2 · **Workstream:** ws-run
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

Add retention note: how long run history kept vs Secureframe (Custom; typically $10k+ (market) tier hints)

## Implementation extraction

`Secureframe · Run history & proof` → what buyer sees at vendor → what we ship on disk with receipt.

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `wb-mkt-0325`
2. Evidence row in `AGENT-AUTO-WITNESSBC` PRIORITY/AUDIT with `Secureframe` link
3. No abstract rename — concrete behavior only

---
agent_tag: AGENT-AUTO-WITNESSBC
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v2
