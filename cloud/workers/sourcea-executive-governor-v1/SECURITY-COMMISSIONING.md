# F2 security-gated commissioning: Executive Governor and Graph Studio

SourceA Issue #74 identified **unverified public ingress**. The patch adds signed, expiring, body-bound, tenant-scoped workload identities and replay protection for the mutating Governor endpoint. It does **not** create a GitHub execution permit, grant writes, or authorize a general Founder OS mission.

## Signed service identity
For each request to a v1 endpoint, the caller sends X-SourceA-Claims (base64url JSON) and X-SourceA-Signature (base64url HMAC-SHA256 of the claims string). The exact audience, method, URL path, tenant query, body SHA-256, scope, nonce, issue time and expiry are cryptographically bound. The maximum token lifetime is 90 seconds. Missing identities fail with 401; missing/short issuer secrets with 503. The Governor Durable Object atomically consumes each signed POST nonce; duplicate requests return 409 before work begins.

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

Use separate staged hostnames to check auth from outside Cloudflare: unsigned POST/GET 401, wrong token 403, expired 403, body mismatch 403, wrong tenant 403, token replay 409 and a valid bounded webpage-repair message admitted under existing policy. Inspect both custom domains and workers.dev endpoints for bypasses. Cloudflare Access/WAF still needs independent inspection.

## Negative scope
- No GitHub write credentials, executor, or production code change are enabled.
- No unrestricted browser key, wildcard CORS or authentication bypass.
- No reuse of a model provider key as an action permit.
- No claim that mere signature authentication resolves SourceA Issue #74. It is one required layer; permit binding and independent verification remain.

## Validation
Run with Node 22:
- node --test scripts/security/sourcea-scoped-ingress.test.mjs packages/n8n-nodes-sourcea/tests/shared.test.js
- PR CI: SourceA scoped Governor ingress security
