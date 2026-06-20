# Sinaai — Agents & Automation Unified Blueprint (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Single reference for all agent, LLM, Cursor, and automation doctrine

**Version:** 1.0 — FINAL LOCKED  
**Classification:** INTERNAL ONLY — never commit to git, never push online  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/sourceA/SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 (ecosystem structure only)  
**Scope:** Agents, automation, Prompt OS, Cursor, Runtime LLM, Telegram/GitHub Lab orchestration — **nothing else**  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## Conflict resolution (FINAL)

**There is no architecture conflict.** Target = weekly ASF strategy + daily Prompt OS Core prompt factory.  
**Canonical decision:** `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`  
**Build next:** `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md`  
**Do not add** another merged blueprint or SSOT.

---

> **Lock statement.**  
> This is the **only blueprint** agents and humans should read for **agents & automation**.  
> It **unifies** the documents listed in §0 without replacing SSOT, Phase 1 product plans, commercial GTM docs, or Noetfield product specs.  
> **Do not edit** superseded one-pagers for new rules — update **this file** and bump version.

---

## 0. Supersession map (agents & automation only)

| Prior document | Status after this file |
|----------------|------------------------|
| `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` | **ACTIVE** — conflict resolution; read before this file for “what we decided” |
| `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | **ACTIVE** — build order M0–M9 |
| `SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md` | **ACTIVE** — production layout + daemon + dashboard (§5 extension) |
| Chat “Production OS merged” | **Narrative only — not law** |
| `SINAAI_AGENT_STACK_POLICY_v1.md` | **Superseded** — content merged §7–8 |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | **Superseded** — content merged §4–6 (keep Farsi § as mirror in that file OR read §5 here) |
| `SINA_PROMPT_OS_CORE_v1.md` | Index only → this file |
| `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` | **Still active** for multi-plane conflicts — agent rules summarized §12 |
| `AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md` | Example only — not doctrine |
| `SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` | Unchanged — roadmap; agent sections defer here |
| `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` | Unchanged — mono consolidation; **agent exit tests** duplicated §14 |
| `sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md` | Active adapter map — referenced §6.4 |

**Implementation (not blueprint):** `Desktop/SinaPromptOS/` — runnable MVP.

---

## Table of contents

1. [North star & ASF operating model](#1-north-star--asf-operating-model)  
2. [Two execution planes](#2-two-execution-planes)  
3. [Authority stack (who decides what)](#3-authority-stack-who-decides-what)  
4. [Autonomy ladder](#4-autonomy-ladder)  
5. [Sina Prompt OS — unified spec](#5-sina-prompt-os--unified-spec)  
6. [Cursor automation plane](#6-cursor-automation-plane)  
7. [SinaaiRuntime agent company](#7-sinaairuntime-agent-company)  
8. [LLM stack & failover](#8-llm-stack--failover)  
9. [Triggers & human gates](#9-triggers--human-gates)  
10. [PAIOS personal agents (Layer A + Runtime)](#10-paios-personal-agents-layer-a--runtime)  
11. [Per-repo `os/` contract](#11-per-repo-os-contract)  
12. [Conflict rules for agents](#12-conflict-rules-for-agents)  
13. [Multi-product registry](#13-multi-product-registry)  
14. [Phase gates (agents & automation only)](#14-phase-gates-agents--automation-only)  
15. [Phase 1 wiring checklist](#15-phase-1-wiring-checklist)  
16. [Never-do list](#16-never-do-list)  
17. [Read order & file map](#17-read-order--file-map)  

---

## 1. North star & ASF operating model

### 1.1 What we are building

> **An AI-assisted execution system** that remembers all parallel projects, picks the next tactical step, produces one Cursor prompt, and (over time) reduces ASF decision fatigue — **without** replacing ASF on structure or law.

**Today (honest):** `AI-powered dev command center`  
**Target (staged):** `minimal-thinking execution loop` — not fully autonomous software factory until L2+ with gates.

### 1.2 ASF mental model (locked)

| Mode | Duration | ASF role | System role |
|------|----------|----------|-------------|
| **Think** | ~1 day / week | Set priority, law, freeze exceptions | Sina OS + `projects.json` |
| **Execute** | ~5 days | Paste prompt, verify, approve prod | Prompt OS + Cursor + `plan.json` |

**Pains addressed:** forgotten projects, lost context, decision fatigue, repetitive prompt writing.

### 1.3 Full day of work (canonical — do not use chat memory)

**Document:** `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md`  
**Implementation:** `SinaPromptOS/scripts/run-day.sh` `{morning|now|evening|full}`  
**Outputs:** `SinaPromptOS/data/day/YYYY-MM-DD/morning-summary.md` + `prompt-*.txt` + `evening-summary.md`

| Block | Time | Script |
|-------|------|--------|
| Morning (صبح) | 15–20 min | `run-day.sh morning` |
| Execute 1 & 2 | 3–4 h | Cursor + `plan.json` |
| Midday | 5 min | `run-day.sh now` |
| Evening (شب) | 15 min | `run-day.sh evening` |

§5.7 below is the **loop**; the playbook is the **timetable**.

### 1.3 Full day of work (canonical — do not use chat memory)

**Document:** `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md`  
**Implementation:** `SinaPromptOS/scripts/run-day.sh` `{morning|now|evening|full}`  
**Outputs:** `SinaPromptOS/data/day/YYYY-MM-DD/morning-summary.md` + `prompt-*.txt` + `evening-summary.md`

| Block | Time | Script |
|-------|------|--------|
| Morning (صبح) | 15–20 min | `run-day.sh morning` |
| Execute 1 & 2 | 3–4 h | Cursor + `plan.json` |
| Midday | 5 min | `run-day.sh now` |
| Evening (شب) | 15 min | `run-day.sh evening` |

§5.7 below is the **loop**; the playbook is the **timetable**.

### 1.3 One-line hierarchy

```text
Sina OS = law
Sina Prompt OS + Runtime agents = tactical suggestion & execution
ASF = structural approval + production confirm
Cursor / Telegram = arms
```

---

## 2. Two execution planes

Do not merge these mentally — they share LLM vendors but **different jobs**.

| Plane | ID | Where | Purpose |
|-------|-----|-------|---------|
| **Dev automation** | `PROMPT_PLANE` | Cursor + `SinaPromptOS` + per-repo `os/` | Multi-repo **code/ops** tasks across TrustField, VIRLUX, Mono, etc. |
| **Personal runtime** | `RUNTIME_PLANE` | `SinaaiRuntime :8000` | Telegram PAIOS, fleet, GitHub Lab, event bus, ingestion agents |

```text
                    [ SINA OS law ]
                           |
            +--------------+--------------+
            |                             |
    [ PROMPT PLANE ]              [ RUNTIME PLANE ]
    SinaPromptOS                  SinaaiRuntime
    Cursor workspaces             @SinaaiOSbot, fleet
    6 product repos               Agent Spine, loops
```

**Rule:** Prompt OS does **not** route Telegram production traffic. Runtime does **not** generate Cursor prompts for TrustField repo unless explicitly bridged later.

---

## 3. Authority stack (who decides what)

| Question | Authority | May use AI? |
|----------|-----------|-------------|
| What systems may exist? | ASF + Sina OS SSOT + registry | No |
| Which repo gets attention today? | Prompt OS router + ASF override | Yes (ranking) |
| What is the next Cursor task? | `os/plan.json` + Prompt OS | Yes (wording) |
| What code runs in production? | Human approval gate (Telegram) + DELIVERY SOT | Execute only after confirm |
| Which LLM for leader/worker? | This blueprint §8 | Yes (chains) |
| New provider / agent role? | Registry note + ASF | Declare first |

```text
Prompt(repo) = f(Source A, RepoContext, GlobalPriority)

RuntimeReply = f(LeaderChain, WorkerPool, EventBus, HumanGate)
```

---

## 4. Autonomy ladder

| Level | Name | ASF effort | System capability |
|-------|------|------------|-----------------|
| **L0** | Assisted command center | Open UI, copy prompt, paste Cursor, edit plan | **NOW** — `SinaPromptOS` |
| **L1** | Scheduled memory | ~2 min/day | cron snapshot + notify (Telegram optional) |
| **L2** | Verify loop | Approve on FAIL only | auto `plan.json` update after verify script PASS |
| **L3** | Semi-autonomous workers | Strategic only | Cursor SDK / agents per repo + Runtime parallel |

**Locked expectation:** L0 → L1 does **not** require SSOT change. L2+ requires ASF sign-off per repo.

**Anti-pattern:** Skipping to L3 while TrustField gates red → amplifies wrong automation.

---

## 5. Sina Prompt OS — unified spec

### 5.1 Definition

Local **execution router** under Sina OS:

1. Snapshot all `os/plan.json` + Cursor transcript tails  
2. Score projects (priority, blocked, next task, weight)  
3. Emit **one** `CURSOR PROMPT` block  
4. Log to SQLite (`data/sina_prompt_os.db`)

### 5.2 Architecture

```text
Source A (law)
      ↓
SinaPromptOS/core/router.py
      ↓
┌─────┬─────┬─────┬─────┬─────┬─────┐
  TF   Mono  VX   NF   777  SPOS
  os/  os/  os/  os/  os/  os/
      ↓
Cursor workspace (one task)
```

### 5.3 Runnable paths

| Asset | Path |
|-------|------|
| App | `~/Desktop/SinaPromptOS/` (= spec `prompt-os-prod/`) |
| Config | `config/projects.json` + `config/settings.json` |
| **10x cycle** | `python main.py` |
| **Daemon** | `python main.py --daemon` |
| Streamlit UI | `scripts/run-ui.sh` → `:8765` |
| **API dashboard** | `scripts/run-dashboard.sh` → `:8766` → `/ui/` |
| Launcher | `~/Desktop/Sina Prompt OS.command` |
| CLI | `python -m core.cli suggest --copy` |
| Doctrine | `SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md` |

### 5.4 Scoring (v1 rules)

| Signal | Weight intent |
|--------|----------------|
| `global_priority` rank | Higher = sooner |
| `weight` in config | Per-project bias |
| Each `blocked` item | +12 (revenue/risk) |
| `next_tasks[0]` present | +18 |
| Missing `os/` | +6 (scaffold task) |

### 5.5 Execution Truth Layer (locked v1)

**Law:** `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`  
**Code:** `core/execution_tracker.py` + `core/ecosystem_feedback.py`

```text
REPO_STATUS_REPORTS (intent) + REPO_EXECUTION_LOGS (evidence)
  → truth verify → re-rank → ECOSYSTEM_STATUS.md
```

**Parallel unchanged:** up to `max_tasks_per_cycle` prompts; truth applies **per lane** after VERIFY.
| Recent Cursor activity + queue | tie-breaker |

### 5.5 Optional LLM layer

- Env: `OPENROUTER_API_KEY`  
- Module: `core/suggest_ai.py`  
- **Never** overrides rule ranking for structural changes — commentary only in v1.

### 5.6 Validator (per repo)

Each `os/validator.md` must enforce:

- One task per prompt  
- DELIVERY freeze respected (TrustField)  
- VERIFY command named  
- `plan.json` update instruction included  

TrustField template: `TrustField Technologies/os/prompt-engine.md`

### 5.7 Daily loop (target)

```text
Read state → Rank → Prompt → Cursor execute → Verify → Update plan.json → Log SQLite
```

L1 adds: morning push of top 3 tasks. L2 adds: scripted verify → auto done/blocked.

### 5.8 Persian canonical narrative

Approved human reference: `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` §4 — still valid; this blueprint is the English/agent canonical merge.

---

## 6. Cursor automation plane

### 6.1 Cursor role (locked)

| Cursor IS | Cursor IS NOT |
|-----------|----------------|
| Code executor | SSOT author |
| One-task worker | Multi-task roadmap planner |
| Workspace-bound | Cross-repo brain |

### 6.2 Workspace rules

| Workspace | Use for |
|-----------|---------|
| `SinaaiMonoRepo` | PAIOS, governance, Runtime |
| `TrustField Technologies` | DELIVERY commercial |
| `VIRLUX` | VIRLUX DELIVERY |
| `The 777 Foundation` | 777 web |
| Avoid empty `SinaaiDataBase` shell | Splits chat history |

### 6.3 Prompt format (strict)

```text
CURSOR PROMPT — {Project} [{PLANE}]
LAW: Source A + repo os/
WORKSPACE: {absolute path}
SINGLE TASK: {next_tasks[0]}
BLOCKED CONTEXT: {if any}
VERIFY: {one command}
UPDATE: os/plan.json done|blocked
```

### 6.4 TrustField adapter map

Line-by-line: `sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md`  
Strategy slice must not override Source A or `TRUSTFIELD_SOURCE_OF_TRUTH.md`.

### 6.5 Chat memory

Prompt OS reads: `~/.cursor/projects/{slug}/agent-transcripts/*.jsonl` (tail only).  
**Chat is not SSOT** — context hint only.

---

## 7. SinaaiRuntime agent company

**Scope:** `SinaaiRuntime/` only — Phase 1 wiring after ASF approval.

### 7.1 Entry points (reality)

| Entry | Path / port | Role |
|-------|-------------|------|
| **Agent Spine** | `agents/runtime/agent_spine.py` | Central task execution |
| **loop_engine** | `agents/loop_engine/` | Background loops (declare in registry Phase 1) |
| **liaison** | integrations/telegram | Human-facing router |
| **fleet** | `fleet/` | Redis workers |
| **GitHub Lab** | `integrations/github_lab/` | Issue/PR → spine |
| **event_bus** | internal pub/sub | Worker coordination |
| **golden_edge** | `:8001` | Scoring — not governance |

**Debt:** 40 agent dirs, 5 Telegram trees — Phase 1 = **one** canonical Telegram, freeze others.

### 7.2 Agent roles (locked intent)

| Agent ID | Job | Plane |
|----------|-----|-------|
| `liaison` / `brain` | Route, synthesize final reply | Leader path |
| `chief_of_staff` | Priorities, brief, escalate to ASF | Leader + L4 mandates |
| `analyst` | Patterns, LAW conflicts | Worker |
| `lead_scout` | Web + corpus research | Worker + Tavily |
| `outreach_writer` | Drafts at volume | Worker |
| `operator` | Scripts, approved automation | Worker |
| `batch_ingest` | Overnight summarize / ingest | Mistral batch only |

**Leadership rule:** Exactly **one** leader synthesis after workers — not first-reply-wins.

### 7.3 Multi-agent flow (Telegram)

```text
Human (@SinaaiOSbot)
  → liaison (route)
  → workers parallel (scout, analyst, writer)
  → event_bus
  → LEADER synthesis (one call)
  → reply
  → [if prod impact] → human confirm → execute
```

### 7.4 Layer A binding

| Layer | Agent use |
|-------|-----------|
| L1-identity | Non-negotiables — flag violations |
| L2-knowledge | Read after promotion |
| L3-process | Approved procedures only |
| L4-agents | Mandates per agent |

Ingestion agent (Phase 1+): writes **only** via approved pipeline to L2/L3.

### 7.5 AI Council (future — Phase 3+)

Optional panel: multiple models debate → **one** leader output.  
Hosts: n8n `:5678` or Runtime module — **not** Prompt OS.

---

## 8. LLM stack & failover

### 8.1 Stack layers

| L | Component | Role |
|---|-----------|------|
| L0 | Upstash Ratelimit / local guard | RPM protection |
| L1 | LiteLLM or OpenRouter | Router |
| L2 | Leader chain | Synthesis |
| L3 | Worker pool | Volume |
| L4 | Tavily + Exa | Research |
| L5 | Supabase + event bus + SQLite | Memory |
| L6 | Langfuse | Traces |
| L7 | Ollama | Last resort (`OLLAMA_ENABLED=false` until declared) |

### 8.2 Leader chain (order locked)

```text
openrouter:deepseek/deepseek-r1-0528:free
  → gemini:gemini-2.5-flash
  → openrouter:meta-llama/llama-3.3-70b-instruct:free
  → github-models:gpt-4o
```

### 8.3 Worker chain (order locked)

```text
groq:llama-3.1-8b-instant
  → gemini:gemini-2.5-flash-lite
  → cerebras:llama-3.1-8b
  → openrouter:openrouter/free
  → mistral:mistral-small (batch only)
```

### 8.4 Agent → provider map

| Agent | Primary | Backup | Never |
|-------|---------|--------|-------|
| liaison/brain | DeepSeek R1 | Gemini Flash | worker models |
| analyst | Cerebras | Mistral small | leader |
| lead_scout | Tavily + Groq 8B | Exa | leader |
| outreach_writer | OR `:free` | Mistral batch | DeepSeek R1 |
| operator | Groq 8B | Cerebras 8B | leader |
| batch | Mistral Experiment | Ollama | real-time TG |

### 8.5 Runtime rules R1–R7

| # | Rule |
|---|------|
| R1 | Never single-vendor chain |
| R2 | Leaders not on trivial tasks |
| R3 | Cloud-first; Ollama last |
| R4 | Noetfield compliance data read-only for Runtime agents |
| R5 | New providers → registry declaration |
| R6 | Langfuse before scaling agent count |
| R7 | One canonical Telegram |

### 8.6 Never-silent test (Phase 1 exit)

Disable Gemini → Telegram reply within 30s via failover chain.

### 8.7 Tier 0 services (implement order)

OpenRouter → Groq → Cerebras → Gemini (≤2 leader) → Mistral Experiment → GitHub Models → Tavily → Langfuse → LiteLLM → Upstash → Ollama.

**Already use:** Supabase, event bus, fleet, SQLite tasks, n8n, GitHub Lab, `@SinaaiOSbot`.

---

## 9. Triggers & human gates

| Trigger | Target | Automation level |
|---------|--------|------------------|
| ASF opens Prompt OS UI | Best Cursor prompt | L0 |
| Cron `daily-snapshot.sh` | SQLite snapshot | L1 |
| Telegram message | Runtime agents | L0–L2 |
| GitHub webhook | Agent Spine | L1 |
| n8n workflow | External glue | Optional |
| Cloud Agent (Cursor) | Repo-scoped | Same as Cursor rules |

### Human approval gate (production — locked)

Any Runtime agent action that:

- deploys,
- changes production data,
- alters DNS/infra,

requires **explicit ASF confirm on Telegram** before execute.

**Phase 1 exit:** Live test documented — not intent-only.

Prompt OS **does not** bypass this gate — it may only **suggest** infra tasks in DELIVERY repos for ASF to run in Cursor.

---

## 10. PAIOS personal agents (Layer A + Runtime)

**Not** the same as Prompt OS — PAIOS is **life/work OS** on Runtime spine.

| Capability | Phase | Owner |
|------------|-------|-------|
| Chief-of-Staff daily brief | 3 | liaison + L4 |
| Ingestion pipeline | 1–2 | operator + approved writes |
| Conflict vs non-negotiables | 1+ | analyst |
| Memory bridge Supabase | 3 | Runtime |

Prompt OS may **suggest** MonoRepo tasks that advance PAIOS (ingestion, Telegram declare) — execution still via Cursor on `SinaaiMonoRepo`.

---

## 11. Per-repo `os/` contract

Every project in `SinaPromptOS/config/projects.json` must maintain:

```
{repo}/os/
  strategy.md    # execution slice — subordinate to Source A + delivery SOT
  plan.json      # next_tasks[], done[], blocked[]
  prompt-engine.md   # optional — Cursor adapter rules
  validator.md       # optional — freeze + one-task checks
```

### plan.json schema (minimum)

```json
{
  "repo": "string",
  "plane": "DESIGN|DELIVERY",
  "phase": "string",
  "active_focus": "string",
  "authority": {},
  "next_tasks": ["string"],
  "done": ["string"],
  "blocked": [{ "item": "string", "reason": "string" }],
  "updated_at": "YYYY-MM-DD"
}
```

**Update rule:** After every Cursor session that executed a task — move task to `done` or `blocked` with VERIFY evidence.

---

## 12. Conflict rules for agents

From Auto-Conflict Engine v3 — **agent-relevant only:**

| Layer | Agents must… |
|-------|----------------|
| DESIGN (SSOT) | Re-read before structural work; never invent registry |
| EXECUTION (Runtime) | Treat `:8000` reality as operational truth |
| DELIVERY (product repos) | Ship without registry blocking; sync ledger after burst |

**Prompt OS sits in DESIGN-adjacent tooling** — suggests only; does not activate products.

When SSOT says TrustField = corpus but DELIVERY repo is live → **DELIVERY alignment wins for ops** until registry updated.

---

## 13. Multi-product registry

Locked in `SinaPromptOS/config/projects.json`:

| id | plane | primary automation |
|----|-------|-------------------|
| trustfield | DELIVERY | Prompt OS → Cursor → founder scripts |
| sinaai_mono | DESIGN | Prompt OS + Runtime spine |
| virlux | DELIVERY | Prompt OS → staging scripts |
| noetfield | DESIGN | Prompt OS → docs/spec tasks only |
| seven77 | DELIVERY | Prompt OS → web ops |
| sina_prompt_os | DESIGN | Tooling meta |

**Parallel execution:** all may advance same week; **global_priority** breaks ties.

---

## 14. Phase gates (agents & automation only)

| Gate | Criterion |
|------|-----------|
| **Phase 0** | This blueprint + agent stack declared; Prompt OS MVP running |
| **Phase 1 entry** | ASF signs Phase 0 exit; picks track |
| **Phase 1 agent exit** | Leader/worker env wired; never-silent PASS; one Telegram canonical; approval gate tested; Langfuse on multi-agent path; undeclared modules declared or frozen |
| **Phase 2** | CI + registry enforcement for agent paths |
| **L1 automation** | Daily snapshot scheduled |
| **L2 automation** | Per-repo verify scripts tied to plan updates |

---

## 15. Phase 1 wiring checklist

- [ ] `AGENT_LEADER_CHAIN` / `AGENT_WORKER_CHAIN` in Runtime `.env`
- [ ] Map agent dirs → provider map §8.4
- [ ] Langfuse traces on Telegram multi-agent path
- [ ] Declare or freeze: `loop_engine`, `civilization`, etc.
- [ ] Single Telegram import path
- [ ] Human approval gate e2e test
- [ ] Prompt OS: all 6 projects have valid `os/plan.json`
- [ ] Never-silent test recorded
- [ ] No new FastAPI stacks on mono spine

---

## 16. Never-do list

1. Prompt OS or Cursor changes Source A / registry without ASF  
2. Third “OS brain” (chat memory, README, blueprint > SSOT)  
3. Leader models on worker tasks  
4. Five Gemini models in one chain  
5. Runtime writes Noetfield compliance records  
6. Fully autonomous prod deploy without human gate  
7. TrustField feature work under engineering freeze  
8. Prompt OS suggests random features bypassing `next_tasks[0]`  
9. 38 LLM providers at once — use Tier 0 order only  
10. Commit Desktop `sourceA/` or Prompt OS DB to public git  

---

## 17. Read order & file map

### Read order (agent or automation session)

```
1. SINA_OS_SSOT_LOCKED.md v3
2. SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md
3. SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md  ← this file
4. PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md
5. AUTO_CONFLICT_ENGINE_V3_LOCKED.md  (if plane clash)
6. SinaaiMonoRepo/AGENTS.md
7. Repo-local os/plan.json
```

### File map

| File | Role |
|------|------|
| **This file** | Unified agents & automation blueprint |
| `SINA_OS_SSOT_LOCKED.md` | Ecosystem law |
| `SinaPromptOS/` | Prompt OS Core implementation |
| `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` | Conflict resolved + Sun/Mon–Fri model |
| `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | Build order M0–M9 |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | Farsi narrative mirror |
2. SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md  ← this file
3. AUTO_CONFLICT_ENGINE_V3_LOCKED.md  (if DESIGN vs DELIVERY vs EXECUTION clash)
4. SinaaiMonoRepo/AGENTS.md
5. Repo-local os/plan.json + strategy.md
6. sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md  (TrustField Cursor only)
```

### File map

| File | Role |
|------|------|
| **This file** | Unified agents & automation blueprint |
| `SINA_OS_SSOT_LOCKED.md` | Ecosystem law |
| `SinaPromptOS/` | Prompt OS implementation |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | Farsi narrative mirror |
| `SINAAI_AGENT_STACK_POLICY_v1.md` | Archived — see §8 |
| `sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md` | TrustField mapping |

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-02 | Initial unified lock — merges Prompt OS + agent stack + autonomy + Cursor + Runtime |

**ASF approval:** ___________________ **Date:** __________

**Phase 1 agent wiring authorized:** ☐ Yes ☐ No (declare only until checked)
