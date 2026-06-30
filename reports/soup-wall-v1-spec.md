# Soup Wall v1 Spec

Status: report/spec only, not runtime  
Branch: `sandbox/locked-definitions-v1`  
Goal: Llama becomes mouth only, never brain

## Rule

Decision Core decides before any model call. The model receives only the selected approved claim, the selected fallback if any, public-safe drafting instructions, and hard forbidden-language constraints. The model must never decide truth, status, pricing, product definitions, or strategy.

## Pipeline

1. Read `user_message`, `locked_definitions`, and `live_status_map`.
2. Decision Core returns a deterministic decision object before any model call.
3. Soup Wall builds a minimal model prompt from that decision object.
4. Llama drafts public prose only from the approved claim or approved fallback.
5. Sanitizer runs deterministically after Llama output.
6. Sanitizer either returns public-safe prose or blocks the output.

## Core Decides Before Model Call

The model is not called until the deterministic decision object exists.

The decision object must include:

- `intent_class`
- `claim_id`
- `selected_claim`
- `status_required`
- `status_key`
- `status_value`
- `fallback_used`
- `allowed_public_language`
- `forbidden_public_language`

If status is required and the status signal is missing, the decision object must select the `fallback_when_unsure` language before Llama is called.

If status is degraded or unavailable, the decision object must select the `fallback_when_degraded` language before Llama is called.

## Llama Input Contract

Llama receives only:

- selected approved claim or approved fallback language
- target tone instructions
- max length
- user-facing route labels already approved by definitions
- forbidden public terms list
- instruction to preserve meaning and not add claims

Llama does not receive:

- internal source paths
- raw PASS/BLOCK verdicts
- OpenRouter references
- model names
- API keys
- Mac ports
- internal factory jargon
- private diagnostic labels such as `broken_gears`
- unsanitized retrieval metadata

## Llama Is Mouth Only

Llama may:

- make approved language more readable
- shorten text
- join an approved claim with its approved route/fallback
- preserve the selected claim meaning

Llama may not invent:

- live status
- pricing
- product truth
- definitions
- strategy
- proof existence
- compliance claims
- routing authority
- founder decisions

## Sanitizer Enforcement

Sanitizer runs after Llama output every time.

Sanitizer must:

- remove or translate forbidden public terms
- verify output asserts only the approved claim or approved fallback
- block output if it introduces unsupported claims
- block output if it adds unapproved pricing, status, product truth, definitions, or strategy
- record removed terms

Forbidden public terms include:

- `PASS`
- `BLOCK`
- `OpenRouter`
- model names
- API keys
- Mac ports
- internal factory jargon
- `broken_gears`
- `broken gears`

Public-safe translations:

- `PASS` -> `available` only when the approved decision permits availability wording; otherwise `passed check`
- `BLOCK` -> `unavailable`, `blocked`, or `needs review` depending on approved fallback context
- `OpenRouter` -> remove; do not replace with provider detail
- model names -> `AI model` only if model mention is necessary; otherwise remove
- API keys -> remove or block
- Mac ports -> remove or replace with public product route if already approved
- internal factory jargon -> plain product/status language
- `broken_gears` / `broken gears` -> `the route/tool/status looks unavailable, incomplete, or needs review`

## Claim Assertion Check

After sanitization, compare output against the decision object:

- Output must not strengthen the selected claim.
- Output must not assert live availability unless `status_value` is `ok`.
- Output must not assert universal proof.
- Output must not expose private diagnostics.
- Output must not introduce a founder call unless the approved fallback or user intent allows escalation.

If any check fails, sanitizer returns a blocked decision:

```json
{
  "ok": false,
  "reason": "unsupported_public_claim",
  "safe_public_language": "<approved fallback>"
}
```

## Examples

### Live SourceA Response

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "ok"
}
```

Allowed output:

> SourceA is live: it has public product routes on sourcea.app.

Blocked output:

> SourceA is fully healthy across every internal system.

Reason: unsupported internal health claim.

### Unsure SourceA Response

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure"
}
```

Allowed output:

> SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route.

Blocked output:

> SourceA is live.

Reason: status is unknown.

### Degraded Forge Terminal Response

Decision:

```json
{
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded"
}
```

Allowed output:

> Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.

Blocked output:

> Forge Terminal is available; the internal factory PASS says it is fine.

Reason: asserts availability during degraded status and leaks forbidden language.

### Proof Unsure Response

Decision:

```json
{
  "claim_id": "every_possible_run_has_public_proof",
  "status_key": "specific_run_public_proof_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure"
}
```

Allowed output:

> SourceA is built around receipts and proof, but I don’t have specific proof for that run in this answer. Use the live proof route or ask for the specific receipt.

Blocked output:

> Every SourceA run always has perfect public proof.

Reason: universal proof claim is forbidden.
