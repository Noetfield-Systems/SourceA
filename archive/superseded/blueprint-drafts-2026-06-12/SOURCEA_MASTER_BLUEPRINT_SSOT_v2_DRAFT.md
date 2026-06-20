# SOURCEA MASTER BLUEPRINT — v2 DRAFT (NOT LAW)

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** DRAFT · **VOID as LOCKED** — mistakenly superseded v1 plans · demoted ASF order 2026-06-12
**Canonical SSOT (v1):** `brain-os/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` · `ENFORCEMENT-6MO-MASTER-PLAN-v1.md` · `ENFORCEMENT-6MO-VC-ROADMAP-v1.md`
**Written:** 2026-06-12 | **Authority:** Claude + GPT + Gemini convergence — **inform only**
**Do not cite as law** until ASF FIVE-STEP LOCK pick

---

# PART 0 — WHAT SOURCEA IS

## 0.1 External Identity (use with investors, customers, partners)

> **A governance and execution infrastructure that provides deterministic auditability and policy enforcement for AI-assisted operations.**

One sentence. Use it everywhere. Nothing else publicly.

## 0.2 Internal Identity (engineering and architecture)

> **A governance runtime with event sourcing characteristics.**

Not: AI Operating System. Not: Decision Cloud. Not: Trust OS. Not: Governance OS. Not: Control Plane. Those labels are archived. This is the label.

## 0.3 The One Commercial Sentence

> **"Every AI action your team takes is logged, signed, and auditable. If an agent does something wrong — wrong decision, wrong output, wrong step — you have a cryptographic receipt proving exactly what happened, who authorized it, and what law it violated. You cannot get that from ChatGPT, Copilot, or any wrapper. You get it from us in 30 days or we refund the deposit."**

This sentence drives: the website, the Zoom demo, the outreach email, the pricing, the pilot agreement, and the pitch deck. If any communication cannot be traced back to this sentence, cut it.

## 0.4 The One Question Every Decision Must Pass

> **What expensive problem disappears within 30 days if a customer pays SourceA CAD $2,000?**

Answer: Unauditable AI actions. Uncontrolled agent behavior. No receipt = no accountability = regulatory and operational liability. SourceA closes that gap deterministically.

---

# PART 1 — GOLDEN RULES (LOCKED, NEVER TOUCH)

## 1.1 Architecture Golden Rule

```
State is canonical.
Events are history.
Graph is intelligence.
Projections are disposable.
Validators are authority.
Router is governor.
Workers are replaceable.
```

Source: `brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md`

## 1.2 Hub Law

Hub = projection only. Delete Hub → Rebuild → Same Hub. Hub is never state. Hub is never authority. Agents read form JSON before reading hub.

## 1.3 Read Order Law (MANDATORY for all agents)

```
Form JSON (~/.sina/live-founder-decision-form-v1.json)
↓
PROGRAM_PROGRESS.json
↓
SESSION_LOG
↓
Hub projection (last, advisory only)
```

Violating this read order is an INCIDENT-027 class event.

## 1.4 External Critic Law (FR-003)

GPT, Gemini, Claude, any external model paste = EXTERNAL_CRITIC class. Report only. Never auto-apply. ASF FIVE-STEP adopt row required before any build order executes.

## 1.5 No Auto-Run Law

No Cursor AUTO-RUN. No auto-prompt. No agent self-scheduling without ASF explicit pick. Kill flag is permanent unless ASF issues a new FIVE-STEP pick.

---

# PART 2 — CURRENT DISK STATE (2026-06-12)

## 2.1 GREEN — Proven, Receipt-Backed

| Component | Proof | Location |
|-----------|-------|----------|
| Governance Event Spine v1.1 (15 fields) | `validate-governance-event-spine-v1.sh` PASS | `~/.sina/governance-event-spine-v1.jsonl` |
| RT LIVE gate | hub_sync 678ms · cascade 15.9s · PASS | `~/.sina/rt-live-gate-receipt-v1.json` |
| Receipt ↔ Spine binding | `spine_event_id` on receipt · checksum confirmed | `~/.sina/governance-event-spine-v1.jsonl` |
| Golden Rule | Locked in law/ | `brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md` |
| Knowledge/Reference Graph | Shipped | `scripts/governance_reference_graph_v1.py` |
| Universe invariants | `validate-universe-invariants-v1.sh` PASS | `~/.sina/` |
| Maintainer scan P0 | `validate-maintainer-scan-p0-v1.sh` PASS | `~/.sina/` |
| Session gate | ASG-20260612-b303c81f PASS | `~/.sina/` |
| L1 Judge audit | 6/6 PAST_STALE_ONLY (healthy) | `~/.sina/judge-center/` |
| INCIDENT-027 structural fix | read-order LOCKED · hub P0 gate check | `scripts/founder_p0_next_action_v1.py` |
| INCIDENT-029 fix | Scratch canvas deleted · M1 Canvas = official office | `brain-os/incidents/` |
| Form v2 | Filled 2026-06-11 · 6 picks locked | `~/.sina/live-founder-decision-form-v1.json` |
| Canonical/Runtime split | Two projection files logged | `agent-control-panel/command-data-canonical.json` · `command-data-runtime.json` |

## 2.2 AMBER — Shipped But Gap Remaining

| Component | Current State | Gap |
|-----------|--------------|-----|
| W2 Enforcement kernel | ~55% | Receipt validator on read MISSING — forged receipt not caught |
| W1 Demo | ~25% | Kernel shipped (S1-S6 PASS) · Hub button open · Not filmed |
| Hub disposable | FAIL (expected) | Hub still embeds volatile state · P1 materializer fix needed |
| G3 propagation | Partial | LAW_CHANGED → queue → selective materializer not end-to-end |
| Voyage AI embeddings | hash_local fallback | Key added — hub restart needed to activate |

## 2.3 RED — Not Started

| Component | State | Blocker |
|-----------|-------|---------|
| W3 Revenue | $0 · 0 LOIs · 0 deposits | ASF must initiate — no Worker ships this |
| Receipt validator on read | Not built | Highest engineering P0 |
| Append-only receipt log | Not built | Single-file overwrite = tamper gap |
| L2 Counsel + L3 Bench (auto-run) | Scripts shipped · not activated | Q-JUDGE-STACK-v1 A on M1 Canvas |
| First outreach email | Not sent | ASF action only |
| Pilot agreement (SOW) | Not drafted | Needed before first call |

---

# PART 3 — WIN CONDITIONS

## W1 — Demo Filmed
**Definition:** BLOCK / ALLOW / TAMPER FAIL sequence on camera. Under 6 minutes. No cuts. Terminal visible. Receipt visible. Validator output visible.
**Current:** ~25% — kernel works · Hub button open · not filmed
**Who:** ASF films · Maintainer 2 wires Hub button · Worker sets up terminal

## W2 — Enforcement Kernel Closed
**Definition:** Single write path + receipt + validator HARD FAIL. Receipt validator on read passes. Bypass inventory = 0. `validate-demo-enforcement-v1.sh` PASS. `validate-enforcement-kernel-v1.sh` PASS.
**Current:** ~55% — spine PASS · receipt binding PASS · validator on read MISSING
**Who:** Maintainer 2 builds receipt validator · Worker closes bypass paths

## W3 — First Revenue
**Definition:** CAD $2,000 minimum deposit received. LOI or pilot agreement signed. TrustField (TF) or Noetfield (NF) as primary target.
**Current:** $0 — 0 LOIs · 0 outreach sent
**Who:** ASF only. No Worker ships this. No Maintainer ships this.

---

# PART 4 — THE FROZEN ZONE

The following are LOCKED FROZEN until Stage 3 (CAD $10K repeat customer) is achieved. No exceptions without ASF FIVE-STEP pick.

**DO NOT BUILD:**
- New governance layers or abstraction levels
- New naming paradigms (no new OS names, no new category names)
- New Judge Center layers beyond what is already shipped
- New graph layers or knowledge graph expansions
- Voyage AI embedding upgrades beyond `voyage-4-lite` activation
- Snapshot Engine, Logical Clock, CRDT, or distributed consistency features
- New LOCKED doc files for existing architecture
- New incident categories or conduct frameworks
- WTM (FR-002) strategic build — deferred to post-W3

**WHY:** Governance is approaching diminishing returns. The system is internally optimized. Every hour on new architecture is an hour not spent converting the system into a product a customer understands, trusts, and pays for.

---

# PART 5 — KERNEL HARDENING LIST

The following IS authorized engineering. Kernel hardening ≠ architecture expansion. These close gaps that block the demo or diligence.

| # | Task | Priority | Who |
|---|------|----------|-----|
| K1 | Receipt validator on read — `validate-demo-enforcement-v1.sh` + `validate-enforcement-kernel-v1.sh` | P0 | Maintainer 2 |
| K2 | Bypass inventory audit → must reach 0 | P0 | Worker |
| K3 | Append-only receipt log (no single-file overwrite for key receipts) | P1 | Maintainer 2 |
| K4 | Hub disposable PASS — P1 materializer split (canonical vs runtime clean) | P1 | Maintainer 2 |
| K5 | G3 end-to-end — LAW_CHANGED → selective materializer queue | P2 | Worker |
| K6 | Voyage AI activation — `VOYAGE_API_KEY` → `~/.sina/secrets.env` → hub restart | P2 | Maintainer 2 (receipt written) |
| K7 | Hub "Commit" button wired to `sourcea_execute_v1.py --demo-enforcement` | P1 | Maintainer 2 |
| K8 | `validate-governance-propagation-live-v1.sh` run_inbox_truth fix | P3 | Maintainer 2 |

---

# PART 6 — 8-WEEK EXECUTION PLAN

**Governing principle:** Outreach does NOT wait for the demo. Demo does NOT wait for perfect kernel. Kernel hardening runs in parallel with commercial motion.

## Week 1 — Days 1-7

| Day | Track A: Engineering | Track B: Commercial |
|-----|---------------------|---------------------|
| 1-2 | K1: Receipt validator on read (P0) | Draft one-paragraph outreach email |
| 2 | K7: Hub Commit button | Draft TF Discovery SOW (CAD $4K / $2K deposit) |
| 3 | K2: Bypass inventory audit | **SEND first outreach — TF + NF — do not wait** |
| 3-7 | Film W1 demo (terminal · receipt · validator · BLOCK/ALLOW/TAMPER) | Book first calls |
| 5-7 | K3: Append-only receipt log | Follow up batch 1 |

## Week 2

| Track A: Engineering | Track B: Commercial |
|---------------------|---------------------|
| K4: Hub disposable fix | Live demo calls begin |
| K8: Propagation fix | Pilot proposal sent |
| Write `validate-enforcement-kernel-v1.sh` | Collect first objections |

## Weeks 3-4

| Track A: Engineering | Track B: Commercial |
|---------------------|---------------------|
| K5: G3 end-to-end | First deposit target (CAD $2K) |
| K6: Voyage activation confirmed | Refine demo from call feedback |
| Bypass inventory = 0 confirmed | Expand outreach to batch 2 (50 targets) |

## Weeks 5-8

| Track A: Engineering | Track B: Commercial |
|---------------------|---------------------|
| Kernel complete — W2 PASS | Close first pilot |
| Governance freeze maintained | Collect testimonials |
| Architecture expansion: FROZEN | CAD $10K repeat customer target |

---

# PART 7 — ENERGY ALLOCATION LAW

For the next 8 weeks this is the operating ratio. No exceptions without ASF FIVE-STEP pick.

```
Revenue / W3 outreach      ████████████████████████████  45%
Kernel hardening           ████████████████             25%
Demo polish / W1           ██████████                   15%
Customer interviews        ██████                       10%
New architecture           ███                           5%
```

The old ratio was the inverse. That era is over.

---

# PART 8 — KPI DASHBOARD

## Old KPIs (archived)
Validators passing · Receipt count · Governance coverage · Pass rates · Incident count · Spine row count

## New KPIs (active now)

| Metric | Target Week 2 | Target Week 4 | Target Week 8 |
|--------|--------------|---------------|---------------|
| Outreach emails sent | 10 | 30 | 50 |
| Meetings booked | 2 | 6 | 15 |
| Live demos delivered | 1 | 4 | 10 |
| Pilot proposals sent | 1 | 3 | 6 |
| Deposits received (CAD) | $0 | $2K | $10K |
| Renewals | 0 | 0 | 1 |

Engineering KPIs (secondary, tracked but not primary):
- Bypass inventory count (target: 0 by Week 2)
- Receipt validator on read: PASS/FAIL
- W1 demo filmed: YES/NO
- W2 kernel closed: YES/NO

---

# PART 9 — COMMERCIAL MILESTONE HIERARCHY

```
Stage 0 — Kernel works
  W2 ~55% today. K1-K3 closes it.
  ↓

Stage 1 — 5-minute live demo filmed
  W1. Terminal visible. Receipt. Validator. BLOCK/ALLOW/TAMPER.
  ↓

Stage 2 — CAD $2K pilot deposit (TARGET: Week 4)
  First paying customer. TF or NF. 30-day pilot.
  ↓

Stage 3 — CAD $10K repeat customer (TARGET: Week 8)
  Second paid engagement. Reference begins.
  ↓

Stage 4 — 3 reference customers
  Sufficient for seed narrative.
  ↓

Stage 5 — Seed raise ($3-10M)
  6-month timeline realistic once Stage 3 exists.
  ↓

Stage 6 — Platform expansion
  Architecture expansion resumes. New layers. New features.
  Only here.
```

**Everything above Stage 3 is dramatically easier once Stage 2 exists.**
**Everything above Stage 2 is impossible without W3 outreach starting this week.**

---

# PART 10 — COMMERCIAL OUTREACH SPEC

## Target Priority

| Target | Type | Priority | Contact method |
|--------|------|----------|----------------|
| TrustField (TF) | Design partner — known | P0 | Direct call / email |
| Noetfield (NF) | Design partner — known | P0 | Email batch 1 |
| 50 outreach targets | Cold / warm enterprise | P1 | Email + LinkedIn |

## Pilot Package

**Name:** SourceA Enforcement Pilot
**Duration:** 30 days
**Price:** CAD $4,000 (CAD $2,000 deposit to start)
**What they get:** Governance runtime deployed on their AI workflow. Every agent action logged, signed, receipted. BLOCK/ALLOW/TAMPER enforcement live. Full audit trail. If not delivered in 30 days: refund.
**What you need from them:** One AI workflow to instrument. One stakeholder. One hour of access.

## Outreach Email Template (first send)

```
Subject: AI governance receipt for [Company] — 30-day pilot

[Name],

If one of your AI agents made a wrong decision last week, do you have a 
cryptographic receipt proving what happened, who authorized it, and what 
rule it violated?

Most teams don't. We fix that.

SourceA is a governance runtime that wraps any AI workflow with 
deterministic receipts, policy enforcement, and a complete audit trail. 
30-day pilot. CAD $4K. Refund if we don't deliver.

10 minutes to see a live demo?

[ASF name]
```

---

# PART 11 — DEMO SPEC (W1)

**Format:** Terminal screen recording. No slides. No narration script (natural). Under 6 minutes.

**Sequence:**
```
1. Show a live agent action executing (ALLOW case)
   → Receipt generated logged
   → Spine event appended
   → Validator confirms: PASS

2. Attempt to tamper with the receipt (hand-edit the JSON)
   → Re-run validator
   → FAIL: checksum mismatch detected

3. Attempt to bypass governance (direct write without spine event)
   → Gatekeeper BLOCKS execution
   → FAIL: EXECUTION DENIED

4. Show the RT LIVE gate receipt logged
   → hub_sync 678ms · cascade 15.9s · spine_event_id · checksum
   → "This is what an auditor sees."
```

**One sentence at the end:** "You cannot fake this. You cannot bypass this. That is the product."

---

# PART 12 — ARCHITECTURE REFERENCE (READ ONLY)

These are stable. Do not modify without ASF pick.

## 12.1 Governance Event Spine (15 fields — LOCKED v1.1)

```
event_id · parent_event_id · correlation_id · object_id · version
agent_id · event_type · object_kind · law_id · skill_id
validator_set · affected_objects · replay_pointer · projection_version
status · checksum (SHA-256[:16]) · at
```

File: `~/.sina/governance-event-spine-v1.jsonl` (append-only)

## 12.2 Hub Projection Split (P1 — ACTIVE)

```
command-data-canonical.json  (schema: hub-canonical-projection-v1)
  → Stable state: laws, tasks, forms, receipts, scoreboard

command-data-runtime.json    (schema: hub-runtime-projection-v1)
  → Live volatile: fleet, queue, worker inbox, drain orchestrator
```

Delete either file → Rebuild → Same output. Hub is not state.

## 12.3 Execution Flow

```
Intent (ASF FIVE-STEP)
  → Form JSON (SSOT for picks)
  → Spine event appended
  → Gatekeeper invariant check
  → Worker execution
  → Validator confirms
  → Receipt written (with spine_event_id + checksum)
  → Hub projection rebuilt (disposable)
  → Monitor
```

## 12.4 Judge Center Pipeline (L1 active / L2-L3 on demand)

```
L1 Audit   → judge_center_audit_v1.py    (pattern scan vs disk truth)
L2 Counsel → judge_center_counsel_v1.py  (settle / escalate alarms)
L3 Bench   → judge_center_bench_v1.py    (final verdict + form row drafts)
```

Activation: `Q-JUDGE-STACK-v1 A` on M1 Canvas (pending)

## 12.5 Key Paths

```
SSOT root:            ~/Desktop/SourceA/brain-os/
Hub server:           scripts/sina-command-server.py  (:13020)
Hub rebuild worker:   scripts/hub_rebuild_worker_v1.py (:13030)
Gatekeeper:           scripts/gatekeeper_v1.py
Spine:                scripts/governance_event_spine_v1.py
Form SSOT:            scripts/live_founder_decision_form_v1.py
Form submit:          scripts/canvas_form_submit_v1.py
Judge pipeline:       scripts/judge_center_run_v1.py
Runtime state:        ~/.sina/
Secrets vault:        ~/.sina/secrets.env
```

---

# PART 13 — DECISIONS LOCKED (DO NOT RE-DEBATE)

These are closed. Reopening requires ASF FIVE-STEP pick.

| Decision | Pick | Locked by |
|----------|------|-----------|
| No Cursor AUTO-RUN | LOCKED OFF | Q-RT-LIVE YES · 2026-06-11 |
| EXTERNAL_CRITIC report-only | LOCKED | Q-CRITIC YES · FR-003 |
| Embedding provider = Voyage AI (voyage-4-lite) | LOCKED | Architecture decision |
| SHA-256 spine checksum stays | LOCKED | Golden Rule — validators are authority |
| Hub = projection not state | LOCKED | P1 law |
| OpenRouter embeddings deferred to phase-s9 | LOCKED | `validate-openrouter-embeddings-deferred-s9-v1.sh` |
| Architecture freeze (new layers) | LOCKED until Stage 3 | This document |
| SourceA external name | "governance and execution infrastructure" | This document |
| W3 outreach starts before W1 filmed | LOCKED | GPT + Claude + Gemini convergence |
| $100M is 5-10% regime, not plan | ACKNOWLEDGED | Commercial analysis |

---

# PART 14 — OPEN QUESTIONS (M1 CANVAS PENDING)

These are not debates. They are founder picks waiting on M1 Canvas.

| ID | Question | Recommended |
|----|----------|-------------|
| Q-1.10-SEAL | Seal Phase 1 closeout now? | YES |
| Q-JUDGE-STACK-v1 | Activate Judge Center L2/L3? | A |
| Q-THREAD-ROOM-v1 | Activate Thread Room pipeline? | A |
| Q-M2-029 | Ship INCIDENT-029 remediation? | YES |
| Q-SYS-INTEGRITY-RESUME | Resume playbook Phases 3-10? | YES |
| Q-M2-FORM-SYNC | Sync all rows to M1 Canvas? | YES |
| Q-WIRE-G3 | Reconcile Tailscale G3 status? | RECONCILE |

---

# PART 15 — AUTHORITY HIERARCHY

```
1. ASF explicit instruction (current session)
2. This document (`archive/superseded/blueprint-drafts-2026-06-12/SOURCEA_MASTER_BLUEPRINT_SSOT_v2_DRAFT.md`) — **DRAFT only**
3. brain-os/ governance files
4. plan-registry / REGISTRY.json
5. scripts/ validators
6. Runtime logs (~/.sina/)
7. Advisor reasoning (lowest)
```

Chat is not truth. Disk state > conversation state. If conflict: disk wins.

---

# PART 16 — THE FINAL STATEMENT

**SourceA's primary bottleneck is no longer technical maturity.**

It is converting a sophisticated internal governance engine into a product that a customer understands, trusts, and pays for.

The architecture is the moat. It stays hidden underneath.

The product is what the customer sees. It must be explainable in one sentence and demonstrable in three minutes.

**The next action that changes everything is the first outreach email — not the next validator.**

---

*LOCKED 2026-06-12 · ASF + Claude + GPT + Gemini converged synthesis · v2*
*Draft only — does not supersede v1 plans · Next review: after ASF FIVE-STEP LOCK pick or Stage 2 (first deposit)*
