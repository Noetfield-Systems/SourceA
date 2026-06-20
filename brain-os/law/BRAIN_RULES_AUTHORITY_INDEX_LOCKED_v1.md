# BRAIN RULES AUTHORITY INDEX — unified (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-06  
**Purpose:** One concrete map for **Brain** — every rule, incident, and enforcement path. **Pointers only** — does not replace canonical laws.  
**Rule:** Search this index → open canonical doc → **never** invent a parallel rule in chat.

---

## 0. Why agents “forget” (brain must internalize)

| Failure | Fix |
|---------|-----|
| Chat summary treated as law | **Disk wins** — `SOURCEA-PRIORITY.md`, validators, LOCKED `*.md` |
| New rule written instead of search | **Supersession law** — extend or supersede ONE doc (`AGENT_RULES_IN_CHARGE_LOCKED_v1.md` §3) |
| Founder given Terminal steps | **Session law** — `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` + `.cursor/rules/agent-loop.mdc` |
| Brain implements instead of routes | **Brain contract** — `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` |
| Rules loop not run | **Every session:** `GET /api/agent-rules-in-charge-v1` or `agent_rules_loop_orchestrator.py` |

**ASF said repeatedly:** Do not ask founder for Terminal. Canonical law exists since 2026-05-27+. Agents ignore it when they skip the read chain.

---

## 1. TOP 10 LAWS — brain enforces every reply

| # | Law | Canonical path | Charge |
|---|-----|----------------|--------|
| 1 | **No Terminal for founder** | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | session |
| 1b | **No ask Refresh — agent self-sync** | `scripts/hub_self_refresh_v1.py` · Hub `/api/hub-sync` auto-poll | session |
| 2 | **One-tap Actions / Refresh / tabs** | `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` §8.4 | session |
| 3 | **Chat ≠ memory** | `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` | operational |
| 4 | **No auto-paste into Cursor** | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | operational |
| 5 | **Search existing rule first** | `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` §3–§4 | session |
| 6 | **Locked source wins over GPT** | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | operational |
| 7 | **External critic compare only** | `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | operational |
| 8 | **Fast track — parallel lanes** | `SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md` | apex |
| 9 | **dispatch_ready = orchestrator_dispatch_ready()** | `DISPATCH_POLICY_LOCKED_v1.md` v1.1 | operational |
| 10 | **Brain picks / worker codes** | `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` | session |
| 11 | **Miss → disk-first correction** | `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md` | **every session** |
| 12 | **Brain disk-before-chat gate** | `BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md` · `scripts/brain-session-start.sh` | **session start + read receipt each turn** |
| 13 | **Brain no validator recursion** | `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` v1.1 · **INCIDENT-026** · `scripts/brain_session_guard_v1.py` | **read receipt · no bash validate marathon** |

### Daily mandatory loop (ASF order 2026-06-07)

On any miss, confusion, or wrong routing answer:

```text
IDENTIFY root doc → EDIT DISK → WIRE → VERIFY → THEN reply to ASF
```

Chat-only “sorry / correction” without disk edit = **loop not run**.

### No Terminal — exact meaning (do not paraphrase)

**Forbidden to tell ASF:**
- Open Terminal, run `bash`, `python3`, `curl`, `cd … && …`
- Copy shell from chat into any terminal
- “Run this in zsh” (including JSON settings lines — those go in `settings.json`)

**Allowed for ASF:**
- Hub **Refresh**, **Actions**, **Track**, **Agent hub** Start/Submit round, **Ask**, **Backlog**
- Clicks only — maintainer/agent runs shell OR ships one-tap Action

**Executor/agent/brain-verify:** May run shell **themselves** — never delegate to founder.

**Machine mirror:** `scripts/agent_rules_in_charge.py` → `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md`  
**Cursor alwaysApply:** `.cursor/rules/agent-loop.mdc`  
**Hub UI:** Actions tab “one tap, no Terminal” · site guide chip “One-tap not Terminal”

---

## 2. Authority hierarchy (who wins)

```
ASF human override (structure + commercial)
    ↓
SINA_OS_SSOT_LOCKED.md (ecosystem apex)
    ↓
SINA_GOVERNANCE_ENTRY_LOCKED_v1.md (router — pick ONE branch)
    ↓
SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md (one doc per topic)
    ↓
Topic LOCKED_vN.md at SourceA root (active only)
    ↓
Machine validators + ~/.sina/*.json
    ↓
Chat / GPT / Claude (compare only — never steer build)
```

**Decision stack detail:** `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` §1

---

## 3. Rules-in-charge machine (live highlights)

| Resource | Path |
|----------|------|
| Law | `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` |
| Engine | `scripts/agent_rules_in_charge.py` (`RULE_CHARGE_META`) |
| Loop | `scripts/agent_rules_loop_orchestrator.py` |
| API | `GET /api/agent-rules-in-charge-v1` |
| Validator | `bash scripts/validate-agent-rules-in-charge-v1.sh` |

**Brain session start:** Read `in_charge_now` from API — not from memory.

### Registered in RULE_CHARGE_META (hub highlights)

| Path | Level |
|------|-------|
| `SINA_OS_SSOT_LOCKED.md` | apex |
| `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | apex |
| `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | apex |
| `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | **session** |
| `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` | session |
| `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` | session |
| `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` | session |
| `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` | session |
| `COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md` | session |
| `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | operational |
| `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` | operational |
| `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | operational |
| `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | progress |

**Full inclusive index:** Hub → Council / Rules in charge panel (all rules, not only highlights).

---

## 4. Cursor `.mdc` rules (alwaysApply — do not duplicate)

| File | Topic |
|------|-------|
| `.cursor/rules/000-brain-unified.mdc` | **Brain SSOT** — narrate / spawn / refuse / session |
| `os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md` | **Brain full unified law** |
| `scripts/brain_gather_rules_v1.py` | Inventory all Brain rule paths logged |
| `.cursor/rules/agent-loop.mdc` | **No Terminal for founder** · rules loop · three roles |
| `.cursor/rules/sina-governance-entry.mdc` | Router |
| `.cursor/rules/agent-smart-judgment.mdc` | Decision stack |
| `.cursor/rules/chatgpt-external-critic.mdc` | EXTERNAL_CRITIC |
| `.cursor/rules/sina-command-readonly.mdc` | Founder one-tap only |
| `.cursor/rules/sina-command-protected.mdc` | Edit protection |
| `.cursor/rules/sina-command-ui.mdc` | Hub UI law |
| `.cursor/rules/prompt-queue.mdc` | Prompt queue |
| `.cursor/rules/sina-advisor.mdc` | Advisor lane |
| `.cursor/rules/semej-agent.mdc` | SEMEJ scope |
| `.sina-agent/.cursor/rules/workspace-governance.mdc` | Private agent workspaces |

**Law:** Edit existing `.mdc` — **never** add parallel alwaysApply on same topic.

---

## 5. Incidents index (all — brain reminds, does not reopen)

| ID / doc | Topic | Status |
|----------|-------|--------|
| `SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` | Worker prompt in Brain chat | FIXED — refuse + headsup |
| `SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md` | Step-2 OpenRouter impossible inject | FIXED — gate active |
| `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` | Claimed RUNNING without AGENT DONE | LOCKED — §5 acceptance |
| `GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md` | PEV spine · headless vs Worker chat | LOCKED |
| `GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md` | INJECT → VALIDATE → ACTIVATE → SYNC | LOCKED mandatory |
| `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | Cursor spam inject | FIXED — stay off |
| `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` | Chat ≠ SSOT | LOCKED |
| `AGENT_DIAG_CLIPBOARD_PAIRING_HIJACK_2026-05-27_LOCKED.md` | URL+PIN clipboard | FIXED in bridge |
| `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` | Maintainer audit | LOCKED |
| `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | WTM UI cockpit drift | LOCKED record |
| `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` | Phase naming | LOCKED record |
| `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | Hub incident surfaces | Index |
| `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` | Weekly incident share | UI tab |
| `SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md` | Law conflicts | ACE |
| Mac/WiFi audit (2026-06-06 chat) | Phishing concern | Closed — clean DNS |

**Hub tab:** Incident Room · Conflict Room · Backlog → Agent reports

---

## 6. Governance router branches (brain picks one)

From `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`:

| Branch | Canonical entry |
|--------|-----------------|
| Ecosystem | `SINA_OS_SSOT_LOCKED.md` |
| Daily ops / automation | `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` |
| External paste | `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` |
| Agent fleet | `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` |
| WTM | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` |
| Hub edit | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` |
| Conflicts | `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` |
| Important docs list | `ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md` |
| Hub tabs map | `SINA_HUB_ESSENTIALS_LOCKED_v1.md` + `hub_essentials_index.py` |

---

## 7. Archive (superseded — never cite as active)

| Manifest | Path |
|----------|------|
| WTM archive log | `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md` |
| WTM v1–v4 maps | `archive/superseded/wtm/v*/` |
| Examples only | `archive/attachments/examples/` |

**Rule:** Active law = `*_LOCKED_vN.md` at **SourceA root** only. Audit fails on stale v2/v3/v4 pointers.

---

## 8. Brain / worker / founder — rule split

| Role | Rules that bind them |
|------|----------------------|
| **ASF (founder)** | No Terminal · Refresh/Actions · Track commercial · edit lock for Command |
| **Brain** | `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` · no implement · route worker · remind laws |
| **Worker** | `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` · one sa-XXXX · verify · closeout |
| **Maintainer chat** | Only lane that may edit SourceA per edit lock |
| **Product agents** | `AGENT_GOVERNANCE_INDEX` forbidden paths · Backlog reports only |

---

## 9. Known doc conflicts (brain flags — do not invent fix)

| Conflict | Detail | Action |
|----------|--------|--------|
| `founder/ASF_DAILY_CARD.md` | **FIXED** — hub taps only; `validate-founder-docs-no-terminal-v1.sh` | Founder uses **Actions** / **Refresh** |
| `agent-loop.mdc` shows `curl` example | **Executor only** — not for founder | Brain must label “agent runs this” |
| Strategic synthesis one-liner | **FIXED** — `machine_gates` honest; eval plan status tracks `eval_1b_gate_ok` | Brain cites live API / SOURCEA-PRIORITY |
| Chat handoffs vs 133 root LOCKED files | Brain pack is index not replacement | Read chain order in §10 |

---

## 10. Brain read chain (concrete — heavy brain)

```
0. BRAIN_UNIFIED_RULES_LOCKED_v1.md                 ← SSOT decision tree
1. MANDATORY_BRAIN_CHAT_LOCKED_v1.md
2. BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md          ← THIS FILE
3. BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md
4. CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md   ← goal architecture + operating loop
5. BRAIN_FOUNDER_INTENT_REGISTRY_LOCKED_v1.md
6. BRAIN_FULL_SYSTEM_MAP_LOCKED_v1.md
7. ~/.sina/brain/BRAIN_MASTER_MEMORY_LOCKED_v1.md
8. SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md       ← read full text once per week
9. AGENT_RULES_IN_CHARGE_LOCKED_v1.md
10. SOURCEA-PRIORITY.md §Machine truth
11. docs/system-audits/README_INDEX.md (audit vault pointer — evidence not law)
12. Live: plan-no-asf-run.sh pick 3 + /api/agent-rules-in-charge-v1
```

---

## 11. Brain reply checklist (every message)

- [ ] Did I tell ASF to open Terminal? → **STOP — rewrite with Actions/Refresh**
- [ ] Did I invent a new rule? → **STOP — cite existing LOCKED path**
- [ ] Did I implement sa-XXXX? → **STOP — worker handoff**
- [ ] Did I read pick script for next task? → **Required**
- [ ] Did I remind commercial P10 if relevant? → **If parallel clock active**

---

## 12. Sync to runtime brain folder

```bash
bash ~/Desktop/SourceA/scripts/sync-brain-pack.sh
```

Copies all `BRAIN_*.md` to `~/.sina/brain/`.

---

*End BRAIN RULES AUTHORITY INDEX v1 — pointers only, not new law*
