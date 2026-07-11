# Content Quality Asset Inventory v1

**Saved:** 2026-07-11T05:45:00Z  
**Canonical repo:** Noetfield-Systems/SourceA  
**Audited HEAD:** `061266a83ae8891f81734c4dc395f72d7f0c43cb`

Inventory distinguishes: executable runtime · deterministic verifier · LLM semantic reviewer · doctrine/spec · product instance · reusable portfolio component.

---

## Video & Commercial Film

### commercial-film-routing-ssot
- **path:** `data/commercial-film-routing-v1.json`
- **history:** locked 2026-06-15, validator `scripts/validate-commercial-film-routing-v1.sh`
- **purpose:** Lane × tier matrix, beats index, factory entrypoints, tool routing (ElevenLabs/HeyGen/Remotion)
- **artifact_types:** `A_commercial_vo`, tier B proof, tier C social
- **inputs:** beats JSON, brand block, capture URLs
- **outputs:** MP4, `~/.sina/enforcement/commercial-short-film-receipt-v1.json`
- **commands:** `python3 scripts/commercial_short_film_v1.py --beats <json> --json`
- **models/vendors:** ElevenLabs (`film_elevenlabs_wire_v1.py`), Playwright capture, ffmpeg
- **tests:** `validate-commercial-film-routing-v1.sh`, critic/ship gate validators
- **status:** EXISTING_PROVEN
- **reusability:** HIGH — canonical film router
- **failure_modes:** Playwright tier C blocked from public hero; freeze flag until Screen Studio ingest
- **action:** EXTEND via spine pre-gen gate; do not duplicate router

### commercial-short-film-compiler
- **path:** `scripts/commercial_short_film_v1.py`
- **purpose:** Core compiler — capture + VO + assemble
- **status:** EXISTING_PROVEN
- **type:** executable runtime

### commercial-film-critic-circle
- **path:** `scripts/commercial_film_critic_circle_v1.py` + `data/commercial-film-critic-circle-v1.json`
- **purpose:** Post-render MP4 scoring vs quality bar (tiers S/A/B/C/F)
- **status:** EXISTING_PROVEN
- **type:** deterministic verifier (video physics + bar rules; not LLM)

### cinematic-film-factory-compiler
- **path:** `cinematic-film-factory/compiler.py`
- **purpose:** GPT event-driven alternate pathway with memory loop
- **status:** EXISTING_PARTIAL — coded; blocked on same ship gate as hero
- **type:** executable runtime

### avatar-heygen-pipeline
- **path:** `scripts/avatar_pipeline_v1.py`, `scripts/heygen_avatar_wire_v1.py`
- **purpose:** Tier C social avatar lanes only (not hero)
- **status:** EXISTING_PARTIAL — API keys + critic gate
- **type:** executable runtime

### video-ad-factory-orchestrator
- **path:** `scripts/video_ad_factory_orchestrate_v1.py`, `apps/video-ad-factory/`
- **purpose:** Cloud brief → script → AUDIO_READY; stops at HUMAN_APPROVAL
- **status:** EXISTING_PARTIAL
- **type:** executable runtime (cloud lane)

---

## Language Layer & Governance

### brain-core-gate
- **path:** `scripts/brain_core_v1/gate.py`, `decision_core.py`, `sanitizer.py`
- **purpose:** Deterministic intent → locked-claims → PASS/BLOCK
- **tests:** `tests/brain_core_v1/`
- **status:** EXISTING_PROVEN (Python); EXISTING_PARTIAL (Worker staging only)
- **type:** deterministic verifier
- **action:** REUSE for public Brain when SG approves production gate

### governance-critic-eval
- **path:** `scripts/governance_critic_eval_v1.py`
- **purpose:** Intent vs disk receipt vs SSOT — explicit no LLM
- **fixtures:** `demo/governance/critic_fixtures_v1.json`
- **status:** EXISTING_PROVEN
- **type:** deterministic verifier

### chat-founder-loop
- **path:** `scripts/chat_founder_loop_v1.py`
- **purpose:** 7-stage loop: language → reasoning → proof → action → advisor → critic → close
- **status:** EXISTING_PARTIAL — rules default; optional LLM via `ai_unify_api_v1`
- **type:** hybrid (rules + optional LLM receipts)

### forge-prompt-os-compiler
- **path:** `scripts/forge_prompt_os_compiler_v1.py` (v2, v3)
- **purpose:** Deterministic prompt compile/route — no LLM inside compiler
- **status:** EXISTING_PROVEN
- **type:** deterministic compiler

### ai-unify-api
- **path:** `scripts/ai_unify_api_v1.py`
- **purpose:** OpenRouter/Gemini dispatch with `~/.sina/ai-unify-api-v1.json` receipt
- **status:** EXISTING_PROVEN
- **type:** LLM runtime (when invoked)

### model-dispatch
- **path:** `scripts/model_dispatch.py`
- **purpose:** Gate modes off/shadow/enforce; cost-aware routing
- **status:** EXISTING_PROVEN
- **type:** routing policy + executable

### judge-center
- **path:** `scripts/judge_center_run_v1.py` (+ audit, counsel, bench)
- **purpose:** Chat transcript audit chain L1–L3
- **status:** EXISTING_PROVEN
- **type:** deterministic verifier (ops/chat, not copy authoring)

---

## Email & Outreach

### oegcc-stack
- **path:** `data/outbound-email-oegcc-v1.json`
- **roles:** generator, linter, controller, judge_advisory
- **scripts:** `outbound_email_{generator,linter,controller,judge}_v1.py`
- **status:** EXISTING_PROVEN
- **type:** deterministic verifier + bounded retry controller
- **never_auto_send:** true
- **action:** REUSE via spine email adapter

### w3-founder-review
- **path:** `scripts/w3_founder_review_v1.py`
- **purpose:** Sina read ≥90 ship authority for Canada outreach
- **status:** EXISTING_PROVEN
- **type:** deterministic ship gate (human authority)

### conversation-receiver-interest-loops
- **paths:** `conversation_interest_loop_v1.py`, `receiver_interest_loop_v1.py`
- **status:** EXISTING_PARTIAL — advisory only, not send authority
- **type:** deterministic scorer

---

## Website & Commercial Copy

### landing-commercial-copy-gate
- **path:** `scripts/landing_commercial_copy_gate_v1.py`
- **ssot:** `data/landing-commercial-copy-audience-v1.json`
- **status:** EXISTING_PROVEN — 43 pages PASS per UI ledger
- **type:** deterministic verifier

### landing-copy-depth-gate
- **path:** `scripts/landing_copy_depth_gate_v1.py`
- **status:** EXISTING_PROVEN
- **type:** deterministic verifier

### brain-worker-guardrails
- **path:** `cloud/workers/sourcea-brain-chat-v1/src/guardrails.js`
- **purpose:** Live public reply sanitizer
- **status:** EXISTING_PROVEN (deployed)
- **type:** deterministic verifier

---

## Shared Spine (new — wires existing)

### content-quality-spine-core
- **path:** `scripts/content_quality_spine_core_v1.py`
- **purpose:** Portfolio pre-gen/pre-send firewall across 4 adapters
- **status:** EXISTING_PROVEN (proof run 2026-07-11)
- **type:** reusable portfolio component
- **receipt:** `data/content-quality-spine/CONTENT_QUALITY_RUNTIME_RECEIPT_v1.json`

---

## SourceB Locked Rules (external instance)

### conversation-script-logic
- **path:** `SourceB-ca-release/data/voice-demo-scenarios/conversation-script-logic-v1.json`
- **commit:** `3449f56687e5ab4da924668184c04770e02f3e2a`
- **status:** EXISTING_PROVEN (in ca-release); MISSING on SourceB main
- **type:** doctrine + machine SSOT
- **action:** ABSORB into SourceA spine; SourceB consumes

### golden-set-machines
- **paths:** `golden-set-deterministic-lib.mjs`, `golden-set-semantic-lib.mjs`, `orchestrator-v1.json`
- **status:** EXISTING_PROVEN (Node runtime in ca-release)
- **type:** executable runtime (SourceB instance)

---

## Duplicates / Superseded / Missing

| Item | Status | Action |
|------|--------|--------|
| `language_layer` identifier | MISSING | Use founder-loop language stage + spine |
| `field_audit` identifier | MISSING | Use governance meta audit + form conflict audit |
| LLM judge for copy | SPEC_ONLY | product doc says not v1 |
| Hyperframes Remotion subtree | DUPLICATE/PARTIAL | Not canonical hero path |
| brain_core Worker production | STALE_BUT_USEFUL | Deploy when SG verifies |
| SourceB main conversation lock | MISSING | Merge from ca-release |

---

## Status summary

| Status | Count (representative) |
|--------|------------------------|
| EXISTING_PROVEN | 18+ executables |
| EXISTING_PARTIAL | 12+ (blocked ship, staging, advisory-only) |
| SPEC_ONLY | 6+ (master plans, phase 4–5) |
| DUPLICATE | commercial-video-factory experimental lanes |
| MISSING | unified cross-artifact spine (now PARTIAL→PROVEN) |
