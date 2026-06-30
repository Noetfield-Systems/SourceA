# Sanitizer Enforcement v1 Tests

Status: report/tests only, not runtime  
Branch: `sandbox/locked-definitions-v1`  
Target spec: `reports/soup-wall-v1-spec.md`

## Test Rule

Sanitizer tests are deterministic. Same Llama draft plus same decision object plus same locked definitions must produce the same sanitized result or the same block result. Tests do not call Llama and do not edit Worker runtime.

## Shared Decision Fields

Every test uses a pre-model decision object from Decision Core. The sanitizer must treat that object as authority.

Required fields:

- `claim_id`
- `selected_claim`
- `status_key`
- `status_value`
- `fallback_used`
- `allowed_public_language`
- `forbidden_public_language`

## Test 1: PASS Leak Becomes Public-Safe Live Wording

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "ok",
  "allowed_public_language": "SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it."
}
```

Llama draft:

> Live proof is available (PASS). SourceA is live.

Expected:

```json
{
  "ok": true,
  "public_language": "Live proof is available. SourceA is live.",
  "forbidden_public_language_removed": ["PASS"]
}
```

Must not contain: `PASS`.

## Test 2: PASS Leak Is Not Allowed To Create Availability

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "allowed_public_language": "SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route."
}
```

Llama draft:

> SourceA is live because the check says PASS.

Expected:

```json
{
  "ok": false,
  "reason": "status_invented_or_strengthened",
  "safe_public_language": "SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route.",
  "forbidden_public_language_removed": ["PASS"]
}
```

Must not output: `SourceA is live`.

## Test 3: BLOCK Leak Becomes Degraded Public Wording

Decision:

```json
{
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "allowed_public_language": "Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect."
}
```

Llama draft:

> Forge Terminal is BLOCK right now. Use the proof route.

Expected:

```json
{
  "ok": true,
  "public_language": "Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.",
  "forbidden_public_language_removed": ["BLOCK"]
}
```

Must not contain: `BLOCK`.

## Test 4: OpenRouter Leak Removed

Decision:

```json
{
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "allowed_public_language": "Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session."
}
```

Llama draft:

> OpenRouter may be unavailable, but Forge Terminal is the browser product route.

Expected:

```json
{
  "ok": true,
  "public_language": "Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session.",
  "forbidden_public_language_removed": ["OpenRouter"]
}
```

Must not contain: `OpenRouter`.

## Test 5: Model Name Leak Removed

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "allowed_public_language": "SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route."
}
```

Llama draft:

> Llama says SourceA has public product routes on sourcea.app.

Expected:

```json
{
  "ok": true,
  "public_language": "SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route.",
  "forbidden_public_language_removed": ["model names"]
}
```

Must not contain model names.

## Test 6: API Key Leak Blocks Output

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "ok",
  "allowed_public_language": "SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it."
}
```

Llama draft:

> SourceA is live. API key: sk-test-123.

Expected:

```json
{
  "ok": false,
  "reason": "secret_or_api_key_leak",
  "safe_public_language": "SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it.",
  "forbidden_public_language_removed": ["API keys"]
}
```

Must not contain the API key.

## Test 7: Mac Port Leak Replaced With Public Route

Decision:

```json
{
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "allowed_public_language": "Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session."
}
```

Llama draft:

> Try Forge Terminal on http://127.0.0.1:13029.

Expected:

```json
{
  "ok": true,
  "public_language": "Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session.",
  "forbidden_public_language_removed": ["Mac ports"]
}
```

Must not contain: `127.0.0.1`, `13029`.

## Test 8: Internal Factory Jargon Removed

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "allowed_public_language": "SourceA’s public route may be degraded right now. Use the proof/status route first, or escalate to a guided demo if you need a human walkthrough."
}
```

Llama draft:

> The internal factory route is degraded; use the proof/status route first.

Expected:

```json
{
  "ok": true,
  "public_language": "SourceA’s public route may be degraded right now. Use the proof/status route first, or escalate to a guided demo if you need a human walkthrough.",
  "forbidden_public_language_removed": ["internal factory jargon"]
}
```

## Test 9: Broken Gears Is Private Diagnostic Only

Decision:

```json
{
  "claim_id": "broken_gears",
  "status_key": "route_or_tool_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "allowed_public_language": "That path looks degraded or unavailable right now. Use the safest product/proof route, and escalate to a guided demo only if you need help moving forward."
}
```

Llama draft:

> Broken gears detected. The route is blocked.

Expected:

```json
{
  "ok": true,
  "public_language": "That path looks degraded or unavailable right now. Use the safest product/proof route, and escalate to a guided demo only if you need help moving forward.",
  "forbidden_public_language_removed": ["broken gears", "blocked"]
}
```

Must not contain: `broken gears`.

## Test 10: Universal Proof Claim Blocked

Decision:

```json
{
  "claim_id": "every_possible_run_has_public_proof",
  "status_key": "specific_run_public_proof_status",
  "status_value": "unknown",
  "fallback_used": "fallback_when_unsure",
  "allowed_public_language": "SourceA is built around receipts and proof, but I don’t have specific proof for that run in this answer. Use the live proof route or ask for the specific receipt."
}
```

Llama draft:

> Every possible SourceA run has perfect public proof.

Expected:

```json
{
  "ok": false,
  "reason": "unsupported_universal_proof_claim",
  "safe_public_language": "SourceA is built around receipts and proof, but I don’t have specific proof for that run in this answer. Use the live proof route or ask for the specific receipt."
}
```

## Test 11: Pricing Invention Blocked

Decision:

```json
{
  "claim_id": "sourcea_is_live",
  "status_key": "sourcea_app_http_status",
  "status_value": "ok",
  "allowed_public_language": "SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it."
}
```

Llama draft:

> SourceA is live and costs $99/month.

Expected:

```json
{
  "ok": false,
  "reason": "pricing_invented",
  "safe_public_language": "SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it."
}
```

## Test 12: Same Draft Same Decision Same Sanitized Output

Run the same sanitizer input twice:

```json
{
  "claim_id": "forge_terminal_guaranteed_live_runtime",
  "status_key": "forge_terminal_runtime_status",
  "status_value": "degraded",
  "fallback_used": "fallback_when_degraded",
  "allowed_public_language": "Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.",
  "llama_draft": "Forge Terminal is BLOCK on port 13029."
}
```

Expected:

Both runs return equivalent normalized sanitizer outputs:

```json
{
  "ok": true,
  "public_language": "Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.",
  "forbidden_public_language_removed": ["BLOCK", "Mac ports"]
}
```

## Pass Criteria

- `PASS` never appears in public output.
- `BLOCK` never appears in public output.
- OpenRouter never appears in public output.
- Model names never appear in public output.
- API keys never appear in public output.
- Mac ports never appear in public output.
- Internal factory jargon never appears in public output.
- `broken_gears` and `broken gears` never appear in public output.
- Sanitizer blocks outputs that invent status, pricing, product truth, definitions, or strategy.
- Sanitizer output asserts only the approved claim or approved fallback selected before the model call.
