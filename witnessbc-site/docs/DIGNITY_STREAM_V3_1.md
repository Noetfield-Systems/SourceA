# Witness BC — Systemic Stream: Specialist Routing & Intake Priority v3.1

**Effective:** 23 November 2026  
**Venture:** Independent Witness BC, British Columbia  
**Build-on:** Existing seven-stage Systemic Stream v3 on `main` (public `/dignity/stream`, `/dignity/process`, protected case workboard, editorial status and synthetic Blob read-back verification).

## Mission and non-targets
Witness BC reviews systems, service procedures, franchise pickup rules, training and management oversight instead of targeting individuals or their gender, sexual orientation, ethnicity or other identities. One branch's reported conduct cannot be attributed to every Richmond store. A first-hand account is not proof of misconduct or of protected-ground discrimination.

## Intake → Triage → Route → Follow up
1. **Confidential receipt.** The public report is validated, privately persisted and read back before the reporting person receives a case ID and private access code. An email draft or visit is not counted as a case.
2. **Protection signals.** Two optional booleans are now stored privately: fear of retaliation and immediate danger. Neither asserts a legal violation or replaces emergency services.
3. **Explainable initial priority.** `lib/dignity-triage.mjs` recommends `urgent` (1 business day) when the reporter explicitly signals safety or retaliation risk, `high` (2 business days) for repeated conduct or accessibility barriers, and `standard` (3 business days) for other cases. These are *internal review targets*, not statutory complaint deadlines or promises of resolution.
4. **Source-appropriate route.** `GET /api/dignity/routes` returns eight categories with a description of the relevant system and conditional referral options. `/dignity/process` allows an interactive read-only category selection; it never initiates contact.
5. **Human owner and next action.** Existing protected case workboard retains the original status, evidence classifications and event history and now stores a concrete next action, contact channel, and optional outcome type. No event overwrites the witness's original private report.
6. **Evidence before status.** An actual request for response requires a dated correspondence/evidence URL. Corroboration and resolution remain evidence-constrained. Public editorial release follows separate permission, redaction, source verification, right-of-reply and editor approval checks.
7. **Follow-through.** The authorized case lead checks procedure changes and records a documented response or explicitly unresolved closure. This release does not send messages automatically, create regulator complaints, or claim corrected policies without receipts.

## Jurisdiction notes
- **Delivery / gig work** — identify exact restaurant and relevant franchise operator; consult the delivery platform. Assess any employment or protected-ground route *only from the actual facts*.
- **Retail / customer service** — operator first; Consumer Protection BC only if covered by consumer law.
- **Employment / workplace** — WorkSafeBC, Employment Standards Branch or BC Human Rights Tribunal only as appropriate to the issue and worker relationship.
- **Public administration** — BC Ombudsperson and responsible authority; private restaurants generally outside Ombudsperson remit.
- **Housing, access, community** — sector-appropriate service, tenancy, accessibility or social support routes.

## UI and operational integrity
Public stream remains the source-first editorial feed created in concurrent main stream v3. The existing process page remains seven-stage; v3.1 enhances its specialist routing. Operator workboard retains the original state machine and proofLevel with optional action/channel/outcome details.

**Synthetic E2E:** report save → receipt → authenticated private status event → reporter read-back → deletion of synthetic report and event. Synthetic records are not counted as community cases or company responses.

**Acceptance:** GitHub CI tests, Playwright 320/390/1440 px, preview build on the same SHA, `GET /api/dignity/routes` returns eight conditions-based categories, production custom-domain 200 and storage health 200.

## Primary references (not affiliations)
- https://www.bchrt.bc.ca/human-rights-duties/services/
- https://www.bchrt.bc.ca/human-rights-duties/employment/
- https://bcombudsperson.ca/complaints/what-we-do/
- https://services.labour.gov.bc.ca/Complaints/s/employer-summary
- https://www.consumerprotectionbc.ca/complaint-assistant/
- https://www.worksafebc.com/en/health-safety/hazards-exposures/bullying-harassment

## Out-of-scope, not secretly completed
Staff roles with individual audit identities (current operator access remains key-based), consented private file attachments, automatic notifications from a verified Witness-owned sender, a confirmed franchise-owner identity for the Richmond case, automated SEO indexing and independently verified external corrective action. These require separate real integrations, evidence, and the applicable source permissions.
