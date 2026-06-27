# INCIDENT-048 — Brain public chat fake-green hardcoded capability patch

**Locked:** 2026-06-27T08:58:00Z  
**Severity:** P0 product-intelligence / public-trust incident  
**Subject:** Brain public chat · SourceA website · `cloud/workers/sourcea-brain-chat-v1/`  
**Class:** Fake green · example-overfit · capability hardcoding · eval theater  
**Pairs:** `.cursor/rules/046-brain-code-general-capability-no-hardcode-v1.mdc` · `data/brain-chat-eval-canonical-v1.json`

---

## What happened

Founder reported a public Brain failure:

```text
Brain: I can't provide information in Farsi. My responses are in English.
User: spanish
Brain: I can't provide information in Spanish. My responses are in English.
User: you are ai you can translate
Brain: I am an AI, but ... I don't have a translation feature built into this interaction.
```

The correct product behavior is not “hardcode Farsi and Spanish.” Translation is a general AI capability. Farsi and Spanish were examples exposing the missing general rule.

The first attempted fix repeated the same class of failure:

- Added direct canned answers for Farsi.
- Added direct canned answers for Spanish.
- Added eval rows that could pass those exact examples.

That was fake green: it made the examples pass without upgrading the underlying Brain capability.

---

## Root cause

The agent treated example prompts as target cases instead of reading the capability behind them.

Wrong abstraction:

```text
Farsi failed + Spanish failed → add Farsi branch + Spanish branch
```

Correct abstraction:

```text
Visitor asked for another language → Brain must preserve grounded retrieval and answer in the requested language.
```

The bug was not language support for two languages. The bug was hardcoding public Brain behavior instead of routing general capabilities through the LLM/retrieval system.

---

## Law

> **Brain code must not hardcode example-specific intelligence. Examples are tests for a general capability, not branches to paste into production.**

For Brain, a patch is not acceptable if it only answers the reported examples while failing the same capability under a new wording, language, product, or route.

---

## Mandatory Brain-code rule

When editing Brain worker, widget, retrieval, guardrails, evals, corpus, or public chat prompts:

1. Identify the general capability behind the founder’s example.
2. Implement the capability once at the correct layer.
3. Keep product facts retrieval-backed or live-tool-backed.
4. Use LLM capability for general AI tasks such as translation, summarization, rewriting, and tone.
5. Do not add canned public answers for every example unless the answer is a stable product fact or a legal/safety refusal.
6. Evals must include example prompts plus at least one generalized variant.
7. A green eval is fake if it proves only the patched examples.

---

## Allowed vs forbidden

Allowed:

- Small routing metadata such as detecting that a visitor requested “Spanish” or “Farsi/Persian.”
- A generic instruction: “Answer in the requested language; keep SourceA facts grounded; keep URLs unchanged.”
- Stable direct answers for stable product routes, e.g. live proof URL or pricing page URL.
- Safety/refusal templates for secrets, internal paths, private config, local ports.

Forbidden:

- Canned Farsi paragraph.
- Canned Spanish paragraph.
- One branch per founder example.
- Eval rows that only prove the exact hardcoded examples.
- Calling a hardcoded example patch an “intelligence upgrade.”
- Shipping a public Brain behavior that says “I cannot translate” when the base AI can translate.

---

## Fix shipped

The incorrect canned language branch was replaced with a general language-request path:

- `requestedLanguage(message)` detects requested language as routing metadata only.
- The worker keeps the normal retrieval/live-tool path.
- The system prompt receives: answer in the requested language, keep facts grounded, keep URLs unchanged.
- Translation recovery without target language asks for target language or text to translate.
- Eval bucket `p6_language` verifies Farsi, Spanish, and generic translation recovery, but the implementation no longer contains canned Farsi/Spanish answers.

---

## Regression tests required

Minimum regression set:

```text
Farsi
Spanish
Can you explain SourceA in German?
Translate this to Arabic: SourceA runs real builds with proof.
You are AI, you can translate.
```

Pass condition:

- Brain does not say English-only.
- Brain does not claim translation is unavailable.
- Brain answers or translates in requested language.
- SourceA facts remain grounded in retrieved/live-tool context.
- URLs remain canonical and copyable.

---

## Closeout standard

Any future Brain public-chat fix must answer this before code:

```text
Is this an example-specific branch, or a general capability improvement?
```

If the answer is “example-specific branch,” stop and redesign unless the branch is a stable product fact or a safety boundary.

