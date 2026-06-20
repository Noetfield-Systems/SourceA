# INCIDENT-028-REPEAT — Worker stale close-line relapse (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**sequence_id:** SA-2026-06-13-INCIDENT-028-REPEAT  
**Parent:** `SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md`  
**Reporter:** SourceA Worker `fd67502f`  
**Severity:** High (founder trust / wrong operating instructions)

---

## Executive summary

On **2026-06-13**, SourceA Worker repeated INCIDENT-028: ended substantive replies with *"Open Sina Command → Prompt feed — review the 10 steps and tap Confirm to auto-send 10 prompts."* That path was **removed at INCIDENT-024**. Execution was unaffected; **founder instructions were wrong**.

---

## Main reason (one root cause)

> **Agents emit founder operating instructions from stale injected Cursor rule snapshots and hub projection literals without mandatory disk-truth read immediately before founder-facing output.**

| Rank | Cause | % |
|------|-------|---|
| 1 | **Cursor session injects cached pre-v3 `prompt-queue.mdc` text** while disk law already forbids auto-send | 35% |
| 2 | **No mechanical fail-closed gate on agent reply text** before ship (only disk surface scan) | 30% |
| 3 | Agent skipped `agent_truth_bundle` + mirror `founder_close_line` before close-line | 20% |
| 4 | Hub `must_do_today` hardcoded "answer pending" ignoring `open_questions_count=0` | 10% |
| 5 | Conversation summary preserved early wrong close-line after mid-session fixes | 5% |

**Not the root cause:** broken queue · broken Prompt feed API · missing skills logged.

---

## What broke

| Said | Disk law | Match |
|------|----------|-------|
| Confirm auto-send 10 prompts | Forbidden since 024/028 | NO |
| Prompt feed drives execution | `run inbox` + live-ongoing SSOT | NO |
| Form "answer pending" (hub) | `open_questions_count: 0` | NO |

---

## Remediation shipped (2026-06-13)

| # | Fix | Status |
|---|-----|--------|
| 1 | `prompt-queue.mdc` v3 — FORBIDDEN + CORRECT blocks | shipped |
| 2 | `scripts/founder_close_line_gate_v1.py` — scan reply text | shipped |
| 3 | `agentic_conduct_gate_v1.py` — violations on 028 patterns | shipped |
| 4 | `agent_session_gate_run_v1.py` — pass `--task-text` to conduct | shipped |
| 5 | `validate-founder-close-line-gate-v1.sh` | shipped · wired anti-staleness bundle |
| 6 | `agent_session_gate_run_v1.py` — worker/maintainer fail on conduct violations | shipped |
| 7 | `cursor_entry_gate.py` — `--scan-text` blocks founder close-line (worker) | shipped |
| 8 | `sina_command_lib.py` — must_do_today reads live form | shipped |
| 9 | `agent_memory_mirror` F09 + `founder_close_line` inject | shipped |
| 10 | `agent_session_gate_run_v1.py --pre-ship` fast reply gate | shipped |
| 11 | `find_critical_bugs.py` auto-ensure `:13030` worker | shipped |

---

## Correct law (effective)

**Execution:** `run inbox` · `live-ongoing-prompts-next-10-v1.json`  
**Prompt feed:** display · optional See big picture commentary · Confirm = cosmetic only  
**Pre-ship:** `python3 scripts/agent_session_gate_run_v1.py --role worker --scan-text "<draft reply>"`

---

## Verify

```bash
bash scripts/validate-founder-close-line-gate-v1.sh
bash scripts/validate-prompt-feed-no-autosend-copy-v1.sh
python3 scripts/founder_close_line_gate_v1.py --text "tap Confirm auto-send"  # exit 1
```

---

*End INCIDENT-028-REPEAT LOCKED v1*
