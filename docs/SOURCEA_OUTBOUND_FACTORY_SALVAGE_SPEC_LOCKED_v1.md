# Outbound Factory — Salvage Spec (LOCKED v1)

**Version:** 1.0.0 · **Saved:** 2026-06-18T21:35:40Z · **Status:** LOCKED
**Path:** `~/Desktop/SourceA/docs/SOURCEA_OUTBOUND_FACTORY_SALVAGE_SPEC_LOCKED_v1.md`
**Machine mirror:** `data/outbound-factory-salvage-spec-v1.json`
**Parents:** `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md` · `data/factory-email-translation-v1.json`

**Source:** Founder salvage of GPT/Gemini factory thread + Opus critique — wired to SourceA disk, not greenfield.

---

## 0. One law

> **Cold email KPI = one thoughtful human reply.**  
> The pipeline is the product; the email is the compiled artifact.  
> **Valid output ≠ passing rules alone** — it must reproduce human receiver behavior (**RRL D/E**) plus **Sina read ≥90**.

**Ship authority:** Sina (human) only. Agents produce ready-to-send packs; founder sends manually from Mail.

---

## 1. Four real stages (human work)

| # | Stage | Output | Email yet? |
|---|-------|--------|------------|
| 1 | **Research** | Structured profile — company, role, signals (human-confirmed) | No |
| 2 | **Tension** | ONE failure moment / operational anxiety (FDG) | No |
| 3 | **Insight** | One peer-level observation — not a pitch | No |
| 4 | **Compose** | 70–140 word body + subject | Yes |

Machine stages after compose: **CIL · RIL · OQG · RRL** — then **Sina read**.

---

## 2. Product translation matrix (mandatory)

Never ship engineering nouns. Use human primitives:

| Forbidden | Say instead |
|-----------|-------------|
| ledger | evidence / trail |
| dispatch | what the AI did |
| runtime | while the AI is working |
| attestation | proof |
| governance | control / defensibility |
| controlled issuance | proof each step was permitted |
| auditable execution trail | proof of what actually happened after the fact |

**SSOT:** `data/factory-email-translation-v1.json` → `translate` + `forbidden_in_email_one`

---

## 3. Hard fails (deterministic — immediate reject)

**Banned openers** (substring match, case-insensitive):

- i came across · i noticed · hope you're well · we're building · our platform · your company · i wanted to reach out

**Content reject:**

- Architecture chains · disclaimer stacks · cold refund/pricing
- \>150 words (target 70–100, max 140 Mode B)
- Product before curiosity / tension
- Generic skeleton: *"We've been spending time with teams… One pattern keeps appearing…"*
- \>3 engineering buzzwords stacked in one paragraph

**Subject reject:** partnership · quick question · synergy · collaboration (marketing fluff)

**Enforced by:** `scripts/best_loop_oqg_score_v1.py` (FEFS + structural) · `data/factory-email-translation-v1.json`

---

## 4. Two human tests (before Sina read)

1. **AI eraser:** Delete the company name — would you know a bot wrote this?
2. **Curiosity vs confusion:** Reader thinks *"I haven't thought about that"* — not *"I don't understand that"*

---

## 5. What is real lint vs theater

| Real (keep) | Theater (reject) |
|-------------|------------------|
| Regex banned phrases · word count · FEFS rubric | LLM self-score `insight_quality: 18/20` |
| OQG structural + persuasion | "If model says ≥92, auto-send" |
| RRL human receiver sim (D/E) | Pydantic scorecard from same model that wrote email |
| Sina read ≥90 | Advisor/GPT labeled "founder score" |

**Law:** Never let the model grade its own homework as ship authority.

---

## 6. Compile order (commercial factory)

```text
Noetfield ∥ TrustField  (parallel — active now)
SourceA                 (deferred — after commercial)
Forge product           (after SourceA)
```

**ICP compile:** `scripts/icp_output_compiler_v1.py` · accounts: `data/icp-compile/`  
**Founder bundle:** `python3 scripts/w3_founder_review_v1.py --show`

---

## 7. Explicitly deferred (do not build yet)

- Supabase `targets` / `compilation_logs` / webhook async worker — volume infra; not needed for named sends
- Proxycurl / gray-market LinkedIn scrape — API dead; credibility risk for governance vendor
- Agentic auto-send from outbox queue — founder manual send only until products have real proof
- Gemini noun-stacking regex on proper nouns — false positives on company/person names

---

## 8. Ingestion discipline (when you add research workers)

Structured JSON in, not raw HTML dumps:

```json
{
  "target_metadata": { "company_name": "", "executive_name": "", "executive_role": "" },
  "signals": {
    "financial_regulatory": "",
    "professional_dna": "",
    "technical_velocity": ""
  }
}
```

**Human confirms** signals before FDG compile — especially regulated targets (no hallucinated filings).

Canadian issuers: use SEDAR+/AIF — not SEC 10-K Item 1A alone.

---

## 9. Disk routing

| Topic | Path |
|-------|------|
| This salvage spec | `docs/SOURCEA_OUTBOUND_FACTORY_SALVAGE_SPEC_LOCKED_v1.md` |
| Machine mirror | `data/outbound-factory-salvage-spec-v1.json` |
| Email factory v2 | `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md` |
| Translation | `data/factory-email-translation-v1.json` |
| OQG linter | `scripts/best_loop_oqg_score_v1.py` |
| ICP compiler | `scripts/icp_output_compiler_v1.py` |
| RRL | `scripts/response_reality_layer_v1.py` |
| Sina read bundle | `scripts/w3_founder_review_v1.py` |
| Ready packs | `~/.sina/outbound/w3-canada-{account}/` |

---

*Salvage spec — keep linter + translation + RRL + Sina read. Drop self-score theater and volume stack until proof.*
