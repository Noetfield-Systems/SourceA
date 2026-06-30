---
updated: 2026-06-30T12:40:38Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/sourcea-inbox-live-status-v1.json
public: true
kind: json
---

# Sourcea Inbox Live Status V1

- **schema**: sourcea-inbox-live-status-v1
- **version**: 1.0.0
- **saved_at**: 2026-06-24T01:30:00Z
- **vault_path**: ~/.sina/secrets.env
- **portfolio_tags**: data/portfolio-vault-email-tags-v1.json
- **one_law**: No mailto commercial CTA shown as live until verified=true for that address
## inboxes
### hello@sourcea.app
- **role**: greet
- **vault_tag**: SA-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD
- **verified**: False
- **stab**: STAB-101
### contact@sourcea.app
- **role**: intake
- **vault_tag**: SA-CONTACT-GOOGLE_WORKSPACE_APP_PASSWORD
- **verified**: False
- **stab**: STAB-008
- **intake_api**: /api/commercial/mvp-intake/v1
### proof@sourcea.app
- **role**: ops
- **vault_tag**: SA-PROOF-GOOGLE_WORKSPACE_APP_PASSWORD
- **verified**: False
- **stab**: STAB-102
### forge@sourcea.app
- **role**: forge
- **vault_tag**: SA-FORGE-GOOGLE_WORKSPACE_APP_PASSWORD
- **verified**: False
- **stab**: STAB-005
## fallback_cta
- **label**: Start free sandbox
- **href**: /sourcea/factories/try-factory-demo
- **signature_url**: https://sourcea.app
