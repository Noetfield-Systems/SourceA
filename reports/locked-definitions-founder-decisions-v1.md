# Locked Definitions Founder Decisions v1

Saved: 2026-06-30T15:22:00Z  
Status: draft decision packet, not live-locked  
Scope: four unresolved definition decisions only  
Source draft: `reports/locked-definitions-v1.json`

## Context

`approved_existing` items in `reports/locked-definitions-v1.json` are ratified as draft-accepted evidence, not live policy. This packet leaves commercial decisions unresolved and only structures the choices that still need founder judgment.

## Decision 1: `sourcea_is_live`

Current draft text:

> SourceA has public product routes on sourcea.app.

Current tag: `needs_founder_review`  
Status signal proposed in draft: `sourcea_app_http_status`

Source evidence:

- `data/CHATBOT_KNOWLEDGE_MANIFEST.json`: `"www": "https://sourcea.app"`
- `data/brain-public-rules-v1.json`: `"primary_ctas": [
    { "label": "Try Forge Terminal", "url": "/sourcea/forge/terminal" },
    { "label": "Live proof", "url": "/sourcea/proof/live" },
    { "label": "Pricing", "url": "/sourcea/pricing" },
    { "label": "Factories", "url": "/sourcea/factories/" }
  ]`

Why founder decision is needed:

The sources prove public routes and sourcea.app exist. They do not define the threshold for saying the broader claim `SourceA is live` instead of the narrower claim `SourceA has public product routes`.

Founder decision needed:

Define the allowed public wording and the status signal required before Brain can say `SourceA is live`.

## Decision 2: `forge_terminal_guaranteed_live_runtime`

Current draft text:

> Forge Terminal is available as a live runtime.

Current tag: `needs_founder_review`  
Status signal proposed in draft: `forge_terminal_runtime_status`

Source evidence:

- `sites/SourceA-landing/green-unified/forge/terminal.html`: `<title>Forge Terminal — live demo | SourceA</title>`
- `sites/SourceA-landing/green-unified/forge/terminal.html`: `<span class="sa-ft-status" id="sa-ft-status">Connecting…</span>`

Why founder decision is needed:

The page calls itself a live demo, but runtime availability depends on whether the demo can actually connect. The static title alone should not decide a live-runtime claim.

Founder decision needed:

Decide whether Brain can say `Forge Terminal is available` only after a fresh runtime/status signal, or whether it should default to `Forge Terminal is the browser product route`.

## Decision 3: `every_possible_run_has_public_proof`

Current draft text:

> Every possible SourceA run has perfect public proof.

Current tag: `unsafe_or_unclear`  
Status signal proposed in draft: `specific_run_public_proof_status`

Source evidence:

- No clear source found for the universal claim.
- Closest supported text from `data/brain-public-rules-v1.json`: `SourceA is an AI execution platform powered by Forge — real builds, automations, and agent workflows, with a verifiable receipt on every run.`
- Closest supported text from `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`: `> **SourceA is an AI execution platform powered by Forge — not a “proof records” product. Proof is built in; it is not the whole product.**`

Why founder decision is needed:

Existing sources support proof/receipts as built in. They do not support a universal promise that every possible run has perfect public proof.

Founder decision needed:

Approve the narrower proof wording, or provide a real source and limits for any stronger public proof claim.

## Decision 4: `broken_gears`

Current draft text:

> broken gears response ladder

Current tag: `unsafe_or_unclear`

Source evidence:

- No clear source found for the phrase `broken gears` or a named broken-gears ladder.
- Closest sourced recovery behavior from `data/brain-public-rules-v1.json`: `If user says 'you just give me records' — acknowledge pushback; reframe: Forge runs work, proof shows what ran.`
- Closest sourced status behavior from `data/brain-public-rules-v1.json`: `For status, health, live proof, and availability questions, use current live-tool/status evidence first and say when evidence is unavailable.`

Why founder decision is needed:

The requested category exists as a task requirement, but no source-backed definition was found. The draft can only cite nearby recovery/status behavior.

Founder decision needed:

Decide whether `broken gears` is a public response ladder, a private diagnostic label, or unsupported wording to remove.
