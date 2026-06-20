# SourceA / Sina Command — Onboarding Guide

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Goal:** New founder, maintainer, or lane agent is productive in **≤30 minutes**.  
**Updated:** 2026-06-06  
**Start here after:** `README_SOURCE_A.md` (LEVEL 1 mandatory reads)

---

## 1. Choose your role

| Role | Where you work | Terminal? | Edits SourceA? |
|------|----------------|-----------|----------------|
| **Founder (ASF)** | Sina Command hub | **No** — Refresh + Actions only | Laws only (you) |
| **Maintainer agent** | Cursor chat (this repo) | Executor runs shell | **Yes** — `~/Desktop/SourceA/` |
| **Lane agent** | Own repo + hub attest | Per lane law | **No** SourceA code |
| **SEMEJ / multi-AI** | Chrome loop + inject | Executor only | No SourceA unless maintainer |

**One THREAD per Cursor chat** — pick P0 from **Today** tab before deep work.

---

## 2. First 15 minutes (everyone)

1. Open hub: `http://127.0.0.1:13020/`
2. Read **Today** → active P0 + ops cards
3. Read generated bowl: `sina-bowl/DAILY_BOWL.md` (after Refresh)
4. Skim machine queue: `os/plan-library/SOURCEA-PRIORITY.md`
5. Read architecture overview: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (this folder)

**Governance entry:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` → pick your branch (§1–§8).

---

## 3. Founder onboarding (no Terminal)

### Daily loop

1. **Refresh** hub
2. **Today** — confirm one THREAD for the day
3. **Track** — attest lane items when prompted
4. **Actions** — one-tap ops (spine bridge, MP-SHIP, fleet, etc.)
5. **Agents Window** tab — copy `Do task N — …` into Cursor Agents (not Editor)

### Agents Window priority stack

Credibility tasks: **1, 5, 10, 22, 35, 66, 86, 94, 96, 100**  
Catalog law: `FOUNDER_AGENT_USE_GUIDE_LOCKED_v1.md`

### Never ask founder to

- Open Terminal or paste `curl` / `python3` / `bash`
- Run validators or rebuild — say **Refresh** or tap an **Action**
- Poll agent-loop inbox on a timer

---

## 4. Maintainer agent onboarding

### Session start (mandatory)

```bash
cd ~/Desktop/SourceA/scripts
python3 cursor_agent_self_audit.py session-start
```

Read chain (disk):

1. `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md`
2. `MANDATORY_READ_CHAIN.md` (workspace)
3. `SESSION_CLOSEOUT_LATEST.md`
4. `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` §7 (do now)

### What you ship

- Hub server + panel (`scripts/sina-command-server.py`, `build-sina-command-panel.py`)
- Validators in `scripts/validate-*.sh`
- Runtime under `scripts/runtime/`
- LOCKED law docs when council requires

### What you do not ship without gates

- `orchestrator dispatch_ready: true` (needs Eval-1b live + LOCKED v2)
- Duplicate `.cursor/rules/` alwaysApply files
- Lane-specific code in SourceA (lanes report via Backlog)

### Verify before claiming done

```bash
cd ~/Desktop/SourceA/scripts
SINA_RUN_BACKEND_E2E=0 python3 build-sina-command-panel.py
python3 find_critical_bugs.py
```

Ops detail: [`docs/RUNBOOK.md`](RUNBOOK.md)

---

## 5. Lane agent onboarding

1. Read your lane START_HERE (e.g. `mergepack/START_HERE.md`, `AI Dev Bridge OS/docs/…`)
2. Work **only** in your repo — not `~/Desktop/SourceA/`
3. Post progress via hub **Backlog → Agent reports**
4. Founder attests on **Track** when physical proof exists (G3, pilot, payment)

Boundaries: `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md`

---

## 6. Key concepts (vocabulary)

| Term | Meaning |
|------|---------|
| **SSOT** | Disk truth — `~/.sina/*.json`, LOCKED docs, validators |
| **Bowl** | Generated founder dashboard (`command-data.json`) |
| **Spine** | Branch actions executed via hub `/api/action` |
| **dispatch_ready** | Always **false** at orchestrator until Phase 3 gates |
| **Eval-1b** | Behavioral proof — live LLM A/B vs packet |
| **STRUCTURAL_ONLY** | CI mode when OpenRouter 402 blocks live eval |
| **No ASF** | Machine validators are progress authority — not human sign-off |

---

## 7. Repo map (quick)

| Need | Go to |
|------|-------|
| Hub UI | `agent-control-panel/index.html` |
| API routes | `scripts/sina-command-server.py` |
| Founder actions | `scripts/sina_command_lib.py` |
| Runtime C1–C7 | `scripts/runtime/` |
| Dispatch policy | `scripts/runtime/dispatch_policy/` |
| Plan prompts | `os/plan-library/sourcea-1000/` |
| Product P0 | `product/PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md` |

---

## 8. First tasks by role

### Founder

- [ ] Refresh hub · confirm P0 on **Today**
- [ ] Run one **Action** from ops card (if red)
- [ ] Mark Agents Window task **Wanted** · run top priority in Agents chat

### Maintainer

- [ ] `session-start` + read closeout
- [ ] `build-sina-command-panel.py` PASS
- [ ] Pick one T0 from `SOURCEA-PRIORITY.md` backlog

### Lane

- [ ] Read lane START_HERE + `PROGRAM_PROGRESS.json` row
- [ ] Ship one verify script PASS in your repo
- [ ] Vault note + request Track attest

---

## 9. Help and escalation

| Issue | Doc / tab |
|-------|-----------|
| Strategic direction | `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` |
| Council build order | `COUNCIL_BRIEF_STRATEGIC_SLICE_*` |
| Agent loop | Hub **Agent loop** (inactive unless INBOX active) |
| Conflicts | Hub **Conflict Room** / **Council Room** |
| Dispatch law | `DISPATCH_POLICY_LOCKED_v1.md` |

---

## 10. Document index (this pack)

| Doc | Purpose |
|-----|---------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System shape, planes, C1–C7, dispatch |
| [`RUNBOOK.md`](RUNBOOK.md) | Start/stop, build, validators, incidents |
| [`ONBOARDING.md`](ONBOARDING.md) | This guide |

Parent index: `README_SOURCE_A.md`
