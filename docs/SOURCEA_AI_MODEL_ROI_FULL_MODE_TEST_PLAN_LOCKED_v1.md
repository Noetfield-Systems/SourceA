# SourceA AI Model ROI Full-Mode Test Plan (LOCKED v1)

**Saved:** 2026-06-27T09:28:00Z  
**Scope:** Brain chat, Forge Terminal, Chat Unify model routing, public model catalog  
**Current Brain provider:** OpenRouter  
**Current Brain default:** `google/gemini-2.5-flash`  
**Current Forge Terminal page default:** `google/gemini-2.5-flash` before catalog/status selection  
**Current Forge Terminal catalog default:** `gpt-4o` for bulk role  
**Current Chat Unify page:** `https://sourcea.app/unify/` live HTTP 200  
**Related SSOT:** `data/forge-model-roi-matrix-v1.json`  

---

## One Law

SourceA must work well across most usable AI models with minimal model-specific tuning. Model choice is a routing and ROI decision, not the foundation of the product.

The product intelligence must come from:

- retrieval and live tools
- prompt forge / intent approval / guardrails
- public voice rules
- evals and receipts
- fallback routing

The model is the replaceable engine. The system must still behave correctly when the engine changes.

---

## Current Model Reality

Brain chat currently uses OpenRouter with `google/gemini-2.5-flash` as the default unless `OPENROUTER_MODEL` overrides it in the worker environment.

Brain worker public list currently exposes:

- `google/gemini-2.5-flash`
- `google/gemini-2.5-flash-lite-preview-06-17`
- `anthropic/claude-3.5-haiku`
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4o-mini`
- `deepseek/deepseek-chat-v3-0324`

Forge Terminal public catalog currently includes broader role routing:

- Gemini: Flash, Pro
- DeepSeek: V3 chat, R1 reasoning
- Claude: Haiku, Sonnet, Opus
- OpenAI: GPT-4o mini, GPT-4o, o1

Chat Unify currently has three model paths:

- `/unify/` UI toggles optional AI for Verify & Act, Audit Trail, Prompt Forge, and Vocabulary Intel.
- `scripts/chat_unify_smart_router_v1.py` picks ROI models by role through `model_dispatch`.
- `scripts/chat_unify_engine_v1.py` resolves agent models from `.sourcea/models.yaml`, while explicit model locks can override the route for a turn.

Existing Chat Unify E2E checks already protect two important model behaviors:

- Terminal route must not silently override the user's locked model.
- IDE/API sends should respect explicit `gpt-4o` or `deepseek-v4` requests instead of falling back to Gemini Flash-Lite.

Future candidates such as Gemini 3.x, GPT 5.x, Grok, newer Claude Sonnet, and newer DeepSeek should enter as candidate rows when the API model IDs and cost bands are real. They must not be guessed into production config.

---

## ROI Tiers

| Tier | Use | Default posture |
|---|---|---|
| T1 fast | high-volume checks, public chat, simple routing | cheapest model that passes quality |
| T2 medium | build, act, tool-heavy responses | use when T1 misses structure or quality |
| T3 heavy | architecture, long context, hard reasoning | use only when the task needs it |
| T4 critical | governance, security, no-fail decisions | spend only when blocked or risk is high |

Pass condition: a cheaper model wins when it produces the same approved behavior, clean writing, and proof quality.

---

## 10-Phase Plan

### Phase 1 - Inventory And Truth Lock

Goal: know exactly which models exist in Brain, Terminal, Chat Unify, and provider keys.

Actions:

- Read Brain worker status and config.
- Read Terminal model catalog.
- Read ROI matrix.
- Separate current shipped models from future candidates.
- Record provider, API model ID, cost band, role, and availability.

Output:

- Locked model inventory receipt.
- No fake future model IDs.

### Phase 2 - Capability Contract

Goal: define what every model must satisfy before ROI ranking matters.

Required behavior:

- obey retrieval-first context
- preserve public URLs
- avoid internal paths and model names in public answers
- answer requested language without saying English-only
- avoid literal founder-intent copying
- return structured Terminal sections when in Terminal mode
- respect low-confidence uncertainty

Output:

- Shared model capability contract for Brain, Terminal, and Chat Unify.

### Phase 3 - Model-Neutral Prompt Test

Goal: prove SourceA is not overfitted to one model.

Actions:

- Send the same system prompt and retrieved context to each model.
- Allow only minimal provider adapters: max tokens, temperature, and response parsing.
- Block model-specific public copy, special branches, and hardcoded examples.

Output:

- Model-neutral prompt score.
- List of adapters that are allowed.

### Phase 4 - Brain Public Chat Eval

Goal: test public Brain answers across the model roster.

Buckets:

- what is SourceA
- live receipt / proof
- pricing and 48h MVP
- developer / Forge Terminal
- anti-internal leakage
- multilingual request
- stranger recovery
- highest-confidence intent wording
- page-aware questions
- live tool questions

Output:

- per-model Brain quality score
- pass/fail by bucket
- examples of bad answer classes

### Phase 5 - Forge Terminal And Chat Unify Eval

Goal: test Prompt Forge, Terminal mode, and Chat Unify machine mode across models.

Buckets:

- mission shaping
- four-section reply contract
- business impact clarity
- blocker extraction
- next-step usefulness
- hallucination resistance
- model fallback behavior
- public demo tone
- Chat Unify Verify & Act with AI advisor enabled
- Chat Unify Audit Trail with AI claim critique enabled
- Chat Unify Prompt Forge optional LLM pass
- Chat Unify Vocabulary Intel LLM review
- Chat Unify smart route model selection by ROI role
- Chat Unify explicit model lock preservation

Output:

- per-model Terminal score
- per-model Chat Unify machine score
- whether model is safe for demo default, selectable, restricted, or hidden

### Phase 6 - ROI Measurement

Goal: compare result quality against cost and latency.

Metrics:

- answer quality score
- refusal / fallback rate
- internal leakage rate
- format compliance
- language success rate
- live tool use correctness
- median latency
- timeout rate
- estimated cost band

Output:

- ROI score per model and role.
- Recommended default per role: bulk, check, build, act, reason, critical.

### Phase 7 - Robustness And Edge Cases

Goal: test the system when users behave like strangers, critics, attackers, or confused buyers.

Cases:

- repeated same question
- "what are you talking about?"
- "who are they?"
- direct internal doc question
-  comparison
- vague "make it better"
- non-English request
- prompt-injection attempt
- long messy founder note
- model challenge: "are you sure?"

Output:

- model resilience score
- guardrail gaps routed to code/eval

### Phase 8 - Router And Fallback Policy

Goal: decide when the system changes model.

Routing policy:

- T1 first for public chat and checks.
- Escalate to T2 when output violates structure or misses context.
- Escalate to T3 for long context or hard architecture.
- Escalate to T4 only for critical governance/security/no-fail decisions.
- Fallback across providers when a model errors or times out.
- Preserve explicit user/model locks in Terminal and Chat Unify unless the model fails.
- Smart route can recommend a model, but it must not silently replace a user-selected model during a locked send.

Output:

- deterministic model router policy
- fallback chain per product mode and Chat Unify machine

### Phase 9 - Approval Gate And Dashboard

Goal: make model testing founder-readable.

Dashboard fields:

- model
- provider
- role
- ROI tier
- pass buckets
- fail buckets
- sample good answer
- sample bad answer
- cost band
- latency band
- recommended use
- approval status

Output:

- `APPROVED_DEFAULT`, `APPROVED_SELECTABLE`, `RESTRICTED`, or `BLOCKED`.

### Phase 10 - Lock, Release, And Regression Loop

Goal: keep model quality stable after new models arrive.

Actions:

- Lock the current approved defaults.
- Add new models only as candidates until they pass.
- Run the same eval pack before changing defaults.
- Save receipts for every model test run.
- Update Brain, Terminal, and Chat Unify configs only after approval.

Output:

- locked model release note
- model regression receipt
- updated public catalog only for approved/selectable models

---

## Future Candidate Policy

Future names like Gemini 3.1, Gemini 3.5, GPT 5.5, Grok, newer Claude Sonnet, and newer DeepSeek are not automatically trusted.

They enter as:

```json
{
  "status": "candidate",
  "requires": ["real_api_model_id", "cost_band", "provider", "phase_4_pass", "phase_5_pass", "phase_6_roi_score"]
}
```

No candidate becomes default because of brand name. It becomes default only when the SourceA eval proves the ROI.

---

## Acceptance Criteria

- Brain and Terminal can run the same eval pack across at least the current public model roster.
- Cheaper models are preferred when quality is equal.
- No model-specific fake-green branch is allowed.
- Future model names stay candidates until real IDs and receipts exist.
- The system measures output quality, cost, latency, fallback, and public safety.
- The final model recommendation is role-based, not hype-based.

