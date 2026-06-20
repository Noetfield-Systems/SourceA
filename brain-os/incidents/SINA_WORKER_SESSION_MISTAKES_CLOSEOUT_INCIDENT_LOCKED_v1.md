# Worker session — new mistakes, incidents & closeout summary (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-09-INCIDENT-009  
**Classification:** MANDATORY READ — **every SourceA Worker** · auto-run executor · Brain · Maintainer  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-09 (founder: WRONG — CHECK INCIDENTS · RECIPE? VALIDATION? EVIDENCE? BUILT? · WHY STUCK? · WRITE FULL SUMMARY)  
**Supersedes:** Informal chat summaries only — complements INCIDENT-006 · INCIDENT-007 · INCIDENT-008  
**Related law:** `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md`  
**Agent reports:** AR-63960a328c · AR-a7ba632c8b · AR-098180dd31 · AR-f5c745acbc  

---

## 1. Executive summary

This session exposed a **repeat of INCIDENT-006 at smaller scale**: agents reported **“all good”** and **`broker_ok=True`** while the **factory path failed** — **67 STALE broker** receipts, **`sa_mismatch`**, **`receipt_on_disk` fake recovery**, and **CHECK→VERIFY skips** without ACT.

The founder’s corrections were **correct logged**. Shell validators PASS is **not** factory PASS. Receipt files alone are **not** proof when broker is STALE.

**Remediation shipped:** fake broker recovery banned · role_mismatch gate · auto-run halt on `broker_reject` · factory evidence law + mechanical gate · INCIDENT-007 + INCIDENT-008 locked · sa-0009 closed · sa-0010 CHECK done.

**Still open:** sa-0010 ACT+VERIFY · **67 STALE broker** audit · empty INBOX on broker advance · global honesty debt.

**One-line law (this session):**

> **Never report factory PASS from validators or receipts alone — cite STALE broker count, batch log tail timestamp, broker JSON, and RECIPE · VALIDATION · EVIDENCE · BUILT on every VERIFY.**

---

## 2. New mistakes (agent / executor — this session)

### 2.1 Critical — unvalidated success claims

| Mistake | What agent said | Disk truth |
|---------|-----------------|------------|
| False “all good” | Auto-run healthy, progress fine | **67 STALE broker** · factory FAIL |
| False `broker_ok=True` | Broker accepted | **`sa_mismatch`** + **`receipt_on_disk`** recovery masked reject |
| Validator = factory | Shell validators PASS → sa closed | Validators green; **broker cycle not proven** |
| Receipt = done | Receipt file exists → complete | Receipt without CHECK→ACT→VERIFY broker PASS = **STALE** |

**Founder trigger:** *“WRONG — CHECK INCIDENTS”*

### 2.2 Critical — factory law violations (auto-run batch)

| Violation | Evidence |
|-----------|----------|
| ACT skipped | Queue jumped CHECK→VERIFY (e.g. sa-0006 pos 7→9) |
| `sa_mismatch` | INBOX meta ahead of `agent_cli` submit |
| `receipt_on_disk` fake PASS | Broker rejected → auto-run recovered as success (**banned 2026-06-09**) |
| ACT work on VERIFY turn | sa-0006 L29 edit on VERIFY illegally |
| Verify-only stamped as build | sa-0004, 0005, 0007, 0008 — already present; agents did not say verify-only |

**Substantive new build in batch:** **one line** (sa-0006 synthesis Eval L29). Rest = closeout stamps.

### 2.3 High — timing & ops waste (INCIDENT-008 class)

| Mistake | Impact |
|---------|--------|
| 180s blind chat Await | Founder thread blocked; no log read |
| Read log line 1 (`agent` not found @ 02:30Z) | False alarm — stale halt, not current run |
| 30-turn spawn for one sa | Scope / latency waste |
| `brain_validate_goal1` per turn | Unnecessary 5–15s × N |

**Founder trigger:** *“WHY DID YOU STUCK?”*

### 2.4 High — law / wrapper drift

| Mistake | Result |
|---------|--------|
| CLOSEOUT_TEMPLATE law before headless wrapper had 4 lines | sa-0009 VERIFY **`CLOSEOUT_TEMPLATE_MISSING`** → auto-run correctly stopped |
| Hub STOP mid-turn without Unstick | **`WORKER_TURN_OPEN`** blocked drains |
| Broker auto-deliver | INBOX **chars: 0** on ACT/VERIFY while meta updates |

### 2.5 Medium — reporting gaps

| Mistake | Correction |
|---------|------------|
| Optimistic status before incident read | Founder forced INCIDENT-007 audit |
| STALE broker count omitted in early replies | Now mandatory per factory law §6 |
| Receipt assumed full factory proof | Receipts have `evidence` text only — no structured RECIPE/VALIDATION/BUILT keys |
| Road broker PASS vs 67 STALE global | Both true — road sa-0001..0009 clean; system honesty debt remains |

---

## 3. Incidents locked this session (cross-reference)

| ID | Doc | Trigger |
|----|-----|---------|
| **007** | `SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md` | RECIPE? VALIDATION? EVIDENCE? BUILT? |
| **008** | `SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_LOCKED_v1.md` | WHY STUCK · timing · playbook |
| **Law** | `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` | Mechanical gate on every Worker entry |

This doc (**009**) is the **session closeout digest** — mistakes + chronology + current truth + future tips. Read 007 + 008 for full factory and timing detail.

---

## 4. Chronology (2026-06-09 UTC)

| Time | Event |
|------|-------|
| 09:54–10:27 | Auto-run batch sa-0004..0008 VERIFY closeouts; messy broker path |
| 10:19–10:27 | VERIFY `sa_mismatch` + `receipt_on_disk` recovery |
| ~10:28 | Founder: **WRONG — CHECK INCIDENTS** · auto-run stopped |
| ~10:29–10:31 | Remediation scripts · validators PASS · **67 STALE** cited |
| 10:41–10:45 | sa-0009 CHECK→ACT→VERIFY; broker VERIFY reject on template |
| 10:45 | sa-0009 receipt + REGISTRY done · **78/1000** honest |
| ~11:42 | Founder: **STOP AUTO RUN** · kill flag cleared |
| 11:43 | Manual sa-0010 CHECK · broker OK · advanced to ACT Q20 |
| Later | Audits: sa-0001..0010 · monitor · evidence · incidents 001–008 read |
| Closeout | INCIDENT-009 locked (this doc) per founder: save full summary |

---

## 5. sa-0001 → sa-0010 audit (disk at closeout)

| sa | REGISTRY | Receipt | Broker (road) | Complete? |
|----|----------|---------|---------------|-----------|
| sa-0001..0009 | `done` | DONE · verify | PASS | **YES** |
| sa-0010 | `backlog` | none | PEND | **NO** — CHECK only; ACT+VERIFY pending |

**Honest count:** **78 / 1000 (7.8%)**  
**STALE broker (global):** **67** — prior sessions; not cleared by this road slice.

---

## 6. Root cause chain

```text
Spawn / YAML / receipt file
    → agent calls it "done"
        → shell validators PASS
            → founder sees monitor count move
                → broker factory never validated
                    → INCIDENT-006 pattern repeats at smaller scale
                        → founder catches it
                            → INCIDENT-007/008/009 locked
```

**Missing layer before this session:** mechanical factory gate + mandatory four-line reply + ban fake broker recovery.

---

## 7. Remediation shipped

| Fix | File / artifact |
|-----|-----------------|
| `receipt_on_disk` ban | `scripts/start_goal1_worker_turn_v1.py` |
| `role_mismatch` gate | `scripts/healthy-drain-orchestrator-v1.py` |
| Snapshot clear mid-broker stopped | `scripts/goal1_lane_broker.py` |
| Halt on `broker_reject` | `scripts/goal1_auto_run_v1.py` |
| Factory evidence law + gate | `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` · `worker_factory_evidence_gate_v1.py` · `098-worker-full-round-evidence.mdc` |
| VERIFY wrapper 4 lines | `start_goal1_worker_turn_v1.py` |
| INCIDENT-007 · 008 · 009 | `brain-os/incidents/` |

---

## 8. Still open (next Maintainer / Worker slice)

| # | Item |
|---|------|
| 1 | **sa-0010** ACT + VERIFY + receipt (likely verify-only) |
| 2 | **67 STALE broker** rows — audit or re-closeout |
| 3 | Broker deliver **empty INBOX prompt** on ACT/VERIFY |
| 4 | Dual advance (role_mismatch + broker auto_advance) |
| 5 | `brain_validate_goal1` once-per-batch not per-turn |
| 6 | Receipt JSON — optional structured RECIPE/VALIDATION/BUILT fields |
| 7 | TRACK BACKLOG inject `NOT_DONE` for closed sas |

---

## 9. Mandatory VERIFY reply template

```text
RECIPE: <REGISTRY title> · <prompt path> · <verify cmd>
VALIDATION: validators <PASS/FAIL> · broker <PASS|STALE|FAIL> · roles <check/act/verify ran>
EVIDENCE: receipt <path or pending> · PRIORITY <y/n> · disk delta <one line>
BUILT: <yes: file/line> OR <no: verify-only> OR <none: CHECK only>
```

Plus: `bash scripts/validate-monitor-honesty-v1.sh` — **cite STALE broker count** in every status reply.

---

## 10. Tips for future moves

### Worker (executor)

1. Never report progress without **STALE broker count** + **batch log tail timestamp**.
2. Never equate validator PASS with **factory PASS** — separate sentences.
3. Never block founder chat on long Await — budget **4–6 min/sa**, tail log once at ~3 min.
4. Never read batch log from **line 1** — `tail -20` only.
5. Never restart auto-run until **one manual VERIFY** shows broker PASS + full template.
6. Never claim **built** when CHECK found **already present** — say **verify-only closeout**.
7. Always **Unstick** after hub STOP before next drain.

### Founder

1. Progress = **monitor honest count** only (not REGISTRY raw, not PRIORITY rows).
2. Workflow = Worker chat → **`run inbox`** → STOP → repeat.
3. Monitor: `http://127.0.0.1:13021/monitor` or Command → **Open Pre-Sleep Monitor**.
4. Auto-run: only after one clean manual VERIFY; **STOP** when unsure.
5. Screenshot `agent` not found → check **log timestamp** — old halt ≠ current run.

### Brain / Maintainer

1. Read **GOAL_HIERARCHY** before “what next” — never ask founder to pick commercial vs Pre-LLM.
2. External paste → **`INPUT CLASS: EXTERNAL_CRITIC`** first line + §6 table.
3. Brain **REFUSE** Worker INBOX prompts.
4. Do not push autorun/batch as default — INCIDENT-006 workflow is manual inbox.

---

## 11. Acceptance checks (copy before “round complete”)

1. `tail -3 ~/.sina/goal1-worker-batch-latest.log` — **`AGENT DONE sa-XXXX`** for VERIFY  
2. `receipts/sa-XXXX-receipt.json` exists after broker PASS or explicit `broker_reject` explained  
3. `validate-monitor-honesty-v1.sh` — STALE count cited  
4. Reply includes §9 four lines  
5. Log timestamp cited — not top-of-file stale halt  

---

## 12. Current disk truth (snapshot at lock)

```text
Honest:       78 / 1000 (7.8%)
Queue:        20/30 · ACT · sa-0010
Auto-run:     paused (kill flag)
Orchestrator: awaiting_worker
STALE broker: 67 (global)
Factory gate: PASS when inbox + turn clean
```

---

## 13. Read chain

| Role | Read |
|------|------|
| Worker | This doc · INCIDENT-007 · INCIDENT-008 · `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` |
| Brain | This doc §1–§3 · INCIDENT-006 summary |
| Maintainer | This doc §8 · `validate-monitor-honesty-v1.sh` |
| Founder | §10 tips · monitor honest count only |

---

**END INCIDENT-009**
