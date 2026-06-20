---
name: sina-agentic-commercial
description: >-
  Agentic outreach and demo booking for TrustField and Noetfield — founder never
  sends email or places calls. Use for commercial lane work, GTM outreach, demo
  scheduling, voice AI outbound, and tracker/debrief receipts.
---

# Agentic commercial (shared)

**Law:** `brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md`

## Founder never

- Send outreach email
- Place sales or demo calls
- Book calendar slots manually

Founder: approve bounded orders · tap Hub · ASK responses only.

## Agent jobs

| Job | Output |
|-----|--------|
| Draft + send outreach | Tracker row · `sent_by: agent` · template id |
| Qualify reply | CRM/tracker status · next agent action |
| Book demo | Calendar event · `booked_by: agentic` · debrief path |
| Voice outbound (when live) | Call log + receipt · employee handoff if human needed |

## Lanes

| Brand | Skill also load | Hero line |
|-------|-----------------|-----------|
| TrustField | `@sina-trustfield` | FINTRAC fear → evidence pilot |
| Noetfield | `@sina-noetfield-cloud` | Copilot audit trail → Trust Brief |

## Proof

- `partner-api-tracker.csv` or hub Track tab — non-empty agent rows
- `BUYER_DEBRIEF_TEMPLATE_v1.md` after booked demo
- No claim of commercial progress without tracker + receipt

## Not in scope

- Cursor AUTO-RUN as commercial substitute
- Founder “just send 5 emails today” as advice
- SourceA public marketing homepage
