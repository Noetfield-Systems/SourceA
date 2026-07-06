# SourceA Website UI E2E Audit (v2)

**At:** 2026-07-06T12:36:16Z  
**Base:** https://sourcea.app  
**Verdict:** `PASS`  

## Summary

| Metric | Count |
|--------|-------|
| Live BFS paths | 51 |
| Dist paths | 116 |
| Unique audited | 117 |
| Counted (non-rejected) | 115 |
| PASS | 115 |
| FAIL | 0 |
| Buyer funnel FAIL | 0 |
| SPA fallback rejected | 2 |

## Buyer funnel

- `/` — **PASS**
- `/start` — **PASS**
- `/pricing` — **PASS**
- `/sourcea/pricing` — **PASS**
- `/proof` — **PASS**
- `/sourcea/proof` — **PASS**
- `/sourcea/offer` — **PASS**
- `/eval` — **PASS**
- `/forge/terminal` — **PASS**
- `/sourcea/forge/terminal` — **PASS**
- `/security` — **PASS**
- `/sourcea/security` — **PASS**

## Checks

- Live BFS + sitemap discovery (not splat URLs)
- Dist vs live drift receipt
- Path leaks, {ENTITY}, forbidden phrases, regex v2
- SPA fallback rejection
- Buyer funnel explicit bucket
- Contact: hello@ / forge@ / contract@sourcea.*

`scripts/sourcea_website_ui_e2e_audit_v1.py` · gate `data/sourcea-ui-mechanical-gate-v1.json`
