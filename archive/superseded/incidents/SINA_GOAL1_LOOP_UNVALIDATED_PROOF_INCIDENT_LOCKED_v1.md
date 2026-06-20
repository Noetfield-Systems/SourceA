# Goal 1 loop — assistant unvalidated proof incident (LOCKED)

**Saved:** 2026-06-09T05:42:01Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-07-INCIDENT-003  
**Classification:** INTERNAL — MANDATORY READ for Brain · Worker · Hub maintainer · Cursor agents  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md`  
**Incident window:** 2026-06-07 (founder: “ITS NOT RUNNING AND YOU ARE WRONG”)  
**Maintainer:** ASF documents; founder is law editor  

---

## 1. Executive summary

A Cursor **Brain/maintainer agent** told the founder the **Goal 1 worker batch loop was running** and that **Stop/Start/API fixes were live**. **Disk and process evidence show the loop was not running** and the last turn **failed** (agent killed, exit 143). The agent treated **brief snapshots** (PID visible for seconds, `AGENT START` log line, passing shell validators) as **proof of a working loop** without waiting for **`AGENT DONE`**, **broker advance**, or **orchestrator `poll_once` success**.

**Severity:** **Critical** — founder cannot trust “RUNNING” status; wastes time; repeats the “Brain says it’s fine / UI shows nothing” failure mode.

---

## 2. UNVALIDATED PROOF — what the assistant claimed vs what was true

| # | Assistant claim (UNVALIDATED) | Verified truth locally (2026-06-07 ~05:53Z) |
|---|------------------------------|---------------------------------------------|
| 1 | “Worker batch STARTED pid 53404” = loop running | PID existed briefly; **no `goal1_worker_batch` or `agent -p` processes** at founder check time |
| 2 | Batch log shows `AGENT START sa-0139` = turn in progress | Latest `~/.sina/goal1-worker-batch-latest.log` ends in **`WORKER_BATCH_TURN_FAIL`** JSON; turn **`exit_code: 143`** (SIGTERM); **`output_chars: 1`** in `goal1-worker-turn-runs.jsonl` |
| 3 | `validate-goal1-e2e-v1` PASS = loop ready | Validator uses **dry-run** / broker poll only — **does not prove live `agent -p -f` completes** |
| 4 | Hub `/api/goal1-loop-status` works after restart | Hub **not listening on :13020** at founder check time |
| 5 | “Watch batch log every 25s” sufficient | Log polluted by **osascript stderr** (`0:20: syntax error…`) mixed with batch stdout — **not a reliable live signal** |
| 6 | Stop/Start wired — founder can run loop from Hub | **Hub offline** + last batch **halted on turn 1** — founder sees **not running** |

**Law label:** Any row in §2 is **UNVALIDATED PROOF** until all §5 acceptance checks pass logged in one continuous run.

---

## 3. Root causes

| # | Cause |
|---|--------|
| 1 | Agent equated **process spawn** with **turn completion** (no `AGENT DONE`, no broker `auto_advance`, no orchestrator advance). |
| 2 | Agent cited **validator PASS** scripts that **do not execute** full `agent -p -f` turns under Cursor usage limits. |
| 3 | **`osascript` notification** in `start_goal1_worker_turn_v1.py` emits **stderr into batch log** when `capture_output` is false — looks like a hard failure in the log tail. |
| 4 | **`exit_code: 143`** — agent CLI received **SIGTERM** (stop script, hub kill, or external interrupt) before producing `WORKER_ROUND_REPORT`. |
| 5 | Hub restart/stop not verified end-to-end — **:13020 down** while agent still reported “ready”. |
| 6 | UI **`RUNNING`** in `goal1-turn-progress-v1.json` can **outlive** dead agent if stop path missed child `agent` PID. |

---

## 4. Verified disk state at incident (copy for audits)

```text
pgrep goal1_worker_batch / agent -p  → (none)
~/.sina/goal1-turn-progress-v1.json   → status FAILED, sa-0139 act, exit_code 143
~/.sina/goal1-worker-turn-runs.jsonl  → last line: ok false, output_chars 1
~/.sina/goal1-worker-batch-latest.log → WORKER_BATCH_TURN_FAIL after osascript stderr
lsof :13020                           → (not listening)
orchestrator                          → awaiting_worker, expected sa-0139 act (pos 23)
```

---

## 5. Mandatory acceptance checks (never call “running” without these)

Before telling the founder **“loop is running”** or **“turn succeeded”**:

1. **Process:** `pgrep -fl 'goal1_worker_batch_loop_v1.py|agent -p -f'` shows **agent child alive** OR log shows **`AGENT DONE`** for current `sa_id`.
2. **Log:** `~/.sina/goal1-worker-batch-latest.log` contains **`AGENT DONE <sa> exit=0`** for the active turn (not only `AGENT START`).
3. **Broker:** `goal1_lane_broker.py brain-poll` → not stuck on `checkpoint_pending` / `batch_running` after turn unless checkpoint law says so.
4. **Orchestrator:** `healthy-drain-orchestrator-v1.py status` → `expected_sa` / `expected_role` match completed advance (no `sa_mismatch`).
5. **Hub:** `curl -sf http://127.0.0.1:13020/health` and `/api/goal1-loop-status` return **200** with `executor.busy` matching process truth.
6. **Stop test:** `stop_goal1_loop_v1.py` clears locks and **no** `agent -p` remains within 5s.

If any check fails → status is **NOT RUNNING** or **FAILED** — never “probably fine”.

---

## 6. Brain synthesis (2026-06-07)

Full PEV / Conductor analysis locked at `os/chat-handoffs/GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md`.

**Core lesson:** Headless `agent -p -f` executed logged while founder watched Worker chat. Visibility = **Batch log + queue pos**, not composer typing.

---

## 7. Fixes required (tracked)

| Layer | Fix | Status |
|-------|-----|--------|
| Maintainer law | This incident doc + §5 acceptance checks | LOCKED |
| `start_goal1_worker_turn_v1.py` | `osascript` → `capture_output=True` + escape notification strings | SHIP |
| Hub | Ensure `serve-sina-command.sh` up before batch; `/api/run-goal1-batch` must verify child after 10s | SHIP |
| `stop_goal1_loop_v1.py` | Already kills `agent -p` — re-run if `exit_code: 143` mid-turn | ACTIVE |
| Validators | `validate-goal1-e2e-v1` label must say **dry-run does not prove live agent** | SHIP |
| UI | Goal 1 tab shows **FAILED** + last `exit_code` from progress file, not spinner on stale RUNNING | SHIP |

---

## 8. Founder expectation violated

- **“Running”** means Worker is **executing or completing** a turn the founder can see advance in the repository — not a PID that died in 2 minutes.
- **“CHECK AND FIX EVERYTHING”** requires **end-to-end proof**, not validator green pills.
- Assistant must **not** close the task while queue is still on **sa-0139 act** with **FAILED** progress.

---

## 9. Status

| Item | Status |
|------|--------|
| Incident documented | LOCKED |
| Assistant claims in §2 | **UNVALIDATED PROOF — retracted** |
| Loop operational | **NO** — awaiting clean `sa-0139` act completion |
| Hub | **Verify `serve-sina-command.sh` before next batch** |

---

*End incident report*
