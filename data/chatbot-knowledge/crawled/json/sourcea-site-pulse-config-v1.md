---
updated: 2026-06-30T08:50:46Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/sourcea-site-pulse-config-v1.json
public: true
kind: json
---

# Sourcea Site Pulse Config V1

- **schema**: sourcea-site-pulse-config-v1
- **version**: 1.1.0
- **saved_at**: 2026-06-25T16:00:00Z
- **api_worker_url**: https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev
- **event_path**: /api/site/event/v1
- **feedback_path**: /api/site/feedback/v1
- **stats_path**: /api/site/stats/v1
- **dashboard_path**: /api/site/dashboard/v1
- **founder_dashboard_page**: /sourcea/pulse-founder
- **public_stats_page**: /sourcea/status
- **booking_url**: https://cal.com/sourcea/proof-demo
- **booking_overlay_url**: https://cal.com/sourcea/proof-demo?overlayCalendar=true&embed=true
- **booking_label**: Talk to a human
## feedback_types
## bug
- **id**: bug
- **label**: Something is broken
## confused
- **id**: confused
- **label**: This confused me
## idea
- **id**: idea
- **label**: You should add…
## praise
- **id**: praise
- **label**: This worked well
- **founder_key_hint**: wrangler secret put FOUNDER_PULSE_KEY — worker sourcea-site-pulse-v1
