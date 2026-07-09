# SOURCEA MASTER OPERATING TRACKER

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## LOCKED v1 — Canonical Founder Command Center

**Document type:** Strategic SSOT — Permanent  
**Owner:** SourceA Brain (Execution Core)  
**Location:** `brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md`  
**Wired into:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b` · `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` · `GOVERNANCE_P1_LOOPS_LOCKED_v1.md`  
**Validator:** `scripts/validate-master-operating-tracker-v1.sh`  
**Last updated:** 2026-06-08T02:30:00Z (ASF hub home redesign · sa-0821 Phase A · home_founder_view payload)  

---

---

# SECTION 0 — GOVERNING LAW

## Golden Rule

> If information exists anywhere in SourceA but is not represented in this tracker, it is **operationally invisible**.  
> If information in this tracker contradicts runtime or canonical disk state, **disk state wins**.  
> The tracker is the map. The runtime is the territory.

## Core Operating Principle

This document contains **strategic truth**.  
It does not duplicate volatile runtime state.  
It references canonical runtime artifacts maintained elsewhere.  

**One source of truth per responsibility. No duplicated authority.**

## Design Boundary

| This tracker IS | This tracker is NOT |
|---|---|
| Permanent founder-level operational dashboard | A runtime database |
| Strategic map of goals, roadmap, architecture, gaps | A chat log or receipt archive |
| Pointer index to live runtime state | A duplicate of execution.json or events/ |
| Accountability registry for every open item | A static governance document |

## Mandatory Session Flow

**Every Brain session:**
```
READ tracker
  ↓
VERIFY pointer consistency (Section 8)
  ↓
DECIDE / EXECUTE
  ↓
UPDATE tracker before session close
```

**Every Worker session:**
```
READ tracker
  ↓
VERIFY pointer matches sa-XXXX in INBOX
  ↓
BUILD
  ↓
UPDATE build progress and receipt status
```

**Every Specialist session:**
```
READ tracker
  ↓
ANALYZE relevant sections
  ↓
ADVISE
  ↓
REGISTER trace ID in Decision Registry or Missing Registry
```

**Every Validator session:**
```
VERIFY structural integrity
  ↓
VERIFY pointer freshness
  ↓
PASS or FAIL (see Validation section)
```

**No execution begins without reading this tracker.**  
**No session closes without updating this tracker if state changed.**

## Enforcement Failure Clause

If Brain fails to update this tracker after any phase transition, goal state change, or pointer update, **Broker marks the tracker STALE** and the next Validator run **automatically fails Condition 1** — regardless of content.  

The system is self-enforcing. Compliance is not honor-based.

---

---

# SECTION 1 — EXECUTIVE SNAPSHOT

**Owner:** Brain (mandatory)  
**Update triggers:** Any Goal Registry change · Any roadmap phase transition · Any runtime pointer update · Any validator FAIL/PASS event · Any ASF directive  

| Field | Value |
|---|---|
| Current founder objective | **ENFORCEMENT-6MO:** W1 film · W3 NF/TF pilot — hub tap only |
| Current operating phase | CLOCK C investor wedge · demo kernel shipped · RT LIVE PASS |
| Current maturity level | L3 broker-enforced · L1 semi-auto · agentic commercial **LAG** |
| Current active roadmap | ENFORCE → STRATEGIC-SLICE · factory **background** |
| Current execution rail | Hub Actions · SCAN→PICK→PROVE — **not** Cursor AUTO-RUN P0 |
| Current highest priority | `validate-demo-write-path-v1.sh` · agentic W3 batch 1 · film W1 |
| Current execution pointer | → `~/.sina/next-execution-pointer-v1.json` (`sa-9002` ACT · queue pos 2) |
| Brain phase-first pick | enf-* / CLOCK C — **not** Cloud Forge Run hero |
| Current system health | → validators + RT LIVE receipt (refresh disk) |
| Current strategic blocker | **W3 = $0** · agentic outreach not wired |
| Current next milestone | W1 recording on disk OR W3 LOI conversation |
| Tracker last verified | 2026-07-08T01:58:47Z |

> Runtime state is referenced from canonical runtime files (Section 8). It is never duplicated here.

---

---

# SECTION 2 — GLOBAL GOAL REGISTRY

**Rule:** Every active, pending, completed, deferred, or cancelled goal must appear here. Nothing may exist outside this registry.

**Owner per goal:** Named in each row. Brain owns registry structure.

| Field | Description |
|---|---|
| Goal ID | Unique identifier (e.g. GOAL-001) |
| Name | Short name |
| Description | What this goal achieves |
| Owner | Brain / ASF / Worker / Specialist |
| Status | ACTIVE · PENDING · BLOCKED · DEFERRED · CANCELLED · COMPLETE |
| Priority | P0 / P1 / P2 / P3 |
| Progress | % honest — never optimistic |
| Dependencies | List of Goal IDs or sa-XXXX this depends on |
| Current blocker | NONE or specific blocker description |
| Next action | Exact next step — never vague |
| Linked sa-XXXX | Task assignment on the SourceA spine |
| Unlock condition | What must be true before this advances |
| Last updated | ISO timestamp |

| Goal ID | Name | Status | Priority | Progress | Linked sa | Next action | Unlock | Last updated |
|---|---|---|---|---|---|---|---|---|
| GOAL-AUTH-FREEZE | Factory FREEZE + anti-staleness latches | ACTIVE | P0 | — | sa-0778 | Tap Safety · Brain sync · bounded ASF resume only | Kill flag ON · INCIDENT-022 remediated | 2026-06-10 |
| GOAL-AUTH-LIVE | Live AUTO-RUN proof | **SUPERSEDED** | — | — | sa-0730 | Cursor AUTO-RUN rejected — see FOUNDER_AGENTIC law | ASF resume token only | 2026-06-10 |
| GOAL-AUTH-P2 | Strict gates (reconciled · NL pick · manual_fallback audit) | PENDING | P1 | 0% | — | After live chain PASS | ASF names P2 | 2026-06-08 |
| GOAL-MP-SHIP | MergePack public ship | ACTIVE | P0 | — | — | Disable Vercel deployment protection | Founder Hub card | 2026-06-08 |
| GOAL-W1-PACK | Worker 1 unified pack w1-01..w1-40 | COMPLETE | P0 | 100% | sa-0150 | — | E2E PASS · worker_2 purged | 2026-06-08 |
| GOAL-COMM-PARTNER-V3 | AI infra partnerships — governed receipt wedge (LOCKED v3) | ACTIVE | P1 | 20% | P05 shipped | P03 NVIDIA Inception apply · P05 Voyage live (629 chunks · semantic:true) | Parallel with dual P0 · does not reorder factory | 2026-06-15 |
| GOAL-COMM-TF-NF-001 | First commercial invoice — TF-001 or NF-001 | ACTIVE | P0 | — | — | Outreach + SOW · 90-day falsifier | Independent of partner credits | 2026-06-10 |
| GOAL-HUB-P0-1 | Honest counter Hub §1 (596/1000 · unproven · kill chip) | ACTIVE | P0 | — | — | SinaaiDataBase · `HUB_PROOF_UX_P0_LOCKED_v1.md` §1 · AR-7073a0ed55 | — | 2026-06-10 |
| GOAL-HUB-P0-2 | Event chain JSONL export (one sa_id · contract fields) | ACTIVE | P0 | — | — | After P0-1 · AR-7b461bcca6 | P0-1 shipped | 2026-06-10 |
| GOAL-HUB-P0-3 | Overnight verify button (Haiku read-only CHECK) | ACTIVE | P0 | — | — | After P0-1 · AR-774df3e0a5 | P0-1 shipped | 2026-06-10 |

---

---

# SECTION 3 — MASTER ROADMAP

**Rule:** Complete roadmap from current state to final vision. No optimistic reporting. Every phase must have an honest status.

**Phase status values:** `COMPLETE` · `ACTIVE` · `FUTURE` · `DEFERRED` · `CANCELLED` · `EXPERIMENTAL`

Each phase contains:

| Field | Description |
|---|---|
| Phase ID | Sequential identifier |
| Name | Short descriptive name |
| Objective | What this phase delivers |
| Status | See phase status values above |
| Owner | Who drives this phase |
| Dependencies | Phases that must complete first |
| Blockers | Current impediments — NONE if clean |
| Expected outputs | Concrete deliverables |
| Actual outputs | What was actually shipped (fill on close) |
| Target milestone | Date or trigger |
| Honest notes | Any partial, deferred, or incomplete items |

### Commercial partnerships (GOAL-COMM-PARTNER-V3)

| Phase ID | Name | Status | Owner | Next action | Target |
|---|---|---|---|---|---|
| CP-A | Bootstrap credits — P05 done → P03→P06→P04→P02 | **ACTIVE** | ASF + Executor | P03 NVIDIA Inception apply · P05 Voyage live | Week of 2026-06-10 |
| CP-B | Anthropic · OpenRouter · AGT/ISV | **FUTURE** | Commercial + Brain | Receipt deck · NF-001/TF-001 gate | After disk proof |
| CP-C | GCP/AWS full cloud | **DEFERRED** | ASF | Inception stack credits | After AUTO-RUN sustained |

**Law:** `AI_INFRA_PARTNERSHIP_PROPOSALS_LOCKED_v1.md` · **Decision:** `DEC-PARTNER-012-V3`

### Hub proof UX (GOAL-HUB-P0-1..3)

| Phase ID | Name | Status | Owner | Next action | Target |
|---|---|---|---|---|---|
| HUB-P0 | Counter → JSONL export → overnight verify | **ACTIVE** | SinaaiDataBase | P0-1 honest counter · AR-7073a0ed55 | Week of 2026-06-10 |

**Law:** `HUB_PROOF_UX_P0_LOCKED_v1.md`

---

---

# SECTION 4 — BIG PICTURE ARCHITECTURE

**Rule:** Single system diagram showing all layers, authority boundaries, and information flow. Updated only when architectural changes occur.

```
┌─────────────────────────────────────────────────────────┐
│                    ASF (Founder)                        │
│          Final override · Hub only · No Terminal        │
└──────────────────────┬──────────────────────────────────┘
                       │ approve / override / AUTO-RUN
┌──────────────────────▼──────────────────────────────────┐
│                  Hub (:13020)                           │
│       Refresh · Actions · AUTO-RUN · dispatch unlock    │
└──────────────────────┬──────────────────────────────────┘
                       │ activates loop / execute turn
┌──────────────────────▼──────────────────────────────────┐
│           SourceA Execution Core (Brain)                │
│  execution_authority: true · route · pick · reconcile   │
│  dual-mode: narrator (default) / executor (activated)   │
└────────┬─────────────────────────────────┬──────────────┘
         │ specialist input                │ execution order
┌────────▼──────────┐           ┌──────────▼──────────────┐
│   Specialists     │           │  Decision Layer          │
│ Commercial        │           │  reconciled_decision.yaml│
│ Governance        │           │  → next-execution-       │
│ Research Acq.     │           │    pointer-v1.json       │
│ execution: false  │           └──────────┬───────────────┘
└───────────────────┘                      │ pointer
                              ┌────────────▼────────────────┐
                              │   Broker (gate)             │
                              │ broker=yes · Rail A check   │
                              │ authority check · feasible  │
                              └────────────┬────────────────┘
                                           │ INBOX delivery
                              ┌────────────▼────────────────┐
                              │   Worker Layer              │
                              │ SourceA Worker (sa-XXXX)    │
                              │ Portfolio Workers (TF/NF)   │
                              │ Headless CLI Worker         │
                              │ build only · one-sa rule    │
                              └────────────┬────────────────┘
                                           │ disk changes
                              ┌────────────▼────────────────┐
                              │   Validation Layer          │
                              │ validators · broker=yes gate│
                              │ receipts · proof layer      │
                              └────────────┬────────────────┘
                                           │ verified state
                              ┌────────────▼────────────────┐
                              │   Memory Fabric             │
                              │ REGISTRY · LOCKED docs      │
                              │ RESEARCH/ · receipts        │
                              │ authority.yaml · SSOT       │
                              └────────────┬────────────────┘
                                           │ appended
                              ┌────────────▼────────────────┐
                              │   Event System              │
                              │ ~/.sina/events/YYYY-MM-DD   │
                              │ DECISION_RECONCILED         │
                              │ BROKER_ACCEPT / REJECT      │
                              │ INBOX_DELIVERED             │
                              │ WORKER_STARTED / SUBMIT     │
                              │ VALIDATOR_PASS / FAIL       │
                              │ MEMORY_COMMIT               │
                              │ TASK_CLOSED                 │
                              └────────────┬────────────────┘
                                           │
                              ┌────────────▼────────────────┐
                              │ Knowledge / Artifacts       │
                              │ SinaaiDataBase (broker only)│
                              │ Old Brain (archive/advise)  │
                              │ GPT / Claude (advise only)  │
                              └─────────────────────────────┘
```

**Authority boundary rule:**  
- `execution_authority: true` — Brain only  
- `build authority` — Workers only (one-sa per turn)  
- `override authority` — ASF + Hub only  
- `advise only` — Specialists, Research, GPT, Claude, Old Brain

---

---

# SECTION 5 — MASTER MISSING REGISTRY

**Rule:** Every incomplete, partial, deferred, blocked, or debt item lives here. Nothing disappears from visibility until explicitly closed with evidence.

**Debt categories:** technical · governance · documentation · architecture · runtime · automation · commercial · security

**Severity:** P0 (critical blocker) · P1 (required before next phase) · P2 (hardening) · P3 (future consideration)

Each item:

| Field | Description |
|---|---|
| Item ID | Unique identifier (e.g. MISS-001) |
| Category | Debt type or classification |
| Severity | P0 / P1 / P2 / P3 |
| Description | What is missing or incomplete |
| Owner | Who is responsible for closing it |
| Reason | Why it exists — never "unknown" for P0/P1 |
| Unlock condition | Exact condition that allows closure |
| Target phase | Roadmap phase when this should be resolved |
| Last reviewed | ISO timestamp — must not age past 30 days for P0/P1 |
| Status | OPEN · IN PROGRESS · BLOCKED · CLOSED |
| Closed by | sa-XXXX or decision ID when closed |

**P0/P1 items without an owner and unlock condition cause Validator FAIL Condition 3.**

| Item ID | Category | Severity | Description | Owner | Unlock condition | Target phase | Status | Last reviewed |
|---|---|---|---|---|---|---|---|---|
| MISS-001 | governance | P2 | 118 legacy `*_LOCKED_v1.md` files at SourceA root — should live in `brain-os/system/` or `brain-os/laws/` per FILE_STORAGE_GOVERNANCE | Brain | Governance batch migration or index map in tracker | next cleanup sprint | OPEN | 2026-06-08 |
| MISS-002 | runtime | P1 | `scripts/validate-file-storage-v1.sh` referenced in FILE_STORAGE_GOVERNANCE | Worker | Ship validator matching §6 FAIL conditions | — | CLOSED (sa-0712) | 2026-06-08 |
| MISS-003 | documentation | P2 | Full LOCKED law copy in RESEARCH: `RESEARCH/.../2026-06-08_RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md` — Tier 1 canonical is root `RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md` | Brain | Replace with summary mirror + pointer only | next cleanup sprint | CLOSED | 2026-06-08 |
| MISS-004 | runtime | P2 | Multiple `~/.sina/*.json` runtime files not registered in Section 8 canonical pointer list | Brain | Audit `~/.sina/` vs Section 8 · register or archive | next cleanup sprint | OPEN | 2026-06-08 |
| MISS-005 | governance | P2 | `brain-os/plan-registry/worker-dual-40/WORKER1_UNIFIED_CLOSEOUT_LOCKED_v1.md` — LOCKED doc in plan-registry not `brain-os/system/` | Brain | Move or downgrade to non-LOCKED receipt | next cleanup sprint | CLOSED | 2026-06-08 |
| MISS-006 | runtime | P1 | Hub home UI plain-English redesign | Worker | `renderHomeFounderView` + validator PASS · sa-0821 | phase-s8-hub-ui-ux | CLOSED (sa-0821) | 2026-06-08 |
| MISS-007 | governance | P1 | CIR-COSPRO-2026-06-07 — Research Lane B edited product SSOT (AGENTS/SSOT/voice roadmap) + registry spam | Brain | Guardrail rule + LANE_REGISTER gate + registry INDEX dedup · incident closed | — | CLOSED | 2026-06-09 |
| MISS-008 | governance | **P0** | Cross-lane edit — any agent touching another agent SSOT/docs without `EDIT ALLOWED` | Brain | `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` + `000-cross-lane-edit-forbidden.mdc` + `cross_lane_edit_guard_v1.py` | — | CLOSED | 2026-06-09 |

---

---

# SECTION 6 — DECISION REGISTRY

**Rule:** Append-only. No major architectural, governance, or strategic decision may exist only in chat history. Every decision that affects system behavior, authority, or roadmap must be registered here.

Each decision:

| Field | Description |
|---|---|
| Decision ID | Unique identifier (e.g. DEC-001) |
| Title | Short descriptive name |
| Date | ISO date |
| Approver | ASF · Brain · Governance Specialist |
| Reason | Why this decision was made |
| Alternatives rejected | What was considered and why it was declined |
| Evidence | Trace IDs, research saves, validator results |
| Impact | What this changes in the system |
| Superseded by | DEC-XXX if this decision was later overridden |
| Status | ACTIVE · SUPERSEDED · EXPERIMENTAL |

| Decision ID | Title | Date | Approver | Reason | Evidence | Impact | Status |
|---|---|---|---|---|---|---|---|
| DEC-PARTNER-012-V3 | Lock AI infra partnership strategy v3 + Phase A/B/C apply order | 2026-06-10 | ASF | Web-verified programs · fix v2 apply order (P05 before P03) · dual P0 credits ≠ invoice | `COMMERCIAL_GOAL-REF-2026-06-10-PARTNER-012-V3` · `RESEARCH-ACQUISITOR-20260610-PARTNER-012` · `AI_INFRA_PARTNERSHIP_PROPOSALS_LOCKED_v1.md` | Canonical commercial partner law · wired to roadmaps | ACTIVE |

---

---

# SECTION 7 — RISK & DEPENDENCY DASHBOARD

**Rule:** Hidden coupling must never exist. Every risk with severity P0 or P1 must have an owner. Dependencies between system components must be explicit.

## Risk Register

| Risk ID | Domain | Severity | Description | Owner | Mitigation | Status |
|---|---|---|---|---|---|---|
| RISK-AUTH-LIVE | runtime | P0 | Claimed vs observed — full AUTO-RUN event chain not yet proven in one Hub run | Brain | ASF tap Rail A AUTO-RUN · tail events jsonl | OPEN |

**Domains covered:** technical · architectural · runtime · memory · governance · execution · validation · automation · commercial · security · documentation

## Dependency Graph

Explicit dependencies between:

- Goals → Goals (prerequisite relationships)
- Goals → Roadmap phases
- Workers → Validators (which validator gates which worker)
- Specialists → Decisions (which specialist input fed which decision)
- Roadmap phases → sa-XXXX (which tasks implement which phase)
- Policies → Execution gates (which policy enforces which step)
- Memory artifacts → Authority claims (what evidence supports what authority assertion)

Brain maintains this graph. Any undocumented dependency discovered during execution must be added here before the session closes.

---

---

# SECTION 8 — RUNTIME POINTERS

**Design principle:** This tracker references runtime truth. It does not duplicate it. Validators compare pointer freshness against these canonical sources.

## Freshness Rules

| Layer | Max age before STALE |
|---|---|
| Strategic sections (1–7) | 24 hours |
| Runtime pointer references (this section) | 1 hour |

## Canonical Runtime Sources

| Artifact | Path | Owns |
|---|---|---|
| Authority map | `brain-os/system/authority.yaml` | Role definitions · maturity levels |
| File storage law | `brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md` | Tier 1/2/3 placement rules |
| Master tracker | `brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md` | Strategic SSOT (this file) |
| Execution state | `~/.sina/runtime/execution.json` | Current status · heartbeat |
| Next task pointer | `~/.sina/next-execution-pointer-v1.json` | next_sa · rail · source |
| Active execution rail | `~/.sina/active-execution-rail-v1.json` | Rail A/B · manual_fallback flag |
| Reconciled decision | `~/.sina/brain/reconciled_decision.yaml` | Brain SYNC · specialist traces |
| Event log | `~/.sina/events/YYYY-MM-DD.jsonl` | Full execution history |
| Worker registry | `RESEARCH/_GOVERNANCE/WORKERS_REGISTRY.yaml` | Agent roles · authority flags (canonical) |
| Research root cache | `~/.sina/research-root/` | Filtered digest · machine registry |
| Agent workspaces | `~/.sina/agent-workspaces/` | Per-agent vault staging |
| Plan registry | `brain-os/plan-registry/sourcea-1000/REGISTRY.json` | sa-XXXX assignments |
| Hub command data | `agent-control-panel/command-data.json` | Hub state |

**No agent reads volatile runtime state from this document.  
Every agent reads runtime state from the canonical source listed above.**

---

---

# VALIDATION

**Script:** `scripts/validate-master-operating-tracker-v1.sh`  
**Runs:** Every Brain session start · Every Worker INBOX request · Scheduled hourly  
**Behavior:** Fail closed on critical governance violations. Warn on non-critical items.

## FAIL Conditions (execution blocked)

| # | Condition | Why |
|---|---|---|
| 1 | Strategic sections older than 24h OR runtime pointers older than 1h | Staleness — tracker cannot be trusted |
| 2 | Any active or blocked goal absent from Goal Registry | Goal is operationally invisible |
| 3 | Any P0 or P1 item in Missing Registry without an owner AND unlock condition | Unowned critical gap |
| 4 | Runtime pointer reference in Section 8 inconsistent with `next-execution-pointer-v1.json` | Map/territory mismatch |
| 5 | Any required section incomplete, absent, or marked `[DRAFT]` or `[TBD]` | Tracker structurally invalid |

## WARNING Conditions (logged, execution continues)

- P2/P3 missing items without owner
- Decision Registry entries older than 90 days with no review
- Risk items with severity P1 not reviewed in 14 days
- Dependency graph entries referencing deleted or renamed sa-XXXX

## Stale Trigger

If Brain fails to update after any phase transition or goal state change, Broker writes `tracker_status: STALE` to `execution.json` and Validator Condition 1 fails automatically on next run.

---

---

# UPDATE RULES

## Brain updates on:
- Phase transition (roadmap)
- Goal state change (any status update)
- Architectural decision (Section 6 append)
- Specialist reconciliation (trace ID registration)
- New missing item discovered
- Pointer change in `next-execution-pointer-v1.json`
- Any Validator FAIL event

## Workers update on:
- Build progress (Goal Registry progress %)
- Implementation completion (receipt reference)
- New technical debt discovered (Section 5 append)

## Specialists update on:
- Analysis trace registration (Section 6 or 5)
- Governance observation (Section 7 risk or Section 5 debt)

## Validators:
- Verify structural integrity only
- Do not modify content
- Write PASS/FAIL result to `execution.json`

## Enforcement failure:
If Brain fails to update this tracker after any phase transition, goal state change, or pointer update:
1. Broker marks `tracker_status: STALE` in `execution.json`
2. Next Validator run automatically fails Condition 1
3. Worker INBOX delivery is blocked until Brain updates and Validator re-runs PASS

**The system is self-enforcing. Compliance is not honor-based.**

---

---

# AUTHORITY REFERENCE

Quick reference — full authority map lives in `brain-os/system/authority.yaml`.

| Role | execution_authority | can_route | can_build | can_override |
|---|---|---|---|---|
| ASF + Hub | true | true | — | true |
| SourceA Brain | true | true | false | false |
| SourceA Worker | false | false | true | false |
| Portfolio Worker (TF/NF) | false | false | true (scoped) | false |
| Headless CLI Worker | false | false | true | false |
| Broker | false | gate only | false | false |
| Commercial Specialist | false | false | false | false |
| Governance Specialist | false | false | false | false |
| Research Acquisitor | false | false | false | false |
| Old Brain (SinaaiDataBase) | false | false | false | false |
| GPT / Claude (external) | false | false | false | false |

**Golden law:**  
> Specialists advocate · Execution Core decides · Workers act · Disk remembers · ASF controls

---

---

# DOCUMENT INTEGRITY

**This document is LOCKED.**  
Structural changes (adding/removing sections, changing enforcement rules, changing freshness thresholds) require:
1. ASF explicit instruction
2. New version suffix (`_v2`) with pointer update in `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b`
3. `validate-master-operating-tracker-v1.sh` updated to match

**Content updates** (filling in goals, roadmap, decisions, risks) are Brain's ongoing responsibility and require no version bump.

**Last structural version:** v1  
**Authored by:** Brain (Execution Core) — synthesized from five-source convergence (Old Brain · New Brain · Governance Specialist · GPT · Claude External Advisor) · 2026-06-08  
**Trace:** AUTO-TRACE-AUTHORITY-CONVERGENCE-LOCK-2026-06-08
