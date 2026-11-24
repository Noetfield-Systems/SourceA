# Witness BC — Dignity Stream v3.0
**Operational standard:** 23 November 2026 • Product owner: independent Witness BC • Component: Community Dignity & Systemic Accountability

## Mandate
Witness BC examines **systems, practices, policies, accessibility and repeat patterns**, not the personal identity, gender, sexual orientation or membership in any protected group of a worker or manager. An individual's rude conduct is not automatically evidence that management ordered it or a legal human-rights violation. The starting subject is a report, not a finding.

## Lifecycle — nine specialist stages
| Stage | Trigger | Required verifiable receipt | Default next action |
|---|---|---|---|
| 1. Receive | First-hand report submitted | Private Blob save + read-back + non-recoverable reporter code | Protect source, acknowledge receipt |
| 2. Triage | Case enters review queue | Dated workflow event, operator owner | Confirm location, dates, urgency and jurisdiction |
| 3. Clarify | Account incomplete | Dated internal event and request if actually sent | Request concrete first-hand details |
| 4. Review | Facts require checking | Evidence URL or factual private note | Source-corroborate and distinguish interpretations |
| 5. Request response | An actual letter/message was sent | Documentary evidence URL required for this status | Seek comment from responsible organization |
| 6. Evaluate reply | Company submits response | Append independent private event with accurate summary | Resolve factual disputes fairly |
| 7. Seek correction | Documented improvement pursued | A verifiable policy/action link before claiming resolution | Request policy clarification, training or remedy |
| 8. Public editorial review | Public brief proposed | Separate redaction/verification/permission check | Publish only qualified and correctly attributed facts |
| 9. Follow through | Improvement/outcome recorded | Verified outcome and follow-up evidence, or unresolved closure | Correct, close or re-open with new evidence |

The software's stored state machine uses existing statuses `received, triage, more_information, under_review, response_requested, corroborated, resolved, corrected, closed`. Editorial publication remains a distinct manual activity. No stage means a complaint was automatically sent to an external regulator.

## Internal service targets (not statutory deadlines)
- **P1**: 24-hour *triage* target for a declared safety concern or retaliation risk, not an emergency-response commitment; direct users to emergency services if in immediate danger.
- **P2**: 48-hour triage target for recurring reported treatment or an accessibility barrier.
- **P3**: 96-hour triage target for other reports.
- Operator can set and explain the next action, owner and a case-specific follow-up target in the append-only event log. Overdue is computed dynamically; this is not a legal finding or evidence score.
- Workload counters reflect only fetched private case pages; no unqualified total or “100 cases solved” is displayed.

## Jurisdictional referral logic
Explicitly defined in `lib/dignity-stream.mjs`, served read-only via `GET /api/dignity/routes`, which drives the public interactive route explorer:
- **Delivery/restaurant**: named location/franchise policy and delivery platform; do not blanket-label all Richmond businesses.
- **Retail/service**: management; Consumer Protection BC only for covered regulatory areas.
- **Employment**: WorkSafeBC bullying/harassment procedures where the employment relationship is covered; BC Employment Standards for statutory employment standards; Human Rights Tribunal only where protected-ground discrimination is implicated.
- **Public administration**: BC Ombudsperson where within its jurisdiction and normal complaints channels.
- **Housing/accessibility/community services**: sector-specific jurisdictional suggestions and official referral links.

Rules come from BC sources and remain *suggestions*, not definitive legal classifications. Any referral or organizational contact needs an actual authorized sender, delivered message and dated evidence before its case status changes.

## Architecture / receipts
1. Public intake `POST /api/dignity/report` validates a scoped structured schema, privately stores the report and reads it back before creating a reporter receipt.
2. Private Blob report records have random IDs and hashed access code; optional safety/retaliation flags only guide triage.
3. Reporter `POST /api/dignity/status` reveals only case stage and editorially approved short progress notes to the valid code bearer.
4. Key-protected operator API `GET/POST /api/dignity/admin` computes routing, internal priority, due target, owner, next action, status and events. POST appends a distinct event record; it cannot overwrite the original witness account.
5. Public `/dignity/stream` explains caseflow and suggested routes without exposing private records or unsourced allegations.
6. Incident-level press publication continues through separate human editorial approval; case briefs must distinguish first-hand allegation from independent finding.

## Example: Richmond McDonald's — deliberately precise
A witness reports recurring disrespectful treatment during pickups at **one particular but still unidentified branch**. Limited experiences elsewhere do not make this representative of all McDonald's restaurants in Richmond, all local workers or the city. No private individual is targeted. The investigation questions are: what written pickup rules apply, who supervises adherence, whether training exists, how delivery workers can complain safely, and whether management will provide a response. Any alleged managerial instruction is explicitly unverified. No outreach, response or policy change is counted without evidence.

## Quality and execution
- Source checks + `node --test tests/*.test.mjs`.
- Local static 24-page build and Playwright at 320, 390 and 1440px.
- Production Vercel Blob smoke creates a clearly labelled **synthetic report** and **synthetic audit event**, verifies both via the actual handlers, then deletes both. Never count synthetic cases as a real report.
- Confirm production deployment exact commit SHA, static stream page HTTP 200, `/api/dignity/routes` HTTP 200, `/api/dignity/health` indicates private storage connectivity.
- Do not expose raw operator key, private notes or full report content in pages, sitemap, public stats or journalists' briefing.
- No automatic outbound emails, public publication, human-rights finding or resolution is implemented by this release.

## Next operating integrations
Secure consented evidence attachments, differentiated staff roles and short-lived sessions replacing a single shared key, authorized organization-specific outbound from Witness sender with receipts, follow-up reminders using low-cost verified scheduled runs, public anonymized outcome summaries, and privacy-preserving trend aggregation. These are **not** claimed as shipped here.

## Primary routing authority references
- BC Human Rights Tribunal: https://www.bchrt.bc.ca/human-rights-duties/employment/ and https://www.bchrt.bc.ca/human-rights-duties/services/
- BC Ombudsperson: https://bcombudsperson.ca/complaints/what-we-do/
- BC Employment Standards: https://services.labour.gov.bc.ca/Complaints/s/employer-summary
- WorkSafeBC: https://www.worksafebc.com/en/health-safety/hazards-exposures/bullying-harassment
- Consumer Protection BC: https://www.consumerprotectionbc.ca/complaint-assistant/
