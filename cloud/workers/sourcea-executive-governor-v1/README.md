# sourcea-executive-governor-v1

Cloudflare Worker + Durable Object for governed Executive Mesh ingress and follow-through.

## Runtime boundaries

- Executive Mesh makes deterministic policy and routing decisions.
- The Governor creates one Runway Goal only for the registered WEBPAGE_REPAIR decision class.
- Runway's existing Goal Pursuit Workflow is the only executor; it owns retries, staging approval waits, execution and Goal state.
- ExecutiveFollowupWorkflow is a separate durable observer. It polls the canonical Runway Goal, verifies terminal evidence and closes the Executive commitment only after an independently verified artifact.
- This Worker does not approve staging, merge, deploy production, send external communications, move money, change DNS or modify governance.
- HTTP 200 means an Executive run reached a terminal state. HTTP 202 means the Goal was created and the Executive commitment remains OPEN / AWAITING_EXECUTION.

## HTTP routes

- GET /health — non-secret configuration status only.
- POST /v1/executive/runs?org=sourcea — authenticated, idempotent event ingress. Returns 202 AWAITING_EXECUTION until the real Goal is terminal; never treats Goal creation or HTTP 200 as task completion.
- GET /v1/executive/runs/{run_id} — read the durable Executive run.
- POST /internal/executive/runs/{run_id}/reconcile — internal-only completion reconciliation; requires the internal bearer token.

## Required secrets

Provision only through Cloudflare Worker secrets (never in Wrangler vars, source, Git or receipts):

- EXECUTIVE_INGRESS_TOKEN — caller token for the event-ingress route; n8n's SourceA API credential must use the same value.
- EXECUTIVE_INTERNAL_TOKEN — private token used by the Durable Workflow to call its Governor's internal reconcile route.
- SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY — canonical evidence sink access.

The n8n custom node SourceA Governor requires the SourceA API credential. Store the base URL and ingress token in n8n's encrypted credential store, not in workflow JSON.

## Completion contract

A Goal may be READY, RUNNING, WAITING_FOR_APPROVAL, BLOCKED, SLEEPING or another non-terminal state. These states keep the commitment open.

Executive acceptance requires all of the following from the canonical Runway Goal:

1. status equals PASSED.
2. work_packet_terminal equals ACCEPTED_ARTIFACT.
3. A non-empty receipt_id.
4. A valid SHA-256 receipt_hash.
5. Every required acceptance criterion has PASS.
6. POST /v1/goals/{goal_id}/verify returns passed=true for that same receipt.

PARTIAL_PASS creates a Founder Decision Packet. Failed, cancelled, budget-exhausted and time-exhausted Goals close as bounded failures. Missing, malformed, stale or conflicting evidence fails closed as an incident.

## Tests

From this directory:

    npm test

The test suite exercises the Runway outcome classifier. The SourceA n8n adapter has its own Node test suite:

    node --test packages/n8n-nodes-sourcea/tests/*.test.js

## Commissioning

The Worker and durable follow-up Workflow are implementation artifacts only until separately commissioned. Current Runtime Reality is BLOCKED_NOT_COMMISSIONED; autonomous production mutations remain HOLD. Do not deploy, schedule, merge or promote from this change. First commissioning requires provisioned secrets, a cold-checkout build, CI evidence, an authenticated staging request, a real Goal lifecycle reaching an accepted artifact, verified receipt custody, and separate founder/SG authorization to lift HOLD.

## Deployment (after commissioning approval only)

    npx wrangler@4 deploy

Required secrets are set with wrangler secret put NAME; do not print or commit their values.
