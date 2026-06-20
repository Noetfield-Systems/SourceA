# Brain unified rules (LOCKED v1 — SSOT)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-07  
**Workspace:** `/Users/sinakazemnezhad/Desktop/SourceA`

**Gather:** `python3 scripts/brain_gather_rules_v1.py --json`  
**Cursor:** `.cursor/rules/000-brain-unified.mdc`

---

## 0. Decision tree (NOW)

```
Founder message
    │
    ├─ "check e2e" / "check everything" / "validate everything" →  §0.5 AUDIT_CHEAP (Brain)
    ├─ "run the loop" / step-by-step / monitor / for workers  →  §1 RUN+TRACE (DEFAULT)
    ├─ "narrate only" / "watch only" / "do not spawn"         →  §1a snapshot only
    ├─ "activate loop" / "execute turn"                       →  §2 spawn only
    ├─ Worker task / run inbox in Brain chat                  →  §3 refuse
    └─ else                                                     →  §4 session
```

### §0.5 AUDIT_CHEAP_E2E (ASF audit — not executor marathon)

```bash
python3 scripts/brain_intent_gate_v1.py --message "<founder order>" --write --json
python3 scripts/brain_session_guard_v1.py --write --json
```

| If | Brain runs | Then STOP |
|----|------------|-----------|
| not idle | preflight + `SINA_FCB_FAST=1 find_critical_bugs` | Worker inbox one tap |
| idle | same cheap proof only | delegate ladder to Worker |

**Law:** `BRAIN_RULE_COLLISION_MATRIX_LOCKED_v1.md` · `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md`

---

## 1. Run the loop + trace (DEFAULT)

**Founder says:**
```text
Run the loop step-by-step, narrating each action until we have a final answer.
```

```bash
python3 scripts/brain_run_loop_trace_v1.py
```

| Step | What |
|------|------|
| 1–9 | Narrate each gate + timing |
| 10 | **Spawn** if ACTIVATE READY (`brain_run_loop_v1.py`) |
| Reply | `who_runs_loop` · `injection` · `which_chat` · `final_answer` |
| Brain chat time | **<30s** then STOP |

**Loop on disk after spawn is OK only when Brain proves cleanup.** Law: `BRAIN_NO_LEFTOVER_PROCESS_LOCKED_v1.md`

**End every turn (mandatory):**
```bash
python3 scripts/cleanup-goal1-leftovers-v1.py --json
```
`remaining_count` must be **0** before Brain claims loop/overnight is running. Paste: `BRAIN_END_TURN_NO_LEFTOVER_PROMPT_LOCKED_v1.md`

**Brain chat must NOT:** leave orphan `start-overnight` / `autorun_dispatcher` / CLI children · sit and poll batch log · implement sa · paste WORKER_ROUND_REPORT · start Cursor overnight.

**Watch progress:** `~/.sina/goal1-worker-batch-latest.log` or Hub Batch log — not by blocking Brain reply.

---

## 1a. Narrate only (explicit watcher)

Say: `narrate only` · `watch only` · `do not spawn` → `brain_narrate_loop_v1.py` only.

---

## 2. Spawn only (`activate loop` / `execute turn`)

`brain_run_loop_v1.py` or `brain_execute_turn_v1.py`

---

## 3. Brain ≠ Worker

Worker prompts in Brain chat → `BRAIN_REFUSE_WORKER_PROMPT`

---

## 4. Normal Brain

`bash scripts/brain-session-start.sh` · route · no multi-file implement · founder never Terminal

---

*End BRAIN UNIFIED RULES v1.1*
