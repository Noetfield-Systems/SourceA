---
updated: 2026-07-06T10:57:13Z
lane: core
source_path: data/sourcea-dual-plane-v1.json
public: true
kind: json
---

# Sourcea Dual Plane V1

- **schema**: sourcea-dual-plane-v1
- **version**: 1.0.0
- **saved_at**: 2026-06-23T07:00:00Z
- **one_law**: SourceA has TWO sides: KERNEL (foundation — feeds all repos) and COMMERCIAL (paying customers — less infra, more agentic product). Never mix them logged or in agent rules.
## foundation_kernel
- **role**: Governance systems, engines, cloud factory, brain-os entry, scripts, data SSOT
### feeds
- TrustField
- Noetfield
- WitnessBC
- VIRLUX
- all portfolio repos
### paths
- brain-os/law/entry/
- scripts/
- cloud/
- apps/
- data/
- packages/
- **backup_tag**: foundation-kernel-2026-06-23
- **backup_broker**: ~/Desktop/SinaaiDataBase/archive/sourcea-foundation-kernel-backup-2026-06-23/
- **living_center**: data/sourcea-living-center-v1.json
- **archive_broker**: ~/Desktop/SinaaiDataBase/archive/sourcea-exit-2026-06-23/
## commercial_plane
- **role**: Paying customers only — service + future platform
- **domain_primary**: sourcea.app
- **domain_vercel**: deprecated_interim_only
- **domain_pages**: sourcea-com.pages.dev
- **domain_email**: hello@sourcea.app
- **url_mvp_home**: https://sourcea.app/
- **url_kernel**: https://sourcea.app/kernel/
- **website_surface**: SourceA-landing/green-unified/
### must_not_leak_into_kernel
- trial infra vibes
- customer PII in brain-os
- sandbox auth in governance law
### business_a_service
- **id**: 48h-mvp-service
- **headline**: We build your startup's MVP in 48 hours.
- **target**: founders, startups
- **revenue**: $2k–$10k per project
- **timeline_first_dollar**: this week
- **cta**: Start your project →
#### form_questions
- What are you building? (app / website / MVP / video / free text)
- Competitor or example? (URL or name)
- Deadline? (this week / 2 weeks / flexible)
- Budget? ($500–1k / $1k–3k / $3k–10k / let's talk)
- Your email
- **end_screen**: We'll respond in 2 hours with a plan.
- **scope_v1**: No platform · no sandbox · no free tier — form + skills + Cursor delivery
- **wedge**: Apple App Store apps built with AI — specific, credible ICP
- **landing_path**: SourceA-landing/green-unified/start.html
- **intake_api**: /api/commercial/mvp-intake/v1
- **intake_script**: scripts/sourcea_mvp_intake_submit_v1.py
- **e2e_validator**: scripts/validate-sourcea-mvp-intake-e2e-v1.sh
### business_b_platform
- **id**: forge-platform
- **headline**: Come build on our platform
- **target**: broader market
- **revenue**: subscriptions + usage
#### needs
- Forge complete
- auth
- sandbox
- billing
- **timeline_first_dollar**: 2–3 months minimum
- **phase**: AFTER first 3 service clients fund build ($6k–$10k)
### lock_order
- Business A landing + 5-field form FIRST
- Business B only after service revenue
## human_docs
- docs/SOURCEA_DUAL_PLANE_KERNEL_AND_COMMERCIAL_LOCKED_v1.md
- docs/SOURCEA_FOUNDER_AI_AGENTIC_PLATFORM_PROPOSAL_v1.md
