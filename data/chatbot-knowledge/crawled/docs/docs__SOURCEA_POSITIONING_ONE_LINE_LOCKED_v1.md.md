---
lane: core
updated: 2026-06-30T12:43:40Z
source_path: docs/SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md
public: true
---

# SourceA Positioning — One Line (LOCKED v1)

**Saved:** 2026-06-25T05:07:30Z  
**Version:** 1.0 — LOCKED  
**Machine SSOT:** `SourceA-landing/green-unified/data/sourcea-positioning-v1.json` (schema `sourcea-positioning-v1` v3.1.0)  
**Brain prompt:** `cloud/workers/sourcea-brain-chat-v1` · `brain_prompt_version` 2.0.0

---

## One law

> **SourceA is an AI execution platform powered by Forge — not a “proof records” product. Proof is built in; it is not the whole product.**

---

## The one line (canonical)

**SourceA is an AI execution platform powered by Forge — it runs real builds, automations, agent workflows, and controlled development pipelines for founders and agencies.**

Use this verbatim when a stranger asks “What is SourceA?” — in Brain, sales copy, and founder answers.

---

## What SourceA is NOT

| Wrong (forbidden as primary pitch) | Right |
|-----------------------------------|--------|
| “AI proof / verification / audit trail software” | **Execution platform** — Forge runs the work |
| “We just give you records” | **Forge executes**; proof shows what ran and why |
| “ChatGPT wrapper for agencies” | **Controlled agent workflows** with quality gate + execute |
| Lead with **$1,500–$5,000** before value | **Problem → solution → example → value → price** |

---

## Product stack (stranger-safe)

```
Founder / agency goal
  → Forge Terminal (execution desk)
  → Prompt forge → agents → quality gate → execute (Cursor / cloud)
  → Proof & receipts (built in — not sold alone)
```

| Surface | Role | URL |
|---------|------|-----|
| **Forge Terminal** (product) | Mac founder desk + public browser demo | Mac `:13029` · public `/sourcea/forge/terminal` |
| **Brain** (site chat) | Positioning + routing strangers | Every landing page with `sourcea-chatbot.js` |
| **Proof** (feature) | Show clients what ran and passed quality | Case studies · pureflow.sourcea.app |

---

## Forge vs proof

| Layer | What it is |
|-------|------------|
| **Forge** | Execution — builds, automations, agents, IDE desk |
| **Proof** | Feature — tracked runs, validation, client-ready audit trail |

**Chain:** Prompt → Forge execution → Agents → Quality gate → Proof → Client delivery → Retention

---

## Brain conversation rules (public chatbot)

Wired in `cloud/workers/sourcea-brain-chat-v1/src/index.js` · mirrored in `scripts/sourcea_brain_chat_v1.py`.

1. **Answer the actual question first** — match energy; no generic sales blob.
2. **Never open with dollar amounts** — pricing only when asked or after value is clear.
3. **Max one** `cal.com/sourcea/proof-demo` link per reply unless they ask to book.
4. **IDE / cloud questions** — lead with Forge Terminal (browser demo + Mac desk); never open with “We don’t offer.”
5. **“You just give me records??”** — acknowledge pushback; reframe: Forge runs work, proof is how you show it.
6. **Lists / examples** — three concrete bullets (agency QBR, content engine, dev/automation) — no abstract fluff.
7. **Never mention** OpenRouter, models, API keys, PASS/BLOCK, factories, or governance jargon to strangers.

**E2E proof:** `bash scripts/validate-sourcea-brain-chat-v1.sh` (what-is · IDE cloud · records recovery)

---

## External headline (marketing)

> Turn AI into real production work — builds, automations, and agent workflows through Forge, with proof built in.

---

## Outcome bullets (buyer language)

- Run real AI work (not just chat)
- Ship client deliverables faster
- Automate research, content, and dev tasks
- Show clients what ran and why (proof built in)

---

## CTAs (priority order for strangers)

1. Try Forge Terminal — `/sourcea/forge/terminal`
2. See live receipt — `/sourcea/proof/live`
3. Proof quiz / sandbox — self-serve verify
4. Offer — `/sourcea/offer`
5. Pricing — `/sourcea/pricing` (after value)
6. Talk to a human — `https://cal.com/sourcea/proof-demo` (optional escalation only)
7. Email — `hello@sourcea.app`

---

## Incident that locked this (2026-06-25)

Stranger chat on [sourcea.app/sourcea/forge/](https://sourcea.app/sourcea/forge/) exposed:

- Brain sold “verification / records” instead of execution
- Price appeared before value
- “Do you have IDE cloud?” answered with flat **No** instead of Forge Terminal
- User objection **“You just give me records??”** was not recovered

**Fix:** Positioning v3.1.0 logged + Brain system prompt v2.0.0 deployed to Cloudflare worker.

---

## Do not change without

1. Update `sourcea-positioning-v1.json` first (machine SSOT).
2. Update Brain worker + `sourcea_brain_chat_v1.py` in same commit/ship.
3. Re-run `validate-sourcea-brain-chat-v1.sh`.
4. Founder approval for one-line or proof-is-not-product changes.
