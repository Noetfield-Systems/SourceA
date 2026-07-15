# Worker stale goal_progress chat parrot & false repeating steps — INCIDENT-013 (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
[AUTO_AGENT_REF · Auto · AUTO-TRACE-WORKER-STALE-GOAL-PROGRESS-INCIDENT-v1.0]

**trace_tag:** `AUTO-TRACE-WORKER-STALE-GOAL-PROGRESS-INCIDENT-v1.0`
**agent:** `Auto`
**role:** `SourceA-Worker`
**repo:** `sourcea`

**Version:** 1.0 — FINAL LOCKED
**sequence_id:** SA-2026-06-10-INCIDENT-013
**Classification:** MANDATORY READ — **every SourceA Worker** · auto-run executor · Brain · Maintainer · all Cursor executor agents
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_REPORT_LOCKED_v1.md`
**Incident window:** 2026-06-10 (founder: “how many times you said 157/1000 done??? wrong report and proof” · healthy pack `sa-0084`→`sa-0093`)
**Related:** INCIDENT-006 (receipt law) · INCIDENT-007 (STALE broker) · INCIDENT-008 (stall/timing) · INCIDENT-009 (session closeout) · `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md`
**Not this incident:** INCIDENT-010 = CIR-COSPRO (`SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md`) · INCIDENT-011 = REWRITE disk edit
**Source copied from:** `brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md` (wrong id — left untouched)
**Tags:** `INCIDENT-013`, `goal-progress`, `stale-report`, `healthy-drain`, `sa-0084-0093`, `worker-inbox`, `monitor-honesty`

---

## 1. Executive summary

During a long **manual `run inbox`** drain of healthy pack **`sa-0084`→`sa-0093`**, the Worker agent **repeated the same progress line — `157/1000 (15.7%) honest` — across many turns** even while the queue advanced and receipts were written. The founder correctly identified this as **wrong report / wrong proof**: chat progress did not match disk, and the experience felt like **“repeating the same steps every turn.”**

**Severity:** **High** (trust / monitor honesty) — not a validator failure; a **reporting and UX proof incident**.

| Metric (disk SSOT at report time) | Value |
|-----------------------------------|------:|
| `python3 scripts/goal-progress-v1.py` | **158/1000** (15.8%) honest |
| `receipts/sa-*-receipt.json` count | **158** |
| `registry_honest_lib_v1` audit | **158** honest · **0** unproven · **no drift** |
| Current pack cursor | **19/30** → **sa-0090 CHECK** |
| Pack `sa-0084`–`sa-0093` receipts | **6/10** SAs (0084–0089 VERIFY closed) |

**One-line law (never forget):**

> **Never cite `goal_progress` from broker SESSION MEMORY or INBOX inject. Run `goal-progress-v1.py` (or `registry_honest_lib_v1`) every status reply. One honest point = one SA with REGISTRY `done` + receipt — not one `run inbox` turn.**

---

## 2. What the founder experienced

1. **Same fraction in chat** — “157/1000” appeared turn after turn while work clearly advanced (0084→0089 closed).
2. **Same-looking turns** — CHECK → ACT → VERIFY on SAs whose validators were already green; ACT often “idempotent, no diff.”
3. **INBOX TRACK BACKLOG** — still listed Q1–Q18 as `VALIDATE_FIRST` / pending after receipts existed.
4. **Question:** “why just repeating steps each turn?! what is the problem with your queue??”

The founder was **right** on reporting. The queue was **mostly behaving**; **chat proof was wrong** and **three progress signals disagreed**.

---

## 3. Root causes (technical)

### 3.1 Primary: parroted stale SESSION MEMORY

Worker INBOX prompts include a block like:

```text
goal_progress: GOAL_1: 157/1000 (15.7%) honest · backlog 843
```

That value is **snapshotted at inject time** and **lags** broker closeouts. The agent **copied it into every summary** instead of re-querying disk SSOT.

**Failure mode:** Receipt written → REGISTRY/honest ticked 157→158 → **inject still said 157** → agent reported 157 repeatedly.

### 3.2 Secondary: three different “progress” meanings

| Signal | What it measures | Founder saw |
|--------|------------------|-------------|
| **Honest bar** (`goal-progress-v1.py`) | REGISTRY `done` ∩ receipt logged | Stuck-sounding **157** in chat |
| **Queue cursor** (`healthy-queue-state-v1.json`) | Turn **19/30** in current 30-pack | Real mechanical advance |
| **TRACK BACKLOG** (`track_validate_backlog_v1.py`) | Matrix gaps / `VALIDATE_FIRST` | “30 pending” every turn |

Agents conflated these. Founder saw **pending everywhere** and **157 forever**.

### 3.3 Tertiary: 3-turn rhythm on pre-shipped SAs

Pack law: **each SA = CHECK + ACT + VERIFY** (30 turns for 10 SAs).

For **sa-0084–0089**, implementation was **already logged** from earlier sessions. Turns were **ceremony**:

- CHECK: validators PASS, gap none  
- ACT: idempotent, **no diff**  
- VERIFY: validators PASS, receipt + broker closeout  

**Not infinite loop** — but **feels like repetition** when combined with stale progress text.

### 3.4 Quaternary: pack regen + autorun / stuck recovery (context)

- Prior pack **`sa-0069`→`sa-0083`** exhausted; `build-achievable-healthy-queue.py` started **`sa-0084`→`sa-0093`** at pos 1.  
- **Auto-run** (when on) raced queue → `sa_mismatch`, wrong bind.  
- **Stuck recovery** replayed **sa-0086 CHECK** at Q7 after ~35 min idle; required manual `--set-pos 8` heal.

These amplified “why am I doing this again?” but are **separate** from the **157 parrot** bug.

---

## 4. Timeline (abbreviated)

| Phase | Event |
|-------|--------|
| Pack 1 complete | `sa-0069`→`sa-0083` · `next_pos: 31` · INBOX empty |
| Pack 2 loaded | `build-achievable-healthy-queue.py` · **sa-0084**→**sa-0093** · pos reset to **1** |
| Drain | Manual `run inbox` · CHECK/ACT/VERIFY for 0084–0089 |
| Chat reports | **`157/1000` repeated** across many summaries (stale inject) |
| Disk reality | Honest moved **152→156→157→158** slowly (+1 per VERIFY closeout) |
| Founder callout | Wrong report / wrong proof incident named |
| Report time SSOT | **158/1000** · queue **19/30** · **sa-0090 CHECK** next |

### 4.1 Pack 2 receipt evidence

| sa_id | VERIFY receipt at (UTC) |
|-------|---------------------------|
| sa-0084 | 2026-06-10T00:36:48 |
| sa-0085 | 2026-06-10T00:39:38 |
| sa-0086 | 2026-06-10T03:41:50 |
| sa-0087 | 2026-06-10T03:51:51 |
| sa-0088 | 2026-06-10T04:05:01 |
| sa-0089 | 2026-06-10T04:31:40 |

---

## 5. What was NOT broken

- **Validators** — phase-s0 / pack-specific scripts **PASS**; `find_critical_bugs` critical **0** on sampled turns.  
- **Broker advance** — `turn_closed: true`, `next_pos` incremented on successful submit (when not racing autorun).  
- **Receipt law** — `receipts/sa-XXXX-receipt.json` written on VERIFY; `registry_honest_lib_v1` **no drift** at report time.  
- **Queue cursor** — reached **19/30** predictably (6 SAs × 3 turns + pos 19 = start of sa-0090).

---

## 6. What WAS broken

| # | Failure | Impact |
|---|---------|--------|
| 1 | Agent cited **inject `goal_progress`** not live SSOT | Founder saw **frozen 157** |
| 2 | Agent did not explain **+1 honest per VERIFY**, not per inbox | Felt like zero progress |
| 3 | **TRACK BACKLOG** not reconciled to receipts in chat | False “30 pending” |
| 4 | Idempotent **3-turn ceremony** on green SAs not labeled clearly | Felt like “repeating steps” |
| 5 | Occasional **autorun / stuck_recovery** races | Replay / mismatch (INCIDENT-007 class) |

---

## 7. Correct reporting procedure (SSOT)

### 7.1 Before every progress sentence

```bash
cd ~/Desktop/SourceA && python3 scripts/goal-progress-v1.py
```

Use the printed line: `GOAL_1: N/1000 (pct%) honest · backlog B`.

Optional JSON:

```bash
python3 scripts/goal-progress-v1.py --json
```

### 7.2 Queue position (mechanical)

```bash
python3 -c "import json; from pathlib import Path; st=json.load(open(Path.home()/'.sina/healthy-queue-state-v1.json')); print(st)"
```

Report: **`next_pos` / 30**, **next sa_id + role** from `healthy-queue-30-active.json`.

### 7.3 Receipt proof for bound SA

```bash
test -f receipts/sa-XXXX-receipt.json && echo RECEIPT_OK || echo RECEIPT_MISSING
```

### 7.4 Never use as sole proof

- INBOX `goal_progress:` SESSION MEMORY line  
- TRACK BACKLOG `VALIDATE_FIRST` table without cross-check  
- “Validators PASS” without stating **CHECK vs ACT vs VERIFY** and **built vs idempotent**

---

## 8. Tips for other Worker agents

### 8.1 Progress reporting

1. **Run `goal-progress-v1.py` every turn** you mention honest %.  
2. **Say what moved:** e.g. “158/1000 (+1 since last VERIFY sa-0089).”  
3. **Separate metrics in one table:** honest bar | queue cursor | pack receipts | live_pick.  
4. If honest **unchanged** for 2+ turns, say **why**: “on ACT idempotent — honest ticks only on VERIFY.”

### 8.2 “Repeating steps” explanation

1. State pack rhythm: **3 turns per SA**.  
2. Label turn: **CHECK / ACT / VERIFY** — not “another inbox.”  
3. If idempotent: **“disk already green; broker closeout only.”**  
4. Give **remaining turns**: e.g. “4 SAs left × 3 = 12 turns.”

### 8.3 INBOX / broker hygiene

1. **Bind = INBOX meta `sa_id`** at submit time; if `sa_mismatch`, re-pickup — do not submit stale YAML.  
2. **Disable auto-run** when founder uses manual `run inbox` (INCIDENT-007).  
3. After **stuck_recovery**, verify `next_pos` — heal with `advance-healthy-queue-v1.py --set-pos N` if CHECK replayed after PASS.  
4. **`deliver --force`** when INBOX empty but cursor ≤ 30.

### 8.4 Proof vocabulary (RECIPE · VALIDATION · EVIDENCE · BUILT)

| Question | Answer pattern |
|----------|----------------|
| RECIPE? | sa_id + role + queue pos + task .md title |
| VALIDATION? | Named scripts + PASS/FAIL + critical count |
| EVIDENCE? | Receipt path + broker `turn_closed` + `next_pos` |
| BUILT? | **diff yes/no** — honest “idempotent, no diff” on ACT when true |

### 8.5 Anti-patterns (do not)

- ❌ Copy `goal_progress` from inject  
- ❌ Say “30 pending” from TRACK BACKLOG without receipt check  
- ❌ Claim “pack complete” from validators alone  
- ❌ Report hub status without `hub_self_refresh_v1.py` when giving founder UI state  
- ❌ Apologize-only correction — **disk-first** per `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP`

### 8.6 Anti-patterns (do)

- ✅ One turn = one role; STOP after broker submit + clear  
- ✅ Cite `receipts/sa-XXXX-receipt.json` on VERIFY  
- ✅ When founder asks “what’s wrong with queue?” — **diagnose three signals** (§3.2)  
- ✅ File agent-review when monitor/chat proof diverges from disk

---

## 9. Remediation (agent-side, immediate)

| Action | Owner | Status |
|--------|-------|--------|
| Stop parroting inject `goal_progress` | Worker agents | **Adopt §7–8 this session** |
| Run `goal-progress-v1.py` before progress claims | Worker agents | **Required every turn** |
| Explain 3-turn rhythm + idempotent closes | Worker agents | **Required when ACT has no diff** |
| POST `agent-review` for INCIDENT-013 | Executor | **This filing** |
| Append `~/.sina/agent-governance-events.jsonl` | Executor | **This filing** |
| Hub TRACK BACKLOG sync lag | Sina Command / Maintainer | **Open — not Worker code edit** |
| Refresh SESSION MEMORY `goal_progress` on inject | Hub / broker | **Open — Maintainer lane** |
| Optional: skip idempotent CHECK when receipt+validators exist | ASF product decision | **Not implemented** |

---

## 10. Verification commands (copy for audits)

```bash
# Honest SSOT
cd ~/Desktop/SourceA && python3 scripts/goal-progress-v1.py

# Receipt count
ls -1 receipts/sa-*-receipt.json | wc -l

# Registry honest audit
python3 -c "import sys; sys.path.insert(0,'scripts'); from registry_honest_lib_v1 import audit_registry_done; import json; print(json.dumps(audit_registry_done(), indent=2))"

# Queue cursor
cat ~/.sina/healthy-queue-state-v1.json

# Pack head
python3 -c "
import json
from pathlib import Path
st=json.load(open(Path.home()/'.sina/healthy-queue-state-v1.json'))
q=json.load(open(Path.home()/'.sina/healthy-queue-30-active.json'))
p=st['next_pos']
i=q['queue'][p-1]
print(i['queue_pos'], i['sa_id'], i['queue_role'])
"
```

---

## 11. Founder-facing summary (plain language)

You were not wrong. The Worker kept saying **157/1000** because the agent **copied a stale number from the inbox prompt** instead of checking the real counter logged (**158/1000** now). The queue **was** advancing (turn 19 of 30), but each goal only moves **+1** when a full **VERIFY** closes — so three “run inbox” clicks often change the bar by one, not three. Many turns were **closing out work that was already built**, which feels like repetition even when validators are correct.

**Trust disk:** `goal-progress-v1.py` + receipt files + queue position — not the paragraph at the bottom of the inbox template.

---

## 12. References

| Doc / script | Role |
|--------------|------|
| `scripts/goal-progress-v1.py` | Honest % SSOT |
| `scripts/registry_honest_lib_v1.py` | Receipt ∩ REGISTRY done |
| `scripts/track_validate_backlog_v1.py` | INBOX backlog table (can lag) |
| `scripts/healthy-drain-orchestrator-v1.py` | Deliver / stuck recovery |
| `scripts/goal1_lane_broker.py` | worker-submit / sa_mismatch |
| `SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_REPORT_LOCKED_v1.md` | Receipt law origin |
| `SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_REPORT_LOCKED_v1.md` | Autorun / STALE broker |
| `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md` | Miss correction law |

---

**END INCIDENT-013** — SA-2026-06-10-INCIDENT-013
