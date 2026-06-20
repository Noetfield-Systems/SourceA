# Agent governance index (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Parent:** `SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md`  
**Operational blueprint:** `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` — **start here for full E2E agent use**  
**Workspace vault:** `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md` — **deposit all docs + activity via app**  
**Automation blueprint:** `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` §6 (Cursor plane)  
**Edit lock:** `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md`

## Who may edit Sina Command (SourceA)

| Editor | Allowed |
|--------|---------|
| ASF (founder human) | Yes |
| **SinaaiDataBase** Cursor workspace (not a scoreboard agent) | Yes |
| All registered private agents | **No** — `POST /api/agent-review` or Backlog → Agent reports |

## Registered private agents (v3)

| id | Role | Thread | Pack | Repo | Forbidden (summary) | Private workspace |
|----|------|--------|------|------|---------------------|-------------------|
| trustfield | portfolio | THREAD-PORTFOLIO | trustfield | TrustField Technologies | SourceA | `~/.sina/agent-workspaces/trustfield/` |
| virlux | portfolio | THREAD-PORTFOLIO | virlux | VIRLUX | SourceA | `~/.sina/agent-workspaces/virlux/` |
| ai_dev_bridge_os | portfolio | THREAD-WIRE | ai_dev_bridge_os | AI Dev Bridge OS | SourceA | `~/.sina/agent-workspaces/ai_dev_bridge_os/` |
| noetfield_local | portfolio | THREAD-PORTFOLIO | noetfield_local | Noetfield-All-Documents | Noetfield cloud + SourceA | `~/.sina/agent-workspaces/noetfield_local/` |
| noetfield_cloud | portfolio | THREAD-PORTFOLIO | noetfield_cloud | Desktop/Noetfield | Local docs + SourceA | `~/.sina/agent-workspaces/noetfield_cloud/` |
| seven77 | portfolio | THREAD-PORTFOLIO | seven77 | The 777 Foundation | SourceA | `~/.sina/agent-workspaces/seven77/` |
| semej | automation | THREAD-PORTFOLIO | — | SourceA (read-only) | **All SourceA** | `~/.sina/agent-workspaces/semej/` |

**MergePack is NOT a registered agent** — semi-separate lane only → `AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md` · hub **Live products** / **Repos**.

Governance file per agent: `~/.sina/agent-workspaces/<id>/GOVERNANCE_LOCKED.md`

## Ecosystem unification & Council Room

| Phase | Doc | Hub tab |
|-------|-----|---------|
| **1 (now)** | `AGENT_MIND_SHARE_LOCKED_v1.md` | **Council Room** — shared rules, repo lens, mind share, paradoxes |
| **2 (later)** | `AGENT_COUNCIL_ROOM_LOCKED_v1.md` | Formal ballots on frozen options |

**Law:** Registered private agents **never** edit SourceA — report via Backlog, Conflict, Incident, Council (Phase 0). Hub code edits: SinaaiDataBase workspace only.

## Decision stack & smart judgment

→ `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` — authority hierarchy, what to load before builds, beneficial line, self-healing loop.

## External critic input

→ `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §3 · `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` (canonical — not restated here).

## Founder (no Terminal)

1. **Private agents** (sidebar) → pick agent page  
2. Read **Governance & rules** on that page  
3. **Start loop** / **Submit round** on **that page only**  
4. **Agent hub** = index tiles only  

## Live agents (online API / cloud — not repo chats)

**Tab:** Sina Command → **Live agents**

- **OpenRouter API**, **Cursor Cloud**, **Cursor IDE bridge**, **SEMEJ** (when running)
- **Ping live agents** — real-time online check
- Hub ↔ agent log: `~/.sina/live-agent-comms.jsonl` (not repository chats)
- Per-repo Cursor work → **Private agents** pages only

## Traceability

| Log | Path |
|-----|------|
| Live agent comms | `~/.sina/live-agent-comms.jsonl` |
| Governance events | `~/.sina/agent-governance-events.jsonl` |
| Agent reports | `~/.sina/agent-command-reviews.jsonl` |
| Loop state | `~/.sina/agent-loop.json` |
| Edit lock manifest | `~/.sina/command-edit-lock.json` |

## Audits (hub edit workspace)

```bash
cd ~/Desktop/SourceA/scripts
python3 audit_agent_governance_e2e.py
python3 audit_private_agent_pages.py
python3 build-sina-command-panel.py
```

## Smoke (founder, after Refresh)

1. Private agents → TrustField, noetfield_local, semej — governance visible  
2. TrustField start loop → 10 prompts on that page; switch agent → mismatch banner if loop active  
3. Backlog → Agent reports  
4. Sources → governance laws open  
5. Fleet vs Agents tab — fleet is supplemental Cursor activity  
