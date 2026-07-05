# ACG First Prospect — Personalized Instance (FOUNDER FILL)

**Audit ID:** `ACG-20260705-001`  
**CRM ID:** `RE-ACG-001`  
**Status:** DRAFT — founder must replace FOUNDER_FILL_* fields before send

---

## Prospect (founder fill)

| Field | Value |
|-------|-------|
| Company | **FOUNDER_FILL_COMPANY** |
| Contact name | **FOUNDER_FILL_NAME** |
| Title | **FOUNDER_FILL_TITLE** |
| Email | **FOUNDER_FILL_EMAIL** |
| Sector | SaaS (example — change if needed) |
| Org size | **FOUNDER_FILL_TEAM_SIZE** |
| Pain | AI tool sprawl · premium model leakage · no spend visibility |

---

## Commercial

| Field | Value |
|-------|-------|
| Offer | AI Spend Leak Audit + Premium Model Firewall pilot |
| SKU | `SKU-ACG-001` |
| Investment band | CAD $2,500–$4,000 (narrow at discovery) |
| Booking | Reply to schedule OR https://cal.com/sourcea/proof-demo |

---

## Intake instance

- JSON: `data/acg-intake-instances/ACG-20260705-001-v1.json`
- Receipt (after founder approves): `python3 scripts/agentic_cost_governance_intake_v1.py receipt --audit-id ACG-20260705-001 --json`

---

## Kickoff email (ready to personalize)

**Subject:** AI Spend Leak Audit — next steps & intake

Hi **FOUNDER_FILL_NAME**,

Thanks for your interest in the AI Spend Leak Audit. To get started we need a short intake so we can scope the audit and confirm timelines. Please reply with the checklist below or book a 20-min kickoff call.

What we'll do:
- Map your AI tool usage and costs
- Identify premium-model leakage and quick wins
- Deliver a prioritized findings report and pilot policy for one workflow

Investment: CAD $2,500–$4,000 (finalized at discovery). No production changes without your approval.

This is a diagnostic and advisory service only — we do not guarantee specific cost savings. Any pilot enforcement is scoped and controlled by you.

Best,  
Sina — SourceA  
hello@sourcea.app

---

## CRM commands (run after founder approves send)

```bash
python3 scripts/sourcea_revenue_engine_crm_v1.py init
python3 scripts/sourcea_revenue_engine_crm_v1.py add \
  --id RE-ACG-001 \
  --name "FOUNDER_FILL_NAME" \
  --company "FOUNDER_FILL_COMPANY" \
  --segment acg_prospect \
  --channel email \
  --sku SKU-ACG-001 \
  --deal 3000 \
  --audit-id ACG-20260705-001 \
  --json

python3 scripts/sourcea_revenue_engine_crm_v1.py touch \
  --id RE-ACG-001 \
  --stage outreach_sent \
  --template acg_kickoff_email \
  --audit-id ACG-20260705-001 \
  --note "First ACG prospect — founder approved send" \
  --json
```
