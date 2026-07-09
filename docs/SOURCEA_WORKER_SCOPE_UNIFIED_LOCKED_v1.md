# SourceA Worker Scope — Unified (LOCKED v1)

**Saved at:** 2026-07-05T12:40:00Z  
**Version:** 1.0.0 LOCKED  
**Supersedes:** fragmented Worker defs across entry-gate · commercial loop · autorun laws  
**Cursor rules:** `.cursor/rules/000-entry-gate.mdc` · `.cursor/rules/sourcea-worker-inbox.mdc`

---

## One sentence

> Worker executes bounded `WORK:` / INBOX tasks — feasibility gate → implement → receipt → one atomic commit per lane.

---

## Decision tree

```
Worker session start
    │
    ├─ python3 scripts/cursor_entry_gate.py --role worker
    ├─ python3 scripts/cursor_agent_self_audit.py session-start
    ├─ Read ~/.sina/worker-prompt-inbox-v1.json · .sina-loop/INBOX.md
    │
    ├─ Founder WORK: / INBOX item with scope?
    │     ├─ python3 scripts/prompt_feasibility_gate.py --role worker --strict
    │     ├─ cross_lane guard if path outside apps/
    │     ├─ implement (20–40 files max per pass)
    │     └─ receipt + commit
    │
    └─ No scope → REFUSE · ask one clarification
```

---

## Worker DOES

| Action | Gate |
|--------|------|
| Run INBOX head | `~/.sina/worker-prompt-inbox-v1.json` |
| Implement `sa-*` in bounded path | `WORK:` or INBOX scope in founder message |
| Edit product code under `apps/` | Lane ownership · dirty-tree map |
| One atomic commit per lane | `AGENTS.md` |
| Write receipts to `~/.sina/` | Append / update per schema |

---

## Worker DOES NOT

| Forbidden | Route to |
|-----------|----------|
| Cross-lane law edits without `EDIT ALLOWED:` | Brain / Governance |
| Unbounded repo search | Brain picks scope |
| Validator chains on Mac founder session | Cloud CI |
| Hub full rebuild as default | Maintainer 2 only |
| Guess save path | `agent_filing_registry_gate_v1.py resolve` |

---

## Approval boundaries

| Verb | Disk |
|------|------|
| `WORK: sa-XXXX — apps/foo/` | Full speed in scope |
| `EDIT ALLOWED: path ACTION:` | That path only |
| `SAVE TO: path` | One new file |
| Bare "fix" / "implement" | REFUSE — ask ASF |

Law: `brain-os/law/enforcement/AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md`

---

## Examples

**Good:** `WORK: sa-REV-001 — docs/commercial/ only — personalize outreach templates`  
**Bad:** Worker chat receives task in Brain chat without INBOX inject  
**Good:** Gate line 1: `GATE: hash8 | iso | gate_id=...`  
**Bad:** Implement governance law rewrite without `EDIT ALLOWED:`
