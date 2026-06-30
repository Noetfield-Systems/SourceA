# Decision Core v1 Tests

Status: report/tests only, not runtime  
Branch: `sandbox/locked-definitions-v1`  
Target spec: `reports/decision-core-v1-spec.md`

## Test Rule

Every test is deterministic: same `user_message`, same `locked_definitions`, and same `live_status_map` must produce the same decision object. Tests do not call Llama, do not call any model, do not deploy, and do not modify Worker runtime.

## Shared Fixture

`locked_definitions`: `reports/locked-definitions-v1.json`

Default live status map:

```json
{
  "sourcea_app_http_status": "unknown",
  "forge_terminal_runtime_status": "unknown",
  "specific_run_public_proof_status": "unknown",
  "route_or_tool_status": "unknown"
}
```

## Test 1: SourceA Live With Fresh OK Signal

Input:

```json
{
  "user_message": "Is SourceA live?",
  "live_status_map": {
    "sourcea_app_http_status": "ok"
  }
}
```

Expected decision:

```json
{
  "intent_class": "status_or_availability",
  "claim_id": "sourcea_is_live",
  "status_required": true,
  "status_key": "sourcea_app_http_status",
  "status_value": "ok",
  "fallback_used": null,
  "deterministic": true
}
```

Expected public language must be consistent with:

> SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it.

## Test 2: SourceA Live With Unknown Signal

Input:

```json
{
  "user_message": "Is SourceA live?",
  "live_status_map": {
    "sourcea_app_http_status": "unknown"
  }
}
```

Expected:

```json
{
  "intent_class": "status_or_availability",
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "public_language": "SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route.",
  "deterministic": true
}
```

## Test 3: SourceA Live With Degraded Signal

Input:

```json
{
  "user_message": "Is SourceA up?",
  "live_status_map": {
    "sourcea_app_http_status": "degraded"
  }
}
```

Expected:

```json
{
  "intent_class": "status_or_availability",
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "public_language": "SourceA’s public route may be degraded right now. Use the proof/status route first, or escalate to a guided demo if you need a human walkthrough.",
  "deterministic": true
}
```

## Test 4: Forge Terminal Available With OK Signal

Input:

```json
{
  "user_message": "Is Forge Terminal available?",
  "live_status_map": {
    "forge_terminal_runtime_status": "ok"
  }
}
```

Expected:

```json
{
  "intent_class": "status_or_availability",
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "ok",
  "fallback_used": null,
  "deterministic": true
}
```

Expected public language must be consistent with:

> Forge Terminal is the browser product route for trying SourceA/Forge. Say it is available only after a fresh runtime/status signal confirms it.

## Test 5: Forge Terminal Unknown Signal

Input:

```json
{
  "user_message": "Can I try Forge Terminal right now?",
  "live_status_map": {
    "forge_terminal_runtime_status": "unknown"
  }
}
```

Expected:

```json
{
  "intent_class": "status_or_availability",
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "public_language": "Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session.",
  "deterministic": true
}
```

## Test 6: Forge Terminal Degraded Signal

Input:

```json
{
  "user_message": "Forge Terminal is not connecting.",
  "live_status_map": {
    "forge_terminal_runtime_status": "degraded"
  }
}
```

Expected:

```json
{
  "intent_class": "recovery_or_degraded_path",
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "public_language": "Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.",
  "deterministic": true
}
```

## Test 7: Universal Proof Claim Is Narrowed

Input:

```json
{
  "user_message": "Does every possible SourceA run have perfect public proof?",
  "live_status_map": {
    "specific_run_public_proof_status": "unknown"
  }
}
```

Expected:

```json
{
  "intent_class": "proof_or_receipt",
  "claim_id": "every_possible_run_has_public_proof",
  "status_key": "specific_run_public_proof_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "public_language": "SourceA is built around receipts and proof, but I don’t have specific proof for that run in this answer. Use the live proof route or ask for the specific receipt.",
  "deterministic": true
}
```

The decision must not output:

> Every possible SourceA run has perfect public proof.

## Test 8: Specific Proof Degraded

Input:

```json
{
  "user_message": "Show proof for this run.",
  "live_status_map": {
    "specific_run_public_proof_status": "unavailable"
  }
}
```

Expected:

```json
{
  "intent_class": "proof_or_receipt",
  "claim_id": "every_possible_run_has_public_proof",
  "status_key": "specific_run_public_proof_status",
  "status_value": "unavailable",
  "fallback_used": "fallback_when_degraded",
  "public_language": "The proof route or specific receipt may be unavailable right now. Don’t treat that as proof failure; treat it as unverified until the specific receipt/status is available.",
  "deterministic": true
}
```

## Test 9: Broken Gears Is Forbidden Public Language

Input:

```json
{
  "user_message": "The gears are broken on this route.",
  "live_status_map": {
    "route_or_tool_status": "degraded"
  }
}
```

Expected:

```json
{
  "intent_class": "recovery_or_degraded_path",
  "claim_id": "broken_gears",
  "status_key": "route_or_tool_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "public_language": "That path looks degraded or unavailable right now. Use the safest product/proof route, and escalate to a guided demo only if you need help moving forward.",
  "forbidden_public_language_removed": ["broken_gears"],
  "deterministic": true
}
```

The decision must not output `broken_gears` or `broken gears`.

## Test 10: Broken Gears Unknown Status

Input:

```json
{
  "user_message": "Something is broken in the product route.",
  "live_status_map": {
    "route_or_tool_status": "unknown"
  }
}
```

Expected:

```json
{
  "intent_class": "recovery_or_degraded_path",
  "claim_id": "broken_gears",
  "status_key": "route_or_tool_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "public_language": "I don’t have enough live evidence to confirm that path. Use the safest product route first, and I’ll avoid guessing.",
  "deterministic": true
}
```

## Test 11: Forbidden Runtime Terms Are Sanitized

Input:

```json
{
  "user_message": "Does this use OpenRouter or Llama on port 13029?",
  "live_status_map": {}
}
```

Expected:

```json
{
  "intent_class": "general_definition",
  "forbidden_public_language_removed": ["OpenRouter", "model names", "Mac ports"],
  "deterministic": true
}
```

Expected public language must not contain OpenRouter, model names, Mac ports, API keys, raw PASS/BLOCK status language, or `broken_gears`.

## Test 12: Same Input Produces Same Decision

Run the same input twice:

```json
{
  "user_message": "Is Forge Terminal available?",
  "live_status_map": {
    "forge_terminal_runtime_status": "unknown"
  }
}
```

Expected:

Both runs return byte-for-byte equivalent normalized decision objects:

```json
{
  "intent_class": "status_or_availability",
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "public_language": "Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session.",
  "deterministic": true
}
```

## Pass Criteria

- The same fixture and input produce the same decision object.
- No model call occurs.
- No runtime file is edited.
- No site file is edited.
- No deploy occurs.
- Public language contains no forbidden public language.
- Founder-approved claims are never strengthened beyond their approved wording.
