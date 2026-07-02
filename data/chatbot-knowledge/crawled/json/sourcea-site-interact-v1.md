---
updated: 2026-07-02T08:56:13Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/sourcea-site-interact-v1.json
public: true
kind: json
---

# Sourcea Site Interact V1

- **schema**: sourcea-site-interact-v1
- **version**: 1.3.0
- **saved_at**: 2026-07-01T23:45:00Z
- **execution_first**: True
- **booking_url**: https://cal.com/sourcea/proof-demo
- **booking_overlay_url**: https://cal.com/sourcea/proof-demo?overlayCalendar=true&embed=true
- **booking_label**: Talk to a human
- **use_cal_overlay**: True
- **playbook_label**: Tools
- **playbook_intro**: Pick your lane — each path ends with proof you can verify alone.
- **guided_once_per_session**: True
- **guided_title**: What brings you here?
- **guided_subtitle**: One question · real destination · no calendar required
## segments
## startup
- **id**: startup
- **audience**: buyer
- **label**: Building a startup / agentic system
- **href**: /start
- **track**: segment_startup
## vc-proof
- **id**: vc-proof
- **audience**: buyer
- **label**: VC-grade production proof
- **href**: /sourcea/proof/live
- **track**: segment_vc_proof
## beginner
- **id**: beginner
- **audience**: learner
- **label**: I'm new — show me how to start
- **href**: /learn
- **track**: segment_beginner
## agency
- **id**: agency
- **audience**: buyer
- **label**: Agency / client work
- **href**: /sourcea/case-studies/
- **track**: segment_agency
## cursor
- **id**: cursor
- **audience**: technical
- **label**: I use Cursor daily
- **href**: /forge/terminal
- **track**: segment_cursor
## guided_prompts
## startup
- **id**: startup
- **audience**: buyer
- **label**: Building a startup / agentic system
- **href**: /start
- **track**: segment_startup
## vc-proof
- **id**: vc-proof
- **audience**: buyer
- **label**: VC-grade production proof
- **href**: /sourcea/proof/live
- **track**: segment_vc_proof
## beginner
- **id**: beginner
- **audience**: learner
- **label**: I'm new — show me how to start
- **href**: /learn
- **track**: segment_beginner
## agency
- **id**: agency
- **audience**: buyer
- **label**: Agency / client work
- **href**: /sourcea/case-studies/
- **track**: segment_agency
## cursor
- **id**: cursor
- **audience**: technical
- **label**: I use Cursor daily
- **href**: /forge/terminal
- **track**: segment_cursor
## skills
## forge-terminal
- **id**: forge-terminal
- **label**: Forge Terminal
- **hint**: Live agentic demo
- **href**: /forge/terminal
- **technique**: living_ui
- **icon**: ◎
## sourcea-boot-eval
- **id**: sourcea-boot-eval
- **label**: sourcea-boot eval
- **hint**: PASS or BLOCK · 5 min
- **href**: /eval
- **technique**: proof_surface
- **icon**: ⎋
## proof-receipt
- **id**: proof-receipt
- **label**: Live receipt
- **hint**: Verify yourself — no call
- **href**: /sourcea/proof/live
- **technique**: proof_surface
- **icon**: ✓
## proof-quiz
- **id**: proof-quiz
- **label**: Proof quiz
- **hint**: ALLOW / BLOCK game
- **href**: /sourcea/scenario#proof-quiz
- **technique**: interactive_education
- **icon**: ?
## learn-start
- **id**: learn-start
- **label**: Learn & build
- **hint**: Beginner on-ramp
- **href**: /learn
- **technique**: interactive_education
- **icon**: ★
## mvp-intake
- **id**: mvp-intake
- **label**: 48h MVP
- **hint**: Scoped build + receipt
- **href**: /start
- **technique**: commercial_intake
- **icon**: ◆
## case-studies
- **id**: case-studies
- **label**: Client stories
- **hint**: Agency proof paths
- **href**: /sourcea/case-studies/
- **technique**: proof_surface
- **icon**: ◇
## book-demo
- **id**: book-demo
- **label**: Talk to a human
- **hint**: Optional escalation
- **action**: cal_overlay
- **technique**: cal_com
- **icon**: 📅
## brain_extra_chips
## item 1
- **label**: Run sourcea-boot
- **message**: How do I evaluate SourceA with sourcea-boot in five minutes — clone, install, and read BOOT_REPORT.json?
## item 2
- **label**: I'm new here
- **message**: I'm new to agentic AI — what's the simplest path to learn and build on SourceA?
## item 3
- **label**: See live receipt
- **message**: Show me what a client receives as proof after a job completes — no call needed.
## item 4
- **label**: Ship 48h MVP
- **message**: I need a 48-hour MVP — what's the intake path and what proof do I get?
## techniques
- **cal_com**: Optional human walkthrough — fallback only
- **living_ui**: Browser Forge Terminal — chat + controlled run
- **proof_surface**: Client-facing receipt — verify without a call
- **commercial_intake**: GOAL · DONE · VERIFY scope lock
- **proof_sandbox**: Bounded job intake — output + receipt async
- **interactive_education**: Learn by doing — quiz and guided steps
