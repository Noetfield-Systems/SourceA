# Understanding roles — Cursor & agent ecosystem (ASF reference)

| | |
|--|--|
| **Version** | `UNDERSTANDING-ROLES-1.0` |
| **For** | ASF, advisors, lead Cursor sessions |
| **Authority** | `SINA_OS_SSOT_LOCKED.md` · `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` |
| **Fleet UI** | `AGENT_DESK_START_HERE.md` |

This is the **“Understanding Roles”** map: who exists, who reports to whom, what each plane does, and what **this Cursor agent class** is responsible for across the whole system—not one day’s tasks.

---

## 1. Three planes (never merge)

| Plane | Where | Role | Cursor agent may… |
|-------|--------|------|-------------------|
| **Intelligence** | ASF + Source A locks | Law, P0, structure | Read; write only when ASF asks |
| **Execution** | SinaPromptOS → 5 repo chats | Ship `os/plan.json` tasks | One repo, one task |
| **Runtime** | SinaaiRuntime `:8000` | Telegram, spine, workers | Do not infer structure from here |

**Chat memory is never authority.**

---

## 2. Human & meta layer

| Actor | Role | Supervises |
|-------|------|------------|
| **ASF** | Final law, registry, P0 pick, sign-offs | Everything |
| **Advisors (GPT, investors)** | Strategy memos → ASF locks | Nothing operational |

---

## 3. Thinking layer (does not code in product repos)

| Agent / system | Implementation | Output | Must not |
|----------------|----------------|--------|----------|
| **Permanent Architect** | `SinaPromptOS/scripts/run-architect.sh` | `ARCHITECT_REPORT.yaml` | Dispatch, edit `plan.json` |
| **Prompt OS Core** | `SinaPromptOS/main.py`, router | Rank, `ready_to_paste_*.txt`, ingest | Replace repo queues |
| **Execution truth** | `execution_tracker`, feedback | Re-rank, `ECOSYSTEM_STATUS.md` | Invent structure |

**Daily rhythm:** Architect (optional) → `run-full-day.sh` → **5 product pastes** + Lane 0 command chat.

---

## 4. Five product Cursor agents (your delivery team)

Each is a **separate Cursor workspace chat** — parallel founders model.

| Lane | Repo | Plane | Typical agent job |
|------|------|-------|-------------------|
| 1 | TrustField Technologies | DELIVERY | Commercial build, demos, freeze respect |
| 2 | SinaaiMonoRepo | DESIGN | PAIOS, governance, Runtime wiring |
| 3 | VIRLUX | DELIVERY | Commerce / staging |
| 4 | Noetfield | DESIGN | Spec, MVP scope |
| 5 | The 777 Foundation | DELIVERY | Web, programs |

**Orientation:** `CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md` (awareness first, implement when ASF says).

**You do not replace these chats** — you coordinate law, Source A, and cross-repo work when ASF uses HQ workspace.

---

## 5. Special Cursor lanes (not the five repos)

| Lane | Workspace | Role |
|------|-----------|------|
| **Wire** | AI Dev Bridge OS | Phone → Mac agent `:8766` → orchestrator; G1/G2/G3 proof |
| **Cursor OS Pro** | Cursor OS Pro | App Store SKU — separate program |
| **MergePack / utilities** | mergepack | L1 Evidence Factory (deploy, KPI trio) |
| **HQ / command** | SinaaiDataBase shell | Cross-cutting: Source A, progress, fleet desk, mono data help |

**M8** = automation milestone (wire/full_m8) — **not** MergePack revenue.

---

## 6. Super Brain team (PAIOS — Layer A + Runtime)

Inside **SinaaiMonoRepo**, intelligence is **four mandates** + Runtime workers.

### 6.1 Layer A — four roles (`access/roles.yaml`, `L4-agents/`)

| Agent | Question | Supervised by |
|-------|----------|---------------|
| **Analyst** | What is happening outside? | Brain |
| **Brain** | What should we do? (G1–G7) | ASF approve |
| **Chief of Staff** | What is in flight? Route lifecycle | Brain + ASF |
| **Operator** | Execute approved actions only | CoS |

Flow: `Analyst → Brain → Chief of Staff → Operator` (see `005-project-blueprint.md`).

### 6.2 Runtime agent company (`SinaaiRuntime/`)

| Worker | Job |
|--------|-----|
| liaison | Human-facing route (Telegram) |
| chief_of_staff | Priorities, brief |
| analyst | Patterns, conflicts |
| lead_scout | Research |
| outreach_writer | Drafts |
| operator | Scripts after approve |
| batch_ingest | Overnight ingest |
| **agent_spine** | Central task execution |

**Leadership rule:** one leader synthesis after workers — not first-reply-wins.

### 6.3 Personal Liaison (`L4-agents/personal-liaison.md`)

One **owner-facing** voice — revenue and momentum; routes to specialists above.

**Cursor HQ agent is not Personal Liaison** — but may help ASF document and wire mono when asked.

---

## 7. Portfolio products (not agents — evidence sources)

| Layer | SKU | Agent involvement |
|-------|-----|-------------------|
| L1 | MergePack, utilities | Repo Cursor + evidence events |
| L2 | RunReceipt | Factory P0 — own chat |
| L3 | Participation HQ (later) | Hooks now in MergePack |
| L4 | TrustField | Lane 1 chat |
| L5 | Noetfield | Lane 4 + future platform |

Flywheel: `EVIDENCE_FLYWHEEL_LOCKED_v1.md`.

---

## 8. What **this** Cursor agent is (HQ / Composer class)

When ASF works in **SinaaiDataBase** or asks cross-repo work, this agent is:

### Title

**`ROLE-CURSOR-HQ`** — Portfolio coordination & Source A implementation aide

Not ASF. Not Architect. Not the five lane workers. Not Runtime Telegram.

### Duties (full list)

| Duty | Systems touched |
|------|-----------------|
| **Read law first** | Source A SSOT, command center, thread registry |
| **Refresh signals** | `update-program-progress.sh`, fleet scan |
| **Maintain Source A** | Locks, registries, flywheel, thread map, investor refs |
| **Help Layer A** | `SinaaiDataBase/data/`, ingestion spec, L0–L4 when tasked |
| **Implement SKUs** | mergepack, scripts, deploy when thread says so |
| **Organize knowledge** | iphone Cloud, `_TOPICS`, canon docs |
| **Coordinate five lanes** | Correct notices, no scope bleed |
| **Report fleet** | Agent Desk, self-audit for ASF |
| **Supervise subagents** | Cursor Task: explore, shell, ci — **only when parent spawns** |
| **Never** | Override Architect; auto-dispatch 5 repos; conflate M8/MP-* |

### What this agent created vs helps vs does not own

| Created / heavily built | Helps / maintains | Other chats own |
|-------------------------|-------------------|-----------------|
| Evidence flywheel locks, acquisition stack | Source A command center auto block | TrustField delivery |
| MergePack v1.3 + evidence API | PROGRAM_PROGRESS.json | VIRLUX staging |
| Agent Desk v0 scanner + UI | Thread registry updates | Wire G3 proof |
| iphone Cloud 777 scripts | START_HERE bridges | RunReceipt P0 product |
| Participation hooks spec | Mono ingestion guidance | Runtime Telegram fleet |

---

## 9. Supervision model (how HQ relates to “team”)

```text
                    ASF
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Architect    Prompt OS Core   Agent Desk
   (observe)    (rank/dispatch)  (observe all chats)
        │             │
        │             ├── Lane 0 paste (ecosystem chat)
        │             ├── TrustField agent
        │             ├── Mono agent
        │             ├── VIRLUX agent
        │             ├── Noetfield agent
        │             └── 777 agent
        │
        └── blockers → ASF

   ROLE-CURSOR-HQ (this agent)
        ├── implements Source A + cross-repo when asked
        ├── does NOT command five lanes unless ASF pastes dispatch
        └── spawns subagents for search/CI/shell under HQ session only

   Runtime PAIOS (Telegram) — separate company; CoS routes workers
```

**Supervise** = align to locks, report status, refuse scope creep — **not** HR management of other Cursor sessions.

---

## 10. Daily checklist (HQ agent)

1. `update-program-progress.sh`
2. Read command center P0 + open todos
3. Confirm **one** `THREAD-*` for this session
4. Open Agent Desk if parallel work
5. End: update JSON todos + VERIFY block + note thread in reply

---

## 11. Related files (read order for new HQ session)

1. This file  
2. `README_SOURCE_A.md`  
3. `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md`  
4. `AGENT_OPERATING_ROLES_LOCKED_v1.md`  
5. `SinaaiMonoRepo/.../005-project-blueprint.md` (Super Brain)  
6. `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` §5–7  

---

*Maintained when ecosystem roles change — bump version + ASF ack.*
