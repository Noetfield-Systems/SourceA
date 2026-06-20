# Advisor pre-call email — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-18T18:54:21Z · **Status:** LOCKED
**Path:** `~/Desktop/SourceA/docs/SOURCEA_ADVISOR_PRE_CALL_EMAIL_STANDARD_LOCKED_v1.md`
**Authority:** Sina Kazemnezhad (founder · human only)
**Lane:** `advisor_pre_call` — **not** W3 commercial cold outbound

**Parents:**
- `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md` (compose mode D)
- `docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md` (founder = Sina only)

---

## 0. One law

> **Advisor pre-call email reduces setup on a scheduled call — it does not pitch, teach architecture, or replace the conversation.**  
> Audience: **business operators and advisors who are not AI/agentic specialists.**  
> **Ship authority:** Sina read only — not machine, not GPT/Gemini advisor critique.

---

## 1. When this lane applies

| Use | Do not use |
|-----|------------|
| Call already scheduled with advisor / entrepreneur / mentor | Cold W3 commercial (Ocree, Fundmore) |
| Relationship or warm intro exists | First-touch sales |
| Goal: signal on the call, not setup burn | Mini landing page or deck paste |

---

## 2. Structure (repeatable — APC stages)

| Stage | Block | Rule |
|-------|-------|------|
| **APC1** | Opening frame | “Before our call…” · snapshot · signal not setup |
| **APC2** | Ventures (plain) | One paragraph — what each venture **does for a customer**, not how it’s built |
| **APC3** | Live surfaces | Label + 1–3 URLs (https) |
| **APC4** | In motion (optional) | **One** plain sentence — no stack hero list |
| **APC5** | Not-a-pitch + call focus | Scale · control · fit — human words |
| **APC6** | Close | Looking forward · — Sina |
| **APC7** | Attachment (optional) | One line: optional · skip ok |

---

## 3. Human translation (business-not-AI audience)

| Never lead with | Say instead |
|-----------------|-------------|
| agentic infrastructure | related ventures / tools |
| AI governance + agentic | help teams see what happened when AI is used in daily work |
| event bus · decision agents | shared backend for routing work and keeping records straight |
| governance-first architecture | stay in control as it grows |
| Supabase / Vercel / Google Workspace (as bullets) | one backend · deploy quickly · one workspace — or omit |
| orchestration · pipeline design | how work gets routed and recorded |

**SSOT:** `data/advisor-pre-call-email-v1.json`

---

## 4. Hard fails (instant reject)

- Bullet list of architecture or stack (≥3 technical bullets)
- Forbidden jargon in opening paragraph: `agentic`, `event bus`, `decision agents`, `governance-first`, `orchestration` (untranslated)
- Reads like internal engineering doc
- No call frame when email says “before our call”
- \>220 words without Sina read override

---

## 5. Scoring loop (APC bar 90)

**Script:** `python3 scripts/advisor_pre_call_email_loop_v1.py --json`  
**Receipt:** `~/.sina/advisor-pre-call-email-loop-receipt-v1.json`

| Check | Max |
|-------|-----|
| APC frame present | 20 |
| Plain ventures paragraph | 25 |
| No jargon hard fails | 25 |
| URLs present (1–3) | 15 |
| Not-a-pitch + call focus | 15 |

**Minimum:** 90 before send · **final:** Sina read ≥90

---

## 6. Canonical reference (Richard · Alberta advisor · LOCKED example)

**Artifact:** `data/advisor-pre-call-examples/richard-alberta-v1.txt`  
**Subject:** (call-specific — not factory-scored)

This is the **compiled pass** after human-translation refine — use as pattern, not copy-paste names.

---

## 7. Repeatable loop (Observe → Improve)

1. **Observe** — read body + `advisor-pre-call-email-v1.json` rules  
2. **Analyze** — `advisor_pre_call_email_loop_v1.py` → human_clarity_pct  
3. **Improve** — one bounded fix: translate jargon · collapse bullets · shorten  
4. **Re-run** until ≥90  
5. **Sina read** — only Sina scores send  

---

## 8. Disk routing

| Topic | Path |
|-------|------|
| This law | `docs/SOURCEA_ADVISOR_PRE_CALL_EMAIL_STANDARD_LOCKED_v1.md` |
| SSOT + rules | `data/advisor-pre-call-email-v1.json` |
| Loop script | `scripts/advisor_pre_call_email_loop_v1.py` |
| Example | `data/advisor-pre-call-examples/richard-alberta-v1.txt` |
| Receipt | `~/.sina/advisor-pre-call-email-loop-receipt-v1.json` |
