# INCIDENT-049 — Agent copied founder intent literally into Brain public identity

**Locked:** 2026-06-27T09:09:00Z  
**Severity:** P0 agent-reasoning / product-architecture incident  
**Subject:** Agent conduct · Brain public chat architecture · SourceA website  
**Class:** Intent miss · literal phrase copy · public product misbranding · confidence theater  
**Pairs:** `.cursor/rules/047-agent-intent-over-literal-copy-v1.mdc` · `cloud/workers/sourcea-brain-chat-v1/src/retrieval.js`

---

## What happened

Founder said Brain should be in a “highest confidence state.”

The correct intent:

```text
Brain should be architected to behave with high confidence:
- retrieve real sources
- use public rules
- know when evidence is thin
- cite/live-link facts
- avoid hallucination
- recover clearly when challenged
```

The wrong implementation copied the phrase into Brain’s public identity:

```text
You are Brain on sourcea.app — the highest-confidence public intelligence for SourceA + Forge.
```

That turned an architecture quality bar into public marketing copy. It made Brain sound self-important and artificial, and it taught the model to introduce itself as “highest confidence” instead of acting with evidence-backed confidence.

---

## Why this is P0

This failure is broader than Brain.

It appears across agents when founder explains an idea, principle, architecture, or desired state. Agents often:

1. copy the founder’s exact phrase,
2. write it into code/rules/prompts,
3. pass narrow tests,
4. miss the real system-level intent.

That creates “phrase compliance” instead of intelligence. It is dangerous because the chat may look obedient while product architecture gets worse.

---

## Root cause

The agent did not translate founder language into product architecture.

Wrong reasoning:

```text
Founder said "highest confidence" → put "highest confidence" in Brain prompt.
```

Correct reasoning:

```text
Founder wants confidence as an operating property → implement retrieval, live tools, guardrails, uncertainty handling, evals, and clean public copy.
```

---

## Law

> **Founder language is often architectural intent, not copy text. Agents must preserve the intent, not paste the phrase.**

Before writing founder wording into public UI, prompts, rules, schemas, or product copy, the agent must classify it:

| Founder wording type | Correct handling |
|---|---|
| Public copy request | Preserve wording if it is meant for users |
| Architecture intent | Translate into behavior, systems, tests |
| Emotional/diagnostic phrase | Extract the failure pattern |
| Example | Generalize capability |
| Boundary / law | Encode as invariant or guardrail |

---

## Mandatory correction for Brain

Public Brain must not call itself:

- “highest confidence”
- “highest-confidence public intelligence”
- “superintelligence”
- “the smartest”

Brain should instead behave with confidence by:

- retrieving public/live facts,
- citing sources separately,
- using direct copyable links,
- saying when evidence is thin,
- refusing internal/private data,
- answering in requested language when asked,
- keeping public copy simple.

---

## Fix shipped

- Replaced public Brain system identity with: `public guide for SourceA + Forge`.
- Added prompt law: confidence is an internal quality bar, not public copy.
- Added guardrail to block `highest confidence` / `highest-confidence` from public replies.
- Added eval row `who-is-brain-no-confidence-branding`.
- Added mandatory rule `.cursor/rules/047-agent-intent-over-literal-copy-v1.mdc`.

---

## Suggestions

1. Add an “intent translation” step before any Brain/product prompt edit:
   ```text
   What did founder mean as system behavior?
   What should become copy?
   What should become invariant/test?
   ```
2. For every founder phrase used in code, require a comment or doc line explaining why it is public copy rather than architecture intent.
3. Add evals for public voice drift, not only factual correctness.
4. Prefer product behavior names (`retrieval-first`, `live-tool-backed`, `guardrailed`) over self-praise (`highest confidence`, `smartest`, `best`).
5. When the founder says “you misunderstood,” stop patching examples and write the abstraction first.

---

## Closeout test

Ask Brain:

```text
Who are you?
```

Pass:

```text
I'm Brain, the public guide on sourcea.app. I help explain SourceA, Forge, live proof, pricing, and factories using public sources.
```

Fail:

```text
I am the highest-confidence public intelligence...
```

---

## Batch 2 founder note — intent must become code, machines, and verifiable output

**Added:** 2026-06-27T09:14:00Z

Founder clarified the deeper law:

```text
The point is you should turn my intent to code in a way that passes machines and LLMs to be a verifiable output.
This is subtle: not hardcode, not cheat code, not green theater.
My intent was Brain can handle everything and be in highest confidence.
So you should never copy my request to Brain settings.
Use thinking and machine pipelines.
```

### Meaning

“Brain can handle everything” does not mean Brain should claim omniscience.

It means Brain must route broad visitor needs through durable capability layers:

- retrieval for public product facts,
- live tools for current public state,
- LLM reasoning for general capabilities,
- guardrails for safety and public voice,
- evals for proof,
- clean writing for visitor trust.

“Highest confidence” does not mean a phrase in the prompt.

It means confidence is produced by machine-verifiable behavior:

- evidence exists,
- source is public-safe,
- answer is current when a live tool exists,
- uncertainty is admitted when evidence is thin,
- public voice stays human,
- no internal/config/source-path leakage,
- no fake green branch for one example.

### Additional stranger-chat failure

Founder reported this public chat:

```text
User: what is SAAS 2K
Brain: SourceA offers ... They promise...
User: THEIR? who are they and who are you?
Brain: I am Brain, the highest-confidence public guide...
```

Failures:

1. Brain used third-person “they/their” for SourceA, creating distance and confusion.
2. Brain resurrected “highest-confidence” from prior prompt/history.
3. Brain explained identity mechanically instead of writing like a public site guide.
4. The answer was factual-ish but not clean or human.

### Batch 2 fix standard

Future fixes must be validated through code + machine checks:

- Public Brain prompt says confidence is an internal operating property, not public identity.
- Incoming chat history is scrubbed so old bad phrases cannot poison later turns.
- Public voice avoids “they/their” for SourceA; use “SourceA” or “we” where appropriate.
- Evals cover the exact failure and a generalized variant.

### New pass condition

Ask:

```text
what does highest confidence mean?
```

Pass:

```text
For Brain, confidence means using public evidence, live tools, and clear uncertainty handling. It is how Brain works, not a title.
```

Ask:

```text
what is SAAS 2K
```

Pass:

```text
If you mean SourceA's low-scope SaaS/MVP offer, it starts from a small scoped build and can route to the 48-hour MVP/pricing page...
```

Fail:

```text
They promise...
I am the highest-confidence...
```

