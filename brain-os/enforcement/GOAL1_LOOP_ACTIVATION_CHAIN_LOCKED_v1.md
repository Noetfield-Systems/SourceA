# Goal 1 loop activation chain — inject · validate · activate (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Law:** Founder 2026-06-07 — mandatory validation + prompt injection + **real** loop activation  
**Canonical:** `/Users/sinakazemnezhad/Desktop/SourceA/os/chat-handoffs/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md`  
**Supersedes:** “Deliver INBOX = loop running” · “autoloop inject = loop ran”

---

## 1. Three gates (all mandatory — no skipping)

```text
INJECT  → prompt on disk (INBOX pending) — feasibility PASS
VALIDATE → machine validators + WORKER_ROUND_REPORT (Worker chat OR agent CLI output)
ACTIVATE → agent -p -f actually runs (headless) OR Worker chat executes one full turn
SYNC    → broker worker-submit + orchestrator poll_once → queue advances
```

**Law:** Prepare (deliver / lock / inject file) is **not** ACTIVATE. Loop is live only after **ACTIVATE** proof on disk.

---

## 2. INJECT (prompt injection — step 1)

| Check | Command / path | PASS when |
|-------|----------------|-----------|
| Feasibility | `python3 scripts/prompt_feasibility_gate.py --role worker --strict` | `action` ≠ `STOP_INJECT` |
| Deliver | `healthy-drain-orchestrator-v1.py deliver` or Hub **Deliver healthy drain** | `ok: true` |
| INBOX pending | `python3 scripts/worker_inject_lib.py --status` | `pending: true` |
| SSOT files | `~/.sina/worker-prompt-inbox-v1.json` · `.sina-loop/INBOX.md` | `sa_id` + `queue_role` match orchestrator `expected_sa` / `expected_role` |

**Forbidden:** clipboard paste into Brain chat · opening INBOX editor as “loop start” · `healthy-drain-autoloop.py` inject-only without ACTIVATE.

**Brain before inject:** `prompt_feasibility_gate.py --role brain --json` — never inject impossible ACT.

---

## 3. VALIDATE (Worker chat or agent output — step 2)

Every turn ends with **`WORKER_ROUND_REPORT`** YAML (flat `status:` key — not nested parent).

| Lane | Who validates | Proof |
|------|---------------|-------|
| **Worker chat (visible)** | Worker runs prompt validators → last reply = `WORKER_ROUND_REPORT` → `goal1_lane_broker.py worker-submit` | Broker `last_worker_report` · orchestrator advanced |
| **Headless (default)** | `agent -p -f` executes INBOX wrapper → stdout contains `WORKER_ROUND_REPORT` → `start_goal1_worker_turn_v1.py` calls `broker.worker_submit` | Same broker + orchestrator fields |

**Worker chat mandatory order** (visible lane):

```text
0. feasibility gate
1. pickup / INBOX status — execute disk prompt, not chat memory
2. validators per prompt (CHECK / ACT / VERIFY law)
3. WORKER_ROUND_REPORT YAML
4. worker-submit + inbox --clear
5. STOP — one turn
```

**round_type mapping:** `check`→`audit` · `act`→`implement` · `verify`→`fix`

**Forbidden:** skip validators · implement on CHECK · batch multiple sa · trust chat without `worker_inject_lib --status`.

---

## 4. ACTIVATE (real loop — step 3)

| Action | Activates loop? |
|--------|-----------------|
| Deliver INBOX / open INBOX.md | **NO** — INJECT only |
| Hub “Executor running” (lock only) | **NO** — may be stale lock |
| `healthy-drain-autoloop.py` watch/inject | **NO** — no agent |
| `goal1_auto_loop_v1.py --turns N` | **YES** — deliver + detached `goal1_run_loop_v1.py` |
| `goal1_worker_batch_loop_v1.py` | **YES** — batch path |
| `start_goal1_worker_turn_v1.py` (one turn) | **YES** — single turn |
| Worker chat `run inbox` + full turn | **YES** — visible lane |
| `brain_execute_turn_v1.py` | **YES** — debug single-turn |

**ACTIVATE proof (mandatory before “running”):**

```bash
pgrep -fl 'goal1_run_loop|goal1_worker_batch|agent -p -f'   # child alive OR
grep 'AGENT DONE' ~/.sina/goal1-worker-batch-latest.log    # exit=0 for current sa
```

Hub: **▶ AUTO-RUN 10 (headless)** = INJECT + ACTIVATE in one tap.  
Worker chat stays empty on headless path — validation is in **agent CLI output**, not composer typing.

---

## 5. SYNC (orchestrator — step 4)

After VALIDATE:

1. `goal1_lane_broker.py` receives `WORKER_ROUND_REPORT`
2. `healthy-drain-orchestrator-v1.py poll_once` — **no advance without report**
3. Next deliver → INJECT for following turn

**Brain:** `goal1_lane_broker.py brain-poll` / `brain-ack` — routes checkpoints; **does not** replace Worker validate or agent ACTIVATE.

---

## 6. Agent mandatory (Brain · maintainer · Worker)

**Before telling founder loop status — paste `BRAIN_VALIDATION_REPORT` YAML:**

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA
python3 scripts/brain_validate_goal1_v1.py --yaml --write-receipt
```

Script checks: INJECT · VALIDATE (`worker_report.validate`) · ACTIVATE (batch log / pids) · SYNC (orchestrator).  
`goal1_lane_broker.py brain-poll` embeds same `validation:` block. Hub Goal 1 tab shows **Brain validation (machine)**.

**Founder one-sentence narrate prompt (“run the loop step-by-step…”):**

```bash
python3 scripts/brain_narrate_loop_v1.py
```

Paste narration + final_answer. **< 75s. STOP.** No spawn. No poll. Law: `BRAIN_UNIFIED_RULES_LOCKED_v1.md` §1

**Founder explicit spawn (`activate loop` / `execute turn`):**

```bash
python3 scripts/brain_run_loop_v1.py --yaml
```

Never ask founder to Refresh hub or Terminal.

---

## 7. Anti-patterns (INCIDENT-003 + this law)

| Anti-pattern | Why wrong |
|--------------|-----------|
| Cite PID only | Process may die in 30s |
| Worker chat empty = failed | Headless path — check Batch log |
| Inject without ACTIVATE | Prompt landed; agent never ran |
| ACTIVATE without INJECT | agent has no INBOX prompt |
| VALIDATE skipped | orchestrator will not advance / sa_mismatch |

---

*End law*
