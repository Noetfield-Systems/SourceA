# Founder Email Factory Standard — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-18T18:30:40Z · **Status:** LOCKED (FEFS appendix — superseded by v2 spec for pipeline)
**Superseded by:** `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md`  
**Vocabulary:** `docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md` — **Founder = Sina (human) only**
**Path:** `~/Desktop/SourceA/docs/SOURCEA_FOUNDER_EMAIL_FACTORY_STANDARD_LOCKED_v1.md`
**Authority:** Founder · mandatory before any W3/commercial client send
**Phase:** POST-DESIGN — stacks on Best Loop OQG · does not replace structural gates

**Parents:**
- `docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md` (OQG · machine rubric)
- `docs/SOURCEA_FACTORY_OUTPUT_CRITIC_LOOP_LOCKED_v1.md` (Critic Circle CC · improve until true ≥90%)
- `docs/SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` (FROM law)
- `1 PAGER/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` (W3 packs)

---

## 0. One law

> **Cold email has one KPI: get a human to reply.** Everything else is secondary.

Machine OQG must score **persuasion + credibility**, not only placeholders and CASL. High scores require true parameters — not structural pass alone.

| Score type | Who | What it measures |
|------------|-----|------------------|
| **Machine OQG** | `best_loop_oqg_score_v1.py` | Structural + **FEFS persuasion rubric** (this doc) |
| **Brain lane line** | inject only | **Not ship authority** |
| **Pipeline send slot** | Hub/disk workflow | **Cleared to prepare send** — **not** founder quality · **not** a person |
| **Sina read score** | **Sina (human founder) only** | Final 0–100 after reading full email — **ship authority** |

**Pipeline send slot** replaces legacy name `hub_approve` / `founder_approved` — those names mixed workflow clearance with the human founder.

---

## 1. Mandatory rules (FEFS R1–R10)

| ID | Rule | Fail signal |
|----|------|-------------|
| **R1** | Must sound human — not scraped LinkedIn | Opens with "are public on…" / company dossier |
| **R2** | One idea only — no architecture dump | evaluate→enforce→ledger→replay in one mail |
| **R3** | Start from **their** problem | Opens with "We built…" before pain |
| **R4** | Max cognitive load — ≤3s per sentence | Long compound sentences · jargon chains |
| **R5** | Never sound defensive unprompted | Stacked "not custody / not payment / advisory only" |
| **R6** | No architecture — business language | Engineering pipeline in body |
| **R7** | Curiosity > explanation | Product brochure before question |
| **R8** | No buzzword stacking | >2 of {governance, ledger, replay, dispatch, attestation, tokenization} per paragraph |
| **R9** | Respect attention — **90–140 words** (body) | >160 or <70 words |
| **R10** | End with one easy question | Hard close · pilot price in first touch |
| **R11** | Recipient sees one interest path | Empty "I can walk through" with **no** preview/demo/catalog URL |

---

## 2. Instant rejection (machine + founder)

Reject before send if any:

- Reads like GPT / whitepaper / pitch deck
- Contains 5+ technical nouns in one paragraph
- Contains multiple disclaimers (R5)
- Contains refund/deposit offer in **cold** first touch (R10)
- Duplicate hook (same event named twice)
- Primary URL unreachable when cited as proof
- **R11:** No clickable preview/demo/catalog for recipient (see `SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md`)

**Pass test:** "Would a busy founder read this in 20 seconds on an iPhone and reply?"

---

## 3. Machine rubric (W3 · 100 pts)

W3 `output_clean_pct` = **structural (40)** + **persuasion FEFS (60)**.

### 3a. Structural (40)

| Check | Max |
|-------|-----|
| copy_safety registry | 10 |
| brand_separation | 8 |
| no_placeholders | 8 |
| casl_stop + basis present | 8 |
| attach + URL reachability | 6 |

### 3b. Persuasion FEFS (60)

| Check | Max |
|-------|-----|
| human_opening (R1) | 10 |
| word_count 90–140 (R9) | 8 |
| pain_before_product (R3) | 10 |
| one_idea_no_architecture (R2,R6) | 10 |
| no_defensive_stack (R5) | 8 |
| no_cold_refund (R10) | 6 |
| curiosity_close (R7,R10) | 8 |

---

## 4. Pipeline send slot (workflow — not founder)

| Field | Values | Meaning |
|-------|--------|---------|
| `pipeline_send_slot` | `pending` · `cleared` · `blocked` | Hub/disk workflow only |
| `pipeline_send_cleared` | bool | File-level clearance to **prepare** pack |
| `pipeline_cleared_at` | ISO UTC | When slot cleared |
| `pipeline_cleared_by` | `hub_action` · `script` | **Never** labeled as founder quality score |

**SSOT:** `data/commercial/w3-canada-send-approvals-v1.json`

Send still requires: machine OQG ≥90 · **sina_read_score_pct** ≥90 (Sina human only) · Mail FROM · manual Send + confirm-sent.

---

## 5. Disk routing

| Topic | Path |
|-------|------|
| FEFS law | `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_STANDARD_LOCKED_v1.md` |
| OQG scorer | `scripts/best_loop_oqg_score_v1.py` |
| Founder review bundle | `scripts/w3_founder_review_v1.py` → `~/.sina/w3-founder-review-v1.json` |
| W3 packs | `~/.sina/outbound/w3-canada-*/body.txt` |

---

*LOCKED v1 — FEFS mandatory before send · pipeline_send_slot ≠ founder · machine scores persuasion.*
