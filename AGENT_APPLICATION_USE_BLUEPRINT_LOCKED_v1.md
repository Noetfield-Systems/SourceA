# Agent Application Use Blueprint (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Status:** Canonical — end-to-end operational manual for all agents using Sina Command  
**Hub:** `http://127.0.0.1:13020`  
**Parent laws:** `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` · `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md`  
**Machine registry:** `scripts/agent_workspace_registry.py` (GOVERNANCE_VERSION **6**)  
**Unified brief:** `scripts/agent_system_unified.py` → payload `system_unified`

---

## 0. Law (one sentence)

**Every agent session starts in Sina Command — Council Room for the whole-system brief, then the private agent page, then the allowed repo only; all rules, roles, tasks, and report channels are defined here and in the app, not re-pasted per chat.**

---

## 1. System map

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SINA COMMAND (:13020) — pre-unifying hub for all agent chats & repos   │
├─────────────────────────────────────────────────────────────────────────┤
│  Council Room ──► whole-system brief · 29+ rules · mind share         │
│  Agent hub ─────► pick private page (8 agents)                          │
│  workspace-<id> ► governance · 10-pack loop · round submit            │
│  Incident Room ─► weekly share · quiz · certify                         │
│  Conflict Room ─► ACE triage · continue work                            │
│  Backlog ───────► agent reports (hub bugs)                              │
│  Live agents ───► OpenRouter / Cursor Cloud / IDE bridge (no inject)  │
│  SEMEJ tab ─────► Chrome multi-AI automation                            │
└─────────────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
  ~/.sina/agent-workspaces/<id>/   <repo_root>/.sina-agent/
  (private governance)             (repo marker + Cursor rules)
```

### ASF terminology (blueprint scope)

| Term | Meaning in this blueprint |
|------|---------------------------|
| **Exclusive** | **Particular · individual** — each agent’s own role, repo, forbidden paths, private workspace, particular tasks |
| **Inclusive** | **Overall · all-in** — whole app, all 8 registered agents, all shared laws, all tabs/APIs, overall session flow |

**Inclusive:** Every agent sees the **same global laws**; lane-specific needs are additive, never subtractive.  
**Exclusive:** Each agent’s **particular** scope is defined in §4 (one individual definition per registered agent).

---

## 2. Actor types

| Actor | Identity | May use Terminal? | May edit SourceA? | Primary surface |
|-------|----------|-------------------|-------------------|-----------------|
| **ASF** | Founder human | **No** (law) | Yes | Hub clicks only |
| **sinaai_maintainer** | Maintainer agent chat | Via executor when needed | **Yes** | `workspace-sinaai_maintainer` + SinaaiDataBase |
| **Portfolio agents** (6) | Repo implementers | In own repo only | **No** | Council → private page → repo |
| **semej** | Automation agent | Via Actions only | **No** (read-only all SourceA) | SEMEJ tab |
| **MergePack lane** | Semi-separate product (**not** registered agent) | In mergepack repo | **No** | Live products · Repos · Actions |
| **Live agents** | API/cloud bridges | N/A | **No** | Live agents tab — never auto-paste |

---

## 3. Session lifecycle (every agent, every time)

| Step | Where | Action | Required? |
|------|-------|--------|-----------|
| **0** | Hub health | Confirm `http://127.0.0.1:13020/health` OK | Yes if hub up |
| **1** | `?tab=council-room` | Read whole-system brief; scan paradox board | **Mandatory** |
| **2** | Council Room | **Copy whole-system brief** → paste once at top of Cursor chat | **Mandatory** |
| **3** | `?tab=agent-loop` | Open **your** private agent tile | Yes |
| **4** | `?tab=workspace-<id>` | **Workspace vault** — log activity start; read governance | Yes |
| **5** | Cursor workspace | Open `repo_root` from registry — never forbidden roots | Yes |
| **6** | Work | Implement / document / report per lane needs | — |
| **7** | Vault | **Deposit document** + **register repo refs** + **log activity** end | **Mandatory** |
| **8** | Report | Mind share · Conflict · Incident · Agent report as appropriate | Before session end |
| **9** | Loop (if active) | Submit round on **same** private page (auto-deposits to vault) | When loop running |

**Forbidden session starts:**
- Repo chat without Council Room brief when hub is up
- Editing `~/Desktop/SourceA` from any agent except `sinaai_maintainer`
- Starting loop on wrong private page while another agent owns active loop
- Re-enabling Cursor auto-paste / inject (incident law)

---

## 4. Registered agents — full roster

Governance version **6**. **8 registered agents** — Private dir: `~/.sina/agent-workspaces/<id>/`.

### 4.1 trustfield

| Field | Value |
|-------|-------|
| **Role** | portfolio |
| **Lane / plane** | TrustField · DELIVERY |
| **Repo** | `~/Desktop/TrustField Technologies` |
| **Forbidden** | SourceA |
| **Pack** | trustfield (10-pack) |
| **Layer A training** | yes |
| **Hub tabs** | Actions · Private page · Repos lane brief |
| **Governance focus** | Infra truth + law alignment before ship |
| **Real needs** | B-001 law collision; compliance lanes; lane brief + loop pack |
| **Key artifacts** | `os/plan.json`, `prompts/`, `docs/GLOBAL_BLOCKERS.json` |
| **Report via** | mind-share, agent-review, conflict-room, incident-room |

### 4.2 virlux

| Field | Value |
|-------|-------|
| **Role** | portfolio |
| **Lane / plane** | VIRLUX · DELIVERY |
| **Repo** | `~/Desktop/VIRLUX` |
| **Forbidden** | SourceA |
| **Pack** | virlux |
| **Hub tabs** | Actions (DNS, Vercel) · Private page · Live products |
| **Governance focus** | Live site + DNS proof without founder Terminal |
| **Real needs** | DNS/Vercel smoke; GTM progress; public URL verify |
| **Key artifacts** | `os/plan.json`, `vercel.json` |

### 4.3 ai_dev_bridge_os

| Field | Value |
|-------|-------|
| **Role** | portfolio |
| **Thread** | THREAD-WIRE |
| **Lane / plane** | Wire · WIRE |
| **Repo** | `~/Desktop/AI Dev Bridge OS` |
| **Forbidden** | SourceA |
| **Pack** | ai_dev_bridge_os |
| **Hub tabs** | Actions (G1/G2/G3 wire) · Private page · Track |
| **Governance focus** | Wire proof artifacts; executor runs shell |
| **Real needs** | G1/G2/G3 evidence; Tailscale/relay proofs; P0 wire stubs |
| **Key artifacts** | `WIRE_LANE_PROGRESS.md`, `scripts/evidence/` |

### 4.4 noetfield_local

| Field | Value |
|-------|-------|
| **Role** | portfolio |
| **Lane / plane** | Noetfield · DESIGN |
| **Repo** | `~/Desktop/Noetfield-All-Documents` (resolved) |
| **Forbidden** | Noetfield cloud repo **and** SourceA |
| **Pack** | noetfield_local |
| **Layer A training** | yes |
| **Hub tabs** | Private page · Repos — **never** cloud Noetfield |
| **Governance focus** | Local SSOT only — cloud is `noetfield_cloud` |
| **Real needs** | HIERARCHY_INDEX L0–L3; registry validation; _under-analysis decisions |
| **Key artifacts** | `HIERARCHY_INDEX.md`, `registry/source_of_truth_registry.json` |

### 4.5 noetfield_cloud

| Field | Value |
|-------|-------|
| **Role** | portfolio |
| **Lane / plane** | Noetfield · SHIP |
| **Repo** | `~/Desktop/Noetfield` |
| **Forbidden** | Local docs repo **and** SourceA |
| **Pack** | noetfield_cloud |
| **Hub tabs** | Private page · Live products · Actions |
| **Governance focus** | Ship lane only |
| **Real needs** | GitHub/Vercel ship; no local hierarchy migration; release tags |
| **Key artifacts** | `README.md`, `.github/`, `vercel.json` |

### 4.6 seven77

| Field | Value |
|-------|-------|
| **Role** | portfolio |
| **Lane / plane** | 777 · DELIVERY |
| **Repo** | `~/Desktop/The 777 Foundation` |
| **Forbidden** | SourceA |
| **Pack** | seven77 |
| **Layer A training** | yes |
| **Hub tabs** | Actions · Private page · Live products |
| **Governance focus** | Web ops + cohort throughput |
| **Real needs** | Gate 0 outreach; C3 sprint; Next.js + Supabase + Vercel |
| **Key artifacts** | `web/`, `ops/gate0-week1-execution.md`, `supabase/migrations/` |

### 4.7 semej

| Field | Value |
|-------|-------|
| **Role** | automation |
| **Lane / plane** | SEMEJ · AUTOMATION |
| **Repo** | SourceA (read-only reference) |
| **Forbidden** | **All SourceA edits** |
| **Pack** | none — custom goal only |
| **May edit own repo** | **No** |
| **Hub tabs** | SEMEJ tab · Actions (Chrome, Playwright) |
| **Governance focus** | Browser automation; report hub bugs via agent-review |
| **Real needs** | Chrome chain across AIs; Playwright via Actions |
| **Report via** | mind-share, agent-review, incident-room (no conflict-room default) |

### 4.8 sinaai_maintainer

| Field | Value |
|-------|-------|
| **Role** | maintainer |
| **Thread** | THREAD-FACTORY |
| **Lane / plane** | Factory · COMMAND |
| **Repo** | `~/Desktop/SinaaiDataBase` |
| **Forbidden** | none |
| **may_edit_source_a** | **true** |
| **Pack** | sinaai_maintainer |
| **Hub tabs** | May edit SourceA · Private page · P0 RunReceipt · Backlog |
| **Governance focus** | Command app + factory P0 |
| **Real needs** | P0 RunReceipt; implement Actions from agent reviews |
| **Key artifacts** | `runreceipt/`, `AGENT_LOOP_ROUND*.md` |

---

## 5. Role matrix — permissions

| Capability | maintainer | portfolio | product | automation |
|------------|:----------:|:---------:|:-------:|:----------:|
| Edit SourceA (`~/Desktop/SourceA`) | ✅ | ❌ | ❌ | ❌ |
| Edit own `repo_root` | ✅ | ✅ | ✅ | ❌ |
| Start 10-pack loop | ✅ | ✅ | ✅ | ✅ (custom) |
| Submit loop round | ✅ | ✅ | ✅ | ✅ |
| Mind share post | ✅ | ✅ | ✅ | ✅ |
| Conflict report | ✅ | ✅ | ✅ | — |
| Incident weekly + quiz | ✅ | ✅ | ✅ | ✅ |
| Agent review (hub bug) | ✅ | ✅ | ✅ | ✅ |
| Founder directive add | ASF only | — | — | — |
| Live agent auto-inject | ❌ (law) | ❌ | ❌ | ❌ |

---

## 6. Accessibility matrix — who sees what

| Surface / data | ASF | All 8 agents | Live agents | External critic |
|----------------|:---:|:------------:|:-----------:|:---------------:|
| Whole-system brief (`system_unified`) | ✅ | ✅ | via brief file | ❌ |
| All rules list (READ_CHAIN + authority) | ✅ | ✅ | — | ❌ |
| Founder orders (MASTER_ORDERS) | ✅ | ✅ | — | compare only |
| Founder directives jsonl | ✅ | ✅ | — | ❌ |
| Mind share feed | ✅ | ✅ | — | ❌ |
| Paradox board | ✅ | ✅ | — | ❌ |
| Other agents' private INBOX | ❌ | own only | — | ❌ |
| Conflict cases (global) | ✅ | ✅ | — | ❌ |
| Incident SSOT + weekly posts | ✅ | ✅ | — | ❌ |
| Edit lock manifest | ✅ | read | — | ❌ |
| P0 / WTM progress snapshot | ✅ | ✅ | — | ❌ |
| Lane briefs (Repos tab) | ✅ | per lane | — | ❌ |
| Personal DB Layer A | ✅ | training agents | — | ❌ |

**Rule:** No agent receives a private rule list that omits global laws.

---

## 7. Hub surfaces — complete tab map for agents

| Tab id | Title | Agent use |
|--------|-------|-----------|
| `command` | Home | ASF overview; agent start banner → Council Room |
| `council-room` | Council Room | **Session step 1** — brief, rules, mind share, paradoxes, directives |
| `agent-loop` | Agent hub | **Session step 2** — index of 8 private pages |
| `workspace-<id>` | Private agent | Governance, loop, round submit, inbox preview |
| `incident-room` | Incident Room | Read SSOT; weekly share; quiz certify |
| `conflict-room` | Conflict Room | Report law/strategy conflicts; ACE triage |
| `backlog` | Backlog | Agent reports section |
| `intelligence` | Live agents | API/cloud bridge — **no inject** |
| `semej` | SEMEJ | Browser multi-AI chain |
| `agents` | Agents registry | Fleet + workspace metadata |
| `repos` | Repos | Per-lane Cursor briefs |
| `personal-db` | Personal DB | Layer A SSOT (copy agents) |
| `essentials` | Essentials | READ_CHAIN pillars |
| `doc-library` | Doc library | Curated laws |
| `orders` | Your orders | MASTER_ORDERS mirror |
| `actions` | Actions | One-tap commands — ASF primary interface |
| `track` | Track | Orders & started jobs |
| `system-roadmap` | World Target Model | 33-step upgrade map |
| `fleet` | Fleet | Supplemental Cursor activity (not canonical registry) |

---

## 8. Task taxonomy — what agents do in the app

### 8.1 Governance tasks (all agents)

| Task | Surface | API / action |
|------|---------|--------------|
| Read whole system | Council Room | `GET /api/council-room` → `system_unified` |
| Copy session brief | Council Room / Home | UI button → clipboard |
| Post cross-lane insight | Council Room | `POST /api/council-room` `share_mind` |
| Flag paradox | Mind share kind=`paradox` | same |
| Report hub bug | Backlog / Agent reports | `POST /api/agent-review` `submit` |
| Report conflict | Conflict Room | `POST /api/conflict-room` `submit` |
| Ack incident SSOT | Incident Room | `POST /api/incident-room` `ack_report` |
| Weekly incident share | Incident Room | `submit_weekly` |
| Pass incident quiz | Incident Room | `submit_quiz` (≥4/5) |
| Ensure workspace files | Private page | `POST /api/agent-workspaces` `ensure` |

### 8.2 Loop tasks (founder + executor)

| Task | Who clicks | Surface |
|------|------------|---------|
| Select workspace | ASF | Private page |
| Activate 10-pack | ASF | Private page → pack picker |
| Start loop | ASF | Private page → Start loop |
| Read round prompt | Executor (Cursor) | `~/.sina/cursor-inbox.md` or loop INBOX |
| Execute work | Executor | Allowed `repo_root` only |
| Submit round | ASF or executor | Private page → Submit round **or** `POST /api/agent-loop` `response` |
| Cancel / reinject | ASF | Private page (reinject blocked by auto-paste law) |

**Loop state:** `~/.sina/agent-loop.json` · max 10 rounds · owner = `active_workspace`.

### 8.3 Maintainer-only tasks

| Task | Surface |
|------|---------|
| Edit SourceA scripts / hub UI | Cursor in SinaaiDataBase → SourceA |
| Rebuild hub panel | Actions or `build-sina-command-panel.py` |
| Run governance audits | Actions / maintainer scripts |
| Implement Action from agent review | Backlog → ship |
| Add founder directive to canonical doc | Edit LOCKED md + rebuild |

### 8.4 ASF-only tasks (no Terminal)

| Task | Surface |
|------|---------|
| Emergency stop | Home ⛔ / Actions |
| Add runtime directive | Council Room form |
| Ping live agents | Live agents tab |
| Run one-tap Actions | Actions tab |
| Refresh hub payload | Hub Refresh button |

---

## 9. Rule hierarchy — what wins on conflict

Load order for agents (machine-merged in `system_unified.all_rules`):

1. **READ_CHAIN** (25 docs) — `scripts/hub_essentials_index.py`
2. **AUTHORITY_RULES** (15 docs) — `scripts/agent_system_unified.py`
3. **Per-agent GOVERNANCE_LOCKED.md** — lane focus + forbidden roots
4. **Founder orders** — `sina-bowl/MASTER_ORDERS.json` (active/locked)
5. **Founder directives** — `~/.sina/founder-directives.jsonl`
6. **Mind share procedures** — community, not law until ASF promotes

**On conflict between laws:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` → Conflict Room → ACE v3 → **continue work**.

**External ChatGPT paste:** compare only — `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md`.

---

## 10. Report channels — unified feedback

| Channel | Tab | Storage | When to use |
|---------|-----|---------|-------------|
| Mind Share | council-room | `~/.sina/council-room/mind-share.jsonl` | Insight, opinion, procedure, question, paradox |
| Agent review | backlog | `~/.sina/agent-command-reviews.jsonl` | Hub bug, missing Action, broken tab |
| Conflict Room | conflict-room | `~/.sina/conflict-room/cases.jsonl` | Two laws/strategies disagree |
| Incident Room | incident-room | `~/.sina/incident-room/weeks/<ISO-week>/` | Weekly learning, certification |
| Private INBOX | workspace page | `~/.sina/agent-workspaces/<id>/INBOX.md` | Lane tasks table |
| Live comms | intelligence | `~/.sina/live-agent-comms.jsonl` | Hub ↔ API agent messages |

**Phase 2 (reserved):** formal ballots on frozen options — `vote`, `create_topic` rejected until Phase 2.

---

## 11. Workspace vault — app middle layer (mandatory)

**Law:** `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md` · **API:** `/api/workspace-vault`

Every agent **must** interact with the app to gather work:

| Action | When | Method |
|--------|------|--------|
| Deposit document | Every deliverable, report, export | Private page → Workspace vault |
| Register repo ref | Files shipped in `repo_root` | Vault form or API |
| Log activity | Start / end of task | Vault form or API |
| Loop round | Auto on submit | `kind: loop_round` in vault |
| Mind share | Auto on Council post | `kind: mind_share` in vault |

Council **repo lens** shows `vault_doc_count` per agent — compare lanes without Finder.

---

## 12. Private workspace file contract

Each `~/.sina/agent-workspaces/<id>/`:

| File | Purpose |
|------|---------|
| `vault/documents/` | Deposited text/markdown (middle layer SSOT) |
| `vault/refs/` | Repo path registry |
| `activity.jsonl` | Append-only work log |
| `GOVERNANCE_LOCKED.md` | Lane law + forbidden roots + Council pointers |
| `NEEDS.md` | Bullet list from registry `real_needs` |
| `INBOX.md` | Task table |
| `notes.md` | Private scratch |
| `manifest.json` | agent_id, repo_root, pack_id, governance_version |
| `.cursor/rules/workspace-governance.mdc` | Always-on Cursor rule |
| `INCIDENT_REPORT_ALWAYS.md` | Auto-paste incident SSOT copy |
| `INCIDENT_MY_INSIGHTS.md` | Personal incident log |
| `incident-agent-state.json` | Ack week, quiz score, certification |
| `conflict-reports.jsonl` | Local mirror on submit |

Each `<repo_root>/.sina-agent/README.md` + `.cursor/rules/` — repo marker.

Non-maintainers: `<repo>/.cursor/rules/sina-command-readonly.mdc`.

---

## 13. API reference (agent endpoints)

**Base:** `http://127.0.0.1:13020` · **Server:** `scripts/sina-command-server.py`

| Endpoint | Methods | Key actions |
|----------|---------|-------------|
| `/api/council-room` | GET, POST | `list`, `share_mind`, `add_directive` |
| `/api/agent-loop` | GET, POST | `status`, `start`, `response`, `cancel`, `select_workspace`, `activate_pack`, `set_seeds` |
| `/api/agent-workspaces` | GET, POST | `list`, `select`, `ensure` |
| `/api/conflict-room` | GET, POST | `list`, `submit`, `close`, `ensure` |
| `/api/incident-room` | GET, POST | `list`, `ack_report`, `save_insight`, `submit_weekly`, `submit_quiz` |
| `/api/agent-review` | GET, POST | `list`, `submit`, `set_status` |
| `/api/intelligence-circle` | GET, POST | `status`, `chat` — **maintainer_auto_inject always false** |
| `/api/semej` | GET, POST | SEMEJ browser chain |
| `/api/workspace-vault` | GET, POST | `deposit`, `register_ref`, `log_activity`, `list` |
| `/api/emergency-stop` | POST | Full stop |
| `/health` | GET | Hub alive |

**Payload embed:** `command-data.json` → `system_unified`, `council_room`, `agent_workspaces`.

---

## 14. Integration readiness (10 checks per agent)

Council Room shows per-agent integration status:

1. Governance file exists  
2. INBOX exists  
3. Repo marker `.sina-agent/`  
4. Pack wired (if `pack_id` set)  
5. Incident files synced  
6. Hub private page renders  
7. SourceA edit lock respected  
8. Mind share channel reachable  

**Target:** 8/8 green before Phase 2 voting.

---

## 15. 10-pack loop — end-to-end

```
ASF: Council Room brief copied
  → Agent hub → workspace-<id>
  → Activate pack (if applicable) → Start loop (goal from pack or custom)
  → Planner writes round N → ~/.sina/agent-loop.json
  → INBOX: ~/.sina/cursor-inbox.md + .sina-loop/INBOX.md paths
  → Executor works in repo_root (NO auto-paste inject)
  → Submit round (summary + response) on SAME private page
  → Repeat until round 10 → status complete
```

**Packs (7):** trustfield, virlux, ai_dev_bridge_os, noetfield_local, noetfield_cloud, seven77, sinaai_maintainer.  
**No pack:** semej — custom goal or reports only.

**Semi-separate (not §4 roster):** MergePack — `AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md` · repo `~/Desktop/mergepack` · Live products tab.

---

## 16. Emergency & safety

| Event | Action | Law |
|-------|--------|-----|
| Runaway auto-paste | ⛔ Emergency stop | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` |
| Hub broken | Agent review → maintainer | Edit lock |
| Mac compromise suspicion | Mac Health Guard tab | `SINA_MAC_HEALTH_GUARD_LOCKED_v1.md` |
| Fleet must not block | ACE triage → continue | `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` |

**Kill script:** `scripts/kill-sina-command.sh`  
**Guards:** `auto_prompt_guard`, `disable_auto_feed_everywhere`, `intelligence_circle.disable_live_agent_automation`

---

## 17. Progress & orders integration

| Source | In brief as | Tab |
|--------|-------------|-----|
| P0 RunReceipt | Progress snapshot | Today / Track |
| WTM step (D1 shipped → D2 next) | Progress snapshot | system-roadmap |
| MASTER_ORDERS active | FOUNDER ORDERS section | orders |
| Open conflicts count | Progress snapshot | conflict-room |
| Paradox signals | Progress + paradox board | council-room |

Agents use progress block to align work — not to override locked laws.

---

## 18. Per-session checklist (copy for agents)

```
□ Hub up — :13020/health
□ Council Room — read brief + paradox board
□ Copy whole-system brief → paste in Cursor chat
□ Private page — governance + inbox read
□ Repo — correct repo_root only; forbidden roots untouched
□ Work — lane real_needs + artifacts
□ Report — mind share / conflict / incident / review if needed
□ Vault — deposit deliverables + log activity (middle layer)
□ Loop — submit on correct page if active
□ Never — edit SourceA (unless sinaai_maintainer)
□ Never — re-enable auto-paste inject
□ Never — finish work with chat-only artifacts (use vault)
```

---

## 19. Maintainer audit loop

```bash
cd ~/Desktop/SourceA/scripts
python3 audit_agent_governance_e2e.py    # 8 agents · governance v6
python3 audit_private_agent_pages.py       # 8/8 pages · packs
python3 audit_essentials_nav.py          # 37 tabs sync
python3 build-sina-command-panel.py      # refresh embedded payload
```

---

## 20. Phase roadmap

| Phase | Name | Status | Capability |
|-------|------|--------|------------|
| **0** | Integration readiness | ✅ Shipped | 9 workspaces, edit lock, private pages |
| **1** | Mind Share | ✅ Live | Cross-agent insights, repo lens, paradox board |
| **1b** | Whole-system brief | ✅ Live | One copy per session — `system_unified` |
| **1c** | Workspace vault | ✅ Live | Middle layer — deposit docs + activity per agent |
| **2** | Formal Council votes | 🔒 Reserved | Ballots on frozen options after discourse |
| **D2** | Graph Fusion (WTM) | 🔜 Next build | Strategic — maintainer lane |

---

## 21. Related locked docs (do not duplicate — link only)

| Topic | Doc |
|-------|-----|
| Fleet index | `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` |
| Private workspace layout | `SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md` |
| Operating roles | `AGENT_OPERATING_ROLES_LOCKED_v1.md` |
| Decision stack | `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` |
| Mind share law | `AGENT_MIND_SHARE_LOCKED_v1.md` |
| Council law | `AGENT_COUNCIL_ROOM_LOCKED_v1.md` |
| App as hub | `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` |
| Edit lock | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` |
| No Terminal | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` |
| Loop order | `SINA_AGENT_LOOP_ORDER_v1.md` |
| PAIOS blueprint | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` |

---

## 22. Traceability index

| Log | Path |
|-----|------|
| Mind share | `~/.sina/council-room/mind-share.jsonl` |
| Founder directives | `~/.sina/founder-directives.jsonl` |
| Loop state | `~/.sina/agent-loop.json` |
| Agent reports | `~/.sina/agent-command-reviews.jsonl` |
| Governance events | `~/.sina/agent-governance-events.jsonl` |
| Conflict cases | `~/.sina/conflict-room/cases.jsonl` |
| Incident weeks | `~/.sina/incident-room/weeks/` |
| Live agent comms | `~/.sina/live-agent-comms.jsonl` |
| Edit lock | `~/.sina/command-edit-lock.json` |
| Master orders | `~/Desktop/SourceA/sina-bowl/MASTER_ORDERS.json` |

---

*End of blueprint. Machine enforcement: `agent_workspace_registry.py`, `agent_council_room.py`, `agent_system_unified.py`, hub audits.*
