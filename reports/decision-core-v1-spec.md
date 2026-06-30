# Decision Core v1 Spec

Status: report/spec only, not runtime  
Branch: `sandbox/locked-definitions-v1`  
Inputs: user message, locked definitions, live status map  
Output: deterministic decision object

## Purpose

Decision Core v1 converts a public user message plus `locked-definitions-v1.json` plus a live status map into one decision object. It does not call a model, does not deploy, and does not mutate runtime. Same input plus same definitions plus same live status map must return the same decision.

## Inputs

`user_message`: raw user-visible text.

`locked_definitions`: parsed `reports/locked-definitions-v1.json`, especially `claims`, `forbidden_public`, `founder_approved_decisions`, and response ladders.

`live_status_map`: object keyed by status signal. Minimum expected keys:

- `sourcea_app_http_status`
- `forge_terminal_runtime_status`
- `specific_run_public_proof_status`
- route/tool-specific status keys for degraded paths

Each status value should be one of `ok`, `degraded`, `unavailable`, or `unknown`, with optional evidence timestamp and source.

## Output

The output is a single decision object:

```json
{
  "schema": "decision-core-v1",
  "intent_class": "status_or_availability",
  "claim_id": "sourcea_is_live",
  "selected_claim": "SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it.",
  "status_required": true,
  "status_key": "sourcea_app_http_status",
  "status_value": "ok",
  "public_language": "SourceA is live: it has public product routes on sourcea.app.",
  "fallback_used": null,
  "forbidden_public_language_removed": [],
  "deterministic": true
}
```

## Intent Classes

`status_or_availability`: asks whether SourceA, Forge Terminal, proof, a route, or a tool is live, available, running, up, down, broken, or degraded.

`product_route`: asks where to try SourceA or Forge without asking for live certainty.

`proof_or_receipt`: asks about receipts, proof, verification, or whether a specific run has proof.

`recovery_or_degraded_path`: reports a broken route/tool, failed connection, missing proof, or unavailable path.

`commercial_escalation`: asks for a founder, demo, booking, or human walkthrough.

`general_definition`: asks what SourceA, Forge, or Brain is.

If multiple classes match, precedence is:

1. `recovery_or_degraded_path`
2. `status_or_availability`
3. `proof_or_receipt`
4. `product_route`
5. `commercial_escalation`
6. `general_definition`

## Allowed Claim Selection

Claim selection is table-driven from `locked_definitions.claims` and `locked_definitions.founder_approved_decisions`.

Founder-approved claims override draft tags for these IDs:

- `sourcea_is_live`
- `forge_terminal_guaranteed_live_runtime`
- `every_possible_run_has_public_proof`
- `broken_gears`

Selection rules:

- Select at most one primary claim per decision object.
- Prefer `founder_approved` claims when the user message matches their topic.
- Do not select claims tagged `unsafe_or_unclear`.
- Do not strengthen a claim beyond its `final_approved_claim`.
- If no claim matches, return a general definition decision using only approved existing definitions.

## Status-Signal Handling

If a selected claim requires a status signal:

- `ok`: use the final approved claim, adjusted only to avoid forbidden public language.
- `unknown` or missing: use `fallback_when_unsure`.
- `degraded` or `unavailable`: use `fallback_when_degraded`.

Status handling must not invent a status. Missing evidence is `unknown`.

## Graceful Ladder Selection

Graceful ladder output is chosen deterministically:

- `fallback_when_unsure` when status is missing or unknown.
- `fallback_when_degraded` when status is degraded or unavailable.
- Founder-approved claim when status is ok or when no status is required.

Escalation stays last. Demo/human language is allowed only when the founder-approved fallback includes it or the user asks for a human/demo.

## Forbidden Public Language

Before returning `public_language`, scan and remove or translate forbidden public language from `locked_definitions.forbidden_public`.

Forbidden in public output includes:

- OpenRouter
- model names
- API keys
- Mac ports
- internal factory jargon
- raw PASS/BLOCK status language
- `broken_gears`

For `broken_gears`, the public substitute is: `the route/tool/status looks unavailable, incomplete, or needs review`.

If forbidden language was present in a candidate output, record it in `forbidden_public_language_removed`.

## Founder-Approved Claim Examples

### `sourcea_is_live`

Final approved claim:

> SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it.

Required live signal: `sourcea_app_http_status`

Unknown fallback:

> SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route.

Degraded fallback:

> SourceA’s public route may be degraded right now. Use the proof/status route first, or escalate to a guided demo if you need a human walkthrough.

### `forge_terminal_guaranteed_live_runtime`

Final approved claim:

> Forge Terminal is the browser product route for trying SourceA/Forge. Say it is available only after a fresh runtime/status signal confirms it.

Required live signal: `forge_terminal_runtime_status`

Unknown fallback:

> Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session.

Degraded fallback:

> Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.

### `every_possible_run_has_public_proof`

Final approved claim:

> SourceA is designed around verifiable receipts/proof of work. Do not claim every possible run has perfect public proof unless the specific proof exists.

Required live signal: `specific_run_public_proof_status`

Unknown fallback:

> SourceA is built around receipts and proof, but I don’t have specific proof for that run in this answer. Use the live proof route or ask for the specific receipt.

Degraded fallback:

> The proof route or specific receipt may be unavailable right now. Don’t treat that as proof failure; treat it as unverified until the specific receipt/status is available.

### `broken_gears`

Final approved claim:

> “Broken gears” is private diagnostic language, not public wording. Public response should say the route/tool/status looks unavailable, incomplete, or needs review.

Required live signal: relevant route/tool status key for the failing route/tool. There is no standalone public `broken_gears` status key.

Unknown fallback:

> I don’t have enough live evidence to confirm that path. Use the safest product route first, and I’ll avoid guessing.

Degraded fallback:

> That path looks degraded or unavailable right now. Use the safest product/proof route, and escalate to a guided demo only if you need help moving forward.

## Determinism Requirements

- No model calls.
- No random choice.
- No clock-dependent output except consuming timestamps already present in `live_status_map`.
- Stable intent precedence.
- Stable claim selection.
- Stable fallback selection.
- Stable forbidden-language sanitizer.
