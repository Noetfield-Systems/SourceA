# Worker assignment & chat routing (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-07  
**Authority:** ASF — fixes agent routing drift (SinaaiDataBase maintainer · separate FORGE chat · Research L1/L2 confusion)  
**Parent:** `ECOSYSTEM_BRAIN_ROLLOUT_LOCKED_v1.md` · `GOVERNED_EXECUTION_OS_MASTER_LOCKED_v1.md` · `SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md`  
**Supersedes for routing:** any chat/table that assigns **build work** to SinaaiDataBase or a separate FORGE builder chat

---

## 0. Why agents mis-routed (root causes on disk — fixed here)

| Confusion | Old signal on disk | Correct law (this file) |
|-----------|-------------------|-------------------------|
| Hub/sa-queue → SinaaiDataBase | `ECOSYSTEM_BRAIN_ROLLOUT` §4 “HQ maintainer · SinaaiDataBase” · `SINA_COMMAND_EDIT_LOCK` maintainer chat | **SinaaiDataBase = archive/broker only — no jobs.** Hub + panel builds → **SourceA Worker** |
| Separate FORGE builder chat | `GOAL_HIERARCHY` T2 path `~/Desktop/forge/` without worker scope | **No FORGE-only chat.** FORGE checklist + code → **same SourceA Worker** when Brain orders |
| “Prompt 13” / extra prompts | Gap-list item numbers mixed with prompt queue | **Only numbered worker queue = 10-pack** (§6). T5 MSB = **`founder mode revenue`** + TrustField — **not** “prompt 13” |
| One Research Acquisitor | `GOAL_SPECIALIST_CHAT_PACK` §4 single block | **Two chats:** **RA L1** (briefs) · **RA L2** (register/sync/filter) — §3 |
| Who builds SourceA + Hub | Split maintainer vs worker | **One implementation chat:** SourceA Worker — §2 |

**Brain rule:** On assignment questions, cite **this file** — not chat memory or retired archive threads.

**This file exists because** `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md` was run after assignment drift (SinaaiDataBase maintainer · FORGE-only chat · prompt 13 typo).

---

## 1. Active chats (who gets work)

| Chat | Workspace | Gets build jobs? | Handoff |
|------|-----------|------------------|---------|
| **Brain / Execution Core** | `~/Desktop/SourceA` | **No** — route only | `BRAIN_COMPLETE_TRANSFER` §PASTE BLOCK |
| **SourceA Worker** | `~/Desktop/SourceA` | **Yes — all disk builds** | `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` |
| **Research Acquisitor L1** | `~/Desktop/SourceA` | **No** — external briefs only | `GOAL_SPECIALIST_CHAT_PACK` §4 L1 |
| **Research Acquisitor L2** | `~/Desktop/SourceA` | **No** — filter/register/sync only | `GOAL_SPECIALIST_CHAT_PACK` §4 L2 |
| **Commercial Goal Specialist** | `~/Desktop/TrustField Technologies` | **No** — advocate vault YAML | `GOAL_SPECIALIST_CHAT_PACK` §1 |
| **Governance Goal Specialist** | `~/Desktop/SinaaiMonoRepo` | **No** — advocate vault YAML | `GOAL_SPECIALIST_CHAT_PACK` §2 |
| **TrustField delivery** | `~/Desktop/TrustField Technologies` | **Parallel T5 only** | `MANDATORY_TRUSTFIELD_CHAT_LOCKED_v1.md` |
| **Noetfield** | `~/Desktop/SinaaiMonoRepo` | **Spec/advocate** — no default queue | `MANDATORY_NOETFIELD_CHAT_LOCKED_v1.md` |
| **AI Dev Bridge wire** | `~/Desktop/AI Dev Bridge OS` | **Parallel T4 wire** — not default clock | `MANDATORY_DEVBRIDGE_WIRE_CHAT_LOCKED_v1.md` |
| **Cursor OS Pro** | `~/Desktop/AI Dev Bridge OS/mobile` | **T2b side SKU** — parallel | `MANDATORY_CURSOR_OS_PRO_CHAT_LOCKED_v1.md` |
| **SinaPromptOS** | `~/Desktop/SinaPromptOS` | **T4 adapter** — spawn only | `MANDATORY_SINAPROMPTOS_CHAT_LOCKED_v1.md` |
| **SinaaiDataBase** | `~/Desktop/SinaaiDataBase` | **Never** — archive/broker/search only | `SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md` |

---

## 2. SourceA Worker — single implementation lane (LOCKED)

**Law:** ASF operates **one** worker Cursor chat in SourceA for all implementation unless ASF explicitly opens a **parallel T5** lane.

### Worker may edit (when Brain or `sa-XXXX` routes)

| Scope | Paths |
|-------|-------|
| SourceA spine | `~/Desktop/SourceA/**` (scripts, validators, plan-library, handoffs) |
| Hub / Command panel | `agent-control-panel/` · `scripts/build-sina-command-panel.py` · `scripts/sina-command-server.py` (Brain-ordered hub tasks only) |
| FORGE (T2 primary) | `~/Desktop/forge/**` when task is FORGE checklist / Brain order — **not** a separate chat |
| REGISTRY | `os/plan-library/sourcea-1000/` · one `sa-XXXX` per session |

### Worker must not (unchanged)

- Flip `dispatch_ready` / auto-dispatch without council + live Eval-1b  
- Assign Research Acquisitor to `sa-XXXX`  
- Treat SinaaiDataBase archive chat as implementation target  

### Supersedes

- `MANDATORY_SOURCEA_WORKER_CHAT` §FORBIDDEN “edit other product repos” **for FORGE + hub** when this file + Brain handoff explicitly routes there  
- Retired **SinaaiDataBase maintainer** row in rollout tables  

---

## §2.2 — Forbidden routing words (Brain + Worker — LOCKED)

**No such roles exist.** Do not use in handoffs, ACKs, or routing prose:

- `FORGE builder`
- `FORGE builder chat`
- `parallel FORGE lane`
- `open FORGE workspace` (as a separate assignee)

**Required language:** **SourceA Worker — FORGE-scoped task** (same chat · edits `~/Desktop/forge/` when Brain routes).

---

## 3. Research Acquisitor — L1 vs L2 (two chats)

| Level | Role | Input | Output | Build? |
|-------|------|-------|--------|--------|
| **L1** | Brain helping hand — external truth | Brain research **question** | `~/.sina/agent-workspaces/research-acquisitor/briefs/YYYY-MM-DD_RESEARCH_BRIEF.yaml` | **No** |
| **L2** | Search filter — unified root hygiene | L1 briefs + lane YAML paths | `register` + `sync` → `~/.sina/research-root/filtered/` | **No** |

**Flow:** L1 writes brief → L2 registers + syncs → Brain reads `filtered/execution_core.digest.yaml` only.

**10-pack slot:** queue item **#10** → **RA L2** only (hygiene). L1 runs when Brain sends a question — **not** a numbered build prompt.

---

## 4. Parallel lanes (goals — not in default 10-pack)

Open only when ASF names the trigger. Brain **never** puts these ahead of REGISTRY + FORGE on default clock.

| Lane | Tier | Goal | Trigger |
|------|------|------|---------|
| **TrustField** | T5 (Goal 7) | MSB outreach · 3 demos · CanadaBuys · pilots | ASF says **`founder mode revenue`** |
| **Noetfield** | Governance spec | Legal/governance framing · vault advocacy | Governance loop / conflict |
| **AI Dev Bridge** | T4 Wire | M8 phone↔Mac · Wire G3 attest | Hub wire Action or explicit `sa-XXXX` wire task |
| **Cursor OS Pro** | T2b | App Store mobile IDE SKU | ASF activates side-SKU bucket |
| **MergePack / RunReceipt** | T2b | Factory SKUs — parallel factory | Never north star · never default P0 |

**Terminology:** Say **“T5 TrustField parallel”** or **“founder mode revenue lane”** — never **“prompt 13”** (that was a gap-list typo, not a queue id).

---

## 5. How ASF assigns (manual until automation loop)

1. **Pick lane** from §1 (default build → SourceA Worker only).  
2. **New chat** in that workspace → mandatory read handoff (index table).  
3. **Paste one task** — `sa-XXXX` from pick script **or** Brain order from §6 ten-pack.  
4. **One task per session** → verify PASS → Hub **Refresh** → next task = new session or `/clear`.  

**Forbidden:** Assigning any row in §6 to SinaaiDataBase. Assigning FORGE to a non-SourceA chat.

---

## 6. Standard ten-pack queue (Brain emits — order LOCKED until items close)

Until hub automation loop ships, Brain uses this sequence. **All items 1–9 → SourceA Worker.** **Item 10 → RA L2.**

| # | Owner | Task summary |
|---|-------|----------------|
| 1 | Worker | Live REGISTRY pick (`plan-no-asf-run.sh pick 1` — e.g. `sa-0207`) |
| 2 | Worker | RunReceipt / Hub P0 demotion — STRATEGIC-SLICE default per `GOAL_HIERARCHY` v1.1 |
| 3 | Worker | `FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md` wired (this file + index + brain pack) |
| 4 | Worker | Next REGISTRY pick after #1 closeout |
| 5 | Worker | Wire validate tasks — **no** RunReceipt P0 bump (superseded prompts) |
| 6 | Worker | Next REGISTRY pick |
| 7 | Worker | L1 ingest→reducer scaffold (auto-paste stays OFF) |
| 8 | Worker | Hub **sa-queue** tab (was wrongly routed to archive chat) |
| 9 | Worker | FORGE `LAUNCH_CHECKLIST.md` open items (`~/Desktop/forge/`) |
| 10 | RA L2 | Research root `register` + `sync` + manifest hygiene |

Full paste text: Brain copies from `sa-XXXX.md` files + `SOURCEA-PRIORITY.md` evidence rows — not chat improvisation.

---

## 7. Wire (read chain)

| File | Role |
|------|------|
| `MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md` | Active chat table — must match §1 |
| `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` | Worker contract + §BUILD SCOPE |
| `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` | §Supersession — worker replaces retired maintainer |
| `FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md` | ASF daily rhythm |
| `sync-brain-pack.sh` | Mirrors this file to `~/.sina/brain/` |

---

*End WORKER ASSIGNMENT AND CHAT ROUTING v1*
