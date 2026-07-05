# ACG Founder Review Gate (v1)

**Saved at:** 2026-07-05T12:45:00Z  
**Purpose:** Block outbound until founder explicitly approves send

---

## Checklist (all must pass)

- [ ] **Non-claims:** No guaranteed savings; no live production firewall claim
- [ ] **Pricing:** Model rates marked as `audit_time_live_lookup` / placeholders only
- [ ] **Prospect filled:** `ACG_FIRST_PROSPECT_INSTANCE_v1.md` — no `FOUNDER_FILL_*` left
- [ ] **Security:** Questions match prospect sector (regulated data if applicable)
- [ ] **Sender:** `hello@sourcea.app` only
- [ ] **CRM row:** `RE-ACG-001` created with `SKU-ACG-001` and `audit_id`
- [ ] **Intake instance:** `ACG-20260705-001` exists under `data/acg-intake-instances/`
- [ ] **Scope:** No Noetfield.com / NOOS / SG edits in this lane
- [ ] **Git:** ACG committed on `preserve/acg-2026-07-05` before reconcile

---

## Founder sign-off

| Field | Value |
|-------|-------|
| Approved by | __________________ |
| Date | __________________ |
| Send authorized | YES / NO |
| Notes | |

---

## After approval

1. Send kickoff email from `hello@sourcea.app`
2. Run CRM `touch --stage outreach_sent`
3. On reply: `agentic_cost_governance_intake_v1.py receipt --audit-id <id>`

**Mac Law:** Founder final contact only — no auto-send.
