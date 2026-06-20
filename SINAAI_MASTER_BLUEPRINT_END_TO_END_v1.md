# Sinaai — Master Blueprint (End-to-End)
## Future reference & roadmap — from zero to operating system

**Version:** 1.0  
**Classification:** INTERNAL ONLY — never commit to git, never push online  
**Location:** `/Users/sinakazemnezhad/Desktop/sourceA/SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 (law). This document = **roadmap + narrative + sequencing**.  
**Status:** Phase 0 — reference document; not a build order until ASF exits Phase 0  
**Locked:** 2026-06-01  
**Maintainer:** ASF

---

## How to use this document

| You want… | Read… |
|-----------|--------|
| **What is true (law)** | `SINA_OS_SSOT_LOCKED.md` v3 |
| **Full journey (this file)** | Sections 1–18 below |
| **Phase 1 forensic detail** | `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` |
| **Runtime LLM policy** | `SINAAI_AGENT_STACK_POLICY_v1.md` |
| **Conflicts + open questions** | `Desktop/sourceB/SOURCE_B_ECOSYSTEM_AND_CONFLICTS_v1.md` |
| **TrustField Cursor adapter** | `Desktop/sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md` + `TrustField Technologies/os/` |
| **Sina Prompt OS (LOCKED)** | `sourceA/SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` · app `Desktop/SinaPromptOS/` · `Sina Prompt OS.command` |

**Rule:** If this blueprint disagrees with Source A SSOT → **Source A wins**. Update this file after registry changes.

---

## Table of contents

1. [Executive summary](#1-executive-summary)  
2. [North star & what we are building](#2-north-star--what-we-are-building)  
3. [Two planes: DESIGN vs DELIVERY](#3-two-planes-design-vs-delivery)  
4. [Ecosystem architecture](#4-ecosystem-architecture)  
5. [What exists today (reality baseline)](#5-what-exists-today-reality-baseline)  
6. [Phase roadmap (0 → 4)](#6-phase-roadmap-0--4)  
7. [Track A — Personal PAIOS](#7-track-a--personal-paios)  
8. [Track B — Sinaai consolidation](#8-track-b--sinaai-consolidation)  
9. [Track C — Noetfield (commercial product)](#9-track-c--noetfield-commercial-product)  
10. [Track D — TrustField GTM (active delivery)](#10-track-d--trustfield-gtm-active-delivery)  
11. [Intelligence architecture](#11-intelligence-architecture)  
12. [Data, memory & ingestion](#12-data-memory--ingestion)  
13. [Human & agent interfaces](#13-human--agent-interfaces)  
14. [Governance & truth stack](#14-governance--truth-stack)  
15. [Cursor operating model](#15-cursor-operating-model)  
16. [MonoRepo consolidation checklist](#16-monorepo-consolidation-checklist)  
17. [Exit criteria matrix](#17-exit-criteria-matrix)  
18. [SourceA / sourceB file map](#18-sourcea--sourceb-file-map)  
19. [Never-do list](#19-never-do-list)

---

## 1. Executive summary

**Sinaai** is a **Personal AI Operating System (PAIOS)** for ASF — not a single chatbot. It combines:

- **Governance** (what is allowed to exist)  
- **Truth storage** (identity, law, knowledge, agents)  
- **Runtime execution** (Telegram, fleet, event bus, GitHub Lab)  
- **Observation UI** (dashboard, control — not authoritative)  
- **Commercial products** (Noetfield future; TrustField active delivery now)  
- **Cursor adapters** (Prompt OS — one task at a time per repo)

**Today (Phase 0):** Structure is declared; mono repo is powerful but fragmented; SSOT is not fully in git; two Cursor workspaces caused confusion.

**Next:** ASF picks Phase 1 priority (PAIOS ingestion vs Noetfield scaffold vs TrustField-only delivery), exits Phase 0, then executes **one canonical spine** on `:8000` with **subtraction**, not more parallel stacks.

---

## 2. North star & what we are building

### 2.1 One sentence

> **A controlled personal OS that ingests your life and work, runs a company of specialized agents with failover intelligence, and ships commercial products without chaos — ASF approves what matters.**

### 2.2 What success looks like (end state)

| Capability | End state |
|------------|-----------|
| **Personal** | Chief-of-Staff knows priorities, non-negotiables, conflicts; daily brief; ingestion from chats/files |
| **Execution** | Telegram → liaison → workers → leader synthesis → reply; never silent (multi-vendor LLM) |
| **Truth** | Layer A + governance in git; one registry; announcements for activation |
| **Commercial** | TrustField revenue path live; Noetfield compliance engine isolated when built |
| **Build** | Cursor executes one step; Prompt OS + Source A prevent drift |
| **Integrity** | Phase 2 CI enforces registry and boundaries |

### 2.3 What we are NOT building (global)

- One mega-LLM with god-mode access to your Mac  
- Noetfield inside SinaaiRuntime as a submodule  
- Five Telegram integrations active forever  
- Second or third “OS brain” (Prompt OS, Cursor memory, random README)  
- NDAX or domain plugins as core dependencies (frozen external plugins)

---

## 3. Two planes: DESIGN vs DELIVERY

| Plane | Authority | Repos | Agents may… |
|-------|-----------|-------|-------------|
| **[DESIGN]** | Source A + mono `governance/` | `SinaaiMonoRepo`, Desktop `sourceA/` | Declare structure, align registry **after** bursts |
| **[DELIVERY]** | Repo SOT + founder locks | `TrustField Technologies`, other GTM repos | Ship ops, deploy, E2E, bugfixes; **not** redefine ecosystem |

```text
[DESIGN]  Sina OS declares → DataBase stores truth
[DELIVERY] TrustField (etc.) ships → registry records after (ledger, not gate)
```

**TrustField (locked):** ACTIVE PRODUCT in DELIVERY; commercial infra AUTHORIZED; feature freeze ON for new product features; ops AUTHORIZED.

---

## 4. Ecosystem architecture

```
ASF (human — final override)
  └── Sina OS (governance — declares structure; no runtime process)
        ├── SinaaiDataBase/          truth storage (L0–L4, governance/, noetfield/docs)
        ├── SinaaiRuntime/           execution :8000 — agents, spine, fleet, Telegram, GitHub Lab
        ├── ui/                      observe + control :3000
        ├── scripts/                 host automation
        ├── .github/workflows/       external triggers
        ├── golden_edge/ :8001       optional scoring tool (NOT governance)
        │
        ├── FROZEN: backend/ :8010, cacos/ :8020, telegram v1/v2/v3 (one canonical TBD)
        │
        └── Products:
              noetfield/     docs only (0 .py) — future isolated SaaS
              trustfield     corpus in mono; live product = TrustField repo + trustfield.ca
              virelux, 777   placeholders

External (not mono spine):
  Desktop/TrustField Technologies   [DELIVERY] commercial GTM
  Desktop/sourceA, sourceB          [DESIGN] internal SSOT (never public git)
```

**Flow:** Declare → Store → Execute → Observe → Git preserve (Phase 2) → Products isolated when live.

---

## 5. What exists today (reality baseline)

*Observation only — May 2026 forensic audit.*

| Asset | State |
|-------|--------|
| **SinaaiMonoRepo** | ~3928 files logged; ~60 tracked at root git |
| **SinaaiRuntime** | Active `:8000`, ~736 `.py`, agent spine, 5 Telegram trees, fleet, event bus |
| **SinaaiDataBase** | Rich markdown + governance JSON; nested `.git` **0 commits** |
| **Noetfield** | 269 `.md`, 5 `.json`, **0 `.py`** |
| **UI** | Next.js `:3000`, 29 routes; not in root git |
| **TrustField repo** | Live commercial push; Render + Vercel + E2E |
| **Source A Desktop** | SSOT v3 locked locally |
| **Sina OS module** | Does not exist as code — governance is files + registry |

**Critical gaps:** dual SSOT sessions, undeclared runtime modules, registry informational only, Phase 0 not formally exited.

---

## 6. Phase roadmap (0 → 4)

### Overview

| Phase | Name | Duration (indicative) | Theme |
|-------|------|------------------------|-------|
| **0** | Governance / Declaration | Now | Lock truth; no structural build |
| **1** | Consolidation + Foundation | Next | Subtract chaos; git SSOT; wire spine; pick track priority |
| **2** | Integrity / Enforcement | After 1 stable | CI blocks registry violations |
| **3** | Live personal MVP | Parallel/stream | Telegram loop + memory + ingestion |
| **4** | Scale & automation | Future | Auto-ingest, council, plugins, Appsmith |

**You are in Phase 0** until ASF signs Phase 0 exit (Section 17).

---

### Phase 0 — Governance / Declaration (CURRENT)

**Goal:** Everyone (human + agents) shares one story.

| Do | Don't |
|----|-------|
| Lock Source A v3 | New Runtime subsystems |
| Publish agent stack policy (declare) | Wire all LLM keys in prod |
| TrustField Prompt OS `os/` (adapter) | Treat blueprint as law over SSOT |
| Resolve Source B conflicts | Noetfield Python code |
| TrustField commercial ops | Dual SSOT in one Cursor prompt |

**Exit:** Section 17 — Phase 0 row all true.

---

### Phase 1 — Consolidation + Foundation

**Goal:** One spine, one Telegram path, SSOT in git, declared modules.

**Pick ONE primary track for Phase 1 exit (ASF decision):**

| Option | Phase 1 exit focus |
|--------|-------------------|
| **1A — PAIOS first** | Ingestion pipeline + L2/L3 seeds + live Telegram Chief-of-Staff loop |
| **1B — Noetfield first** | Greenfield Noetfield API scaffold + tenant/audit schema |
| **1C — Consolidation only** | Canonical process doc + freeze legacy + git SSOT, minimal features |

**Always in Phase 1 regardless of option:**

- Commit `SinaaiDataBase/governance/` to git (mirror Source A structure)  
- Declare canonical Telegram integration; freeze others  
- Registry sweep for undeclared Runtime modules  
- Rename PM2 `cacos-api` → honest name  
- Wire `AGENT_LEADER_CHAIN` / `AGENT_WORKER_CHAIN` per policy (after ASF approval)  
- Human approval gate **tested** on Telegram  

**Detail:** `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` (Noetfield + consolidation depth).

---

### Phase 2 — Integrity / Enforcement

- `validate-registry.yml` blocking  
- Path guards (no writes to frozen trees)  
- Desktop Source A **still never** in public git  

---

### Phase 3 — Live personal MVP

| Component | Deliverable |
|-----------|-------------|
| Telegram | `@SinaaiOSbot` stable loop |
| Memory | Supabase tasks + conversation bridge |
| Ingestion | `imports/raw/` → L2/L3 promotion workflow |
| Council | Optional multi-model panel (leader/worker split) |
| UI | Read-only ops dashboard hooks |

---

### Phase 4 — Scale

- Auto-ingest chats  
- SoT mining, conflict detection  
- NDAX / plugins as **optional** modules  
- Appsmith on Supabase  
- Revenue-ranked roadmap for Noetfield (distinct from compliance engine)

---

## 7. Track A — Personal PAIOS

**Purpose:** ASF’s life and work — organized, controlled, agent-assisted.

### 7.1 Components

| Component | Location | Phase |
|-----------|----------|-------|
| Identity & non-negotiables | `data/L1-identity/` | 0–1 |
| Agent mandates | `data/L4-agents/` | 0 done |
| Ingestion pipeline | `imports/raw/`, `pipeline/` | 1 |
| Chief-of-Staff | Runtime liaison + L4 | 1–3 |
| AI Council | n8n or Runtime panel (leader/worker) | 3–4 |
| Personal brief | Telegram daily | 3 |

### 7.2 Agent roles (PAIOS factory)

| Agent | Role |
|-------|------|
| **Chief-of-Staff** | Route, prioritize, report to ASF |
| **Brain** | Synthesize after worker discussion |
| **Analyst** | Interpret, conflicts with LAW |
| **Operator** | Execute approved scripts/tasks |
| **lead_scout** | Research (web + corpus) |

### 7.3 Non-negotiables (always on)

Read `002-personal-non-negotiables.md` — Truth, Energy, Trust, Growth, Stability. Agents flag violations; ASF decides.

---

## 8. Track B — Sinaai consolidation

**Purpose:** Subtract parallel chaos in mono repo.

### 8.1 Canonical process map (Phase 1 deliverable)

One committed doc listing:

| Process | Entry | Port | Status |
|---------|-------|------|--------|
| SinaaiRuntime API | `run_api.py` | :8000 | ACTIVE |
| UI | Next.js | :3000 | ACTIVE |
| Golden Edge | `golden_edge/api.py` | :8001 | OPTIONAL |
| backend | `backend/` | :8010 | FROZEN |
| cacos | `run_cacos.py` | :8020 | DEPRECATED |

### 8.2 Subtraction list

- Freeze `backend/`, `cacos/`  
- Archive Telegram v1/v2/v3 from import path  
- Declare `loop_engine`, `civilization`, etc. in registry or freeze  
- No new FastAPI stacks  

**Principle P6:** Phase 1 success = **fewer** active processes, not more features.

---

## 9. Track C — Noetfield (commercial product)

**Purpose:** Compliance decision SaaS — **greenfield**, isolated from Runtime.

### 9.1 Today

- Spec only: `SinaaiDataBase/noetfield/`  
- TrustField narrative lives in **corpus** — not the TrustField GitHub repo identity  

### 9.2 Phase 1 minimum (if track selected)

- Standalone FastAPI (not :8000 route)  
- Own database (not `phase1.db`)  
- Tenant model + append-only audit schema  
- Determinism + replay tests  

### 9.3 Phase 1 exit (blueprint)

- First paying customer on Noetfield  
- Adversarial tenant isolation tests pass  

**Full spec:** `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` §4.

---

## 10. Track D — TrustField GTM (active delivery)

**Purpose:** Revenue and commercial readiness **now** — separate repo.

### 10.1 Authority (locked)

| Field | Value |
|-------|--------|
| Status | ACTIVE PRODUCT [DELIVERY] |
| Commercial readiness | AUTHORIZED |
| Feature freeze | ON |
| Ops (Render, Postgres, E2E, DNS) | AUTHORIZED |
| Implementation | TrustField repo only |
| Registry sync | After implementation burst |

### 10.2 Prompt OS adapter

```
TRUSTFIELD_SOURCE_OF_TRUTH.md
    → os/strategy.md (slice)
    → os/plan.json (queue)
    → prompt-engine → validator
    → Cursor (one task)
    → verify script → update plan.json
```

**Map:** `sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md`

### 10.3 Current queue (seed)

1. Production readiness PASS (Postgres + Redis)  
2. Market gates PASS  
3. API DNS / health  
4. Telegram webhook stable  

---

## 11. Intelligence architecture

### 11.1 Company model (not one model)

```text
Human (Telegram / Cursor)
    → LIAISON / BRAIN (Leader — synthesis)
    → WORKERS (scout, analyst, writer, operator)
    → event_bus + fleet queue
    → LEADER reply (one voice)
```

### 11.2 LLM stack (Phase 1 wire)

| Layer | Technology |
|-------|------------|
| Router | LiteLLM or OpenRouter |
| Leader | DeepSeek R1 → Gemini Flash → GitHub GPT-4o |
| Workers | Groq, Cerebras, OpenRouter free |
| Batch | Mistral 1B tok/mo |
| Research | Tavily, Exa |
| Observe | Langfuse |
| Guard | Upstash Ratelimit |
| Last | Ollama |

**Policy:** `SINAAI_AGENT_STACK_POLICY_v1.md`

### 11.3 Never silent test

Kill Gemini quota → system still replies within 30s via chain.

---

## 12. Data, memory & ingestion

### 12.1 Layer model (subordinate to governance)

| Layer | Content | Status |
|-------|---------|--------|
| L0-law | Boundaries, hierarchy | Active |
| L0-meta | Architecture corpus | Active |
| L1-identity | ASF core, non-negotiables | Active |
| L2-knowledge | Empty → fill via ingestion | Phase 1 |
| L3-process | Empty → fill via ingestion | Phase 1 |
| L4-agents | Factory agents | Active |

### 12.2 Ingestion pipeline (Phase 1)

```text
imports/raw/  →  staging/  →  clusters/  →  promote to L2/L3 (approved)
```

Operator mandate: approved writes only.

### 12.3 Runtime memory

| Store | Use |
|-------|-----|
| Supabase | Tasks, logs, memory MVP |
| SQLite / JSON | Fleet tasks, local state |
| event_bus | Agent pub/sub |

---

## 13. Human & agent interfaces

| Interface | Role | Phase |
|-----------|------|-------|
| **Telegram** `@SinaaiOSbot` | Primary personal + approval gate | 1–3 |
| **Telegram** `@TrustFieldBot` | TrustField production | Now |
| **Cursor** | Code execution; Prompt OS adapter per repo | Now |
| **UI** `:3000` | Observe/control | 1+ |
| **GitHub Lab** | Issue/PR → Agent Spine | Active |
| **Slack / Linear / Jira** | Optional Cloud Agent triggers | Future |
| **Appsmith** | Dashboard on Supabase | 4 |

---

## 14. Governance & truth stack

### 14.1 Read order (every session)

1. `sourceA/SINA_OS_SSOT_LOCKED.md`  
2. `governance/system_registry.json`  
3. `ANNOUNCEMENT_BOARD.md`  
4. `boundaries.json`  
5. `AGENTS.md`  
6. `sourceA/SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` (this file — sequencing)  
7. `sourceB/SOURCE_B_ECOSYSTEM_AND_CONFLICTS_v1.md`  

### 14.2 How truth changes

1. ASF approves  
2. Update registry (+ Source A if structural)  
3. `ANNOUNCEMENT_BOARD` + dated announcement file  
4. Align Layer A **after** registry  

### 14.3 Phase 2

Git becomes enforcement layer — not a second author of truth.

---

## 15. Cursor operating model

### 15.1 Workspaces

| Workspace | Use |
|-----------|-----|
| **SinaaiMonoRepo** | All mono build + main chat history |
| **TrustField Technologies** | Commercial delivery only |
| **SinaaiDataBase shell** | Avoid — empty; splits history |

### 15.2 Chat rules

- Research chat: read Source A + B; no edits unless asked  
- Build chat: one repo; Prompt OS one task  
- Old history: MonoRepo → “Architecture replay protocol…” thread  

### 15.3 Prompt OS rule

> **Prompt OS = Cursor adapter under Sina OS — not a third brain.**

---

## 16. MonoRepo consolidation checklist

- [ ] Phase 0 exit signed  
- [ ] ASF picks Phase 1 track (1A / 1B / 1C)  
- [ ] `governance/` committed to git  
- [ ] Canonical Telegram declared  
- [ ] Telegram v1/v2/v3 frozen  
- [ ] Process map committed  
- [ ] Undeclared modules declared or frozen  
- [ ] SSOT mirror matches Source A  
- [ ] Human approval gate tested  
- [ ] LLM chains wired (Phase 1)  
- [ ] Langfuse tracing on multi-agent path  
- [ ] First L2/L3 entries from real ingest (if 1A)  
- [ ] Noetfield scaffold DB (if 1B)  
- [ ] TrustField registry sync after burst (ledger)  

---

## 17. Exit criteria matrix

| Gate | Criterion |
|------|-----------|
| **Phase 0 exit** | Source A v3 agreed; Source B conflicts resolved; TrustField DELIVERY locks documented; agent stack policy declared |
| **Phase 1 exit (consolidation)** | Process map in git; one Telegram path; SSOT in git; approval gate tested; gaps in SSOT §10 closed or deferred |
| **Phase 1 exit (1A PAIOS)** | Above + ingestion path + live Telegram loop + 10+ L2 entries |
| **Phase 1 exit (1B Noetfield)** | Above + Noetfield API scaffold + tenant/audit tests |
| **Phase 1 exit (TrustField)** | Commercial gates PASS per founder reports (DELIVERY — may parallelize) |
| **Phase 2 exit** | CI blocking on registry |
| **Phase 3 exit** | Daily brief + stable memory + council optional |
| **Phase 4 exit** | Auto-ingest + dashboard |

---

## 18. SourceA / sourceB file map

### Desktop/sourceA/ (DESIGN — law & policy)

| File | Role |
|------|------|
| `SINA_OS_SSOT_LOCKED.md` | **Master SSOT v3** |
| `SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` | **This roadmap** |
| `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` | Phase 1 forensic work plan |
| `SINAAI_AGENT_STACK_POLICY_v1.md` | Runtime LLM declaration |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | **LOCKED** — multi-project Prompt OS + Farsi reference |
| `SINA_PROMPT_OS_CORE_v1.md` | Index only → locked doc |
| `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` | Conflict tooling (if used) |
| `VIRELUX_REPO_ALIGNMENT.md` | Product alignment notes |

### Desktop/sourceB/ (alignment — not law)

| File | Role |
|------|------|
| `SOURCE_B_ECOSYSTEM_AND_CONFLICTS_v1.md` | Trees, conflicts, open questions |
| `TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md` | TrustField Cursor mapping |

### SinaaiMonoRepo/ (implementation)

| Path | Role |
|------|------|
| `SinaaiDataBase/governance/` | Registry mirror target |
| `SinaaiDataBase/data/` | Layer A |
| `SinaaiRuntime/` | Execution |
| `ui/` | Dashboard |
| `sourceB/` | Mirror of Desktop sourceB (optional) |

### TrustField Technologies/

| Path | Role |
|------|------|
| `docs/TRUSTFIELD_SOURCE_OF_TRUTH.md` | Delivery SOT |
| `docs/TRUSTFIELD_DELIVERY_ALIGNMENT.md` | DELIVERY locks |
| `os/` | Prompt OS adapter |

---

## 19. Never-do list

1. Treat Cursor chat memory as SSOT  
2. Add a third “OS brain” (Prompt OS, README, blueprint over Source A)  
3. Build Noetfield inside `:8000` Runtime  
4. Activate products without registry + announcement  
5. Stack five Gemini models in one chain  
6. Use leader models for worker tasks  
7. Block TrustField shipping because mono says `executable: false`  
8. Commit Desktop sourceA/sourceB to public git  
9. Force-merge TrustField, Virlux, 777 into one Cursor workspace without plane tags  
10. Skip human approval for production-affecting agent actions  

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-01 | Initial end-to-end master blueprint |

**Supersedes:** informal chat summaries only — not `SINA_OS_SSOT_LOCKED.md`.

**ASF approval (roadmap adopted):** ___________________   **Date:** __________

**Phase 1 track selected (circle one):** 1A PAIOS · 1B Noetfield · 1C Consolidation only · TrustField parallel OK
