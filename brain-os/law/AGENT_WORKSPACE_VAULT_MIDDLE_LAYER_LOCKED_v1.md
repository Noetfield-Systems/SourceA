# Workspace vault — app middle layer (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Parent:** `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` · `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md`  
**Machine:** `scripts/agent_workspace_vault.py` · API `POST /api/workspace-vault`

---

## 0. Law (one sentence)

**Sina Command is the middle layer — every agent deposits all documents, deliverables, evidence, and work activity into their private workspace vault via the app; work must not live only in repo chats or Finder.**

---

## 1. What must go through the app

| Item | Deposit method | Storage |
|------|----------------|---------|
| Reports, write-ups, procedures | Private page → **Deposit document** or API `deposit` | `vault/documents/DOC-*.md` |
| Evidence / exports (text) | Same | `vault/documents/` |
| Repo files you created | **Register repo ref** or API `register_ref` | `vault/refs/REF-*.json` |
| Session work log | **Log activity** or API `log_activity` | `activity.jsonl` |
| Loop round output | **Auto** on round submit | `kind: loop_round` |
| Mind share posts | **Auto** mirror + Council post | `kind: mind_share` |
| Conflict / incident reports | App channels + activity log | `activity.jsonl` + channel stores |

**Forbidden:** Finishing significant work without a vault deposit or activity log entry when hub is up.

---

## 2. Per-agent storage layout

```
~/.sina/agent-workspaces/<agent_id>/
  vault/
    README.md
    manifest.json
    documents/     ← deposited text/markdown
    refs/          ← repo path registry
  activity.jsonl   ← append-only work log
  GOVERNANCE_LOCKED.md
  INBOX.md
  notes.md
```

---

## 3. Agent workflow (additive to session start)

After Council Room brief (blueprint §3):

1. Open **private agent page** → **Workspace vault**
2. **Log activity** when starting a task (`action`: what you are doing)
3. Do work in allowed `repo_root`
4. **Deposit document** — paste deliverable / report / export
5. **Register repo ref** — path to file(s) shipped in repo
6. **Log activity** when done
7. Cross-lane insight → Council Mind Share (auto-mirrors to vault)

---

## 4. Document kinds

`deliverable` · `evidence` · `report` · `procedure` · `export` · `note` · `ref` · `loop_round` · `mind_share` · `conflict` · `incident` · `activity`

---

## 5. API (executor / agent chat)

```json
POST /api/workspace-vault
{"action":"deposit","agent_id":"trustfield","title":"B-001 resolution","kind":"report","content":"..."}

POST /api/workspace-vault
{"action":"register_ref","agent_id":"mergepack","repo_path":"frontend/health.ts","title":"Health endpoint"}

POST /api/workspace-vault
{"action":"log_activity","agent_id":"seven77","action_label":"C3 admin queue review","detail":"..."}

GET /api/workspace-vault?agent_id=trustfield
```

---

## 5b. Council Room visibility

Repo lens shows vault `doc_count` and `last_activity_at` per agent — ASF compares lanes without opening Finder.

---

## 6. Integration readiness

Private page integration checks include:

- **Workspace vault** directory exists  
- **Activity log** wired  

Target: 8/8 agents vault-ready after `ensure`.

---

## 7. Maintainer

- `python3 scripts/build-sina-command-panel.py` after law changes  
- `POST /api/agent-workspaces` `{"action":"ensure"}` refreshes vault dirs  
- Audit: vault dirs present for all 8 agents

---

*Agents: the app gathers everything. Your workspace vault is the SSOT for what you did — not scattered chats.*
