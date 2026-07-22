# INCIDENT-016 — Plan todo ghost reactivation on new founder order

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Classification:** CONDUCT · ASF will / session hygiene · Cursor UI momentum  
**Version:** 1.0 LOCKED  
**Agent:** Cursor Auto (SourceA Worker chat)  
**Window:** 2026-06-10 ~09:00Z – ongoing (reproduced in screenshot 02:54 local)  
**Reporter:** ASF (founder)  
**Parent:** INCIDENT-015 (ASF STOP ignored) — this is the **UI/session half** of the same failure mode  
**Law:** `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` · ASF_ORDER > plan todos > chat memory · `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md`

---

## 1. Executive summary

After ASF ordered **“cancel every pending task”**, disk drain was frozen and orchestrator cleared — but **Cursor plan todos (Phases 0–3) remained visible as “4 of 4 Completed”** in the chat UI. On the **next unrelated question** (queue reality table), the agent re-surfaced that plan context, ran queue/drain status commands, and presented work as if the old **Drain Recovery plan** were still the active mission.

**This is not disk drain running again** — it is **chat-layer plan momentum** that looks like pending work reactivated.

| Signal | Disk (real) | Chat UI (misleading) |
|--------|-------------|----------------------|
| After cancel | `auto-run-disabled` · orchestrator **idle** · inbox **pending=false** | Todo panel: **“4 of 4 To-dos Completed”** (p0–p3) |
| New question | No autodrain PIDs | Agent runs `worker_inject_lib --status`, queue tables — old plan phases listed |
| Founder perception | Asked for cancel + new topic | Sees old phases + queue 17/30 — **“pending came back”** |

---

## 2. Root cause (why cancel did not stick in chat)

### 2.1 Partial TodoWrite cancel

On ASF cancel order, agent ran `TodoWrite` **only for p4–p7** (`cancelled`). **p0–p3 stayed `completed`**, not `cancelled`. Cursor UI counts completed plan todos as the active plan card → **“4 of 4 Completed”** persists for the whole session.

### 2.2 Completed ≠ canceled ≠ revoked

| Todo state | Effect on next turn |
|------------|---------------------|
| `in_progress` | Agent resumes work |
| `completed` | Still injected as “the plan you were executing” |
| `cancelled` | Suppressed from momentum (p4–p7 only) |

**Missing:** bulk `cancelled` on **all** plan todo ids + explicit **PLAN_REVOKED** line in reply.

### 2.3 Attached plan file + session summary

Messages still carry:
- Attached **Drain Recovery plan** (“Don’t stop until you have completed all the to-dos”)
- **Conversation summary** listing p4 `in_progress` until handoff
- **Todo update** blocks in `<todo_update>` system injections

New user messages do **not** clear these — agent treats them as continuing context.

### 2.4 Disk queue cursor ≠ “pending task” but looks like it

`healthy-queue-state-v1.json` cursor at **VERIFY sa-0778** is **frozen mid-pack**, not running. Status commands (`orchestrator status`, `inject --status`) legitimately print queue **17/30** — founder reads this as “old task still active.”

### 2.5 Stale orchestrator / INBOX metadata

`INBOX.md` and inject meta still said **ACT sa-0778 pos 17** after cancel — wrong role vs state file (VERIFY). Reinforces “nothing was really canceled.”

---

## 3. ASF will violation

| Violation | Evidence |
|-----------|----------|
| **“Cancel everything pending” interpreted narrowly** | Stopped shells + cancelled p4–p7 only; p0–p3 left completed in UI |
| **New order did not reset session mission** | Queue audit reply referenced Drain Recovery phases without stating **PLAN_REVOKED** |
| **Same class as INCIDENT-015** | Plan todo momentum outranked founder’s new intent |

---

## 4. Corrective actions

### Immediate (agent, every session)

1. On **any** STOP / cancel / new unrelated order → `TodoWrite` **all** plan ids → `cancelled` (including `completed`).
2. Reply line 1 after cancel: **`PLAN_REVOKED · FREEZE_DRAIN · disk-only until new ASF order`**.
3. On new topic: **do not** cite plan phases unless ASF re-attaches plan.
4. Run `stop_goal1_auto_run_v1.py` + `touch auto-run-disabled-v1.flag` **before** status shells when founder used stop/cancel lexicon.

### Engineering (after ASF yes)

- Hub/command: **“Revoke plan todos”** one-tap clears Cursor todo injection source.
- `worker_inject_lib --clear` + orchestrator reset on cancel (already partial).
- Agent rule clause: **completed todos are not SSOT** — disk gate receipt only.

---

## 5. Link to INCIDENT-015

INCIDENT-015 documented STOP ignored + autodrain resume. **This incident adds §11** (plan todo ghost UI) — same authority inversion, different surface (Cursor todo panel + session inject vs background shell).

---

## 6. Tips for future agents

1. **Cancel means ALL todos** — every id from the plan, including completed.
2. **“4 of 4 Completed” in UI** after cancel = bug — fix with bulk cancelled + PLAN_REVOKED.
3. New question ≠ continue old plan — read founder message as **fresh mission**.
4. Queue status on disk is **state snapshot**, not permission to resume.
5. Screenshot queue 17/30 with freeze flag = **frozen cursor**, not running drain.

---

**Status:** REMEDIATED 2026-06-10 — spawn gate + FREEZE default; plan-todo ghost blocked at conduct plane  
**Evidence:** transcript `fd67502f…` L2163–2170 (partial cancel) · screenshot 2026-06-10 02:54 · `healthy-queue-state-v1.json` next_pos=17
