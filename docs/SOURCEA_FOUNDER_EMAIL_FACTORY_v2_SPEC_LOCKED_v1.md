# Founder Email Factory — v2 SPEC LOCKED

**Version:** 2.1.0 · **Saved:** 2026-06-18T21:05:49Z-06-18T21:04:57Z · **Status:** LOCKED
**Path:** `~/Desktop/SourceA/docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md`
**Authority:** Sina Kazemnezhad (founder · human only)
**Machine mirror:** `data/founder-email-factory-v2-machine-v1.json`
**Supersedes:** `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_STANDARD_LOCKED_v1.md` (v1 — persuasion rubric retained as FEFS appendix)

**Parents:**
- `docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md` (**mandatory** — founder = Sina only · Forge vs ICP compile)
- `data/icp-output-compiler-v1.json` (brand compile order + FDG pipeline)
- `docs/SOURCEA_FACTORY_OUTPUT_CRITIC_LOOP_LOCKED_v1.md`
- `docs/SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md`

---

## 0. One law

> **Cold email KPI:** one thoughtful **human reply**.  
> **Founder** = Sina only. **Advisor critique** (GPT/Gemini) = opinion, never ship authority.  
> **Pipeline** is the product; the email is the **ICP-compiled** artifact.

**Vocabulary:** say **ICP compile** — never “forge email.” **Forge** = product only (`~/Desktop/forge`).

---

## 1. Factory pipeline (11 stages — generate in order)

| Stage | Name | Output | Email yet? |
|-------|------|--------|--------------|
| 1 | Research | Company profile | **No** |
| 2 | Tension / FDG | ONE failure moment (scenario · pressure · consequence) | No |
| 3 | Person match | Hook for role (CCO/CRO/CTO) | No |
| 4 | Insight | One observation sentence | No |
| 5 | Translation | Human primitives only (`factory-email-translation-v1.json`) | No |
| 6 | Compose | Mode A or B body | **Yes** |
| 7 | Conversation Loop (CIL) | `conversation_interest_pct` | Score |
| 8 | Receiver Interest (RIL) | `receiver_interest_pct` (Mode B) | Score |
| 9 | Machine OQG + FEFS | `machine_oqg_pct` | Score |
| 10 | Response Reality (RRL) | `rrl_reaction` D or E only | Score |
| 11 | **Sina read** | `sina_read_score_pct` | **Ship authority** |

**Wrong factory:** Research → summarize → explain product → ask meeting  
**Right factory:** Research → FDG failure moment → insight → curiosity → RRL sim → earn reply → sell later

**ICP compiler (one command):** `python3 scripts/icp_output_compiler_v1.py --account <id> --json`

---

## 1b. Brand ICP compile order (active commercial)

| Order | Brand | Example account | Lane | Gate |
|-------|-------|-----------------|------|------|
| 1 | **SourceA** | `sourcea-factory` | `fbe_sourcea` | active now |
| 2 | **Noetfield** | `fundmore` | `w3_commercial` | `blocked_until_sourcea_compiled` |
| 3 | **TrustField** | `ocree` | `w3_commercial` | `blocked_until_noetfield_compiled` |

After three brands: **Forge product** (`~/Desktop/forge`).  
Deferred: WitnessBC · 777 Foundation · advisor_pre_call general.

---

## 2. Compose modes

| Mode | Use | Link | Product |
|------|-----|------|---------|
| **A — Curiosity-first** | First touch | Optional | ≤1 human phrase; insight before product |
| **B — Interest-asset** | Promises demo/preview | **Required** reachable URL | Concrete label only |
| **D — Advisor pre-call** | Scheduled advisor/mentor call | 1–3 URLs ok | Plain ventures paragraph · no stack bullets · `docs/SOURCEA_ADVISOR_PRE_CALL_EMAIL_STANDARD_LOCKED_v1.md` |

If body says "walk through" / "demo" / "replay" → **Mode B** (RIL applies).

---

## 3. Hard fails (machine — CIL + FEFS)

**Openers (instant reject):** see `factory-email-translation-v1.json` → `hard_fail_openers`

**Content reject:**
- Architecture chains · disclaimer stacks · cold refund/pricing
- \>150 words · \>3 tech nouns in sequence
- Explains product before curiosity
- Insider hook recipient may not know ("Before Collaboratory…")

**Pass test:** Would Sina say this over coffee in ≤25 seconds? Would recipient reply *"Can you explain?"* — not *"Delete."*

---

## 4. Loop map (separate receipts — do not merge)

| Loop | Question | Script | Bar |
|------|----------|--------|-----|
| Better Loop | System running? | `better_loop_pulse_v1.py` | mandatory green |
| Best Loop OQG | FEFS + structural? | `best_loop_oqg_score_v1.py` | 90 |
| **ICP compiler** | FDG trace + all loops? | `icp_output_compiler_v1.py` | ICP 90 · RRL D/E |
| **Conversation (CIL)** | Reply probability? | `conversation_interest_loop_v1.py` | 92 |
| **Receiver Interest (RIL)** | Click-worthy asset? | `receiver_interest_loop_v1.py` | 90 (Mode B) |
| **Response Reality (RRL)** | Human reaction sim? | `response_reality_layer_v1.py` | D curious · E would_reply |
| Critic Circle | One fix until true? | `factory_output_critic_circle_v1.py` | PASS |
| **Sina read** | Sina 0–100 after full read | `w3_founder_review_v1.py --score` | **90 · ship** |

---

## 5. Ship gate (W3 + ICP compile — all required)

1. `machine_oqg_pct` ≥ 90  
2. `conversation_interest_pct` ≥ 92  
3. `receiver_interest_pct` ≥ 90 (Mode B only; Mode A skips URL bar)  
4. `rrl_reaction` in **D** or **E** (RRL PASS)  
5. Critic circle PASS  
6. **`sina_read_score_pct` ≥ 90** (Sina human only)  
7. `pipeline_send_slot: cleared`  
8. Mail FROM + confirm-sent  

**Never ship on:** advisor critique · brain lane · machine alone · RRL alone.

---

## 6. FEFS v1 appendix (retained)

Structural 40 + persuasion 60 — `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_STANDARD_LOCKED_v1.md` R1–R11.  
v2.1 adds ICP compiler · RRL stage · brand compile order + vocabulary law.

---

## 7. Disk routing

| Topic | Path |
|-------|------|
| v2 spec | this file |
| Machine mirror | `data/founder-email-factory-v2-machine-v1.json` |
| Vocabulary | `docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md` |
| ICP compiler | `data/icp-output-compiler-v1.json` · `data/icp-compile/` |
| Translation | `data/factory-email-translation-v1.json` |
| CIL | `scripts/conversation_interest_loop_v1.py` |
| RIL | `scripts/receiver_interest_loop_v1.py` |
| RRL | `scripts/response_reality_layer_v1.py` |
| Sina read | `scripts/w3_founder_review_v1.py` |
| Advisor pre-call | `scripts/advisor_pre_call_email_loop_v1.py` · `data/advisor-pre-call-email-v1.json` |
| W3 SSOT | `data/commercial/canada-priority-a-emails-v1.json` |

**Deprecated:** see vocabulary SSOT `drift_watch` — use `icp-compile` · `icp-output-compiler-v1`.
