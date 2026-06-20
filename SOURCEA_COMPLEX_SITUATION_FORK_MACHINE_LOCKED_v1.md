# SourceA Complex Situation Fork Machine (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**CROSS-DOC CLUSTER:** SESSION-INTEGRITY-10 · Linkage: `SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md`  
**Stacked on:** `SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` · **Human channel:** fork clarity · Effect · **Machine channel:** T1–T5 · 7-step

**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-FORK-MACHINE  
**Authority:** ASF · Maintainer ships machine · Founder confirms forks only  
**Apex:** `SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` — daily 5 steps; this machine = SAY+PICK depth for complex sessions  
**Parent:** `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` §2–§4 · `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md`  
**Unified map:** `SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md` — hierarchy · one ASF prefix  
**Companion:** `SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md` · Canvas `sourcea-system-integrity-100.canvas.tsx`  
**Prompt (copy-paste):** `prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md`  
**Script:** `scripts/complex_situation_fork_machine_v1.py`  
**Validator:** `scripts/validate-complex-situation-fork-v1.sh`

---

## 0. One sentence

> **When a chat is complex, mega, or high-stakes (Brain, governance, multi-incident), agents run the Fork Machine — inventory every fork, show Effect per option, get Founder clarity, then execute to disk — never vague “confirm”.**

---

## 1. When to trigger (mandatory)

| Trigger | Examples | Agent action |
|---------|----------|--------------|
| **T1 Mega chat** | >30 turns · multiple topics · user says “big picture / whole system / all conflicts” | Run Fork Machine before more builds |
| **T2 High-stakes role** | Brain · Maintainer strict build · Founder law edit · Council | Run at session start |
| **T3 Multi-fork** | ≥2 founder decisions · paradox · conflict case · P0 ambiguity | Run before asking ASF anything |
| **T4 Machine red** | `find_critical_bugs` CRITICAL · ecosystem safety FAIL · drift < target | Triage forks first, then fix |
| **T5 Playbook** | SYS-INTEGRITY-100 · sa-0790 governance · GOV_UNIFY batch | Use 100-step canvas + this machine |

**Rule:** If any trigger matches, **forbidden** to ask “do you confirm recommended?” without **Subject + Question + Effect** per fork.

---

## 2. Fork Machine pipeline (7 steps — every complex session)

```text
① TRIAGE   → Read disk (ACTIVE_NOW · factory-now · command-data · incidents)
② CLASSIFY → LAW | MACHINE | PROJECTION per claim (playbook Appendix C)
③ INVENTORY→ List every fork F1..Fn (id · subject · who decides)
④ OPTIONS  → Per fork: 4 options OR yes/no quad OR text box (§3)
⑤ CLARIFY  → Founder picks / comments / asks — Canvas or chat
⑥ CONFIRM  → Only “Confirmed” forks → explicit ASF order (§5)
⑦ EXECUTE  → Maintainer to disk + validators + Track · closeout §6
```

**Speed rule:** Steps ①–④ in one agent turn when possible. Do not spread across passive chat.

---

## 3. Fork card standard (same as Canvas live form)

Every fork **must** include:

| Field | Required |
|-------|----------|
| **id** | Step id (e.g. `1.02`) or `F-01` |
| **subject** | 3–8 words |
| **question** | One clear sentence |
| **diskToday** | Evidence cite |
| **type** | `choice4` · `yesno` · `text` |
| **options** | A/B/C/D each with **ifYouPick** = Effect on disk |
| **maintainerAction** | What executor writes |
| **founderAction** | What ASF does after (usually hub spot-check) |

**Yes/no forks** still use **4 choices:** YES · NO · DEFER · DISCUSS.

**Founder confirm checkbox** = “I read the Effect line.”

---

## 4. Roles in Fork Machine

| Role | Does | Does NOT |
|------|------|----------|
| **Brain** | Triage · route · spawn · refuse Worker builds · invoke Fork Machine for T2 | Full E2E shell chains · vague founder asks |
| **Maintainer** | ①–④ disk prep · ⑦ execute · validators · hub rebuild | Mark founder forks DONE without ASF order |
| **Worker** | One sa · disk proof · VERIFY closeout | Multi-fork policy · law edits |
| **Founder** | ⑤ clarify · ⑥ confirm · SAVE/LOCK | Terminal · invent parallel rules |

---

## 5. ASF order format (after Founder confirms)

**Batch 2 canonical prefix:** `ASF: FIVE-STEP — PICK:` (see `SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md` §10). Legacy `ASF: FORK-MACHINE —` = same meaning for complex batches.

```text
ASF: FIVE-STEP — PICK: (fork batch)

1. [1.02] Single north star
   Decision: A — WTM spine
   Effect: Hub + GOAL_HIERARCHY headline = STRATEGIC-SLICE only
   Founder note: (optional)

2. [2.03] AUTO-RUN as P0
   Decision: NO — rejected forever
   Effect: No hub hero promotes START AUTO RUN

Maintainer: apply to disk + Track + result table per RESULT_DRIVEN §4.
```

**Forbidden:** `ASF: confirm recommended` without numbered Effect lines.

---

## 6. Mandatory closeout (complex sessions)

Extends `RESULT_DRIVEN` §4 with:

```markdown
## Fork inventory (this session)
| id | Subject | Decision | Effect summary | Disk proof |
|----|---------|----------|----------------|------------|

## Unresolved forks (founder still deciding)
| id | Subject | Blocker | Next clarify question |
|----|---------|---------|------------------------|

## Golden insight (one paragraph — what to do next)
**Problem:** …
**Fixed:** …
**Your next 3 actions:** 1. … 2. … 3. …

## Maintainer receipt
- Validators run: …
- Track rows: …
- Canvas synced: Y/N
```

---

## 7. Surfaces (stable machine)

| Surface | Use |
|---------|-----|
| **Canvas** | `sourcea-system-integrity-100.canvas.tsx` — live form · persists picks/comments/confirm |
| **Session log** | `SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md` — working mirror |
| **Track** | `founder_request_tracker` — `FR-*` per batch |
| **Receipt** | `~/.sina/complex-situation-fork-receipt-v1.json` — script writes after assess |
| **100-step playbook** | Full ecosystem audit cadence |

**Quick start command:**

```bash
cd ~/Desktop/SourceA/scripts
python3 complex_situation_fork_machine_v1.py assess --role brain --json
python3 complex_situation_fork_machine_v1.py open-canvas-hint
```

---

## 8. Integration map

| Law | Relationship |
|-----|--------------|
| `RESULT_POLICY` | Fork Machine extends option matrix + closeout for complex cases |
| `SYS_INTEGRITY_100` | Playbook = scheduled full Fork Machine pass |
| `AGENT_JUDGMENT` | Beneficial line before fork inventory |
| `GOV_UNIFY` | Batch law merges after fork confirm |
| `ACE` | Conflict cases → forks 7.05–7.07 |

---

## 9. Index wiring

| Surface | Path |
|---------|------|
| Authority row | `FORK_MACHINE` in `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` |
| Governance entry | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §0i |
| READ_CHAIN | `scripts/hub_essentials_index.py` |
| Brain mandatory | `MANDATORY_READ_BY_ROLE_LOCKED_v1.md` Brain row |
| Cursor rule | `.cursor/rules/complex-situation-fork.mdc` |
| Rules in charge | `agent_rules_in_charge.py` context `complex_fork` |

---

*End SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1*
