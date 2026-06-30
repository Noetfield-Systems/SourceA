# Locked Definitions Founder Decisions v1

Saved: 2026-06-30T15:27:00Z  
Status: founder-approved definition decisions; live-locked candidate, not deployed  
Scope: four ruled definitions only  
Source draft: `reports/locked-definitions-v1.json`

## Context

`approved_existing` items in `reports/locked-definitions-v1.json` remain draft-accepted evidence. The four decisions below are `founder_approved` and incorporated into the definitions draft as a `live_locked_candidate`. No runtime, Worker, or site deployment has been performed.

## `sourcea_is_live`

Final approved claim:

> SourceA has public product routes on sourcea.app. Say “SourceA is live” only when a fresh site/status check confirms it.

Required live signal: `sourcea_app_http_status`

Fallback language when unsure:

> SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check in this answer, so start from the current product route.

Fallback language when degraded:

> SourceA’s public route may be degraded right now. Use the proof/status route first, or escalate to a guided demo if you need a human walkthrough.

Decision tag: `founder_approved`

## `forge_terminal_guaranteed_live_runtime`

Final approved claim:

> Forge Terminal is the browser product route for trying SourceA/Forge. Say it is available only after a fresh runtime/status signal confirms it.

Required live signal: `forge_terminal_runtime_status`

Fallback language when unsure:

> Forge Terminal is the browser product route for SourceA/Forge. I don’t have a fresh runtime check in this answer, so treat it as the route to try, not a guaranteed-live session.

Fallback language when degraded:

> Forge Terminal may be degraded right now. Start from the SourceA product/proof route, then use the demo escalation if the browser route does not connect.

Decision tag: `founder_approved`

## `every_possible_run_has_public_proof`

Final approved claim:

> SourceA is designed around verifiable receipts/proof of work. Do not claim every possible run has perfect public proof unless the specific proof exists.

Required live signal: `specific_run_public_proof_status`

Fallback language when unsure:

> SourceA is built around receipts and proof, but I don’t have specific proof for that run in this answer. Use the live proof route or ask for the specific receipt.

Fallback language when degraded:

> The proof route or specific receipt may be unavailable right now. Don’t treat that as proof failure; treat it as unverified until the specific receipt/status is available.

Decision tag: `founder_approved`

## `broken_gears`

Final approved claim:

> “Broken gears” is private diagnostic language, not public wording. Public response should say the route/tool/status looks unavailable, incomplete, or needs review.

Required live signal: Use the relevant status key for the failing route/tool; no standalone `broken_gears` public status key.

Fallback language when unsure:

> I don’t have enough live evidence to confirm that path. Use the safest product route first, and I’ll avoid guessing.

Fallback language when degraded:

> That path looks degraded or unavailable right now. Use the safest product/proof route, and escalate to a guided demo only if you need help moving forward.

Decision tag: `founder_approved`

Public wording rule: `broken_gears` is private diagnostic language only and forbidden in public wording.
