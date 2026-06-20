# Cursor Agent — Context / Memory / Closeout Incident (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-06-INCIDENT-002  
**Classification:** INTERNAL — MANDATORY READ for every Cursor agent session  
**Canonical location:** `~/Desktop/SourceA/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md`  
**Companion:** `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` (auto-paste) · `scripts/cursor_agent_self_audit.py` (enforcement loop)

---

## 1. Executive summary

Cursor agents **lose chat memory** when context is summarized or a new session starts. Without a **disk-backed loop**, the agent:

- Re-implements work already done (or claims done without evidence)
- Skips privacy locks, repo boundaries, and verify gates
- Ships www changes with **no session closeout**, **no incident insight**, **no ledger row**
- Repeats the same class of mistake because **chat is not SSOT**

**Severity:** **High** — wastes founder time, risks privacy leaks (e.g.  tables on www), and erodes trust in the agent team.

---

## 2. Verified failure modes (2026-06-06)

| # | Symptom | Root cause | Fix |
|---|---------|------------|-----|
| 1 | User: "you have no memory" after UPG-003/004 | Context summarization; no `SESSION_CLOSEOUT` logged | Run `cursor_agent_self_audit.py session-close` every task end |
| 2 | TrustField fintech research names in chat | Skipped `AUTO_INTERNAL_PRIVACY_LOCK.md` at session start | Session-start read chain before edits |
| 3 | Local agent claims `make verify-gtm` when target missing | Chat memory beat `REPO_TRUTH_CORRECTIONS.md` | Read `AGENT_TEAM_STATE.yaml` + corrections log first |
| 4 | Work in wrong repo (All-Documents vs TrustField vs Noetfield) | No `resolve-agent` from cwd | Run `session-start` — prints forbidden roots |
| 5 | "Implemented" but not committed / not on prod | No verify + no closeout evidence | Closeout must list: files, build, smoke, deploy status |

---

## 3. Mandatory loop (every session)

### A — Session start (before any edit)

```bash
python3 ~/Desktop/SourceA/scripts/cursor_agent_self_audit.py session-start
```

Agent must read printed paths in order:

1. `~/.sina/agent-workspaces/<id>/INCIDENT_REPORT_ALWAYS.md`
2. `~/.sina/agent-workspaces/<id>/MANDATORY_READ_CHAIN.md`
3. `~/.sina/agent-workspaces/<id>/SESSION_CLOSEOUT_LATEST.md` (if exists)
4. Workspace `WORKSPACE_SESSION_PROMPT_LOCKED.md` or repo `os/plan.json`

Then append ack to `SESSION_LEDGER.jsonl`.

### B — During work

Log milestones:

```bash
python3 ~/Desktop/SourceA/scripts/cursor_agent_self_audit.py log-event \
  --summary "UPG-003 vendor-pack page drafted" --evidence "web/app/pilot/vendor-pack"
```

### C — Session close (before last reply on substantive work)

```bash
python3 ~/Desktop/SourceA/scripts/cursor_agent_self_audit.py session-close \
  --summary "..." --files "..." --verify "npm run build PASS" --next "founder deploy"
```

Writes `SESSION_CLOSEOUT_LATEST.md` + hub insight stub.

### D — Weekly (Sina Command)

Incident Room: share one near-miss + pass quiz (auto-paste incident). **This incident counts as a valid weekly share topic.**

---

## 4. Never again

- Do not treat **conversation summary** as truth — **disk wins**
- Do not mark UPG/backlog **done** without evidence URLs or file paths in closeout
- Do not paste **50-company fintech matrix** or named peers on www / committed docs
- Do not end a multi-file implementation turn **without** session-close or explicit "blocked" reason

---

## 5. Emergency / founder phrase

If founder says **"incident"**, **"no memory"**, or **"self audit"**:

1. Stop implementation
2. Run `session-start` + read `SESSION_CLOSEOUT_LATEST.md`
3. File `log-event` for the mistake class
4. Produce closeout report in the reply (template in skill `agent-self-audit-loop`)

---

## 6. Agent skill

Cursor skill: `@agent-self-audit-loop` (`~/.cursor/skills/agent-self-audit-loop/SKILL.md`)

---

*End LOCKED v1*
