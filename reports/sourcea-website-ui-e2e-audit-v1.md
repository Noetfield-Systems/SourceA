# SourceA Website UI E2E Audit (v2)

**At:** 2026-07-08T01:52:47Z  
**Base:** https://sourcea.app  
**Verdict:** `FAIL`  

## Summary

| Metric | Count |
|--------|-------|
| Live BFS paths | 56 |
| Dist paths | 116 |
| Unique audited | 117 |
| Counted (non-rejected) | 115 |
| PASS | 114 |
| FAIL | 1 |
| Buyer funnel FAIL | 0 |
| SPA fallback rejected | 2 |
| Count math | counted = unique_audited - rejected_spa_fallback |

## Deploy drift (live sha256 vs dist)

- `https://sourcea.app/sourcea/factories/try-factory-demo` dist=`SourceA-landing/green-unified/dist/sourcea/factories/try-factory-demo.html` live=436ba1bfb9ec… dist=31b19f564f33…
- `https://sourcea.app/sourcea/home` dist=`SourceA-landing/green-unified/dist/sourcea/home.html` live=957f40b539c2… dist=6844c003fbfd…

## Buyer funnel

- `/` — **PASS** · sha256 `957f40b539c2…` · **dist match**
  - WARN `trust_placeholder_ssr`: SSR trust counters show em-dash — hydrated client-side from trust-signals.json
- `/start` — **PASS** · sha256 `834818e121fa…` · **dist match**
- `/pricing` — **PASS** · sha256 `52b8df159e27…` · **dist match**
- `/sourcea/pricing` — **PASS** · sha256 `52b8df159e27…` · **dist match**
- `/proof` — **PASS** · sha256 `852891f0ebb4…` · **dist match**
- `/sourcea/proof` — **PASS** · sha256 `852891f0ebb4…` · **dist match**
- `/sourcea/offer` — **PASS** · sha256 `ec746d5ec05e…` · **dist match**
- `/eval` — **PASS** · sha256 `e053220621a4…` · **dist match**
- `/forge/terminal` — **PASS** · sha256 `f047e07ddf04…` · **dist match**
- `/sourcea/forge/terminal` — **PASS** · sha256 `f047e07ddf04…` · **dist match**
- `/security` — **PASS** · sha256 `9c6394a55ccb…` · **dist match**
- `/sourcea/security` — **PASS** · sha256 `9c6394a55ccb…` · **dist match**

## Failures

### https://sourcea.app/sourcea/factories/try-factory-demo
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/factories/try-factory-demo.html)

## Checks

- Live BFS + sitemap discovery (not splat URLs)
- Dist vs live body sha256 (deploy drift FAIL)
- Path leaks, {ENTITY}, forbidden phrases, regex v2
- SPA fallback rejection
- Buyer funnel explicit bucket
- Contact: hello@ / forge@ / contract@sourcea.*

`scripts/sourcea_website_ui_e2e_audit_v1.py` · gate `data/sourcea-ui-mechanical-gate-v1.json`
