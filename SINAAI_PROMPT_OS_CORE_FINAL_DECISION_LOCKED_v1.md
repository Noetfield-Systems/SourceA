# Sinaai — Prompt OS Core Final Decision (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Conflict resolution + target architecture + doc hierarchy

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-012  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 only for ecosystem structure  
**Implementation:** `~/Desktop/SinaPromptOS/` (**canonical name:** Prompt OS Core / `prompt-os-core`)  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## 1. Conflict resolution (FINAL — no architecture war)

### There is **no** architecture conflict.

| Tension | Resolution |
|---------|------------|
| “Fully autonomous AI company” vs “prompt factory today” | **Same architecture, different maturity (L0→L3).** Target is locked; **today = L1**. |
| Many Source A docs | **One doctrine stack** (§3) — no fourth mega-SSOT. |
| TrustField vs mono registry (C9) | **DELIVERY repo is live**; registry sync is ledger **after** burst — not a blocker. |
| MonoRepo = orchestration host? | **No.** **Prompt OS Core** (`SinaPromptOS`) orchestrates; **MonoRepo** = PAIOS Runtime spine `:8000`. |
| ASF “cannot produce tasks” | **Wrong.** ASF sets **weekly strategy** (`projects.json`, think day); **Prompt OS** picks **next** from `plan.json` on execute days. |

### What we do **not** claim today (honest — locked)

- Cursor API auto-runs code in IDE  
- `plan.json` auto-updates every daemon cycle (`auto_sync_plan: false`)  
- Verify loop fully automatic (Execution Truth v1 = evidence file, not auto-git)  
- Daemon = unsupervised ship to production  

### What we **do** claim today (locked)

```text
Sina OS (law)
  → ASF (weekly strategy + structural approval)
  → Prompt OS Core (global priority + one prompt per project)
  → Cursor (execute one task)
  → Verify (human or script)
  → EXECUTION LOG (evidence) → truth re-rank
  → Update plan.json (human default; `mark-done-verified.sh` preferred)
```

**Phase 2 locked:** `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` — reports (intent) + execution logs (evidence).

**GPT + Cursor alignment:** You want *think once / execute five days* — **that is the target.** Implementation gap is **automation depth**, not **wrong design**.

---

## 2. Target architecture (LOCKED)

```text
SINA OS — global law (Source A SSOT)
        ↓
ASF — weekly strategy + structure gate
        ↓
PROMPT OS CORE — global brain (SinaPromptOS)
        ↓
Priority Engine — all projects → PRIORITY_MAP.json
        ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
TrustField    Noetfield     Virelux       777 + Mono
local os/     local os/     local os/     local os/
        ↓           ↓           ↓           ↓
   1 prompt    1 prompt    1 prompt    1 prompt
        ↓           ↓           ↓           ↓
   Cursor      Cursor      Cursor      Cursor
```

**Locked requirement:** Multi-project **parallel** = up to N tasks per cycle (**1 task per repo per cycle**), default N=3.

**Formula (unchanged):** `Prompt(repo) = f(Sina OS, RepoContext, GlobalPriority)`

---

## 3. Document hierarchy (FINAL — read this, not everything)

| Order | Document | Use |
|-------|----------|-----|
| 1 | `SINA_OS_SSOT_LOCKED.md` | Ecosystem law |
| 2 | **`SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`** | **This file — decisions + target vs today** |
| 3 | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` | Agents, Runtime LLM, Cursor rules |
| 4 | `SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md` | Production layout + settings |
| 5 | `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` | Human day (Mon–Fri) |
| 6 | `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | **What to build next** |
| 7 | `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` | **Execution evidence** |
| 8 | `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` | **AI control (guarded)** |
| 9 | `SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md` | **Final status + what to do** |
| — | `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | Farsi mirror only |
| — | Chat / “Production OS merged” | **Narrative only — not law** |

**Do not add:** another SSOT, another merged blueprint, or agent memory as authority.

---

## 4. Roles (one table)

| Actor | Weekly (think) | Daily (execute) |
|-------|----------------|-----------------|
| **Sina OS** | Law unchanged | Embedded in every prompt |
| **ASF** | Priority, freeze exceptions, registry | Paste prompt, verify, approve prod |
| **Prompt OS Core** | — | Rank, compile, write `outputs/` |
| **Per-project os/** | Queue `next_tasks` | `done` / `blocked` after verify |
| **Cursor** | — | One task per session |
| **SinaaiRuntime** | — | Separate plane (Telegram) — not Prompt OS |

---

## 5. Implementation alias (locked)

| Name | Path |
|------|------|
| **Prompt OS Core** | `~/Desktop/SinaPromptOS/` |
| Alias `prompt-os-core` | Same folder (do not fork) |
| Memory DB | `data/memory.db` (primary) + SQLite history |
| Config | `config/projects.json` + `config/settings.json` |
| Entry | `main.py` / `daemon.py` |

---

## 6. Sunday / Monday–Friday (locked operating model)

**Sunday (think — ASF):**  
Read SSOT + this decision doc → adjust `global_priority` in `projects.json` → refresh each repo `os/plan.json` queues (not Cursor coding).

**Before any repo Cursor chat:** `./scripts/run-feedback-cycle.sh` or `run-day.sh morning` so SourceA has fresh ecosystem + truth tables.

**Monday–Friday (execute — ASF) — parallel lanes (≤3 prompts/cycle):**

```bash
./scripts/run-day.sh morning
# Up to 3 prompts → 3 Cursor workspaces (one task each) → VERIFY each lane
# ./scripts/submit-execution-log.sh <repo> log.yaml
# ./scripts/mark-done-verified.sh <repo> log.yaml
./scripts/run-day.sh evening   # includes truth cycle
```

**No** rereading all repos. **No** deciding what’s next. **Yes** verify and memory update.

---

## 7. Migration from TrustField-only (DONE)

| Before | After |
|--------|-------|
| Only `TrustField/os/` | Six projects in `config/projects.json` |
| Manual prompt | `core/prompt_compiler.py` + router |
| No global map | `global/PRIORITY_MAP.json` |
| TrustField adapter doc | Still valid: `sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md` |

TrustField `os/` **stays in TrustField repo** — Prompt OS Core **reads** it; does not move it.

---

## 8. ASF sign-off

| Decision | ☐ Approved |
|----------|------------|
| No architecture conflict — proceed on Prompt OS Core | ☐ |
| Target = weekly think + daily prompt factory | ☐ |
| Doc hierarchy §3 is final | ☐ |
| Build order = `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | ☐ |

**Date:** __________

---

## Document control

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-012 | Final conflict resolution + operating model |
| 1.1 | 2026-06-02 | SA-2026-06-02-012 | Execution Truth Layer ref + parallel execute wording |
