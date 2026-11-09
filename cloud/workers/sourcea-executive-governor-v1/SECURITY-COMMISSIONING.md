# F2 security-gated commissioning: Executive Governor and Graph Studio

SourceA Issue #74 identified **unverified public ingress**. The patch adds signed, expiring, body-bound, tenant-scoped workload identities and replay protection for the mutating Governor endpoint. It does **not** create a GitHub execution permit, grant writes, or authorize a general Founder OS mission.

## Signed service identity
For each request to a v1 endpoint, the caller sends X-SourceA-Claims (base64url JSON) and X-SourceA-Signature (base64url HMAC-SHA256 of the claims string). The exact audience, method, URL path, tenant query, body SHA-256, scope, nonce, issue time and expiry are cryptographically bound. The maximum token lifetime is 90 seconds. Missing identities fail with 401; missing/short issuer secrets with 503. The Governor Durable Object atomically consumes each signed POST nonce; duplicate requests return 409 before work begins.

The signed service identity is restricted by **caller and action**, not merely by a valid HMAC. Today only `governor.run.create/read` for the explicitly admitted caller classes is allowed, and a create request must be a `webpage.repair.requested` event with `payload.task_type=webpage_repair`. Graph Studio publishes/runs are intentionally **not** authorized for existing service callers. This does not authorize new Founder mission classes or multi-tenant Company OS.

Tenant scope is explicitly configured through `SOURCEA_GRAPH_ALLOWED_ORGS`, `SOURCEA_N8N_ALLOWED_ORGS`, and `SOURCEA_FOUNDER_ALLOWED_ORGS`, all pinned to `sourcea` in both Workers' `wrangler.toml`. The current Governor has one fixed Runway tenant, so adding another org string must fail closed until a real per-tenant mapping and isolated canonical state are independently commissioned. Exact body `org`/`organization_id` and nested payload selectors must match the signed tenant. No wildcards, implicit tenant grants, or cross-org signed requests.

Governor POST nonces are now consumed via the existing DO storage `transaction()` API to atomically reject same-nonce replays. The nonce ledger remains a security projection, not a work or decision SSOT.

An application-level service identity is not an ActionPermit. Existing Governor webpage-repair task policy and Founder action/tenant/budget permits remain separately required and uncommissioned.

## Provisioning BEFORE production deployment
In Cloudflare Worker secrets, set:
- Governor SOURCEA_GRAPH_CALLER_KEY: distinct 48+ char random secret for the Graph Studio service-binding caller.
- Governor SOURCEA_N8N_CALLER_KEY: distinct 48+ char random secret for n8n.
- Governor SOURCEA_FOUNDER_CALLER_KEY: distinct 48+ char secret for Founder OS when that caller is actually commissioned.
- Graph Studio SOURCEA_GRAPH_TO_GOVERNOR_KEY: exactly the SAME value as Governor SOURCEA_GRAPH_CALLER_KEY; used only server-side.
- Graph Studio SOURCEA_N8N_CALLER_KEY and SOURCEA_FOUNDER_CALLER_KEY: caller-specific ingress secrets as intended.
- Graph Studio SOURCEA_GRAPH_ALLOWED_ORIGIN: an exact trusted HTTPS origin; otherwise cross-origin JS is denied.
- n8n SOURCEA_N8N_CALLER_KEY: same secret as the Governor n8n key; never copy it to client JS.

No secrets are present in this PR, logs, response bodies or test fixtures apart from deterministic fake values. Do not merge/deploy until every active caller has keys, signed clients, and controlled roll-out; the old Graph Studio browser app is not yet adapted for authenticated server-side API calls. Its static assets remain public, but direct /v1/* requests will be denied without trusted service identity.

Use separate staged hostnames to check auth from outside Cloudflare: unsigned POST/GET 401, wrong token 403, expired 403, body mismatch 403, wrong tenant 403, unsupported signed event 403, token replay 409, and a valid bounded webpage-repair request admitted under existing policy.

**Controlled deployment acceptance order:**
1. Inventory the actual Cloudflare account's current Worker routes, Access/WAF rules and both public `workers.dev` origins; keep production untouched until verified.
2. Set distinct caller secrets through Cloudflare's secret manager **without echoing them into GitHub or chat**, confirm matching secrets for n8n and Graph Studio's trusted server-side service binding, and rotate any reused secrets.
3. Stage Governor on a separate hostname with explicit SourceA-only tenant policy; execute negative HTTP probes from an independent network. An unsigned request that reaches the Durable Object is a release blocker.
4. Migrate the Graph Studio browser to an authenticated, server-side session/BFF transport before deploying the Graph API restrictions. Its currently shipped `apps/graph-studio-web/app.js` calls `/v1/*` directly and is **not compatible** with signed service-only ingress.
5. Run positive signed n8n/Graph service-to-service calls, replay/expiry/tenant/action negative cases and a real authorized existing `webpage_repair` request; capture sanitized HTTP status, Worker deployment SHAs and receipt.
6. Only after the identity chain passes should a separate, explicit policy decision admit a Founder GoalContract. Signing a request does not mint a `DecisionRecord`, `NAC WorkPacket`, or `Permit`.

**Current verification status:** GitHub CI (unit, source and Wrangler dry-run) passes on the candidate branch. No Cloudflare secrets, Access rules, remote deployment or live negative probe have been confirmed in this PR. Do not close Issue #74 or claim Governor authentication is live solely from CI. Inspect both custom domains and workers.dev endpoints for bypasses. Cloudflare Access/WAF still needs independent inspection.

## Negative scope
- No GitHub write credentials, executor, or production code change are enabled.
- No unrestricted browser key, wildcard CORS or authentication bypass.
- No reuse of a model provider key as an action permit.
- No claim that mere signature authentication resolves SourceA Issue #74. It is one required layer; permit binding and independent verification remain.

## Validation
Run with Node 22:
- node --test scripts/security/sourcea-scoped-ingress.test.mjs packages/n8n-nodes-sourcea/tests/shared.test.js
- PR CI: SourceA scoped Governor ingress security
