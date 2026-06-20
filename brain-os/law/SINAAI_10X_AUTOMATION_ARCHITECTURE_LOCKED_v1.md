# Sinaai — 10x Automation Architecture (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Runnable multi-repo execution engine under Sina OS

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-011  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 and `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md`  
**Implementation root:** `/Users/sinakazemnezhad/Desktop/SinaPromptOS/` (production layout = `prompt-os-prod` in spec)  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## Lock statement

This document **locks** the 10x automation target architecture, folder layout, loop, daemon rules, and safety defaults.  
**Supersedes** informal chat/spec for agents & automation only — not ecosystem SSOT, Phase 1 product plans, or commercial GTM.

---

## 1. Final architecture (locked)

```text
SINA OS (law) — Desktop/SourceA/SINA_OS_SSOT_LOCKED.md
        ↓
ASF (structure gate only — not daily micro-tasks)
        ↓
UNIFIED AGENT ORCHESTRATOR — core/orchestrator.py
        ↓
PROMPT OS — state_loader + priority + task_gen + prompt_compiler
        ↓
VALIDATOR — core/validator.py (before Cursor)
        ↓
CURSOR — runtime/cursor_executor.py (write prompt + clipboard; human/agent executes)
        ↓
MEMORY — per-repo os/plan.json + global/GLOBAL_STATE.json + PRIORITY_MAP.json
        ↓
[optional] RUNTIME PLANE — SinaaiRuntime :8000 (separate; not in this loop)
```

**Formula (unchanged):** `Prompt(repo) = f(Source A, RepoContext, GlobalPriority)`

---

## 2. Production folder map (implemented)

Spec name `prompt-os-prod/` = **`~/Desktop/SinaPromptOS/`**

| Spec path | Actual path |
|-----------|-------------|
| `core/orchestrator.py` | `SinaPromptOS/core/orchestrator.py` |
| `core/state_loader.py` | `SinaPromptOS/core/state_loader.py` |
| `core/priority_engine.py` | `SinaPromptOS/core/priority_engine.py` |
| `core/task_generator.py` | `SinaPromptOS/core/task_generator.py` |
| `core/prompt_compiler.py` | `SinaPromptOS/core/prompt_compiler.py` |
| `core/validator.py` | `SinaPromptOS/core/validator_gate.py` |
| `core/sync_engine.py` | `SinaPromptOS/core/sync_engine.py` |
| `core/ecosystem_publish.py` | `SinaPromptOS/core/ecosystem_publish.py` |
| `core/ecosystem_feedback.py` | `SinaPromptOS/core/ecosystem_feedback.py` |
| `core/execution_tracker.py` | `SinaPromptOS/core/execution_tracker.py` — **Phase 2 truth** |
| `runtime/cursor_executor.py` | `SinaPromptOS/runtime/cursor_executor.py` |
| `runtime/event_bus.py` | `SinaPromptOS/runtime/event_bus.py` |
| `daemon/main_daemon.py` | `SinaPromptOS/daemon/main_daemon.py` |
| `dashboard/backend/server.py` | `SinaPromptOS/dashboard/backend/server.py` |
| `global/*` | `SinaPromptOS/global/` (generated each cycle) |
| `config/settings.json` | `SinaPromptOS/config/settings.json` |
| `main.py` | `SinaPromptOS/main.py` |
| `repos/*` | **External** — real repos on Desktop; paths in `config/projects.json` |

---

## 3. Five upgrade layers — locked status

| Layer | Target | v1 implementation |
|-------|--------|-------------------|
| L1 Global Awareness | Read all `os/plan.json`, strategy, chats | `state_loader.load_global_state()` |
| L2 Auto task pick | Next best from queue | `task_generator` — **top `next_tasks[0]` per repo**, not invented scope |
| L3 Prompt compiler | One Cursor prompt only | `prompt_compiler.compile_prompt()` |
| L4 Validator gate | APPROVE / REWRITE | `validator_gate.validate_task()` |
| L5 Memory sync | plan.json update | `sync_engine` — **default OFF** (`auto_sync_plan: false`) |
| L6 Parallel | 1 task per repo per cycle | Up to `max_tasks_per_cycle` (default 3) |
| **L2T** | **Execution truth** | `execution_tracker` + `REPO_EXECUTION_LOGS/` — law: `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` |
| **FB** | Feedback loop | `REPO_STATUS_REPORTS/` + `run-feedback-cycle.sh` |
| **P2** | AI Control Core | `core/ai_control/` → `PHASE2_EVALUATIONS.json` |

**Honest 10x today:** ~3–4× vs manual; **10×** when L5 verify-sync + optional daemon + Cursor SDK (L2 autonomy).

---

## 4. Golden rules (locked)

1. **Sina OS untouchable** — agents never edit Source A SSOT  
2. **ASF** — structure, registry, freeze, `projects.json` priority  
3. **Cursor** — dumb executor; one task per prompt  
4. **No auto-done** without verify unless ASF sets `auto_sync_plan: true`  
5. **TrustField** — no new features under freeze; ops/gates only  
6. **Orchestrator** — router only; not a third SSOT  

---

## 5. Control panel — `config/settings.json`

| Key | Default | Meaning |
|-----|---------|---------|
| `mode` | `semi-auto` | `manual` \| `semi-auto` \| `daemon` |
| `max_tasks_per_cycle` | `3` | Parallel repos per cycle |
| `enable_validator` | `true` | Block bad tasks |
| `parallel_repos` | `true` | One task per repo |
| `cycle_interval_seconds` | `60` | Daemon sleep |
| `auto_sync_plan` | **`false`** | **Locked safe default** |
| `write_prompts_to_outputs` | `true` | `outputs/last_prompt_{id}.txt` |
| `dashboard_port` | `8766` | FastAPI (Streamlit UI stays `8765`) |

---

## 6. Entry points (locked)

| Command | Action |
|---------|--------|
| `python main.py` | One orchestrator cycle |
| `python main.py --daemon` | 24/7 loop (watchdog) |
| `python main.py --cycle fast` | 30s interval in daemon |
| `./scripts/run-day.sh morning` | Full-day playbook Block A |
| `./scripts/run-ui.sh` | Streamlit `:8765` |
| `uvicorn dashboard.backend.server:app --port 8766` | API + static UI |

---

## 7. What is NOT automated (v1)

- Cursor IDE does not receive API auto-run (no official unattended agent in v1)  
- `sync_engine` does not mark `done` unless `auto_sync_plan: true`  
- Runtime Telegram / production deploy — separate human gate  
- Task **invention** (e.g. random JWT feature) — forbidden; queue only  

---

## 8. Relation to other Source A docs

| Doc | Role |
|-----|------|
| `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` | Parent doctrine |
| `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` | Human day timetable |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | Farsi mirror + validation |
| **This file** | 10x architecture + production layout |

---

## Document control

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-011 | Lock + bind to SinaPromptOS implementation |

**ASF approval:** ___________________ **Date:** __________
