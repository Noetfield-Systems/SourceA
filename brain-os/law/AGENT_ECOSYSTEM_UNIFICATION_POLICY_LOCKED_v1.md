# Agent ecosystem unification policy (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Sequence:** SA-2026-AGENT-UNIFY-001  
**Parent:** `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md`  
**Phase 2 design:** `AGENT_COUNCIL_ROOM_LOCKED_v1.md`

---

## 0. Purpose

One policy for the **whole Sina Command ecosystem** so every agent:

1. Knows **exactly where to work** (private workspace page in the app)
2. Knows **exactly where to report** (fixed channels — never “please edit the app”)
3. **Never touches Sina Command code** unless `sinaai_maintainer`
4. Can later **share opinions / vote / solve** in a single Council Room (Phase 2 — not live yet)

---

## 1. Two phases (build order)

| Phase | Name | Status | What ships |
|-------|------|--------|------------|
| **0** | **Integration readiness** | **NOW** | Roles, edit lock, complete workspaces, visual job surfaces, Council Room tab (readiness dashboard only) |
| **1** | **Mind Share (live)** | **NOW** | Shared rules digest, repo lens compare, cross-agent insights, paradox board |
| **2** | **Council ballots** | **LATER** | Formal votes on frozen options after discourse in Mind Share |

**Law:** Do not build Phase 1 voting until Phase 0 audits pass (`audit_agent_governance_e2e.py`, `audit_private_agent_pages.py`, hub Council Room shows 8/8 workspace-ready).

---

## 2. Role matrix (concrete limits)

| Role | Agents | May edit own product repo | May edit SourceA | May edit hub UI/scripts |
|------|--------|---------------------------|------------------|-------------------------|
| **maintainer** | `sinaai_maintainer` | Yes (SinaaiDataBase) | **Yes** (ASF-approved) | **Yes** |
| **portfolio** | trustfield, virlux, ai_dev_bridge_os, noetfield_*, seven77 | Yes — `repo_root` only | **No** | **No** |
| **automation** | semej | **No** (SourceA read-only) | **No** | **No** |

**MergePack** is **not** a registered agent — semi-separate lane only (`AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md`).

**Hard rule:** If the task requires changing `~/Desktop/SourceA/`, `agent-control-panel/`, or `scripts/sina-command-server.py` → **stop** → file **Agent report** (Backlog) or Council channel (Phase 0). **Never** ask ASF for repo access to Command.

---

## 3. Where agents work (visual surfaces)

**Sina Command is the pre-unifying hub** — ASF does not re-paste rules per agent. See `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md`.

**Workspace vault (middle layer):** every agent deposits all documents and logs activity in their private page vault — see `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md`. Work must not live only in repo chats.

Every registered agent **must** use these app surfaces — not ad-hoc Finder paths:

| Surface | Tab / route | Job |
|---------|-------------|-----|
| **Council Room** | `council-room` | **START HERE** — whole-system brief, all rules, mind share, paradoxes |
| **Private workspace** | Sidebar → **Private agents** → `<agent>` | Governance, 10-pack loop, round submit, scratch preview |
| **Agent hub** | `agent-loop` | Step 2 — pick your agent page |
| **Backlog** | `backlog` → Agent reports | Bugs, feature requests, “need an Action button” |
| **Conflict Room** | `conflict-room` | ACE triage — doc/strategy conflicts; never block delivery |
| **Incident Room** | `incident-room` | Weekly incident share, insight, certification |
| **Live agents** | `intelligence` | OpenRouter / cloud API chat — **not** repo implementation |
| **SEMEJ** | `semej` | Browser multi-AI chain (`semej` agent only) |

Portfolio agents implement in **their repo**; all **reporting** flows through the rows above.

---

## 4. Forbidden actions (all non-maintainer agents)

- Edit `~/Desktop/SourceA/**` (hub, panel, server, validators, loop scripts)
- Patch `agent-control-panel/assets/app.js` or `index.html`
- Ask founder to run Terminal for Command fixes
- Ask founder for git write access to SourceA
- Store “votes” in random markdown — use Council channels when Phase 1 ships; until then use **Agent reports** + **Conflict Room**

**Allowed:** Read running hub at `http://127.0.0.1:13020`, read laws in SourceA, edit own `repo_root`, write private scratch under `~/.sina/agent-workspaces/<id>/`.

---

## 5. Workspace completeness (Phase 0 gate)

Each of the **9 registered agents** must have on disk and in hub payload:

| Check | Path / signal |
|-------|----------------|
| Governance | `~/.sina/agent-workspaces/<id>/GOVERNANCE_LOCKED.md` |
| INBOX | `INBOX.md` |
| Repo marker | `<repo_root>/.sina-agent/README.md` |
| Cursor rules | `workspace-governance.mdc` + `sina-command-readonly.mdc` (non-maintainer) |
| Hub page | Sidebar **Private agents** → full page with incident + conflict panels |
| Pack or lane | 10-pack ready **or** documented custom lane (semej, mergepack) |
| Incident files | `INCIDENT_REPORT_ALWAYS.md` + state JSON |

Maintainer runs:

```bash
cd ~/Desktop/SourceA/scripts
python3 agent_private_workspaces.py   # or ensure via build
python3 audit_private_agent_pages.py
python3 audit_agent_governance_e2e.py
python3 build-sina-command-panel.py
```

Council Room tab must show **integration %** per agent before Phase 1 starts.

---

## 6. Maintainer-only implementation path

Only **sinaai_maintainer** (`~/Desktop/SinaaiDataBase` chat) + ASF may:

- Implement Council Room Phase 1 (API + ballots)
- Add Actions one-tap buttons requested via agent reports
- Change governance laws after ASF review

All other agents: **propose** via Backlog / Conflict / Council (Phase 1).

---

## 7. Traceability

| Log | Purpose |
|-----|---------|
| `~/.sina/agent-command-reviews.jsonl` | Agent reports |
| `~/.sina/conflict-room/cases.jsonl` | Conflict submissions |
| `~/.sina/incident-room/weeks/` | Weekly incidents |
| `~/.sina/agent-governance-events.jsonl` | Workspace events |
| `~/.sina/council-room/` | Phase 1 topics & votes (reserved) |

---

## 8. Related laws

- `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md`
- `SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md`
- `AGENT_OPERATING_ROLES_LOCKED_v1.md`
- `AGENT_COUNCIL_ROOM_LOCKED_v1.md`
