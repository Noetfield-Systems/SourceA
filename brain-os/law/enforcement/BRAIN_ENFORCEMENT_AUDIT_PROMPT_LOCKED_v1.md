# Brain — enforcement audit prompt (paste exactly)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 LOCKED  
**Use:** **Debug / “show me every gate” only** — NOT for simple `run the loop`.  
**Simple phrase:** `BRAIN_UNIFIED_RULES_LOCKED_v1.md` §1 → `brain_narrate_loop_v1.py` (seconds, no spawn)

---

## BLOCK A — paste to Brain

```text
BRAIN ENFORCEMENT AUDIT — mandatory transparent mode

You are Brain. Do NOT summarize from memory. Run every step on disk, then narrate.

## Phase 0 — run mechanical audit (required first)

cd /Users/sinakazemnezhad/Desktop/SourceA
python3 scripts/brain_enforcement_audit_v1.py --json --write --session

## Phase 1 — your reply structure (required — no skipping)

Reply in EXACTLY these sections:

### §1 BRAIN_ENFORCEMENT_AUDIT
Paste the full JSON from the script (or ~/.sina/brain-enforcement-audit-v1.json).

### §2 STEP-BY-STEP NARRATION
For EVERY step in `steps[]`, one bullet:
- **Sxx_title** — PASS/FAIL
- Command run (verbatim)
- Key disk proof (1–3 lines from result.stdout or result.json)
- What this gate enforces (one sentence)

Cover all step_ids in order: S00 → S15.

### §3 ACTIVATION CHAIN (INJECT → VALIDATE → ACTIVATE → SYNC)
From S10/S11 only — state each gate:
| Gate | PASS/FAIL/WAIT | Disk proof |
| INJECT | | feasibility + INBOX pending + sa match orchestrator |
| VALIDATE | | worker_report.validate.spine + WORKER_ROUND_REPORT |
| ACTIVATE | | S13 pgrep OR S14 AGENT DONE exit=0 broker=yes |
| SYNC | | orchestrator queue_pos / last_completed_sa advanced |

### §4 ONE-SA-PER-TURN
From S08, S09, S15:
- turn open? which sa?
- any ONE_SA_BATCH_VIOLATION in log?
- can agent batch multiple sa right now? (yes/no + why)

### §5 WHAT IS RUNNING NOW (honest)
- Executor busy? (locks + pgrep)
- If NOT running: say NOT RUNNING — do not cite PID alone
- Next mechanical action ONLY (script name, not founder Terminal)

### §6 BRAIN_VALIDATION_REPORT
Also run and paste:
bash scripts/validate-monitor-honesty-v1.sh
python3 scripts/brain_validate_goal1_v1.py --yaml --write-receipt

### §7 MONITOR HONESTY (progress law)
From `validate-monitor-honesty-v1` + `progress_honest` in brain_validate:
- Quote **Valid YES / pct** only for progress bar
- **receipt_done** separate; **PARTIAL** = broker gap
- **STRUCT_OK** ≠ done · **Broker STALE** ≠ done

## Forbidden in this reply
- Prose without step_ids
- "Probably running" / "should be fine"
- Ask founder to Refresh hub or Terminal
- Skip any S00–S15 step
- Implement sa work — audit only unless I say "run the loop"

## If I said "run the loop" (narrate) in same message
Run `python3 scripts/brain_narrate_loop_v1.py` only — **no spawn**. Do not goal1_auto_loop.
```

---

## BLOCK B — short version (status check only)

```text
BRAIN: enforcement audit only — run:
cd /Users/sinakazemnezhad/Desktop/SourceA && python3 scripts/brain_enforcement_audit_v1.py --json --write
Then §1–§6 from BRAIN_ENFORCEMENT_AUDIT_PROMPT_LOCKED_v1.md. Every step_id. No memory.
```

---

## Step map (what each Sxx is)

| step_id | Enforcement |
|---------|-------------|
| S00 | Hub `/health` live |
| S01 | `hub_self_refresh_v1.py` — agent sync |
| S02 | `brain-session-start.sh` — disk SSOT receipt |
| S03 | `cursor_entry_gate.py --role brain` — law hashes |
| S04 | Feasibility brain |
| S05 | Feasibility worker — STOP_INJECT |
| S06 | Orchestrator status |
| S07 | INBOX inject pending |
| S08 | `one_sa_per_turn_gate_v1.py` |
| S09 | `worker_turn_lib` open/closed |
| S10 | `brain_validate_goal1_v1.py` — full chain |
| S11 | `goal1_lane_broker.py brain-poll` |
| S12 | Lock files on disk |
| S13 | pgrep ACTIVATE proof |
| S14 | Batch log tail |
| S15 | One-sa violations log |

---

*End prompt*
