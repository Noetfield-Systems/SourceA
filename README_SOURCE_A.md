# Source A — read this first

**Path:** `~/Desktop/SourceA/`  
**Goal:** New agent understands system in **≤30 minutes** — then executes.

---

## STEP 0 — START HERE (June 2026 — role picker)

**`entry/START_HERE_LOCKED_v1.md`** — pick Brain · Worker · Founder · Research · parallel lane.  
**Mandatory reads by role:** `entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md`  
**Folder map:** `entry/FOLDER_MAP_LOCKED_v1.md` · **Root law index:** `entry/LAW_ROOT_INDEX_LOCKED_v1.md`

Do not read 102 root `*_LOCKED*.md` files blindly — use indexes above.

---

## STEP 0b — GOVERNANCE ROUTER (topic branch)

**`SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`** — branch by task; law registry → **`SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md`**.  
Older versions only in `archive/superseded/`.

**Chat handoffs:** `os/chat-handoffs/MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md` · `os/chat-handoffs/README_INDEX_LOCKED_v1.md`

---

## LEVEL 1 — MANDATORY (read these, then STOP)

| # | File |
|---|------|
| 1 | `README_SOURCE_A.md` (this file) |
| 2 | `SINA_OS_SSOT_LOCKED.md` |
| 3 | `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` |
| 4 | `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` |
| 5 | `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` ← **current operational law (SA-019)** |

**STOP** after LEVEL 1 unless your task branch (governance entry §1–§8) requires more.

**Whole-system progress (daily):** `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` · state `PROGRAM_PROGRESS.json` · refresh `./scripts/update-program-progress.sh`

---

## Morning execution route (4 steps)

```bash
cd ~/Desktop/SourceA && ./scripts/update-program-progress.sh
# Read ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md — P0 + open todos
cd ~/Desktop/SinaPromptOS && ./scripts/run-architect.sh
# Read SourceA/ARCHITECT_REPORT.yaml — system_blockers only (max 5)
cd ~/Desktop/SinaPromptOS && ./scripts/run-full-day.sh
# 5× Cursor paste → VERIFY → ingest-cursor-reply.sh
```

---

## Phase vocabulary

| Prefix | Meaning |
|--------|---------|
| **GOV_PHASE_*** | Governance (mono, git, registry) |
| **EXEC_PHASE_*** | Prompt OS execution |

Never bare "Phase 1/2". **EXEC_PHASE_2** = built, **not** daily driver (SA-019).

---

## Architect v2 (thinking layer)

- **Not:** contradiction hunting, registry police, document perfection  
- **Is:** max **5 system blockers** + consolidation list + this route  
- Output: `ARCHITECT_REPORT.yaml`  
- Law: `SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md`

---

## Project docs (architecture · runbook · onboarding)

| Doc | Purpose |
|-----|---------|
| `docs/ARCHITECTURE.md` | Hub stack, four planes, C1–C7, dispatch, SSOT layout |
| `docs/RUNBOOK.md` | Start/stop, build, validators, incidents (founder vs executor) |
| `docs/ONBOARDING.md` | ≤30 min path — founder, maintainer, lane roles |

Agents Window task **10** — catalog: `FOUNDER_AGENT_USE_GUIDE_LOCKED_v1.md`

---

## Optional (only when needed)

| Need | File |
|------|------|
| Lost | `SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md` |
| Agents | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` |
| **Understanding roles (map)** | `UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md` |
| **Parked vs ship (vocab)** | `PLAN_STATUS_VOCAB_LOCKED_v1.md` |
| Agent desk | `AGENT_DESK_START_HERE.md` |
| Daily hours | `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` |
| Ingest | `SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md` |
| 5 repos | `ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md` |
| No card | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` |

**RUNTIME/** files are generated — never “conflict” law.

**Narrative** blueprints (MASTER_PLAN_FA, END_TO_END) = history — not daily law.
