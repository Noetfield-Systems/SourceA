# SourceA Website UI E2E Audit

**At:** 2026-07-06T12:15:18Z  
**Base:** https://sourcea.app  
**Verdict:** `PASS_WITH_WARNINGS`  

## Executive summary

- **All 212 routes:** mechanical PASS (0 FAIL)
- **Warnings:** 37 (auth/contract pages without chatbot — expected)
- **Fix wave (2026-07-06):** footer sync on security/loops/sources, unify path leaks, legacy kernel page, reference mock CTA

## Summary

| Metric | Count |
|--------|-------|
| Paths discovered | 212 |
| Pages fetched | 212 |
| PASS | 212 |
| FAIL | 0 |
| WARN only | 37 |

## Warnings (review)

- **https://sourcea.app/ai-value-governance**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/enterprise-ai-control-plane**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/forge/terminal/profile**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/forge/terminal/signin**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/forge/terminal/signup**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/forge/terminal/workspace**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/operating-brain-install**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/platform/profile**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/platform/sign-in**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/platform/sign-up**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/platform/workspace**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/sourcea/ai-value-governance**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/sourcea/ai-value-governance.html**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/sourcea/brain-chat-settings**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- **https://sourcea.app/sourcea/brain-chat-settings.html**
  - `no_contact_surface`: commercial page missing hello@/forge@ and chatbot
- … and 22 more (see JSON)

## Checks applied

- Live HTTPS fetch (public hostname only)
- HTTP status + title + HTML shell
- Path leaks, stale positioning, mechanical gate forbidden phrases

**Machine:** `scripts/sourcea_website_ui_e2e_audit_v1.py`
