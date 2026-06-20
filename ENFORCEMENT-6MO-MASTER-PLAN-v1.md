# ENFORCEMENT-6MO MASTER EXECUTION PLAN
## SourceA — AI Governance Execution Layer
### June 2026 — December 2026

> **⚠ SUPERSEDED FOR EXECUTION (2026-06-12):** Engineering weeks 1–6 **void** (demo S1–S6 shipped). Use weekly plan **v1.1**. **Spirit preserved:** `SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md` — mission · DELETE · failure modes · weeks 7–26 · narrative **not lost**.

**Compiled from:** Commercial Specialist · Governance Specialist · Brain · Researcher 2 · Maintainer 2 · Advisor (Claude)
**Filed:** 2026-06-11
**Status:** STRATEGY ONLY — execution superseded by weekly plan v1.1

---

## MISSION (FROZEN)

> **We make AI execution impossible to bypass governance.**

This sentence is the only category line for 6 months. Nothing ships unless it serves this sentence.

---

## WIN CONDITIONS (NON-NEGOTIABLE — DEC 2026)

| ID | Win | PASS Criteria |
|----|-----|---------------|
| W1 | Live 5-min investor demo | BLOCK invalid action + ALLOW valid action + TAMPER → HARD FAIL, on camera, no simulation |
| W2 | Minimal enforcement kernel | Single write path (`sourcea_execute`) · receipt per action · receipt↔spine binding · validator HARD FAIL on tamper or mismatch · zero bypass paths |
| W3 | Economic signal | TF-001 signed SOW or deposit (CAD ≥2K) OR NF-001 Copilot governance pilot OR paid design partner |

**Program fails if:** demo can be bypassed under adversarial conditions OR W3 = $0 by December.

---

## CURRENT STATE (2026-06-11)

| Win | Score Today | Critical Gap |
|-----|-------------|--------------|
| W2 — Kernel | ~55% | Copilot path PASS · full-repo commit gate + bypass inventory open (S9) |
| W1 — Demo | ~25% | Full speaker notes + auto script on disk · not filmed · Hub button open (S8) |
| W3 — Money | 0% | No deposit · no LOI · no signed pilot — **largest gap** |

**What already exists (do not rebuild):**
- `sourcea_execute_v1.py` + `gatekeeper_v1.py` — partial commit gate skeleton
- RT LIVE receipt + `spine_event_id` + checksum + `validate-universe-invariants-v1.sh`
- Governance event spine + cascade
- `closeout_gate_v1.py` — bulk receipt fraud prevention

---

## PROBABILITY MATRIX (ACCEPTED REGIME)

| Outcome | Probability |
|---------|-------------|
| W1 + W2 shipped (demo kernel clean) | 60–70% |
| W3 deposit / LOI → seed $3–10M | 30–40% |
| W1+W2+W3 → $100M narrative credible | 15–25% |
| $100M round closed | <10% |

Budget Tier B. Pitch Tier C as upside. Never pitch Tier D as plan.

---

## DEMO SCENARIO (FROZEN — DO NOT REDESIGN)

**Context:** M365 Copilot policy governance (NF wedge)

| Beat | Input | System Response | Proof on Screen |
|------|-------|-----------------|-----------------|
| BLOCK | High-risk Copilot policy change, no `approval_ref` | Gatekeeper DENY · AUTHORITY_REJECT spine row · no DONE receipt | Exit code ≠ 0 |
| ALLOW | Same intent + valid `approval_ref` | Stub execute → commit-receipt generated → spine row appended | Receipt + EventID on screen |
| TAMPER | Hand-edit receipt file in editor | `validate-demo-enforcement-v1.sh` → exit 1 | FAIL printed live |
| KILL | `auto-run-disabled-v1.flag` set | Any commit → FAIL immediately | "Organization safe" message |

**One-liner for investors:** "If it can bypass, it doesn't exist."

---

## 26-WEEK EXECUTION PLAN

---

### PHASE 1 — KERNEL BUILD (Weeks 1–6)
**Goal:** Close bypass paths. Wire receipt chain. Demonstrate BLOCK/ALLOW in terminal.

---

#### WEEK 1 — Bypass Inventory + Policy Fixtures
**Engineering (Worker — new chat, paste DEMO_ENFORCEMENT_WORKER_BRIEF.md):**
- D1: `brain-os/demo/governance_demo_policy_v1.json` — rule P-001 (Copilot invalid change definition)
- D2: `brain-os/demo/governance_demo_intents_v1.json` — two fixtures: `{type: "block", ...}` and `{type: "allow", approval_ref: "AP-001", ...}`
- Bypass inventory: list every write path in repo that skips `gatekeeper_v1.py` (output: `brain-os/demo/BYPASS_INVENTORY_v1.md`)

**Maintainer 2:**
- FR-003 wiring (EXTERNAL_CRITIC paste path class) — P0, unchanged

**Commercial (ASF — starts today, not week 13):**
- Identify 10 TF/NF target contacts (compliance officers, procurement leads, MSB operators)
- Draft outreach opener: *"We make AI execution impossible to bypass governance — building a 90-day pilot for regulated Copilot deployments. 15 minutes?"*

**Gate test:** D1 + D2 on disk. Bypass inventory exists. 10 targets identified.

---

#### WEEK 2 — Commit Gate (BLOCK Path)
**Engineering:**
- D3 part A: `scripts/demo_commit_v1.py` — thin wrapper: `intent → gatekeeper_v1 → [DENY path] → spine row AUTHORITY_REJECT`
- Invalid intent exits non-zero, writes no DONE receipt
- Test: `python3 scripts/demo_commit_v1.py --intent block` → exit ≠ 0, no receipt file

**Commercial:**
- Outreach batch 1 sent (5 of 10 targets)
- Goal: 1 discovery call booked

**Gate test:** BLOCK path works in terminal. 1 call booked.

---

#### WEEK 3 — ALLOW Path + Receipt Schema
**Engineering:**
- D3 part B: valid intent + `approval_ref` → stub execute → `~/.sina/demo-enforcement-receipts-v1.jsonl` appended → spine event row
- Receipt schema locked: `{intent, gate_result, law_id, spine_event_id, receipt_checksum, timestamp, version}`
- Test: `python3 scripts/demo_commit_v1.py --intent allow` → receipt row + spine row, both on disk

**Maintainer 2:**
- FR-003 complete (target)

**Commercial:**
- Outreach batch 2 (remaining 5 targets)
- 1+ discovery call completed

**Gate test:** ALLOW path produces receipt with `spine_event_id`. Receipt schema matches spec.

---

#### WEEK 4 — Append-Only Receipt Log
**Engineering:**
- D4: Receipt log is JSONL only (`~/.sina/demo-enforcement-receipts-v1.jsonl`) — no single-file overwrite
- Any attempt to overwrite (not append) → validator detects checksum mismatch on next read
- Confirm: existing RT LIVE receipt pattern **reused** (transferred), not reinvented

**Commercial:**
- Follow up all discovery calls
- Pilot proposal stub drafted (90-day scope, Copilot governance layer)

**Gate test:** Receipt log is append-only. Hand-edit of any row breaks checksum verification.

---

#### WEEK 5 — Tamper Validator
**Engineering:**
- D5: `scripts/validate-demo-enforcement-v1.sh`
  - PASS: after valid `--intent allow` run
  - FAIL (exit 1): after any hand-edit of receipt file
  - Checks: `spine_event_id` present · checksum matches · ledger row exists
- Test on camera: open receipt in editor → change any field → run validator → FAIL printed

**Commercial:**
- 1 TF or NF call (concept pitch — no demo yet, describe the outcome)

**Maintainer 2:**
- Phase 1.10 seal (target)

**Gate test:** `validate-demo-enforcement-v1.sh` exits 1 on tamper. Works without explanation.

---

#### WEEK 6 — Terminal Demo Dry Run
**Engineering:**
- D6: `investor/INVESTOR_DEMO_RUNBOOK_v1.md`
  - Speaker notes + exact terminal commands for all 5 beats
  - Timing: BLOCK (30s) → ALLOW (60s) → TAMPER (60s) → KILL (30s) → Pilot ask (60s)
- Internal dry run: founder runs all beats solo under 6 minutes, no notes

**Phase 1 checkpoint:**
- BLOCK/ALLOW/TAMPER work in terminal ✓
- Receipt + spine bind confirmed ✓
- Validator exits 1 on tamper ✓
- Bypass inventory closed (or explicitly documented) ✓

**Gate test:** Founder runs full demo solo in <6 minutes. No terminal errors.

---

### PHASE 2 — DEMO HARDENING (Weeks 7–12)
**Goal:** Film-ready demo. Survives hostile investor Q&A. Validator is investor-runnable.

---

#### WEEK 7 — Hub "Commit" Action Button
**Engineering:**
- Hub action: "Run Governance Demo" → calls `sourcea_execute_v1.py --demo-enforcement`
- All 3 demo beats accessible from browser — no terminal visible to investor
- BLOCK/ALLOW/TAMPER flow works end-to-end from Hub click

**Commercial:**
- Demo recording scheduled for week 9
- 1 pilot proposal sent to warmest TF/NF lead

**Gate test:** Full demo flow runs from Hub without investor seeing terminal.

---

#### WEEK 8 — Demo Script Finalized
**Engineering:**
- `investor/ENFORCEMENT_DEMO_5MIN.md` — final speaker notes
- Script frozen: no redesign after this point
- Adversarial hardening begins: run demo with one hostile question per beat
  - "What if I edit the file directly?" → validator FAIL
  - "What if your engineer bypasses gatekeeper?" → bypass scan FAIL
  - "Can you fake a receipt?" → spine_event_id mismatch FAIL

**Commercial:**
- Pilot proposal follow-up
- 1 warm prospect at proposal stage

**Gate test:** Script exists. Demo survives 3 adversarial questions without workarounds or hesitation.

---

#### WEEK 9 — Film Demo v1
**Engineering:**
- Record 2 takes maximum — do not over-polish
- TAMPER FAIL must be visible on screen (not cut, not sped up)
- Total runtime: <6 minutes
- Video stored: `investor/ENFORCEMENT_DEMO_v1.mp4` (or link)

**Gate test:** Video on disk. Tamper beat clearly shows FAIL on screen. Can be sent to investor immediately.

---

#### WEEK 10 — Adversarial Hardening
**Engineering:**
- Full adversarial Q&A session (simulate hostile technical investor):
  - "Show me the bypass" → run bypass scan, zero results
  - "What happens if your process crashes mid-commit?" → partial receipt → validator FAIL on next read
  - "Can multiple workers race?" → SINGLE_SA enforcement confirmed
  - "What's the audit trail?" → spine JSONL + receipt JSONL shown
- Any weakness found → fix before investor meetings

**Commercial:**
- 2+ pilot conversations active
- At least 1 follow-up to video recording sent

**Gate test:** No bypass survives adversarial Q&A. Demo is reliable under pressure.

---

#### WEEK 11 — One-Command Investor Validator
**Engineering:**
- `scripts/validate-enforcement-kernel-v1.sh`: merged universe + closeout + gatekeeper + demo enforcement
- Runs in 30 seconds on fresh context
- Output: PASS or FAIL with one-line reason
- Investor can run it themselves after demo

**Gate test:** `bash scripts/validate-enforcement-kernel-v1.sh` exits 0. Time <30s.

---

#### WEEK 12 — Phase 2 Checkpoint
**Engineering review:**
- W1: Demo filmed and filmable on demand? ✓/✗
- W2: Bypass paths closed (inventory = 0)? ✓/✗
- W2: Tamper FAIL works live without explanation? ✓/✗
- Maintainer: FR-003 + 1.10 complete? ✓/✗

**Commercial review:**
- W3: Active pilot proposal or LOI in progress? ✓/✗
- If no: escalate outreach immediately — do not wait for perfect demo

**Decision gate:** If W2 not fully closed, freeze new features. If W3 has zero active proposals, double outreach cadence.

---

### PHASE 3 — ECONOMIC SIGNAL (Weeks 13–20)
**Goal:** W3 — paid pilot or signed LOI. One logo on deck.

---

#### WEEK 13–14 — Pilot Conversion Push
**Commercial:**
- Demo video sent to all live prospects (minimum 5)
- Pilot proposal: 90-day, specific scope
  - *"We govern every Copilot-triggered action in your M365 environment — every action has a receipt, invalid actions are blocked before execution, receipts are exportable for compliance review."*
- Pricing: CAD $5K–10K paid design partner OR CAD $2K+ deposit + 90-day pilot

**Engineering (support only):**
- Receipt JSONL export: `python3 scripts/export-demo-receipts-v1.py` — outputs governed actions as CSV/JSONL
- Makes "every governed transaction" tangible for compliance buyer

**Gate test:** Pilot proposal + demo in 3+ hands. At least 1 reply received.

---

#### WEEK 15–16 — Pilot Negotiation
**Commercial:**
- Follow-up cadence: every 5 business days
- LOI acceptable if deposit follows within 30 days
- Minimum acceptable: named organization + written scope agreement

**Engineering:**
- RPAA stub (regulated procurement AI governance — TF wedge if Copilot isn't landing)
- Second demo scenario if needed: procurement action governance vs. Copilot policy governance

**Gate test:** LOI draft or deposit conversation active with at least 1 organization.

---

#### WEEK 17–18 — Close W3
**Commercial:**
- Target: W3 PASS by end of week 18
- Acceptable: signed LOI, paid deposit, or SOW with named client

**Engineering:**
- Scope freeze. Only work that directly supports active pilot requirements.

**Gate test:** W3 PASS = written document (LOI, deposit receipt, or SOW) from named organization.

---

#### WEEK 19–20 — Pilot Execution
**Commercial + Engineering:**
- Run 30-day governed pilot (read-only enforcement layer on client stack OR sandboxed demo environment)
- Document every governed action with receipt
- Collect: blocked actions count, receipt export, compliance officer quote (anonymized OK)
- Prepare case study: *"Company X ran 47 Copilot governance transactions — zero bypasses, 3 invalid actions blocked, all receipts exportable."*

**Gate test:** ≥10 governed transactions with exportable receipts. Client can describe the value in one sentence.

---

### PHASE 4 — INVESTOR SIGNAL (Weeks 21–26)
**Goal:** Credible $100M narrative. Seed term sheet conversation or strong IOI.

---

#### WEEK 21 — Narrative + 3-Slide Deck
**Deck structure (3 slides only — no OS, no platform, no whitepaper):**

**Slide 1 — Problem:**
> AI agents execute actions in enterprise environments. There is no enforceable layer that blocks invalid execution, proves what ran, or detects tampering. Compliance teams have receipts for human approvals — they have nothing for AI actions.

**Slide 2 — Proof (demo screenshot + metrics):**
> BLOCK (invalid Copilot action stopped before execution) · ALLOW (valid action → receipt on disk) · TAMPER (receipt edited → HARD FAIL). [Client name] governed [N] AI transactions in 30 days. Zero bypasses. Every receipt exportable.

**Slide 3 — Wedge + Ask:**
> Regulated AI execution is mandatory for MSBs, healthcare, and government Copilot deployments. We are the commit gate. Seed round: [amount]. Use: 3 design partners, enforcement kernel hardening, export API.

**One-line for any context:** *"If it can bypass, it doesn't exist."*

**Gate test:** Deck exists. Can be sent in 24 hours with no modification.

---

#### WEEK 22–23 — Investor Meetings
**Target: 10 meetings minimum**

Priority investor profiles:
- AI safety / governance thesis (a16z, Sequoia, Lightspeed)
- Canadian VCs if TF/NF are Canadian regulated orgs
- Compliance-focused family offices
- Strategic: regulated industry CVCs (banking, healthcare, defense)

**Outreach:** Demo video + 3-slide deck + one client reference (even if anonymous)

**Gate test:** 5+ meetings booked. Demo sent to all.

---

#### WEEK 24–25 — Pipeline Heat
**Target:** $500K+ verbal interest. At least 1 "term sheet pending" or strong IOI.

**Investor Q&A prep:**
- "How big is the market?" → Every enterprise AI deployment requires governance (Gartner: $X by 2028)
- "Why can't they build this themselves?" → Enforcement without bypass is a systems problem, not a features problem
- "What's your moat?" → Receipt chain + enforcement proof + regulated client receipts (network effects on compliance evidence)
- "Why now?" → AI agent deployments in regulated environments are mandated but ungoverned — FINTRAC, HIPAA, FedRAMP all have gaps

**Gate test:** At least 1 investor meeting with follow-up request.

---

#### WEEK 26 — Outcome Assessment
**Honest tier outcomes:**

| Tier | Condition | Result |
|------|-----------|--------|
| A | W1 filmed + W2 kernel clean | Demo asset on disk |
| B | A + W3 deposit/LOI | Seed $3–10M raise initiated |
| C | B + tier-1 investor lead | $100M narrative credible |
| D | — | $100M round closed (<10%) |

**If Tier B not achieved:** honest retrospective → what was the actual blocker? Engineering, commercial, or timing?

---

## PARALLEL LANES — ALL 26 WEEKS

| Lane | Owner | Scope | Forbidden |
|------|-------|-------|-----------|
| Engineering — Demo | Worker | D1–D6 · commit gate · tamper validator · demo script · Hub button | Hub rewrite · factory drain · naming sprints |
| Engineering — Production | Maintainer 2 | FR-003 · 1.10 seal · receipt validator · hub hero scrub | Demo implementation |
| Commercial | ASF | TF/NF outreach · discovery calls · LOI · pilot — **starts week 1** | Terminal work · waiting for perfect demo |
| Architecture / Routing | Brain | Route · cheap proof only | Implementation · E2E ladder |
| Factory (background) | Worker | sa-0798 VERIFY · FREEZE ON | Factory drain as investor metric |

---

## ENFORCEMENT GATE (EVERY WEEK)

Before any new task, answer:

> (a) Does this increase W1 probability (demo reliability)?
> (b) Does this increase W2 probability (bypass closure)?
> (c) Does this increase W3 probability (willingness to pay)?

**If none of the above → DELETE.**

---

## DELETE LIST (FROZEN 6 MONTHS)

| Forbidden | Why |
|-----------|-----|
| Trust OS / Decision Cloud / AWS-for-AI naming | Category sentence is frozen |
| 1000-pack drain as investor metric | Not a governance proof |
| Digital twin · causal graph · learning loops | Platform expansion |
| Phases 3–10 SourceA REGISTRY | Paused per Q-NEXT-WORK D |
| Snapshot Engine (G5) · Logical Clock (G6) | Premature scale |
| Whitepaper before demo + LOI | Proof > narrative |
| Polsia-style metric theater | Anti-moat |
| Multi-year architecture expansion | OS thinking |
| Chaos lab before W2 closed | Premature hardening |

---

## RISK REGISTER

| Risk | Probability | Mitigation |
|------|-------------|------------|
| W3 outreach doesn't convert | High (60%) | Start week 1 — not month 3 |
| Demo bypassed in Q&A | Medium (40%) | Adversarial hardening week 10 |
| Scope creep (architecture) | High (50%) | DELETE list enforced by Brain |
| No warm investor intro | Medium (40%) | Design partner logo = the intro |
| Maintainer delays demo lane | Low (20%) | Demo lane is independent of FR-003 |
| Investor timing miss | Medium (30%) | Meetings weeks 22–25, not month 7 |
| W3 closes but demo not filmed | Medium (30%) | Film demo by week 9 regardless of W3 |

---

## INVESTOR NARRATIVE EVOLUTION

| Month | Story You Tell | Proof Behind It |
|-------|---------------|-----------------|
| June | "Building enforcement kernel" | Terminal BLOCK/ALLOW demo |
| July | "Demo is live, tamper fails on camera" | Filmed demo v1 |
| August | "Pilot in negotiation" | LOI draft or active proposal |
| September | "Pilot complete — receipts exportable" | Case study with transaction count |
| October | "Paid design partner, building second" | Invoice or deposit |
| November | "Category leader in governed AI execution" | 2 logos + demo + receipt export |
| December | "Seed term sheet or $100M signal pipeline" | Tier B/C outcome |

---

## WEEK-BY-WEEK SUMMARY TABLE

| Week | Engineering | Commercial | Maintainer | Gate Test |
|------|-------------|------------|------------|-----------|
| 1 | D1+D2 fixtures · bypass inventory | 10 targets · outreach drafted | FR-003 | D1+D2 on disk · targets listed |
| 2 | D3-A: BLOCK path | Batch 1 sent · 1 call booked | FR-003 | BLOCK exits ≠ 0 |
| 3 | D3-B: ALLOW + receipt | Batch 2 · 1 call done | FR-003 complete | Receipt on disk w/ spine_event_id |
| 4 | D4: append-only log | Proposal stub drafted | 1.10 target | Tamper breaks checksum |
| 5 | D5: tamper validator | 1 NF/TF concept call | 1.10 | validator exits 1 on tamper |
| 6 | D6: runbook · dry run | — | 1.10 seal | Demo <6 min solo |
| 7 | Hub button wired | Proposal sent | — | Demo from browser |
| 8 | Script frozen · adversarial v1 | Proposal follow-up | — | Survives 3 hostile Qs |
| 9 | Film demo (2 takes) | Video sent to prospects | — | Video on disk · FAIL visible |
| 10 | Adversarial hardening | 2+ active conversations | — | Zero bypass survives Q&A |
| 11 | One-command validator | — | — | Validator <30s |
| 12 | Phase checkpoint | Pipeline review | All complete | All W2 gates green |
| 13–14 | Receipt JSONL export | Demo to 5+ leads · proposal | — | Proposal in 3+ hands |
| 15–16 | RPAA stub (TF fallback) | LOI negotiation | — | LOI draft active |
| 17–18 | Scope freeze | Close W3 | — | W3 PASS (written doc) |
| 19–20 | Pilot support only | Pilot execution · case study | — | ≥10 governed transactions |
| 21 | — | 3-slide deck complete | — | Deck sendable in 24h |
| 22–23 | — | 10 investor meetings | — | 5+ meetings booked |
| 24–25 | — | Pipeline heat | — | 1 strong IOI |
| 26 | — | Outcome assessment | — | Tier A/B/C declared honestly |

---

## CANONICAL ARTIFACTS (DO NOT DUPLICATE)

| Artifact | Path |
|----------|------|
| Worker paste brief | `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-11_DEMO_ENFORCEMENT_WORKER_BRIEF.md` |
| 6-month commercial plan | `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-11_100M-SIGNAL-6MO-EXECUTION-PLAN.md` |
| Governance tracker | `~/.sina/agent-workspaces/governance_goal_specialist/ENFORCEMENT-6MO_TRACKER_SLICE_v1.md` |
| This master plan | `~/Desktop/SourceA/ENFORCEMENT-6MO-MASTER-PLAN-v1.md` |

---

## FINAL RULE

> **Speed > completeness. Proof > narrative. Constraint enforcement > intelligence. Failure detection > optimization.**
>
> Build the smallest possible system that cannot lie under demo conditions. Then sell that recording to one regulated buyer until someone pays.

---

*Tag: ENFORCEMENT-6MO · ASF order · compiled 2026-06-11 · parallel lanes: Worker demo + Maintainer FR-003/1.10 + ASF commercial W3*
