> **INTERNAL ONLY — Phase 1 work plan — NOT SSOT.**
> Read after `SINA_OS_SSOT_LOCKED.md` v3 when Phase 1 starts.
> Location: `/Users/sinakazemnezhad/Desktop/SourceA/PHASE1_UNIFIED_BLUEPRINT_v2_3.md`

# Phase 1 — Unified Source of Truth (v2 — Forensic Edition)
## Noetfield Runtime × SinaaiOS Internal Blueprint

**Status:** Active — Phase 1  
**Version:** 2.0 — updated against forensic audit of SinaaiMonoRepo  
**Classification:** Internal planning — not for external distribution  
**Last updated:** 2026-05-31  
**Supersedes:** PHASE1_UNIFIED_BLUEPRINT.md (v1 — conceptual, pre-audit)

> **Why this version exists.** The v1 blueprint was written from concept briefs. A forensic audit of the actual repository revealed significant gaps between intended architecture and what is physically present on disk. This document replaces v1 entirely. It is grounded in observed reality and uses that as the baseline for Phase 1 work. Anything described here that does not yet exist is explicitly labeled as such.

---

## Table of Contents

1. [Actual State — What Exists on Disk](#1-actual-state--what-exists-on-disk)
2. [Concept vs Reality Gap Map](#2-concept-vs-reality-gap-map)
3. [Revised North Star & Principles](#3-revised-north-star--principles)
4. [Noetfield Runtime — Actual State + Phase 1 Build Plan](#4-noetfield-runtime--actual-state--phase-1-build-plan)
5. [SinaaiOS — Actual State + Phase 1 Consolidation Plan](#5-sinaaios--actual-state--phase-1-consolidation-plan)
6. [Phase 1 Goals (Reality-Grounded)](#6-phase-1-goals-reality-grounded)
7. [Constraints & Non-Negotiables](#7-constraints--non-negotiables)
8. [Architectural Boundaries & Rules](#8-architectural-boundaries--rules)
9. [Decision Framework](#9-decision-framework)
10. [Terminology & Definitions](#10-terminology--definitions)

---

## 1. Actual State — What Exists on Disk

This section is observation-only. No design intent. No fixes assumed.

### Repository structure (SinaaiMonoRepo)

```
SinaaiMonoRepo/                      ← root git: 60 tracked files / ~3928 on disk
├── SinaaiRuntime/                   ← ~736 .py files — PRIMARY EXECUTION SYSTEM
│   ├── api/                         ← FastAPI :8000 — primary API
│   ├── agents/                      ← 40 subdirectories (loop_engine, brain, spine, etc.)
│   ├── fleet/                       ← Redis workers
│   ├── integrations/                ← telegram (v1/v2/v3/v4/fintech), github_lab
│   ├── cacos/                       ← independent FastAPI :8020 (legacy parallel)
│   ├── governance/                  ← Python: constitution_engine, sanction_engine
│   ├── data/                        ← 151+ JSON state files + phase1.db (SQLite)
│   └── supabase/migrations/         ← 25 SQL migration files
├── SinaaiDataBase/                  ← separate .git with ZERO COMMITS
│   ├── noetfield/                   ← 269 .md + 5 .json + 0 .py  ← DOCS ONLY
│   ├── governance/                  ← JSON SSOT + golden_edge FastAPI :8001
│   └── data/                        ← L0–L4 layered markdown identity/mandates
├── backend/                         ← FastAPI :8010 — README: "Deprecated product path"
├── ui/                              ← Next.js :3000 — 29 routes (NOT in root git)
├── .github/workflows/               ← github-lab.yml, validate-registry.yml (manual only)
└── ecosystem.config.cjs             ← PM2: runs SinaaiRuntime/run_api.py as "cacos-api"
```

### What is actually running

| Port | What starts it | What it is | Status |
|---|---|---|---|
| `:8000` | PM2 / `run_api.py` | SinaaiRuntime primary FastAPI + all background loops | Active (primary) |
| `:3000` | PM2 / ecosystem.config | Next.js UI (29 routes) | Active |
| `:8001` | Manual / unknown | `SinaaiDataBase/governance/golden_edge/api.py` — scoring engine | Unknown if routinely started |
| `:8010` | Manual `./start.sh` | `backend/` FastAPI — documented as deprecated | Frozen / legacy |
| `:8020` | `run_cacos.py` | CACOS-N independent FastAPI | Legacy / optional |

### What "SinaaiOS" actually is on disk

SinaaiOS does not exist as a Python module or unified control plane. What exists:

- `SinaaiDataBase/governance/system_registry.json` — JSON file listing known systems
- `AGENTS.md`, `README.md` — documentation describing the concept
- `SinaaiRuntime/api/main.py` — reads registry JSON at startup for informational logging only
- `SinaaiDataBase/governance/control_plane/panel.py` — standalone Python script for boundary scanning; not wired into any running service
- No folder named `sina_os/`, no Python package implementing a unified control plane

Actual decision-making is distributed across: `loop_engine`, `agent_orchestrator`, `agent_spine`, `golden_edge`, `panel.py` (standalone), and shell scripts.

### What "Noetfield" actually is on disk

Noetfield does not exist as executable code. What exists:

- `SinaaiDataBase/noetfield/product/` — 25 subdirectories of markdown specifications
- `SinaaiDataBase/noetfield/corpus/` — uploaded documents and source material
- `SinaaiDataBase/noetfield/prompts/` — prompt templates
- 5 `.json` registry files — corpus and product registries
- **0 `.py` files** under `noetfield/`
- Referenced in `system_registry.json` and `boundaries.json` — no Runtime Python imports of `noetfield/` observed

### Git tracking gap

- Root git: 60 tracked files (primarily: Telegram Liaison, GitHub Lab, Agent Spine slice, `.github/`, `scripts/`, `backend/agents/definitions.json`)
- Not tracked at root: `SinaaiDataBase/` (entire tree), `ui/`, most of `SinaaiRuntime/`, governance SSOT files, `README.md`, `ROADMAP.md`
- `SinaaiDataBase/.git`: exists, zero commits
- Root git: 2 commits total on current branch

### Product modules — observed status

| Product | Code exists? | Location | Actual state |
|---|---|---|---|
| Noetfield | No | `SinaaiDataBase/noetfield/` | Docs + JSON registries only (0 .py) |
| TrustField Technologies | Yes (external) | `Desktop/TrustField Technologies/` + delivery repo | Separate company — active delivery; may collaborate/overlap with Noetfield; not mono submodule |
| Virelux | No | `system_registry.json` mentions only | Not found in repository |
| 777 / Seven Foundation | No | Cycle integers in `brain_memory.json` | No module; integer appears in memory JSON |
| CACOS-N | Yes | `SinaaiRuntime/cacos/` | Legacy parallel stack :8020 |

---

## 2. Concept vs Reality Gap Map

Each row is one gap that Phase 1 must either close, accept, or explicitly defer.

| # | What was assumed | What audit found | Gap severity | Phase 1 action |
|---|---|---|---|---|
| G1 | SinaaiOS is a unified control plane | Distributed across 8+ processes; no single module | Critical | Accept distributed reality; define a minimal spine contract |
| G2 | Noetfield has execution code | 0 `.py` files; docs only | Critical | Build Noetfield from scratch or scope to docs-phase only |
| G3 | One FastAPI execution layer | Four stacks (:8000/:8001/:8010/:8020) with overlapping concerns | High | Declare :8000 as canonical; freeze/remove others in Phase 1 |
| G4 | SinaaiDataBase is a versioned SSOT | Nested git with 0 commits; not tracked at root | High | Commit SinaaiDataBase or merge into root git with proper tracking |
| G5 | Governance enforces boundaries | Registry is read-only informational; validate-registry is manual only | High | Accept advisory-only governance for Phase 1; enforce via human review |
| G6 | Tenant isolation exists in Noetfield | Cannot exist; Noetfield has no code | Critical | Prerequisite: Noetfield code must be built before isolation can exist |
| G7 | Audit/replay system exists | phase1.db + JSON belong to SinaaiRuntime, not Noetfield | Critical | Prerequisite: same as G6 |
| G8 | Single Telegram integration | Five integration trees (v1/v2/v3/v4/fintech) in repo | Medium | Declare one canonical version; archive others |
| G9 | PM2 app name matches function | "cacos-api" runs SinaaiRuntime/run_api.py | Low | Rename for clarity (non-breaking) |
| G10 | SinaaiDataBase/L1-runtime has code | README stubs only | Medium | Acceptable placeholder; do not treat as active |

### What this means for Phase 1

Phase 1 cannot proceed as if these gaps don't exist. The v1 blueprint described a future state as if it were present. This document treats the gaps as the actual starting line.

**The practical consequence:**
- Noetfield Runtime is a greenfield build within an existing monorepo, not a refinement of existing code
- SinaaiOS consolidation is about reducing chaos to a defined set of active components, not about building something new
- The SSOT and git hygiene problems must be resolved before any governance enforcement is possible

---

## 3. Revised North Star & Principles

The distinction between the two systems remains valid. What changes is the acknowledgment that Noetfield is not yet a system — it is a specification — and SinaaiOS is not yet unified — it is a collection of overlapping processes.

### The Core Distinction (unchanged in intent, updated in reality)

| Axis | Noetfield Runtime | SinaaiOS |
|---|---|---|
| **What it is today** | Specification documents (269 .md, 5 .json, 0 .py) | Partially operational distributed system |
| **What it must become** | Production SaaS for compliance decisions | Rationalized orchestration layer |
| **Who it serves** | Paying customers (fintech, regtech) | Internal operations |
| **Failure cost** | Revenue, trust, compliance breach | Internal friction |
| **Development approach** | Greenfield build with strict constraints from day one | Consolidation and deprecation of parallel paths |
| **Phase 1 deliverable** | Minimal viable execution layer with tenant isolation + audit | Single canonical process map with deprecations declared |

### Governing Principles (v2)

**P1 — Acknowledge the actual baseline.** Every decision starts from what is on disk today, not from the intended architecture. Building on false assumptions compounds debt.

**P2 — Noetfield code is greenfield.** No Noetfield execution code exists. When building it, do not inherit `SinaaiRuntime`'s patterns by default — evaluate each choice against Noetfield's specific compliance requirements.

**P3 — Determinism is non-negotiable from the first line of Noetfield code.** It is easier to build determinism in than to retrofit it. Every decision: same inputs + same rule version = same output. No exceptions.

**P4 — Tenant isolation is structural, not policy.** It must be enforced at the authentication layer before any business logic executes. Application-level checks are insufficient.

**P5 — Audit integrity is append-only from schema definition.** The database schema for Noetfield audit records must make modification structurally impossible, not just operationally discouraged.

**P6 — SinaaiOS consolidation means subtraction, not addition.** The current state has too many overlapping paths. Phase 1 success means fewer active processes, not more capabilities.

**P7 — Git tracks truth.** Code and governance documents that are not in git are not managed. Phase 1 requires the SSOT to be tracked, committed, and have a defined ownership.

**P8 — One canonical path per function.** One Telegram integration. One FastAPI primary. One governance registry. Parallel paths are acknowledged technical debt with a declared resolution date, not valid operational alternatives.

---

## 4. Noetfield Runtime — Actual State + Phase 1 Build Plan

### Actual state (audit-verified)

Noetfield is a product specification that does not yet execute. The specification is rich:

- `SinaaiDataBase/noetfield/product/` contains 25 structured subdirectories of product definitions
- Corpus and prompt materials exist as reference inputs
- JSON registries define known entities
- Referenced in governance documents as a distinct product with defined boundaries

There is no Noetfield API, no Noetfield database schema, no Noetfield decision engine, and no Noetfield tenant model in executable form.

### What must be built in Phase 1

Phase 1 for Noetfield is a greenfield build. The specification documents are inputs to that build, not the build itself.

#### Minimum viable Noetfield (Phase 1 scope)

The following must exist and be production-quality before Phase 1 exits. Nothing beyond this list is in scope for Phase 1.

**1. Decision execution layer**

A dedicated FastAPI application (not a route added to SinaaiRuntime) that accepts structured decision requests and returns deterministic results with full provenance.

Constraints:
- Stateless execution — all state lives in the audit store, never in the engine
- Explicit rule set version on every request — never implicit "latest"
- Idempotent — retrying the same request with the same `request_id` returns the same result
- No shared process or memory with SinaaiRuntime

**2. Tenant model**

- Tenant identity resolved and cryptographically validated at the edge, before any business logic
- All data objects scoped to `tenant_id` at the schema level — not enforced by application logic alone
- No cross-tenant query path exists in any ORM or query layer

**3. Immutable audit store**

- Schema-level append-only enforcement (no `UPDATE`, no `DELETE` on decision records — enforced in the database, not only in application code)
- Every audit record captures: `decision_id`, `tenant_id`, `request_id`, `input_snapshot`, `rule_set_version_at_execution`, `result`, `rule_trace`, `executed_at`
- Input snapshot is taken at request submission time and stored independently of any mutable state

**4. Replay capability**

- Any `decision_id` can be re-executed using its stored `input_snapshot` and `rule_set_version_at_execution`
- Replay result must match original result — any mismatch is a determinism failure and a P0 incident

**5. Rule management**

- Rules are versioned monotonically and automatically
- Rule definitions are immutable once status = `active`
- Activation events are themselves audit-logged
- Changes create new versions — they never overwrite existing active rules

**6. Isolated database**

- Noetfield uses its own database instance (not `phase1.db` in SinaaiRuntime)
- Schema defined from the compliance requirements, not inherited from SinaaiRuntime's schema

### Data model — Phase 1 core entities

**Decision Request** (input, immutable after submission)
```
request_id          UUID, globally unique, set by client or generated at edge
tenant_id           UUID, validated cryptographically before processing
rule_set_id         UUID, explicit — never resolved as "latest"
rule_set_version    Integer, explicit
input_payload       JSONB, snapshot taken at submission — immutable
submitted_at        TIMESTAMPTZ, server-authoritative — client value not trusted
```

**Decision Record** (audit — append-only, no UPDATE, no DELETE)
```
decision_id                   UUID, globally unique, server-generated
request_id                    UUID, FK to Decision Request
tenant_id                     UUID, denormalized for query isolation
result                        JSONB, the decision output
rule_trace                    JSONB, ordered list of rules evaluated + outcomes
input_snapshot                JSONB, exact copy of input_payload at execution time
rule_set_version_at_execution Integer, frozen at execution time
executed_at                   TIMESTAMPTZ, server-authoritative
```

**Rule**
```
rule_id         UUID
tenant_id       UUID
version         Integer, monotonically incrementing, auto-assigned
status          ENUM('draft', 'active', 'superseded') — no 'deleted'
definition      JSONB, immutable once status = 'active'
activated_at    TIMESTAMPTZ (nullable)
superseded_at   TIMESTAMPTZ (nullable)
```

**Tenant**
```
tenant_id       UUID
name            TEXT
status          ENUM('active', 'suspended')
created_at      TIMESTAMPTZ
```

### What is explicitly out of scope for Noetfield Phase 1

- Billing / subscription management
- Customer self-service tenant provisioning (admin-only in Phase 1)
- Advanced rule authoring UI
- Multi-region deployment
- SLA enforcement or uptime guarantees beyond basic health monitoring
- Integration with SinaaiRuntime agents or automation pipelines

### Phase 1 production readiness requirements

Before Phase 1 exits, Noetfield must pass all of the following:

- [ ] Adversarial cross-tenant test suite: tenant A cannot read tenant B's data in any error path
- [ ] Append-only enforcement verified at database level (attempted UPDATE/DELETE must fail at DB, not just app)
- [ ] Replay test: 100 historical decisions replayed, all match original results
- [ ] Determinism test: same input submitted 10× against same rule version produces identical outputs
- [ ] All API endpoints require authentication and tenant-scoped tokens
- [ ] Health endpoint live and returning structured status
- [ ] Error responses audited to confirm no cross-tenant data leakage
- [ ] Per-tenant rate limiting enforced
- [ ] API versioning strategy defined (e.g. `/v1/`) and first-version stable
- [ ] Integration documentation sufficient for a new customer to onboard without support

---

## 5. SinaaiOS — Actual State + Phase 1 Consolidation Plan

### Actual state (audit-verified)

SinaaiOS is operationally active but architecturally fragmented. The primary system (`:8000`) works. The problem is that it coexists with three other FastAPI stacks, five Telegram integration trees, duplicate governance namespaces, and a governance SSOT that is not in git.

What is real and active:
- `SinaaiRuntime/api/` — primary FastAPI on `:8000`, mounts 20+ routers, starts many background loops in lifespan
- `SinaaiRuntime/agents/` — 40 subdirectories including `loop_engine`, `brain`, `agent_spine`, `liaison`, `registry`
- `SinaaiRuntime/fleet/` — Redis-based task queue workers (separate process)
- `SinaaiRuntime/integrations/github_lab/` — webhook/dispatch to Agent Spine; task state in JSON
- `SinaaiRuntime/integrations/telegram*/` — one of five implementations selected at runtime via env flag
- `SinaaiDataBase/governance/` — `system_registry.json`, `boundaries.json`, SSOT files (not in root git)
- `.github/workflows/` — three workflows; GitHub Lab active, validate-registry manual-only
- `ui/` — Next.js on `:3000`, 29 routes (not in root git)

What is legacy or frozen:
- `backend/` — documented as deprecated; FastAPI :8010 frozen
- `SinaaiRuntime/cacos/` — CACOS-N :8020; legacy parallel stack
- Telegram v1/v2/v3 — superseded by v4/fintech; remain in repo

What does not exist:
- A single "Sina OS" control plane module
- Unified enforcement of system boundaries in code
- Versioned governance SSOT in git

### Phase 1 consolidation goals

Phase 1 for SinaaiOS is consolidation, not new construction. The goal is a defined, minimal, maintainable system — not a more capable one.

#### What Phase 1 must deliver for SinaaiOS

**1. Canonical process declaration**

A single document (living in SinaaiDataBase, committed to git) that names exactly which processes are active, which port they run on, what they own, and which are frozen or deprecated. This document is the operational SSOT for SinaaiOS runtime state.

Format per entry:
```
Process name:     SinaaiRuntime API
Entry point:      SinaaiRuntime/run_api.py
Port:             :8000
Owns:             Primary execution, agent loops, all active API routes
Status:           ACTIVE — canonical
PM2 name:         sinaai-runtime (rename from cacos-api)
```

**2. Deprecated paths declared and frozen**

The following must be declared frozen (no new development, no active routing to them) before Phase 1 exits:

- `backend/` (:8010) — already documented as deprecated; confirm no active callers, annotate
- `SinaaiRuntime/cacos/` (:8020) — freeze; confirm nothing in the primary path requires it
- Telegram integrations v1/v2/v3 — confirm v4 or fintech is the selected path; others archived
- `golden_edge/` (:8001) — determine if actively used; if yes, document as active; if no, freeze

**3. Git hygiene — SSOT in version control**

- `SinaaiDataBase/` must be tracked. Either: merge into root git with appropriate `.gitignore`, or commit `SinaaiDataBase/.git` with an initial commit of all current files and establish a workflow for keeping it current.
- The governance SSOT files (`system_registry.json`, `boundaries.json`, `ANNOUNCEMENT_BOARD.md`) must be in git before Phase 1 exits. An unversioned SSOT is not a SSOT.
- Root git must track at minimum: all files in `SinaaiDataBase/governance/`, all files in `SinaaiDataBase/noetfield/`, `ui/` package manifests, and the full `SinaaiRuntime/` tree.

**4. Single Telegram canonical path**

One Telegram integration is designated canonical. The others are removed from the active import path (not necessarily deleted from disk in Phase 1, but not loaded and not maintained). The selection is documented in the process declaration.

**5. Human approval gate — confirmed working**

Before Phase 1 exits, it must be demonstrated (not just documented) that:
- A Builder or Spine agent task that would affect a production system requires a Telegram confirmation from a human operator before it executes
- This gate is tested with a real scenario, not a simulated one

**6. SinaaiOS must not be a dependency of Noetfield**

Noetfield must start, execute decisions, and serve its API with SinaaiOS fully offline. This is verified by taking the SinaaiRuntime process down and confirming Noetfield continues to operate. (This also confirms the architectural separation is real, not just documented.)

### What Phase 1 does NOT require SinaaiOS to do

- Build new agent capabilities
- Unify all four FastAPI stacks into one
- Implement automated governance enforcement in code
- Build a new UI beyond what is already at `:3000`
- Achieve full SinaaiDataBase/L1-runtime vision

---

## 6. Phase 1 Goals (Reality-Grounded)

### Noetfield Runtime

| Goal | Success criterion | Priority | Current state |
|---|---|---|---|
| Greenfield decision execution layer | Standalone FastAPI, separate from SinaaiRuntime, executes decisions deterministically | Critical | Does not exist |
| Tenant model implemented | Tenant isolation enforced at schema + auth layer | Critical | Does not exist |
| Immutable audit store | Schema-level append-only; no UPDATE/DELETE path | Critical | Does not exist |
| Replay capability | Any decision_id replays and matches original result | Critical | Does not exist |
| Rule management | Versioned, immutable-once-active, activation logged | Critical | Does not exist |
| Isolated database | Noetfield-own DB, not phase1.db | High | Does not exist |
| Production readiness checklist | All 10 items in Section 4 pass | High | Not started |
| First paying customer onboarded | Real compliance decisions running in production | Phase 1 exit criterion | Not started |

### SinaaiOS

| Goal | Success criterion | Priority | Current state |
|---|---|---|---|
| Canonical process declaration committed to git | Single document names all active/frozen processes | Critical | Not in git |
| SSOT in version control | SinaaiDataBase governance files committed to git | Critical | 0 commits in SinaaiDataBase/.git |
| Deprecated paths frozen | backend/, cacos/, telegram v1/v2/v3 declared frozen, no new work | High | Partially documented, not enforced |
| Single canonical Telegram path | One integration active; others archived | High | Five trees coexist |
| Human approval gate verified | Live test of agent → Telegram confirm → execute flow | Critical | Documented intent; not verified |
| Noetfield independence verified | Noetfield operates with SinaaiRuntime down | Critical | N/A until Noetfield exists |
| PM2 naming corrected | App "cacos-api" renamed to match actual function | Low | cacos-api runs run_api.py |

### Phase 1 exit criteria

Phase 1 is complete when ALL of the following are true simultaneously:

1. Noetfield has all Critical goals above complete and passing
2. At least one paying customer is running real compliance decisions through Noetfield
3. SinaaiDataBase governance files are committed to git with a functioning workflow for updates
4. Canonical process declaration exists and is accurate
5. Human approval gate is tested and confirmed operational
6. No open P0 or P1 bugs in Noetfield
7. Noetfield independence from SinaaiOS is verified by a live test

---

## 7. Constraints & Non-Negotiables

### Absolute constraints — zero tolerance, no exceptions

**AN1 — Noetfield tenant isolation.**  
Once Noetfield code exists, no operation may allow Tenant A to access Tenant B's data. Not in happy paths, not in error paths, not in logging output. This is enforced at schema + auth layer, not application logic.

**AN2 — Noetfield audit records are append-only.**  
The database schema must make UPDATE and DELETE structurally impossible on decision records. Application-level "we don't call DELETE" is insufficient.

**AN3 — Noetfield decisions are deterministic.**  
Same `input_payload` + same `rule_set_version` = same `result`, always. Any deviation is a P0 incident, not a bug to be triaged.

**AN4 — SinaaiOS agents do not touch Noetfield compliance data.**  
No SinaaiRuntime agent, loop, or automation pipeline may write to, modify, or delete Noetfield decision records, audit logs, or active rule definitions. Read-only access for observability is the maximum permitted.

**AN5 — No Noetfield breaking changes after first customer.**  
Once a customer is live, Noetfield API contracts are frozen for the v1 lifetime. Changes require a versioned deprecation cycle with customer communication.

**AN6 — SSOT must be in git.**  
Any governance document, system registry, or architectural boundary definition that is not committed to a git repository is not the SSOT. Files on disk that are not in git can be lost, diverged, or silently modified.

### Development constraints

- All Noetfield production deployments require: passing tenant isolation tests, passing determinism tests, and passing replay tests — in that order, as gates.
- No "temporary" code in Noetfield's decision execution or audit path. Temporary code in these paths becomes permanent.
- SinaaiDataBase must be updated before structural changes are implemented. Document first, build second.
- SinaaiOS consolidation changes (freezing legacy paths, deprecating integrations) require the canonical process declaration to be updated at the same time.

---

## 8. Architectural Boundaries & Rules

### What SinaaiOS may and may not do to Noetfield

```
SinaaiOS permitted:                  SinaaiOS not permitted:
─────────────────────────────        ─────────────────────────────
Observe Noetfield health             Write to any Noetfield data store
Query Noetfield status APIs          Access cross-tenant Noetfield data
Route Telegram commands to           Modify decision records or audit logs
  Noetfield API (via HTTP)           Override Noetfield authentication
Log/surface Noetfield metrics        Bypass Noetfield rate limiting
```

### FastAPI process boundaries (Phase 1)

```
Process          Port    Status          Owns
─────────────────────────────────────────────────────────────────
SinaaiRuntime    :8000   ACTIVE          Orchestration, agents, UI backend, automation
Noetfield API    :TBD    BUILD REQUIRED  Compliance decisions, tenant isolation, audit
Next.js UI       :3000   ACTIVE          Dashboard, monitoring
golden_edge      :8001   VERIFY STATUS   Governance scoring (determine active/freeze)
backend/         :8010   FREEZE          Deprecated; no new work
cacos/           :8020   FREEZE          Legacy parallel; no new work
```

### Agent access boundaries (Phase 1)

| Capability | Noetfield | SinaaiRuntime | GitHub | SinaaiDataBase docs |
|---|---|---|---|---|
| Read | Read-only health/status API only | Full | With auth | Full |
| Write | Never | Full (internal) | With human approval | Full |
| Execute/deploy | Never | Internal loops | With human approval | N/A |
| Delete | Never | Internal only | Never | Never via agent |

---

## 9. Decision Framework

When a new feature, change, or technical decision arises, classify and route it:

### Step 1 — Classify

**Type A — Noetfield core path** (decision execution, audit store, tenant isolation, replay, rule management)  
→ Maximum conservatism. Default is reject unless demonstrably safe. Requires replay test and tenant isolation test before shipping.

**Type B — Noetfield peripheral** (health endpoints, admin tooling, observability, documentation)  
→ Standard engineering judgment. Backward compatibility required.

**Type C — SinaaiOS consolidation** (deprecating a legacy path, migrating Telegram version, fixing PM2 naming)  
→ Subtraction-oriented. Prefer doing less. Must update canonical process declaration at same time.

**Type D — SinaaiOS new capability** (new agent, new integration, new automation)  
→ Evaluate: does this increase chaos (adds a parallel path) or reduce it (replaces an existing one)? If it adds a parallel path without removing one, it is likely out of Phase 1 scope.

**Type E — Cross-system boundary** (anything that touches the interface between Noetfield and SinaaiOS)  
→ Apply AN4. Document the exact data flow, direction, and access type before implementing.

### Step 2 — Test against absolute non-negotiables

Does this change touch AN1 through AN6?  
If yes → stop. The constraint is not negotiable. Redesign.

### Step 3 — Test against Phase 1 exit criteria

Does this change move toward or away from the 7 exit criteria in Section 6?  
If away → document the justification explicitly and get explicit sign-off before proceeding.

### Step 4 — Update SinaaiDataBase before building

For any Type A, Type D, or Type E decision: update the relevant SinaaiDataBase document before writing code. The document is not a post-hoc record — it is the pre-condition.

---

## 10. Terminology & Definitions

| Term | Definition |
|---|---|
| **Actual state** | What is physically present and operational on disk, as verified by the forensic audit. Not what is intended. |
| **Intended state** | The target architecture described in this document and in SinaaiDataBase specifications. |
| **Gap** | The difference between actual state and intended state. Gaps are managed explicitly; they are not ignored. |
| **Determinism** | The property that the same `input_payload` evaluated against the same `rule_set_version` always produces the same `result`. Non-negotiable in Noetfield. |
| **Tenant** | A paying customer organization in Noetfield. All data and execution is scoped to a tenant at the schema level. |
| **Tenant isolation** | The architectural guarantee that no tenant's data or execution context is accessible to any other tenant — enforced at schema + auth layer, not application logic alone. |
| **Decision record** | An immutable (append-only) audit entry capturing the inputs, rule trace, result, and timestamp of a single decision execution. |
| **Replay** | Re-executing a historical decision using its stored `input_snapshot` and `rule_set_version_at_execution`, and verifying the result is identical to the original. |
| **Rule set version** | An immutable, explicitly referenced snapshot of rules at a point in time. Used in every Noetfield decision request. Never resolved implicitly. |
| **Append-only** | A database constraint enforced at the schema level: no UPDATE, no DELETE on protected tables. Cannot be bypassed by application code. |
| **Agent Spine** | `SinaaiRuntime/agents/runtime/agent_spine.py` — the central agent task execution entry point. GitHub Lab and Telegram route through it. |
| **Canonical process** | The single designated active implementation of a function. When two paths exist for the same function, the canonical one is active; the other is frozen. |
| **Frozen** | A codebase or process path that is preserved but receives no new development, is not actively maintained, and has no active callers in the primary execution path. Distinct from deleted. |
| **SinaaiDataBase** | The file-based governance and documentation layer. Files here are the declared source of structural truth. Must be in git to be treated as SSOT. |
| **SinaaiRuntime** | The active primary execution system running on `:8000`. Contains agents, orchestration, integrations, and background loops. |
| **SSOT** | Single Source of Truth. A document or system that is authoritative for a given piece of information. Only valid as an SSOT if it is in git, tracked, and has a defined owner. |
| **Phase 1** | The current development phase. Ends when all 7 exit criteria in Section 6 are met simultaneously. |
| **P0 / P1** | Incident severity. P0 = production down or data integrity breach. P1 = significant degradation or compliance gap in a production customer. Both require immediate response and post-incident review. |
| **Human approval gate** | The operational requirement that any SinaaiOS agent action affecting production systems must be explicitly confirmed by a human operator via Telegram before execution. Must be tested, not just documented. |
| **Greenfield build** | Building from zero within an existing repository. Noetfield is a greenfield build — its code does not yet exist and is not inherited from SinaaiRuntime. |

---

## Document Control

**This document supersedes PHASE1_UNIFIED_BLUEPRINT.md (v1).**

v1 was written from concept briefs before forensic audit. It described an intended architecture as if it were present. v2 starts from observed reality and defines Phase 1 as the work required to reach the intended state.

**To update this document:**
1. Propose the change with rationale and reference to the audit finding or new observation it reflects
2. Test against AN1–AN6 in Section 7
3. Update this file in SinaaiDataBase (committed to git) before implementing in code

**Version history:**
- v1.0 — 2026-05-31 — Initial blueprint from concept briefs
- v2.0 — 2026-05-31 — Full rewrite grounded in forensic audit of SinaaiMonoRepo
