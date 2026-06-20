# Agent rule conflicts & stale truth — audit (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**Date:** 2026-06-10  
**sequence_id:** SA-2026-06-10-RULE-CONFLICT-AUDIT  
**Purpose:** One map of **conflicting** and **not-updated** rules so agents find disk truth smoothly  
**Reporter:** Cursor Worker audit (ASF request)

---

## 0. Where real truth lives (read this first)

| Priority | Canonical | Use for |
|----------|-----------|---------|
| 1 | `~/.sina/*-v1.json` · receipts · queue state | Live machine truth |
| 2 | `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` | Incident ids 001–021 |
| 3 | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | One law per topic |
| 4 | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | Router only — branch, don't restate |
| 5 | `brain-os/INDEX_LOCKED_v1.md` | File location SSOT |
| 6 | `brain-os/law/AGENT_RULES_IN_CHARGE_LOCKED_v1.md` + `/api/agent-rules-in-charge-v1` | Live highlights |
| 7 | `.cursor/rules/*.mdc` | Injected every session — **may conflict** with 1–6 |

**Never use as SSOT:** chat · compendium disk snapshot · `archive/attachments/` incident bodies · `RESEARCH/` mirrors

---

## P0 — Conflicts (agent gets wrong answer)

| ID | Conflict | A says | B says | Canonical |
|----|----------|--------|--------|-----------|
| **C01** | INCIDENT-015 double meaning | Registry: **ID collision filing** | `factory-stop-supremacy.mdc`: **STOP conduct** · INCIDENT-016/017: STOP ignored | Registry row 66 + `SINA_AGENT_INCIDENT_ID_COLLISION_...015_LOCKED_v1.md`. Conduct → new id (proposed **022**) |
| **C02** | Hub edit scope | `sina-command-readonly.mdc` + `sina-command-protected.mdc` (alwaysApply): **never edit SourceA** | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` v1.1: **Worker sole builder** | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` — scope `.mdc` by chat role |
| **C03** | Compendium vs registry | Compendium Part A ends **010** | Registry through **021** | Registry + `INCIDENT_SUBJECT_INDEX_LOCKED_v1.md` for live slice |
| **C04** | INCIDENT-012 body | Banner: superseded → 013 | 300+ lines still say canonical 012 | **INCIDENT-013** only |
| **C05** | Mandatory read paths | `MANDATORY_READ_BY_ROLE` · `000-workspace-lock`: `os/chat-handoffs/` (30 files) | `os/` has **0** handoff files — migrated to `brain-os/` | `brain-os/INDEX_LOCKED_v1.md` · `os/README_LOCKED_v1.md` |
| **C06** | Brain rules in Worker chat | `000-brain-unified.mdc` (alwaysApply): trace/spawn/refuse worker | Worker: `run inbox` full speed | Role-scoped: Brain rules **Brain chat only** |
| **C07** | Execution SSOT | `prompt-queue.mdc`: propose 10 · Confirm feed | `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md`: machine order + live mirror; confirm optional | **RESOLVED** — live ongoing law + prompt-queue.mdc update |
| **C08** | S10 vs bash subject | Tombstone + split docs exist | Residue: easy to cite S10 as bash incident | `INCIDENT_SUBJECT_INDEX` SUBJ-AGENT vs S10 law |
| **C09** | Incident two-layer | Full LOCKED bodies at root **and** `brain-os/incidents/` | Registry: body **only** in `brain-os/incidents/` | Registry §One rule |
| **C10** | START_HERE path | `000-workspace-lock`: `entry/START_HERE` | File at `brain-os/entry/START_HERE_LOCKED_v1.md` | `brain-os/entry/START_HERE_LOCKED_v1.md` |
| **C11** | INCIDENT-011 reuse | REWRITE disk edit (P0) | jsonl id `INCIDENT-011-brain-column-drift` void | 011 = REWRITE only · 014 = monitor |
| **C12** | Who edits hub | `AGENT_GOVERNANCE_INDEX`: sinaai_maintainer editor | `EDIT_LOCK` v1.1: maintainer **retired** | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` |

---

## P1 — Stale (outdated, misleads if cited as live)

| ID | Stale item | Problem | Canonical live |
|----|------------|---------|----------------|
| **S01** | Authority index | No rows: S10, founder bash, incidents registry, run-inbox disk truth | Add rows (ASF) |
| **S02** | Compendium header | 78/1000 · queue 20/30 · Jun 9 snapshot | `factory-now-v1.json` · `goal-progress-v1.py` |
| **S03** | `brain-os/INDEX_LOCKED_v1.md` | Incidents list stops ~002d | `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` |
| **S04** | `brain-os/cursor/rules/` | Partial mirror (9/23 rules) | `.cursor/rules/` active injection |
| **S05** | Conduct INCIDENT-015 report | In `archive/attachments/` not registry | `factory-stop-supremacy` + future **022** |
| **S06** | `AUTOMATION_CONVERGE_PROGRAM` | SUPERSEDED 2026-06-10 | `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` |
| **S07** | `CHATGPT_EXTERNAL_CRITIC` root stub | 9-line MOVED | `brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` |
| **S08** | Registry session-start slice | Omits 016–021 role guidance | Extend registry §Session-start |
| **S09** | `TODAY_AUTORUN_50_PLAN` | Listed ACTIVE in brain INDEX | SUPERSEDED per converge program |
| **S10** | Governance entry §0a | `entry/MANDATORY_READ_BY_ROLE` path | `brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md` |

---

## P2 — Duplicate prose (same rule, many places — slows truth)

| Topic | Copies (sample) | Canonical only |
|-------|-----------------|----------------|
| No Terminal | 6+ `.mdc` + laws | `brain-os/law/SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` |
| Governance routers | 6 files | Entry + Authority index + Rules in charge |
| SAVE·WORK·EDIT | 5 surfaces | `AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` |
| External critic | 4 surfaces | `brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` |
| Brain vs Worker | 5 surfaces | `WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md` |
| Hub edit lock | 3 `.mdc` + LOCKED | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` |
| Incident indexes | 4 files | Registry (ids) · Subject index (taxonomy) · Compendium (001–010 story) |
| **16× alwaysApply true** | Injected all sessions | Role-scoped rules per `AGENT_RULES_IN_CHARGE` |

---

## Fix priority (beneficial line)

1. **C01** — Resolve INCIDENT-015 collision (conduct → new id; fix `factory-stop-supremacy.mdc`)
2. **C02** — Scope hub `.mdc` by chat role; demote global alwaysApply
3. **C05** — Rewrite mandatory-read paths to `brain-os/*`
4. **C03/S08** — Registry session-start through 021; compendium pointer "see registry"
5. **S01** — Authority index rows for new topics
6. **C07** — `prompt-queue.mdc` advisory-only; not execution
7. **C04/C09** — Strip superseded full bodies; pointers only at root

---

## Agent smooth-truth checklist (session start)

```
1. role? → brain-os/entry/MANDATORY_READ_BY_ROLE (fix paths mentally to brain-os/)
2. incident id? → AGENT_INCIDENTS_REGISTRY only
3. topic law? → SINA_AUTHORITY_INDEX_MAP
4. live state? → ~/.sina + goal-progress-v1.py — not compendium
5. execution? → run inbox — prompt feed = live mirror only (`LIVE_ONGOING_PROMPTS`)
6. .mdc conflicts EDIT_LOCK? → EDIT_LOCK wins
```

---

**LOCKED** — Audit snapshot. Update when remediation ships; do not duplicate in companions.
