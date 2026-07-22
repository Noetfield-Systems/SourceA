# SourceA Website UI E2E Audit (v2)

**At:** 2026-07-22T03:17:37Z  
**Base:** https://sourcea.app  
**Verdict:** `FAIL`  

## Summary

| Metric | Count |
|--------|-------|
| Live BFS paths | 49 |
| Dist paths | 122 |
| Unique audited | 125 |
| Counted (non-rejected) | 121 |
| PASS | 1 |
| FAIL | 120 |
| Buyer funnel FAIL | 12 |
| SPA fallback rejected | 4 |
| Count math | counted = unique_audited - rejected_spa_fallback |

## Deploy drift (live sha256 vs dist)

- `https://sourcea.app/` dist=`SourceA-landing/green-unified/dist/index.html` live=b4575f5b174f… dist=72eccee50382…
- `https://sourcea.app/48h-mvp` dist=`SourceA-landing/green-unified/dist/48h-mvp/index.html` live=ca9d32f01b45… dist=5d883df89c4a…
- `https://sourcea.app/agent-run` dist=`SourceA-landing/green-unified/dist/agent-run/index.html` live=720d57cef3dc… dist=1d00efbedde2…
- `https://sourcea.app/ai-value-governance` dist=`SourceA-landing/green-unified/dist/ai-value-governance/index.html` live=14829112e2c9… dist=37c4f778bf47…
- `https://sourcea.app/attach/procurement-pack.html` dist=`SourceA-landing/green-unified/dist/sourcea/attach/procurement-pack.html` live=0df087ba3452… dist=a298305c6f3d…
- `https://sourcea.app/auth/sign-in` dist=`SourceA-landing/green-unified/dist/auth/sign-in.html` live=83273880b8fb… dist=f21192e23409…
- `https://sourcea.app/auth/sign-up` dist=`SourceA-landing/green-unified/dist/auth/sign-up.html` live=adb4bad79b6d… dist=b5430a378f78…
- `https://sourcea.app/changelog` dist=`SourceA-landing/green-unified/dist/changelog/index.html` live=b0f47443d0d0… dist=0a2ee2cd2648…
- `https://sourcea.app/compare` dist=`SourceA-landing/green-unified/dist/compare/index.html` live=cf2500a359bb… dist=e59139170e9c…
- `https://sourcea.app/enterprise-ai-control-plane` dist=`SourceA-landing/green-unified/dist/enterprise-ai-control-plane/index.html` live=0750765bae00… dist=7712ca09a900…
- `https://sourcea.app/eval` dist=`SourceA-landing/green-unified/dist/eval.html` live=e053220621a4… dist=77838e6827b5…
- `https://sourcea.app/forge` dist=`SourceA-landing/green-unified/dist/forge/index.html` live=5aaae81eb369… dist=5fe1a62acbe6…
- `https://sourcea.app/forge/terminal` dist=`SourceA-landing/green-unified/dist/forge/terminal/index.html` live=1c3fe5f86637… dist=e022fc6d6c18…
- `https://sourcea.app/forge/terminal/profile` dist=`SourceA-landing/green-unified/dist/forge/terminal/profile/index.html` live=52c2dd1adc8b… dist=cf84e2de112f…
- `https://sourcea.app/forge/terminal/signin` dist=`SourceA-landing/green-unified/dist/forge/terminal/signin/index.html` live=a1ffda876ed3… dist=ddb8f4ec1be4…
- `https://sourcea.app/forge/terminal/signup` dist=`SourceA-landing/green-unified/dist/forge/terminal/signup/index.html` live=91aa5a847954… dist=0c4a5d8335da…
- `https://sourcea.app/forge/terminal/workspace` dist=`SourceA-landing/green-unified/dist/forge/terminal/workspace/index.html` live=233d4547cd05… dist=427b126a8143…
- `https://sourcea.app/funnel` dist=`SourceA-landing/green-unified/dist/funnel/index.html` live=122987565b73… dist=145e5321ba9b…
- `https://sourcea.app/growth` dist=`SourceA-landing/green-unified/dist/growth/index.html` live=d3c6d943b5a9… dist=64ff8178b3b2…
- `https://sourcea.app/kernel` dist=`SourceA-landing/green-unified/dist/kernel/index.html` live=de72164bfc0b… dist=508714707b62…

## Buyer funnel

- `/` — **FAIL** · sha256 `b4575f5b174f…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/index.html)
  - WARN `trust_placeholder_ssr`: SSR trust counters show em-dash — hydrated client-side from trust-signals.json
- `/start` — **FAIL** · sha256 `0490c25f95e6…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/start/index.html)
- `/pricing` — **FAIL** · sha256 `f53e1c15ea36…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/pricing/index.html)
- `/sourcea/pricing` — **FAIL** · sha256 `f53e1c15ea36…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/pricing.html)
- `/proof` — **FAIL** · sha256 `b3599f1b9c0c…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/proof/index.html)
- `/sourcea/proof` — **FAIL** · sha256 `b3599f1b9c0c…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/proof.html)
- `/sourcea/offer` — **FAIL** · sha256 `29988e80f890…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/offer.html)
- `/eval` — **FAIL** · sha256 `e053220621a4…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/eval.html)
- `/forge/terminal` — **FAIL** · sha256 `1c3fe5f86637…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/terminal/index.html)
- `/sourcea/forge/terminal` — **FAIL** · sha256 `1c3fe5f86637…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/forge/terminal.html)
- `/security` — **FAIL** · sha256 `f12fe5d042d3…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/security/index.html)
- `/sourcea/security` — **FAIL** · sha256 `f12fe5d042d3…` · **DIST DRIFT**
  - FAIL `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/security.html)

## Failures

### https://sourcea.app/
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/index.html)

### https://sourcea.app/48h-mvp
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/48h-mvp/index.html)

### https://sourcea.app/agent-run
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/agent-run/index.html)

### https://sourcea.app/ai-value-governance
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/ai-value-governance/index.html)

### https://sourcea.app/attach/procurement-pack.html
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/sourcea/attach/procurement-pack.html)

### https://sourcea.app/auth/sign-in
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/auth/sign-in.html)

### https://sourcea.app/auth/sign-up
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/auth/sign-up.html)

### https://sourcea.app/changelog
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/changelog/index.html)

### https://sourcea.app/compare
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/compare/index.html)

### https://sourcea.app/enterprise-ai-control-plane
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/enterprise-ai-control-plane/index.html)

### https://sourcea.app/eval
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/eval.html)

### https://sourcea.app/forge
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/index.html)

### https://sourcea.app/forge/terminal
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/terminal/index.html)

### https://sourcea.app/forge/terminal/profile
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/terminal/profile/index.html)

### https://sourcea.app/forge/terminal/signin
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/terminal/signin/index.html)

### https://sourcea.app/forge/terminal/signup
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/terminal/signup/index.html)

### https://sourcea.app/forge/terminal/workspace
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/forge/terminal/workspace/index.html)

### https://sourcea.app/funnel
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/funnel/index.html)

### https://sourcea.app/growth
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/growth/index.html)

### https://sourcea.app/kernel
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/kernel/index.html)

### https://sourcea.app/learn
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/learn/index.html)

### https://sourcea.app/mvp
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/mvp/index.html)

### https://sourcea.app/operating-brain-install
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/operating-brain-install/index.html)

### https://sourcea.app/platform
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/platform.html)

### https://sourcea.app/platform-story
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/platform-story/index.html)

### https://sourcea.app/platform/profile
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/platform/profile/index.html)

### https://sourcea.app/platform/sign-in
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/platform/sign-in/index.html)

### https://sourcea.app/platform/sign-up
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/platform/sign-up/index.html)

### https://sourcea.app/platform/workspace
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/platform/workspace/index.html)

### https://sourcea.app/pricing
- `deploy_drift`: live deploy hash != dist (SourceA-landing/green-unified/dist/pricing/index.html)

## Checks

- Live BFS + sitemap discovery (not splat URLs)
- Dist vs live body sha256 (deploy drift FAIL)
- Path leaks, {ENTITY}, forbidden phrases, regex v2
- SPA fallback rejection
- Buyer funnel explicit bucket
- Contact: hello@ / forge@ / contract@sourcea.*

`scripts/sourcea_website_ui_e2e_audit_v1.py` · gate `data/sourcea-ui-mechanical-gate-v1.json`
