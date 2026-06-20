# ACTIVE_NOW Heartbeat — ecosystem single pulse (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**SSOT file:** `/Users/sinakazemnezhad/Desktop/SourceA/ACTIVE_NOW.md`  
**Mechanism:** `scripts/active_now_v1.py`

---

## Law

**Every agent, every script, every CLI command, every Brain cycle reads `ACTIVE_NOW.md` first.**

That file is the **one heartbeat** for the ecosystem. Only fields listed there are in scope. **Everything else is forbidden** until ASF updates the file.

---

## Mandatory callers

| Caller | Hook |
|--------|------|
| Brain session | `brain-session-start.sh` → `active_now_v1.py --heartbeat` |
| Entry gate | `cursor_entry_gate.py` — hash + heartbeat before gate |
| CLI Worker | `claude_code_agent_v1.py` · `claude_api_agent_v1.py` · `operating_mode_enforce_v1.py` |
| Goal 1 batch | `goal1_worker_batch_loop_v1.py` · `auto_run_worker_batch_v1.py` |
| Orchestrator | `healthy-drain-orchestrator-v1.py` deliver path |
| Worker turn | `start_goal1_worker_turn_v1.py` |
| Brain validate | `brain_validate_goal1_v1.py` · `brain_run_loop_trace_v1.py` |

---

## ASF updates

Founder (ASF) edits **only** `ACTIVE_NOW.md` to change goal, sprint, queue, sa_id, blocker.  
Agents **read** — do not rewrite scope without ASF order.

---

## Validator

`bash scripts/validate-active-now-heartbeat-v1.sh`  
`bash scripts/validate-founder-busy-operating-model-v1.sh`

---

*End ACTIVE_NOW_HEARTBEAT_LOCKED_v1*
