# Goal 1 execution solution — PEV / Conductor DO_WHILE (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Law:** Brain synthesis 2026-06-07 · INCIDENT-003 follow-up  
**Canonical:** `/Users/sinakazemnezhad/Desktop/SourceA/os/chat-handoffs/GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md`

---

## 1. Why we failed (five stacked layers)

| # | Layer | Failure |
|---|--------|---------|
| 1 | **Wrong mental model** | Founder watched **Worker chat**; loop runs **`agent -p -f` headless** — no tab, no composer. |
| 2 | **Prepare ≠ execute** | Deliver INBOX / lock busy ≠ agent running. |
| 3 | **Fragile launch** | Cursor background shells died in ~30–40s; detached `start_new_session` required. |
| 4 | **Hub UX omission** | No headless banner; Batch log = truth not stated; Stop mid-turn → exit 143. |
| 5 | **Stale signals** | sa-TEST poison, wrong `round_type`, overlapping paths (autoloop inject vs batch vs brain_execute). |
| 6 | **Autoloop gap** | `healthy-drain-autoloop.py` injects + watches — **does not call agent**. |

---

## 2. Activation chain (mandatory law)

**Full spec:** `GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md`

```text
INJECT (feasibility + INBOX pending) → VALIDATE (WORKER_ROUND_REPORT) → ACTIVATE (agent -p -f) → SYNC (orchestrator)
```

Deliver alone ≠ ACTIVATE. Worker chat validation required on **visible lane**; headless lane validates via agent CLI output → broker.

---

## 3. PEV spine (disk checkpoints only)

```text
PLAN     → healthy-queue-30-active.json + INBOX on disk
EXECUTE  → agent -p -f (headless) OR Worker chat "run inbox" (visible lane)
VERIFY   → machine validators + WORKER_ROUND_REPORT YAML
SYNC     → orchestrator poll_once — no advance without report
ROUTE    → goal1_lane_broker brain-poll/ack — Brain does not implement sa
```

**Anti-pattern:** Using Worker chat typing as loop checkpoint. **Correct:** Batch log `AGENT START` / `AGENT DONE` + queue pos change.

---

## 4. Two products — do not merge

| Product | Use for |
|---------|---------|
| `goal1_auto_loop_v1` / `goal1_worker_batch_loop` / `goal1_run_loop_v1` | REGISTRY healthy drain (30 = 10 sa × 3 roles) |
| Hub `agent_loop` + 10loop keyword | Meta 10-round **planner** tasks |

Bridge only if 10loop seeds from `healthy_queue_status()` then starts `goal1_auto_loop_v1.py`.

---

## 5. Two execution lanes (founder choice)

| Lane | Visibility | Entry |
|------|------------|-------|
| **Headless (default)** | Batch log only | Hub **▶ AUTO-RUN 10** |
| **Worker chat (optional)** | Composer activity | Deliver INBOX → Worker chat → `run inbox` |

---

## 6. Single auto entry (P1 — shipped — **activate loop only**)

**Not** the one-sentence narrate prompt (`brain_narrate_loop_v1.py` — < 75s, no spawn).

```bash
python3 scripts/goal1_auto_loop_v1.py --turns 10
```

1. `prompt_feasibility_gate` — STOP_INJECT blocks  
2. `stop_goal1_loop_v1.py` — clear stale  
3. `deliver_current` if INBOX empty  
4. Detached `goal1_run_loop_v1.py` → `start_goal1_worker_turn_v1.py` → `agent -p -f`

Hub: **founder-auto-run-healthy-10** · API: `POST /api/run-goal1-auto-loop`

**Agent law:** run `hub_self_refresh_v1.py` before telling founder loop status — never ask Refresh or Terminal.

---

## 7. Acceptance before “running” (mandatory)

See `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` §5:

- Batch log **`AGENT DONE … exit=0`**
- Queue position advanced on disk
- Hub `/health` + `/api/goal1-loop-status` live
- Never cite PID alone or Worker chat silence as proof

---

## 8. round_type mapping (agent wrapper)

| queue_role | WORKER_ROUND_REPORT round_type |
|------------|--------------------------------|
| check | audit |
| act | implement |
| verify | fix |

---

*End law*
