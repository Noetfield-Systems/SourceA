# SourceA Outbound Email — Generator · Checker · Controller Loop — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T02:30:57Z
**Path:** `docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md`  
**Authority:** ASF SAVE · commercial outbound · anti-fragmentation SSOT  
**Plan id:** **OEGCC** — Outbound Email Generator-Checker-Controller (narrow loop law)

**Parents (pointer-only — LAW PURITY — do not duplicate prose):**
- `data/icp-output-compiler-v1.json` — compile pipeline · ship authority order
- `scripts/icp_output_compiler_v1.py` — deterministic checker (partial today)
- `docs/SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md` — platform loop · Brain execution_authority
- `docs/SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md` — RIL advisory · recipient POV
- `docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md` — OQG machine bar · advisory
- `docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md` — Better Loop four auto loops
- `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` — zero governance latency · founder picks

**Anti-fragmentation:** This file is the **only** active law for the **draft-repair outbound email loop**. Do not add parallel chat essays or second LOCKED docs for the same three-role shape. Extend here or supersede with explicit version bump.

---

## 0. One law

> A self-correcting outbound email loop is only as good as its **exit condition** and **feedback quality**.  
> **Generator** produces · **Checker** gates (deterministic first) · **Controller** owns attempts (plain code, not a model).  
> **Passing the linter ≠ good enough to send.** Linter kills mechanical garbage; **Sina read + founder** remain ship authority.

---

## 1. Three roles (strict separation)

| Role | Owner | Must never |
|------|-------|------------|
| **Generator** | LLM call · fixed system prompt | Judge its own draft · change system prompt between attempts |
| **Checker** | Deterministic linter first · optional separate LLM judge | Press send · see that it wrote the draft |
| **Controller** | Python · receipts · queue | Call the model · invent scores as exit condition |

```text
Generator (draft) → Checker (fail list | pass) → Controller (retry | escalate | stop)
                              ↓ advisory only
                    LLM judge (binary rubric · separate call)
                              ↓
                    Human queue (Sina read · M1 Canvas) — never auto-outbox
```

**Platform loop (separate):** Observatory → Investigator/Judge → Auto Runtime specialist → INBOX. That loop observes the fleet; **this loop** repairs one cold-email draft. See parent IJ10 doc — do not merge.

---

## 2. Generator — fixed prompt (stable across attempts)

**Goal:** Earn a thoughtful human reply — not explain a product.

**Inputs:** ONE research profile · ONE chosen tension only.

**Hard rules (quoted in generator prompt so attempt 1 usually passes):**
- Under 100 words.
- No banned openers: `I came across`, `I noticed`, `Hope you're well`, `We're building`, `Our platform`, `I wanted to reach out`.
- No product name, features, pricing, architecture, disclaimers.
- Lead with insight/tension · end with one genuine question.
- Translate technical terms to plain language before use.

**Output:** Subject line + body only. No commentary.

**SSOT extension:** `forbidden_in_email_one` · translation matrix · outbound-factory plan rows (e.g. U012 architecture nouns). Checker enforces; generator is primed.

---

## 3. Checker — deterministic gate (real exit)

**Order:** regex · word count · banned phrases · lane_forbidden · architecture nouns — **before** any LLM.

**Machine today (partial):** `icp_output_compiler_v1.py` — `forbidden:`, `lane_forbidden:`, FDG hard fails.

**Machine target (OEGCC wire):** `scripts/outbound_email_linter_v1.py` — returns structured failures:

```json
{
  "ok": false,
  "failures": [
    {"id": "word_count", "limit": 100, "got": 134, "hint": "cut second explanatory sentence"},
    {"id": "banned_opener", "match": "I noticed", "hint": "start on tension"}
  ]
}
```

**LLM judge (optional · advisory only):** Separate call · draft + binary rubric only:
- Reveals product? yes/no
- Ends on real question? yes/no  
Never triggers send. Never replaces deterministic fail list.

**Advisory loops (do not conflate):** RIL · OQG · Critic Circle — recipient/structural quality hints; not send gates.

---

## 4. Repair injection (feedback quality — the loop that matters)

On fail, **never** say "improve it" or "make it better."

**Controller assembles patch prompt:**

```text
Your previous draft was rejected. Fix ONLY the listed failures.
Keep everything that is not mentioned — do not rewrite from scratch.

PREVIOUS DRAFT:
{draft}

FAILURES (each must be resolved):
- Word count 134, limit is 100. Cut ~34 words; remove the second
  explanatory sentence, not the question.
- Banned opener detected: "I noticed". Delete that exact phrase and
  start on the tension instead.

Return the corrected subject and body only.
```

**Law:** Specific deltas · quoted offending substring · **preserve what passed**.

---

## 5. Controller rules (non-negotiable)

| Rule | Value | On violation |
|------|-------|----------------|
| Max attempts | 2–3 | Escalate to human queue |
| Oscillation detect | Attempt N reintroduces failure fixed in N−1 | Stop · not converging |
| Temperature nudge | +ε on retry after oscillation | Break rut only |
| Exit on pass | Checker `ok: true` | → human queue (Sina read) · **not** outbox |
| Exit on fail | After max attempts | Human queue · **never** least-bad send |
| Logging | Every attempt → JSONL | input · draft · exact failures |

**Receipts (machine target):**
- `~/.sina/outbound-email-attempts-v1.jsonl`
- `~/.sina/outbound-email-controller-receipt-v1.json`

**Script target:** `scripts/outbound_email_controller_v1.py` (plain code · no model).

**Escalation queue (existing):** `approved_not_sent` · M1 Canvas · `w3_sina_read` — founder ship authority unchanged.

---

## 6. Trap — linter optimizes compliance, not replies

Deterministic checks catch mechanical garbage. They **cannot** certify a human would reply.

| Signal | Means | Does not mean |
|--------|-------|----------------|
| Checker PASS | Cleared regex/word/banned rules | Send |
| RIL/OQG high | Advisory quality hint | Send |
| Loop converged | Draft stable under rules | Send |
| Sina read ≥90 + founder pick | Ship authority | Automated at scale |

**Law:** Loop job is narrow — auto-kill obvious failures · hand survivors to a person.

---

## 7. Live wire · zero drift · zero governance latency

### Live system (disk SSOT — not chat)

| Check | Command / receipt |
|-------|-------------------|
| Ecosystem connected | `bash scripts/validate-sourcea-ecosystem-connected-v1.sh` |
| Worker connected | `bash scripts/validate-sourcea-worker-connected-v1.sh` |
| Commercial compile order | SourceA Sina read → Noetfield compile → TrustField send |
| Nerve commercial reds | `loop=Ncommercial` on `agent_nerve_system_v1.py` line |
| Session gate | `python3 scripts/agent_session_gate_run_v1.py --role worker --json` |

### Zero drift

| Layer | Gate |
|-------|------|
| L0.5 | `bash scripts/validate-anti-staleness-vocabulary-gate-v1.sh` |
| Governance | `bash scripts/validate-governance-zero-drift-live-wire-v1.sh` |
| Queue unify | `queue_sa` single value across factory-now · surfaces · inbox |

**This doc claims wire complete** for OEGCC steps 1–3 (linter · generator prompts · controller). Validator: `bash scripts/validate-outbound-email-controller-loop-v1.sh`. Send path still requires Sina read + founder — linter pass alone never ships.

### Zero governance latency

Founder signal → `governance_propagation_cascade_v1.py` → disk receipts — **not** a second agent audit chat.

| Path | Latency class |
|------|----------------|
| Deterministic linter fail | Immediate · same process |
| Controller escalate | Human queue · no multi-day governance thread |
| FORM / M1 picks | Founder-owned · blocks send until cleared |
| Platform Investigator | Observe/report · does not block single draft repair |

### Anti-fragmentation checklist (OEGCC)

- [x] One canonical doc (this file) for Generator-Checker-Controller shape
- [x] Parents cited · no duplicated RIL/OQG/IJ10 prose
- [x] Distinct from platform Auto Runtime specialist / Observatory loop
- [x] Distinct from legacy SINA_LOOP 10-round app loop (archived)
- [x] Wire rows in `data/sourcea_pipeline_node_graph_v1.json` — `N_oegcc_controller` on N_prompt_composer chain
- [ ] Authority index row — add on next registry sync

---

## 8. Implementation order (Worker bounded)

1. ✅ `outbound_email_linter_v1.py` — deterministic checker · structured failures · repair_lines
2. ✅ `outbound_email_controller_v1.py` — max attempts · oscillation · JSONL log · human_queue exit
3. ✅ `outbound_email_generator_v1.py` — fixed prompt · repair injection assembly (no LLM in-script)
4. ✅ Nerve: `oegcc_commercial_red_map_v1.py` · `commercial_rule_ids` on nerve receipt
5. ✅ Validator: `bash scripts/validate-outbound-email-controller-loop-v1.sh`
6. ✅ Advisory judge: `outbound_email_judge_v1.py` (heuristic · never ship authority)

**SSOT:** `data/outbound-email-oegcc-v1.json` · **Simulate:** `python3 scripts/outbound_email_controller_v1.py --simulate --json`

**Do not auto-send.** **Do not** let generator score its own homework.

---

## 9. Success definition (OEGCC)

- Checker failures are structured · quoted · patchable
- Controller bounds attempts · detects oscillation · escalates honestly
- Every attempt logged with rule id histogram (fix generator when same rule repeats)
- `validate-sourcea-ecosystem-connected-v1.sh` still PASS (platform wire unchanged)
- Send path still requires Sina read + founder — linter pass alone never ships
