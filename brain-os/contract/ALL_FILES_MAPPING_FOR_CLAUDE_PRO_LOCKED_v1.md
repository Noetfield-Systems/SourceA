# All Files Mapping — Claude Pro External Advisor (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-07  
**Parent:** `SOURCEA_EXTERNAL_ADVISOR_CONTRACT_LOCKED_v3.md`  
**Purpose:** Full absolute-path map of the SourceA ecosystem for Claude Pro — including everything **outside** `SourceA/brain-os/` attach folder.

**Mac user:** `sinakazemnezhad`  
**Home:** `/Users/sinakazemnezhad/`

---

## 0. How Claude Pro uses this file

| Layer | Full path | Attach to Claude project? |
|-------|-----------|---------------------------|
| **Governance SSOT** | `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/` | **YES — whole folder** |
| **Advisor contract** | `…/brain-os/contract/SOURCEA_EXTERNAL_ADVISOR_CONTRACT_LOCKED_v3.md` | Included in attach |
| **This mapping** | `…/brain-os/contract/ALL_FILES_MAPPING_FOR_CLAUDE_PRO_LOCKED_v1.md` | Included in attach |
| **Runtime truth** | `/Users/sinakazemnezhad/.sina/` | **NO bulk attach** — ASF pastes snapshots only |
| **Product repos** | Desktop paths in §4 | **Optional** per session (FORGE most common) |
| **Archive** | `SinaaiDataBase/` | **NO** — keyword search / broker only |

**Missing path or snapshot:** say **"Insufficient project evidence."** Never invent state.

---

## 1. Three-layer model (whole machine)

```text
GOVERNANCE     brain-os/ + SourceA locked docs + REGISTRY
REPOSITORY     SourceA tree + product repos on Desktop
RUNTIME        ~/.sina/ receipts, queue, orchestrator, research-root
```

**Hub (founder only — no Terminal):** `http://127.0.0.1:13020`

---

## 2. SourceA repo — inside attach vs outside attach

**Repo root:** `/Users/sinakazemnezhad/Desktop/SourceA/`

### 2a. Attached to Claude (brain-os/ — unified SSOT)

**Root:** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/`

| Folder | Full path | Contents |
|--------|-----------|----------|
| `entry/` | `…/brain-os/law/entry/` | START HERE, mandatory read by role |
| `law/` | `…/brain-os/law/` | Unified rules, authority, critic law, no-Terminal |
| `memory/` | `…/brain-os/memory/` | Knowledge index, founder intent, system map |
| `contract/` | `…/brain-os/contract/` | Brain chat, advisor v3, **this file** |
| `enforcement/` | `…/brain-os/law/enforcement/` | Disk-before-chat, Goal1 chain, drain rail |
| `incidents/` | `…/brain-os/incidents/` | Brain/worker cross, unvalidated proof |
| `system/` | `…/brain-os/system/` | Governed OS, goal hierarchy, daily ops |
| `wtm/` | `…/brain-os/wtm/` | World Target Model locked laws (12 files) |
| `plan-registry/` | `…/brain-os/plan-registry/` | SOURCEA-PRIORITY, REGISTRY.json, sa prompts, **worker-dual-40** (10+10 compressed v1.1) |
| Worker pack law | `…/brain-os/contract/WORKER_PROMPT_PACK_FORMAT_LOCKED_v1.md` | **LOCKED v1.1** — one paste/turn; E2E-3 every 3; DEBUG-5 every 5; no CHECK/ACT/VERIFY splits |
| `lanes/` | `…/brain-os/lanes/` | Parallel lane handoffs (TrustField, Noetfield, …) |
| `scripts/` | `…/brain-os/scripts/` | Brain executors + validators (**canonical**) |
| `cursor/rules/` | `…/brain-os/cursor/rules/` | Brain-related `.mdc` mirror (9 files) |
| `runtime/` | `…/brain-os/runtime/` | `~/.sina/` receipt path index (docs only) |

**Master index:** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/INDEX_LOCKED_v1.md`  
**Folder map:** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/FOLDER_MAP_LOCKED_v1.md`  
**Path resolver (code):** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/scripts/brain_os_paths.py`

### 2b. SourceA repo — NOT in brain-os attach (execution surfaces)

| Area | Full path | Role |
|------|-----------|------|
| **Hub UI source** | `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/` | Sina Command panel |
| **Hub generated data** | `…/agent-control-panel/command-data.json` | Generated — not law |
| **Shared scripts** | `/Users/sinakazemnezhad/Desktop/SourceA/scripts/` | Worker, hub, goal1, validators; `brain_*` **shims** → `brain-os/scripts/` |
| **Goal progress** | `…/scripts/goal-progress-v1.py` | `--json` for REGISTRY progress |
| **Live pick** | `…/scripts/plan-no-asf-run.sh pick 1` | Brain/Worker run — advisor cites only |
| **Worker inbox status** | `…/scripts/worker_inject_lib.py --status` | Inbox pending check |
| **Gates** | `…/scripts/brain_validate_goal1_v1.py --json` | Shim to `brain-os/scripts/` |
| **Pre-LLM** | `…/scripts/pre_llm/` | WTM D-modules |
| **RunReceipt SKU** | `…/product/` | T2b factory docs |
| **Brand** | `…/brand/` | Brand assets |
| **Investor** | `…/investor/` | Pitch materials |
| **Docs / audits** | `…/docs/` · `…/docs/system-audits/` | System audits vault |
| **Knowledge library** | `…/knowledge-library/` | Reference |
| **Execution logs** | `…/REPO_EXECUTION_LOGS/` | Batch logs in repo |
| **Archive (in-repo)** | `…/archive/` | In-repo archive |
| **Cursor rules (live)** | `/Users/sinakazemnezhad/Desktop/SourceA/.cursor/rules/` | 15 `.mdc` — 6 not mirrored to brain-os |
| **Legacy stubs** | `…/os/MOVED.md` · `…/entry/MOVED.md` | Pointers only — not law |
| **Repo pointer** | `…/BRAIN_OS_POINTER_LOCKED_v1.md` | Points to brain-os |

### 2c. SourceA repo root — ecosystem law NOT yet in brain-os (87 full files)

**Path pattern:** `/Users/sinakazemnezhad/Desktop/SourceA/*_LOCKED*.md` (repo root only)

| Prefix | Count | Examples (advisor may need for deep governance compare) |
|--------|------:|-----------------------------------------------------------|
| `SINA_*` | 24 | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`, `SINA_HUB_ESSENTIALS_LOCKED_v1.md` |
| `AGENT_*` | 16 | `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md`, `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` |
| `SINAAI_*` | 13 | Monorepo / automation spine laws |
| `ASF_*` | 5 | Program / command-center laws |
| `FOUNDER_*` | 4 | Founder operating laws |
| Other | 25 | `GOVERNANCE_*`, `ECOSYSTEM_*`, `HUB_*`, `PRODUCT_*`, etc. |

**MOVED stubs at root (19):** point into `brain-os/` — not full law.

**Law:** If comparing governance and file not in attach → **Insufficient project evidence** unless ASF pastes or attaches root file.

### 2d. Cursor rules — root-only (not mirrored)

`/Users/sinakazemnezhad/Desktop/SourceA/.cursor/rules/`

| File | Mirrored in brain-os? |
|------|----------------------|
| `sina-command-protected.mdc` | No |
| `sina-command-ui.mdc` | No |
| `prompt-queue.mdc` | No |
| `sina-advisor.mdc` | No |
| `semej-agent.mdc` | No |
| `sourcea-worker-inbox.mdc` | No |

---

## 3. Runtime layer — `~/.sina/` (outside repo, live Mac)

**Root:** `/Users/sinakazemnezhad/.sina/`

### 3a. Goal-1 / Brain loop receipts

| Signal | Full path |
|--------|-----------|
| Orchestrator state | `/Users/sinakazemnezhad/.sina/healthy-drain-orchestrator-v1.json` |
| Healthy queue | `/Users/sinakazemnezhad/.sina/healthy-queue-30-active.json` |
| Worker inbox | `/Users/sinakazemnezhad/.sina/worker-prompt-inbox-v1.json` |
| Batch log (**RUNNING rule**) | `/Users/sinakazemnezhad/.sina/goal1-worker-batch-latest.log` |
| Lane broker | `/Users/sinakazemnezhad/.sina/goal1-lane-broker-v1.json` |
| Brain session receipt | `/Users/sinakazemnezhad/.sina/brain_session_receipt_v1.json` |
| Goal1 validation | `/Users/sinakazemnezhad/.sina/brain-goal1-validation-v1.json` |
| Entry gate receipt | `/Users/sinakazemnezhad/.sina/cursor_entry_gate_receipt_v1.json` |
| Brain narrate / trace / watch | `…/brain-narrate-loop-v1.json` · `…/brain-run-loop-trace-v1.json` · `…/brain-loop-watch-v1.json` |
| Enforcement audit | `/Users/sinakazemnezhad/.sina/brain-enforcement-audit-v1.json` |
| Broker inbox | `/Users/sinakazemnezhad/.sina/brain-broker-inbox-v1.json` |
| LLM context packet | `/Users/sinakazemnezhad/.sina/llm_context_packet_v1.json` |
| Command server log | `/Users/sinakazemnezhad/.sina/command-server.log` |

**RUNNING rule:** only if last `AGENT DONE` in batch log has `broker=yes`.

**Brain pack mirror (sync from brain-os):** `/Users/sinakazemnezhad/.sina/brain/`

**Locked receipt index:** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/runtime/RECEIPTS_INDEX_LOCKED_v1.md`

### 3b. Unified research root

| Item | Full path |
|------|-----------|
| Registry log | `/Users/sinakazemnezhad/.sina/research-root/registry.jsonl` |
| Index manifest | `/Users/sinakazemnezhad/.sina/research-root/INDEX.yaml` |
| Filtered digests dir | `/Users/sinakazemnezhad/.sina/research-root/filtered/` |
| Commercial signal | `…/filtered/commercial.signal.yaml` |
| Governance constraints | `…/filtered/governance.constraints.yaml` |
| Research backlog | `…/filtered/research.backlog.yaml` |
| Execution core digest | `…/filtered/execution_core.digest.yaml` |

**Law doc:** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/system/UNIFIED_RESEARCH_ROOT_LOCKED_v1.md`

### 3c. Agent workspaces (per-lane vaults)

**Root:** `/Users/sinakazemnezhad/.sina/agent-workspaces/`

| Workspace | Full path |
|-----------|-----------|
| Research Acquisitor | `/Users/sinakazemnezhad/.sina/agent-workspaces/research-acquisitor/` |
| TrustField | `/Users/sinakazemnezhad/.sina/agent-workspaces/trustfield/` |
| MergePack | `/Users/sinakazemnezhad/.sina/agent-workspaces/mergepack/` |
| VIRLUX | `/Users/sinakazemnezhad/.sina/agent-workspaces/virlux/` |
| AI Dev Bridge | `/Users/sinakazemnezhad/.sina/agent-workspaces/ai_dev_bridge_os/` |
| Noetfield cloud | `/Users/sinakazemnezhad/.sina/agent-workspaces/noetfield_cloud/` |
| Noetfield local | `/Users/sinakazemnezhad/.sina/agent-workspaces/noetfield_local/` |
| Noetfield OS | `/Users/sinakazemnezhad/.sina/agent-workspaces/noetfeld_os/` |
| 777 Foundation | `/Users/sinakazemnezhad/.sina/agent-workspaces/seven77/` |
| Semej | `/Users/sinakazemnezhad/.sina/agent-workspaces/semej/` |
| Sinaai maintainer | `/Users/sinakazemnezhad/.sina/agent-workspaces/sinaai_maintainer/` |

### 3d. Other runtime (reference)

| Item | Full path |
|------|-----------|
| Agent governance events | `/Users/sinakazemnezhad/.sina/agent-governance-events.jsonl` |
| Agent loop state | `/Users/sinakazemnezhad/.sina/agent-loop.json` |
| Agent research | `/Users/sinakazemnezhad/.sina/agent-research/` |
| Council room | `/Users/sinakazemnezhad/.sina/council-room/` |
| Conflict room | `/Users/sinakazemnezhad/.sina/conflict-room/` |
| Advisor chat state | `/Users/sinakazemnezhad/.sina/advisor-chat.json` |

---

## 4. Desktop ecosystem — outside SourceA repo

**Desktop root:** `/Users/sinakazemnezhad/Desktop/`

### 4a. T0 — Governed automation factory (north star)

| Role | Full path |
|------|-----------|
| SourceA execution core | `/Users/sinakazemnezhad/Desktop/SourceA/` |
| Brain SSOT attach | `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/` |
| Hub | `http://127.0.0.1:13020` |
| Hub source | `/Users/sinakazemnezhad/Desktop/SourceA/agent-control-panel/` |

### 4b. T2 primary — FORGE (default product clock)

| Item | Full path |
|------|-----------|
| Repo root | `/Users/sinakazemnezhad/Desktop/forge/` |
| Launch checklist | `/Users/sinakazemnezhad/Desktop/forge/docs/LAUNCH_CHECKLIST.md` |
| Launch runbook | `/Users/sinakazemnezhad/Desktop/forge/docs/LAUNCH_RUNBOOK.md` |
| PRD | `/Users/sinakazemnezhad/Desktop/forge/docs/PRD.md` |
| Apps | `/Users/sinakazemnezhad/Desktop/forge/apps/` |
| Packages | `/Users/sinakazemnezhad/Desktop/forge/packages/` |
| Scripts | `/Users/sinakazemnezhad/Desktop/forge/scripts/` |
| Docs | `/Users/sinakazemnezhad/Desktop/forge/docs/` |

**Optional Claude attach:** whole `/Users/sinakazemnezhad/Desktop/forge/`

### 4c. T2b — Side SKUs (parallel only — never north star)

| SKU | Full path | Key subpaths |
|-----|-----------|--------------|
| **MergePack** | `/Users/sinakazemnezhad/Desktop/mergepack/` | `docs/`, `backend/`, `frontend/`, `EVIDENCE_FACTORY_LOCKED.md` |
| **RunReceipt** | `/Users/sinakazemnezhad/Desktop/SourceA/product/` | Inside SourceA |
| **Cursor OS Pro** (App Store) | `/Users/sinakazemnezhad/Desktop/AI Dev Bridge OS/mobile/` | Flutter app |
| **DevBridge wire** (Mac agent) | `/Users/sinakazemnezhad/Desktop/AI Dev Bridge OS/` | `agent/`, `apps/`, `PROTOCOL.md` |
| **Cursor OS Pro docs** | `/Users/sinakazemnezhad/Desktop/Cursor OS Pro/` | `docs/research/` |

**Lane laws (in brain-os attach):**

| Lane | Law file |
|------|----------|
| Cursor OS Pro | `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/lanes/MANDATORY_CURSOR_OS_PRO_CHAT_LOCKED_v1.md` |
| DevBridge wire | `…/brain-os/lanes/MANDATORY_DEVBRIDGE_WIRE_CHAT_LOCKED_v1.md` |

### 4d. T3 — World Target Model runtime

| Item | Full path |
|------|-----------|
| WTM laws (canonical) | `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/wtm/` |
| WTM map | `…/brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` |
| Pre-LLM modules | `/Users/sinakazemnezhad/Desktop/SourceA/scripts/pre_llm/` |
| LLM context packet | `/Users/sinakazemnezhad/.sina/llm_context_packet_v1.json` |
| Root WTM stubs (redirect) | `/Users/sinakazemnezhad/Desktop/SourceA/WORLD_TARGET_MODEL_*_LOCKED*.md` |

### 4e. T4 — Execution spine adapters

| Lane | Full path |
|------|-----------|
| **SinaPromptOS** | `/Users/sinakazemnezhad/Desktop/SinaPromptOS/` |
| Lane law | `…/SourceA/brain-os/lanes/MANDATORY_SINAPROMPTOS_CHAT_LOCKED_v1.md` |
| **AI Dev Bridge** (M8 / Wire) | `/Users/sinakazemnezhad/Desktop/AI Dev Bridge OS/` |
| **n8n glue** | `/Users/sinakazemnezhad/Desktop/SinaaiMonoRepo/n8n/` |

### 4f. T5 — Parallel commercial (only on `founder mode revenue`)

| Lane | Full path |
|------|-----------|
| **TrustField MSB** | `/Users/sinakazemnezhad/Desktop/TrustField Technologies/` |
| App code | `…/TrustField Technologies/app/` |
| Lane law | `…/SourceA/brain-os/lanes/MANDATORY_TRUSTFIELD_CHAT_LOCKED_v1.md` |

### 4g. Parallel product / org lanes (specialist — not default routing)

| Lane | Workspace root | Lane law |
|------|----------------|----------|
| **VIRLUX** | `/Users/sinakazemnezhad/Desktop/VIRLUX/` | `…/brain-os/lanes/MANDATORY_VIRLUX_CHAT_LOCKED_v1.md` |
| **777 Foundation** | `/Users/sinakazemnezhad/Desktop/The 777 Foundation/` | `…/brain-os/lanes/MANDATORY_777_FOUNDATION_CHAT_LOCKED_v1.md` |
| **Noetfield** | `/Users/sinakazemnezhad/Desktop/SinaaiMonoRepo/` | `…/brain-os/lanes/MANDATORY_NOETFIELD_CHAT_LOCKED_v1.md` |
| Noetfield product tree | `/Users/sinakazemnezhad/Desktop/SinaaiMonoRepo/SinaaiDataBase/noetfield/` | `docs/`, `os/`, `product/` |
| **Sinaai monorepo** | `/Users/sinakazemnezhad/Desktop/SinaaiMonoRepo/` | `…/brain-os/lanes/MANDATORY_SINAAI_MONOREPO_CHAT_LOCKED_v1.md` |
| Monorepo parts | `…/SinaaiMonoRepo/SinaaiDataBase/`, `SinaaiRuntime/`, `pipeline/`, `os/` | |
| **Noetfield (Desktop)** | `/Users/sinakazemnezhad/Desktop/Noetfield/` | |
| **Noetfield docs archive** | `/Users/sinakazemnezhad/Desktop/Noetfield-All-Documents/` | |
| **Ecosystem conflicts** | `/Users/sinakazemnezhad/Desktop/sourceB/SOURCE_B_ECOSYSTEM_AND_CONFLICTS_v1.md` | |
| **sourceB** | `/Users/sinakazemnezhad/Desktop/sourceB/` | |

**Lane index (all chats):**  
`/Users/sinakazemnezhad/Desktop/SourceA/brain-os/lanes/MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md`

### 4h. Retired / archive (no builds)

| Item | Full path | Law |
|------|-----------|-----|
| **SinaaiDataBase archive** | `/Users/sinakazemnezhad/Desktop/SinaaiDataBase/` | `…/brain-os/system/SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md` |
| Cursor transcript | `/Users/sinakazemnezhad/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/agent-transcripts/` | Search only |

### 4i. Secondary Desktop (reference — not SSOT)

| Path | Role |
|------|------|
| `/Users/sinakazemnezhad/Desktop/Sina-Investor-Package-FINAL/` | Investor materials |
| `/Users/sinakazemnezhad/Desktop/Sina-Investor-Package-PDF/` | Investor PDFs |
| `/Users/sinakazemnezhad/Desktop/APPS/` | App bundles folder |
| `/Users/sinakazemnezhad/Desktop/iphone Cloud/` | iPhone assets |
| `/Users/sinakazemnezhad/Desktop/Backup 5JUNE/` | Backup snapshot |
| `/Users/sinakazemnezhad/Desktop/PDFs/` | Loose PDFs |
| `/Users/sinakazemnezhad/Desktop/Downloads/` | Downloads — not SSOT |
| `/Users/sinakazemnezhad/Desktop/NOETFIELD_SYSTEMS_OPERATING_PLAN.md` | Loose doc at Desktop root |

### 4j. Mac launcher apps (shortcuts — not law)

`/Users/sinakazemnezhad/Desktop/*.app` including:

- `Sina Command.app` · `Sina Command Apps.app`
- `Sina Prompt OS.app` · `Sina Dispatch.app` · `Sina Execute All.app`
- `Sina Run Now.app` · `Sina Status.app` · `Sina Decide.app`
- `Chat Unify.app` · `Mac Health Guard.app` · `Apple Health.app`

---

## 5. Goal hierarchy quick map (tiers → paths)

**Law:** `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md`

| Tier | Name | Primary paths |
|------|------|---------------|
| **T0** | Governed automation factory | `SourceA/brain-os/`, REGISTRY, Hub |
| **T2** | FORGE | `/Users/sinakazemnezhad/Desktop/forge/` |
| **T2b** | Side SKUs | `mergepack/`, `SourceA/product/`, `AI Dev Bridge OS/mobile/` |
| **T3** | WTM + Pre-LLM | `brain-os/wtm/`, `SourceA/scripts/pre_llm/` |
| **T4** | Execution spine | `SourceA/scripts/`, `SinaPromptOS/`, DevBridge |
| **T5** | TrustField MSB | `TrustField Technologies/` — parallel only |

**Daily order (default):** REGISTRY pick → FORGE → WTM → Hub Refresh (not MSB-first).

---

## 6. Claude Pro attach checklist

| Priority | Attach path |
|----------|-------------|
| **Required** | `/Users/sinakazemnezhad/Desktop/SourceA/brain-os/` |
| **T2 product (optional)** | `/Users/sinakazemnezhad/Desktop/forge/` |
| **Revenue session (optional)** | `/Users/sinakazemnezhad/Desktop/TrustField Technologies/` |
| **Never default** | `SinaaiDataBase/`, `~/.sina/` bulk, `Backup 5JUNE/`, `Downloads/` |

**Project instructions:** point to `SOURCEA_EXTERNAL_ADVISOR_CONTRACT_LOCKED_v3.md` + this file.

**First reads:**

1. `brain-os/INDEX_LOCKED_v1.md`
2. `brain-os/contract/SOURCEA_EXTERNAL_ADVISOR_CONTRACT_LOCKED_v3.md`
3. `brain-os/contract/CLAUDE_PRO_FULL_PICTURE_GUIDE_LOCKED_v1.md` (**start here for understanding**)
4. `brain-os/contract/ALL_FILES_MAPPING_FOR_CLAUDE_PRO_LOCKED_v1.md` (this file — full paths)

**Tiered insider maps (same folder):**

| Map | File | Use when |
|-----|------|----------|
| **Main goals Phase 1 + 2** | `ALL_FILES_MAPPING_CLAUDE_PRO_MAIN_GOALS_LOCKED_v1.md` | Brain · Memory · REGISTRY · **automation loop · WTM · Pre-LLM · FORGE · AI Dev Bridge** |
| **Parallel lanes only** | `ALL_FILES_MAPPING_CLAUDE_PRO_PARALLEL_ONLY_LOCKED_v1.md` | TrustField · VIRLUX · 777 · Noetfield · MergePack · archive · investor |

**ASF correction:** Automation loop, Pre-LLM readiness, and AI Dev Bridge are **core Phase 2 goals** — not parallel lanes.

---

## 7. Machine path lookup order (advisor)

1. `brain-os/MANIFEST.yaml` — when Worker builds it
2. `brain-os/scripts/brain_os_paths.py`
3. `brain-os/runtime/RECEIPTS_INDEX_LOCKED_v1.md`
4. This file §2–§4
5. ASF paste snapshot

---

*End ALL_FILES_MAPPING_FOR_CLAUDE_PRO v1*
