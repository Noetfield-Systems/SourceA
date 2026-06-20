# Private agent workspaces + governance (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
Every heavy Sina Command agent has:

1. **Governance** — `GOVERNANCE_LOCKED.md` + `.cursor/rules/workspace-governance.mdc`
2. **Real needs** — `NEEDS.md` (what this agent is for)
3. **Private scratch** — `~/.sina/agent-workspaces/<id>/` (INBOX, notes)
4. **Repo marker** — `<repo>/.sina-agent/` (points to private + rules)
5. **10-pack loop** (portfolio) — sidebar **Private agents** → that agent's page when `prompts/loop-pack-10-active.json` exists

## Registered agents (v3)

Full matrix: `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md`

| id | Label | Repo | Pack |
|----|-------|------|------|
| trustfield | TrustField | TrustField Technologies | trustfield |
| virlux | VIRLUX | VIRLUX | virlux |
| ai_dev_bridge_os | AI Dev Bridge OS | AI Dev Bridge OS | ai_dev_bridge_os |
| noetfield_local | Noetfield local SSOT | Noetfield-All-Documents | noetfield_local |
| noetfield_cloud | Noetfield cloud ship | Desktop/Noetfield | noetfield_cloud |
| seven77 | The 777 Foundation | The 777 Foundation | seven77 |
| semej | SEMEJ | SourceA (read-only) | — |

**MergePack** — not a private agent; see `AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md`.

## Noetfield — two agents (do not mix)

| Agent | Folder | Must not edit |
|-------|--------|----------------|
| **noetfield_local** | Noetfield-All-Documents | Desktop/Noetfield |
| **noetfield_cloud** | Desktop/Noetfield | Noetfield-All-Documents |

## Founder

**Private agents** (sidebar) → one page per agent = **workspace in the app**: governance, INBOX/notes preview, **Start 10-round loop**, **Submit round**. Finder is optional (“Agent notes”) for the coding agent only — not the founder workflow.

**Agent hub** = index only (tiles). **Home** never shows 10-packs.

Never Terminal — agents add **Actions** one-taps for commands.

## Maintainer

Registry: `scripts/agent_workspace_registry.py`  
Ensure: `POST /api/agent-workspaces` `{"action":"ensure"}`  
Audit: `python3 scripts/audit_agent_governance_e2e.py` · `python3 scripts/audit_private_agent_pages.py`
