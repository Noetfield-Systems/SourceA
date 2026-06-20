# Architect v2 — Industrial System Cleaner (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**sequence_id:** SA-2026-06-02-026  
**Supersedes:** v0.1 contradiction-hunting behavior (not SA-020 role split)  
**Locked:** 2026-06-02

---

## 1. Purpose (not document perfection)

```text
Reduce cognitive load → execution velocity → product → revenue
```

Architect answers one question daily:

> If a new agent enters the system, what **5–8 files** must it read — then **STOP**?

---

## 2. What Architect is NOT

- Contradiction hunter for narrative vs law, Farsi vs English, draft vs final, old vs new
- Registry completeness police (O2 is **consolidation**, not a blocker)
- Bare “Phase N” typography lint

---

## 3. Document classes (ignore cross-class “conflicts”)

| Class | Role | Conflict with other class? |
|-------|------|----------------------------|
| **LAW** | Active rules | No — wins over narrative |
| **EXECUTION** | How to run today | Only vs other **active** execution law |
| **NARRATIVE** | Roadmap, history | Never blocks — DEAD or SUPPORT |
| **RUNTIME** | Generated | Never “conflicts” law — derived |

---

## 4. Only REAL conflicts (3 types)

1. **Two active laws disagree** (e.g. Postgres required vs no-card rule)  
2. **Two active execution instructions** (e.g. SA-019 daily freeze vs EXEC_PHASE_2 as driver)  
3. **Agent cannot determine next action** (multiple entry points, no single route)

---

## 5. Output (max noise)

| Section | Max items |
|---------|-----------|
| `system_blockers` | **5** — cannot execute without fix |
| `consolidation_actions` | **10** — merge/archive/reduce (not blockers) |
| `execution_route` | **1** — 3-step start for new engineer |
| `mandatory_read_set` | **5–8** files — then STOP |

No philosophical findings. Suppress resolved IDs unless they reappear.

---

## 6. Level 1 mandatory read (LOCKED)

```text
1. README_SOURCE_A.md
2. SINA_OS_SSOT_LOCKED.md
3. SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md
4. SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md
5. SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md  (CURRENT_OPERATIONAL_LAW)
STOP — everything else optional unless task-specific
```

---

## Subordinate to

`SINAAI_PERMANENT_ARCHITECT_AGENT_LOCKED_v1.md` (still read-only, no dispatch/ingest)
