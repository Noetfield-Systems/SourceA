# Witness BC — persistent dignity reporting and operator ledger v2
2026-11-23 | Independent, dignity-first community reporting. This release establishes real private server-side report persistence, not a mailto draft.

## Storage & trust
- A **private Vercel Blob store**, provisioned and connected only to the Witness BC Vercel project (no new Railway service and no other venture's database).
- Public `POST /api/dignity/report` validates, uploads once and reads back to confirm before returning `saved:true` and a receipt code. Each case contains a cryptographic receipt hash, private report, date and category; nothing is automatically published.
- `POST /api/dignity/status` requires ID + random access code; exposes only progress, category and approved operator-public notes. No unverified allegations in public API.
- `GET/POST /api/dignity/admin` requires an operator bearer key from the Vercel environment. Only the authenticated admin sees raw reports; operators append immutable event records. High-impact statuses require documentary URL.
- Limited IP hashing via a day-specific HMAC; no raw IP persisted; per-connection basic daily write ceiling, honeypot, field length and consent validation.
- No emailed confirmation, no background investigation, no AI fact verification or public allegation publication is claimed.
- In source, only `api/dignity/*` imports the private Blob SDK. No browser token, no personal report data in static pages or JSON-LD.

## Community workflow
Listen → Create receipt → Triage → Verify source, branch/date → Request organizational response with actual correspondence → Record receipt → Resolve/correct/publish only approved redacted summary. Right of reply must be available. Never accuse identified employees based on group identity. Similar reported experiences at other Richmond locations are not evidence about all Richmond businesses.

## Test separation
Fixtures and benchmarks are explicitly illustrative/reference content, not user submissions, client outcomes or completed Witness BC investigations. Temporary end-to-end smoke test submissions must be marked `TEST` and excluded from public cases, or removed after testing.
