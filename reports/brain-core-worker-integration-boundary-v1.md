# Brain Core Worker Integration Boundary v1

Status: sandbox integration artifact, not deployed  
Branch: `sandbox/locked-definitions-v1`  
Runtime files edited: none

## Exact Worker Boundary

The current Brain Worker runtime is `cloud/workers/sourcea-brain-chat-v1/src/index.js`.

The future insertion point is inside `handlePost()` after the model draft is produced and before the final public response is returned:

```text
const llmResult = await chatWorkersAI(...)
const final = finalizeReply(...)
return json(request, { reply: final.reply, ... })
```

The gate must sit between the model draft and public output:

```text
live status evidence
  -> brain_core_v1 gate input
  -> run_gate(user_message, llmResult.reply, live_status)
  -> public reply must come from gate.sanitized_output
  -> raw llmResult.reply is never returned directly
```

## Adapter Contract

Future Worker adapter input:

- `user_message`: request body message text.
- `model_output`: model draft reply from Workers AI.
- `live_status`: live-tool/probe status object mapped to the Brain Core status keys.
- `definitions`: locked definitions snapshot equivalent to `reports/locked-definitions-v1.json`.

Future Worker adapter output:

- `reply`: selected from `gate.sanitized_output.public_language` or `gate.sanitized_output.safe_public_language`.
- `gate_receipt`: full `BRAIN_CORE_GATE_RESULT` receipt.
- `gate_result`: `PASS` or `BLOCK`.
- `reasons`: deterministic block reasons.

## Required Runtime Rule

Public output must never use raw model text after the gate exists. The only valid public reply source is:

1. `gate.sanitized_output.public_language` when sanitizer returns `ok: true`.
2. `gate.sanitized_output.safe_public_language` when sanitizer blocks.

## Boundary Test Plan

Runtime boundary tests should prove:

- Raw model output containing `PASS` never reaches public `reply`.
- Raw model output containing `BLOCK` never reaches public `reply`.
- Raw model output containing provider/model/API/Mac-port language never reaches public `reply`.
- Unknown live status forces `gate_result: BLOCK`.
- Degraded live status forces `gate_result: BLOCK`.
- `reply` comes from `sanitized_output`, not from `llmResult.reply`.

## Feature-Flagged Runtime Wiring Plan

When approved, add a disabled-by-default runtime flag such as `BRAIN_CORE_GATE_V1_ENABLED=false`.

Initial runtime path:

1. If flag is false, existing Worker path remains unchanged.
2. If flag is true, Worker calls the gate adapter after `chatWorkersAI()`.
3. Worker includes the gate receipt in trace metadata.
4. Worker returns only sanitized public language.
5. Deploy remains blocked until focused tests and dry probes pass.

## No-Deploy State

This artifact only identifies the boundary and future adapter contract. It does not modify Worker runtime and does not deploy.
