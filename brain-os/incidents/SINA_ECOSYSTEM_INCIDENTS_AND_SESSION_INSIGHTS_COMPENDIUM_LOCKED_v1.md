# Ecosystem incidents master index + session insights compendium (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-09-COMPENDIUM-INCIDENTS-INSIGHTS-v1  
**Classification:** MANDATORY READ — Brain · Worker · Maintainer · all Cursor agents  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM_REPORT_LOCKED_v1.md`  
**Companion:** `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` · `scripts/ecosystem_incidents_index.py` (hub payload)  
**Registry SSOT (001–025):** `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` — compendium Part A is historical; new ids **011–025** live in registry + `INCIDENT_SUBJECT_INDEX_LOCKED_v1.md` (near-miss C03 remediated 2026-06-10).  
**Related:** INCIDENT-009 session closeout · `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md`  
**Disk snapshot at lock (Jun 9 — historical):** **78/1000 honest** · queue **20/30 ACT sa-0010** · auto-run **paused** · **67 STALE broker** (global)  
**Live snapshot (Jun 10):** **595/1000** · **FREEZE** · queue **sa-0778** · `find_critical_bugs` critical 0

---

## Part A — Incident index (chronological)

> **Note:** Numbering overlaps (multiple INCIDENT-002/003/005). Use **`sequence_id`** in each doc as SSOT.

| ID | Date | Title | Severity | One-line law | Canonical doc |
|----|------|-------|----------|--------------|---------------|
| **001** | Jun 4 | Auto-paste / auto-prompt spam | Critical | Never inject into Cursor without explicit ASF opt-in | `brain-os/incidents/SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` |
| **002a** | Jun 5 | WTM UI content loss | Critical | UI upgrade ≠ delete tables; no agent reads in founder UI | `brain-os/wtm/WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` |
| **002b** | Jun 5 | WTM phase naming (D→A reversed) | High | Founder phases A→B→C→D; step IDs (B4, A1.1) stay stable | `brain-os/wtm/WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` |
| **002c** | Jun 6 | Context / memory / closeout | High | Chat is not SSOT — session-start + session-close every turn | `brain-os/incidents/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md` |
| **002d** | Jun 7 | Healthy drain feasibility (OpenRouter) | High | Never inject impossible ACT steps (live eval without credits) | `brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md` |
| **003a** | Jun 7 | Goal 1 unvalidated proof | Critical | Spawn ≠ running — need AGENT DONE + broker + hub health | `brain-os/incidents/SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` |
| **003b** | Jun 7 | Brain/Worker lane cross | — | Brain REFUSE Worker prompts — Worker only executes INBOX | `brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md` |
| **004** | Jun 8 | Goal hierarchy enforcement | Critical | GOAL_HIERARCHY on disk — never ask founder to pick commercial vs Pre-LLM | `brain-os/incidents/SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_LOCKED_v1.md` |
| **005a** | Jun 8 | Maintainer external-critic procedure | High | First line `INPUT CLASS: EXTERNAL_CRITIC` + §6 table before disk | `brain-os/incidents/SINA_MAINTAINER_EXTERNAL_CRITIC_PROCEDURE_INCIDENT_LOCKED_v1.md` |
| **005b** | May 27 | Maintainer self-audit / Mac lag | High | `maintainer_self_audit_loop.py` before/after every hub edit | `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` |
| **006** | Jun 8–9 | REGISTRY batch fake progress (607 done) | Critical | Done = receipt file only — YAML/batch stamp never counts | `brain-os/incidents/SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_LOCKED_v1.md` |
| **007** | Jun 9 | Auto-run broker STALE receipts | Critical | Receipt alone ≠ proof when broker STALE or `sa_mismatch` | `brain-os/incidents/SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md` |
| **008** | Jun 9 | Worker stall & timing waste | High | Estimate ~4–6 min/sa; tail log — never 180s chat Await | `brain-os/incidents/SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_LOCKED_v1.md` |
| **009** | Jun 9 | Worker session mistakes closeout | High | Validators PASS ≠ factory PASS; cite STALE + four-line VERIFY template | `brain-os/incidents/SINA_WORKER_SESSION_MISTAKES_CLOSEOUT_INCIDENT_LOCKED_v1.md` |
| **010** | Jun 7–9 | CIR-COSPRO cross-lane SSOT edit | **P0** | SAVE = one file in docs only; WORK fast; EDIT ALLOWED cross-desk | `brain-os/incidents/SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` · `AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` |

### Part A supplement — registry 011–025 (one-liners)

| ID | Title | Status |
|----|-------|--------|
| **011** | REWRITE unauthorized disk edit | REMEDIATED 2026-06-10 |
| **012** | Stale goal_progress duplicate | Superseded → 013 |
| **013** | Stale goal_progress chat | Canonical |
| **014** | Monitor brain column drift | Canonical |
| **015** | Incident ID collision | Canonical |
| **016** | Plan todo ghost | REMEDIATED 2026-06-10 |
| **017** | Phase-order drift | PARTIAL — PHASE_STRICT open |
| **018** | Founder scroll respect | Canonical |
| **019** | Bash communication | Canonical |
| **020** | Topic conflation | Canonical |
| **021** | Wrong-folder filing | Canonical |
| **022** | Stale AUTO-RUN advice | REMEDIATED 2026-06-10 |
| **023** | STOP ignored autodrain | REMEDIATED 2026-06-10 |
| **024** | Static prompt feed stale | REMEDIATED 2026-06-10 |
| **025** | Advisor track naming | REMEDIATED 2026-06-10 |

---

## Part A.1 — The arc (what keeps repeating)

```text
Agent claims progress
    → Disk proof?
        → No          → INCIDENT-003 / 006 / 007
        → Yes wrong lane → INCIDENT-004
        → Yes fake broker → INCIDENT-007
            → Receipt gate + honest REGISTRY
            → WORKER_FULL_ROUND_EVIDENCE law
            → RECIPE · VALIDATION · EVIDENCE · BUILT
```

**Three failure modes across all incidents:**

1. **Unvalidated proof** — PID spawn, validator dry-run, chat claims (003, 006, 007, 008)
2. **Wrong SSOT** — REGISTRY raw count, YAML closeout, PRIORITY rows, chat memory (006, 002c)
3. **Procedure bypass** — hierarchy ignored, critic paste shipped as law, Brain runs Worker work (004, 005a, 003b)

---

## Part A.2 — Per-incident essentials

### INCIDENT-001 — Auto-paste (Jun 4)

Hub outlived UI; `inject_cursor_chat` spammed maintainer chat every second. **Fix:** kill switch, opt-in only, Live agents = app-only. **Still open:** hub `/shutdown` on app quit.

### INCIDENT-002 family

- **WTM UI:** Replaced full tables with empty cockpit — founder saw blank tab. **Law:** never strip content on UI upgrade.
- **WTM naming:** Phase D-first confused founder — **A→B→C→D** for humans; **D1/B4/A1.1** IDs unchanged.
- **Context memory:** Agents re-do work after summarization — disk session ledger + closeout.
- **Feasibility:** sa-0129 required OpenRouter — `prompt_feasibility_gate.py` blocks impossible injects.

### INCIDENT-003 — Unvalidated proof + lane cross

Agent said loop RUNNING; disk showed **exit 143**, hub down, FAILED progress. **Acceptance:** `AGENT DONE`, broker advance, `:13020/health`. Brain must **REFUSE** `[GOAL1_HEALTHY_DRAIN]` prompts.

### INCIDENT-004 — Goal hierarchy

Brain asked founder to pick commercial vs Pre-LLM when law already said eval-dispatch first. CLI ran `sa-0501` while queue was `sa-0153`. **Fix shipped:** pick order, `~/.sina` queue SSOT, quarantine commercial pack.

### INCIDENT-005 — Maintainer procedure

~15% compliance on `INPUT CLASS: EXTERNAL_CRITIC`; shipped Gatekeeper from GPT paste without §6 table. **Probation active.** Fix batch pending ASF confirm (`brain-os/remediation/INCIDENT-005_FIX_BATCH_PENDING_ASF_CONFIRMATION_v1.md`).

### INCIDENT-006 — 607 fake done (the big one)

`closeout_sa_task.py` × 400+ stamped REGISTRY `done` with copy-paste YAML — **393 BATCH_CLOSEOUT_ONLY**. Recovery: revert 690 rows, quarantine 494 YAMLs, receipt gate. **Current law:** honest count = receipts only.

### INCIDENT-007 — Broker STALE (factory audit)

Auto-run closed sa-0004..0008 while broker showed **67 STALE**, `sa_mismatch`, `receipt_on_disk` fake recovery, ACT skipped. **Remediation shipped:** ban fake recovery, `role_mismatch` gate, factory evidence law + gate.

### INCIDENT-008 — Stall & timing (ops)

180s blind poll; CLOSEOUT_TEMPLATE law before agent wrapper; stale `agent` not found at log top. **Playbook:** unstick → factory gate → tail log at 3 min. sa-0009 closed on disk; broker VERIFY rejected once then wrapper patched.

### INCIDENT-009 — Session closeout digest

Full mistake catalog + chronology + tips for this session. Read before any “all good” status reply.

---

## Part A.3 — Current state vs incident lessons

| Lesson from incidents | Today (2026-06-09) |
|------------------------|-------------------|
| Honest count = receipts | **78/1000** — gate PASS |
| STALE broker debt | **67** on older sas — road sa-0001..0009 show broker PASS |
| Factory template | sa-0010 needs ACT+VERIFY — CHECK only so far |
| Auto-run | **Stopped** (kill flag) — per 007/008 law |
| Unstick path | Documented in 008 §7 |

---

## Part A.4 — Mandatory read chain (by role)

| Role | Read first |
|------|------------|
| **Worker** | 006 + 007 + 008 + 009 + `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` |
| **Brain** | 003 + 004 + 006 summary + this compendium Part A |
| **Maintainer** | 005a + 001 + self-audit 005b |
| **All agents** | 002c (context memory) every session |

---

## Part A.5 — Open items across incidents

1. **67 STALE broker** receipts — audit/re-closeout (007, 008)
2. **INCIDENT-005 fix batch** — awaiting ASF confirm
3. Broker **empty INBOX** on ACT/VERIFY auto-advance (008)
4. Hub quit → `/shutdown` (001)
5. **sa-0010** incomplete — factory law not satisfied until VERIFY receipt

**Hub:** Doc library → Ecosystem incidents (`ecosystem_incidents_index.py`).

---

## Part B — Session insights (mistakes, better moves, tips)

Synthesis from 2026-06-09 thread: auto-run failures, incidents 001–009, sa-0001..0010 audits, monitor, factory evidence checks.

---

### B.1 — What we learned (insights)

#### A. Progress is a factory, not a counter

Honest progress = one `sa` at a time through CHECK → ACT (if gap) → VERIFY, with:

| Layer | Requirement |
|-------|-------------|
| **Recipe** | REGISTRY title + prompt `.md` + verify command |
| **Validation** | Validators exit 0 **and** broker ≠ STALE |
| **Evidence** | `receipts/sa-XXXX-receipt.json` after broker VERIFY |
| **Built** | Stated honestly (built vs verify-only) |

INCIDENT-006 (607 fake done) and INCIDENT-007 (67 STALE broker) are the **same class**: surface looked green, factory did not.

#### B. Two “PASS” worlds — do not conflate

| World | What PASS means | Trap |
|-------|-----------------|------|
| **Shell validators** | Criteria on disk today are green | “All good” without broker |
| **Factory/broker** | Full role chain + clean submit | Receipt exists but STALE |

sa-0001..0009 on the **current road** show broker PASS + receipts — real for this slice. **67 STALE** is older/other sas — honesty debt, not ignored.

#### C. Auto-run is fast but fragile

Auto-run introduced: `sa_mismatch`, `receipt_on_disk` (banned), ACT skipped, empty INBOX (`chars: 0`), law before wrapper (CLOSEOUT_TEMPLATE). **Good:** auto-run correctly halted on `broker_reject` after fixes.

#### D. Founder corrections were right

| Founder said | Agent was wrong | Disk truth |
|--------------|-----------------|------------|
| WRONG — CHECK INCIDENTS | All good / broker_ok | 67 STALE, factory FAIL |
| RECIPE? VALIDATION? EVIDENCE? BUILT? | Validators only | Template + broker cycle required |
| WHY STUCK? | 180s blind wait | ~4–6 min/sa; tail log once |
| CHECK 001–010 complete? | Receipt = done | Only 0001–0009; 0010 incomplete |

#### E. sa-0001..0010 truth (audit)

- **Complete (9):** sa-0001..0009 — REGISTRY `done`, receipt VERIFY, PRIORITY rows, road broker PASS
- **Incomplete (1):** sa-0010 — CHECK done; ACT pending; no receipt; REGISTRY `backlog`
- **Receipt gap:** JSON has `evidence` text only — no structured RECIPE/VALIDATION/BUILT keys

#### F. Incident arc

Repeating pattern: unvalidated proof · wrong SSOT · procedure skip. INCIDENT-007 + `WORKER_FULL_ROUND_EVIDENCE` are the cure for (1)+(2) on Worker path.

---

### B.2 — Mistakes (session + class)

#### Agent/executor mistakes

| # | Mistake | Impact |
|---|---------|--------|
| 1 | Success without `validate-monitor-honesty` STALE count | Founder lost trust |
| 2 | Validator PASS = factory PASS | False complete for sa-0004..0008 |
| 3 | 180s chat Await vs tail log | Wasted founder time |
| 4 | Read log line 1 (`agent` not found @ 02:30Z) | False alarm — stale noise |
| 5 | `broker_ok` from chat without broker JSON | INCIDENT-006/007 class |
| 6 | “9 complete” before CHECK vs VERIFY distinction | sa-0010 still open |
| 7 | CLOSEOUT_TEMPLATE before wrapper 4 lines | sa-0009 VERIFY broker reject |

#### System mistakes (still open)

| # | Bug/gap | Status |
|---|---------|--------|
| 1 | Broker deliver → INBOX chars: 0 on ACT/VERIFY | Open |
| 2 | Dual advance (role_mismatch + broker moves) | Open |
| 3 | `brain_validate_goal1` per auto-run turn | Latency waste |
| 4 | 67 STALE broker historical receipts | Honesty debt |
| 5 | Receipt schema lacks RECIPE/VALIDATION/BUILT | Template in chat only |
| 6 | TRACK BACKLOG inject `NOT_DONE` for done sas | Monitor bug |

#### What we got right (after founder push)

- Stopped auto-run on broker reject
- Removed `receipt_on_disk` fake recovery
- `role_mismatch` gate + factory evidence gate wired
- INCIDENT-007 + 008 + 009 locked
- sa-0009 VERIFY closeout on disk
- sa-0010 CHECK + broker submit
- Monitor up + hub refreshed

---

### B.3 — Better moves (what should have happened)

#### Per turn (Worker)

```text
BEFORE:  Unstick → factory gate PASS → gatekeeper PASS → tail -5 log (not line 1)
DURING:  Budget 4–6 min/sa → tail -20 at ~3 min → read broker JSON
END:     RECIPE·VALIDATION·EVIDENCE·BUILT + YAML → broker worker-submit
AFTER:   Cite STALE broker count · never claim done without receipt path
```

#### Per status reply (any agent)

1. `validate-monitor-honesty-v1.sh` → cite STALE count
2. Queue head from monitor API (not chat memory)
3. Honest count from `registry_honest` (not REGISTRY raw, not PRIORITY)
4. Last `AGENT DONE` + timestamp from batch log **tail**
5. Separate: validators PASS vs broker PASS

#### Auto-run policy (post-007)

- Do not restart until one manual `run inbox` VERIFY shows broker PASS + full template
- Default **3 turns per sa**, not 30-turn spawn
- On `broker_reject`: read error, STOP — no optimism

#### sa-0010 next move

CHECK found already aligned. **ACT:** no-op if no gap. **VERIFY:** `validate-strategic-synthesis-v1.sh` + FCB → receipt → REGISTRY `done`. Do not invent build.

---

### B.4 — Tips for future moves

#### Founder (one-tap)

1. Progress = monitor **honest count** only (**78/1000**)
2. Worker chat → **`run inbox`** — STOP — repeat
3. Monitor: `http://127.0.0.1:13021/monitor` or Command → Open Pre-Sleep Monitor
4. Before “done”: Broker column ≠ STALE for that `sa`
5. Auto-run only after one clean manual VERIFY; **STOP** when unsure
6. Screenshot `agent` not found → check **log timestamp**

#### Worker (executor)

1. Never skip four-line closeout on VERIFY
2. Never claim `broker_ok` without broker JSON `ok: true`
3. Never block chat on long Await — tail log in shell
4. CHECK no gap → verify-only on ACT; don’t fake implementation
5. After hub STOP → Unstick before next drain
6. Read INCIDENT-007 §8 before “sa closed”

#### Brain / Maintainer

1. Read **GOAL_HIERARCHY** before “what next”
2. External paste → `INPUT CLASS: EXTERNAL_CRITIC` + §6 table
3. Brain **REFUSE** Worker INBOX prompts
4. Don’t push autorun/batch as default

#### Audit (“is it real?”) — five questions

1. Recipe 3-file exists for queue head?
2. Validators passed for that sa’s verify cmd?
3. Broker PASS (not STALE) for that `sa_id`?
4. Receipt with `round_type: verify`?
5. Built or verify-only — stated explicitly?

Any “no” on VERIFY closeout → **not complete**.

#### Priority backlog (Maintainer)

| Priority | Item |
|----------|------|
| P0 | Finish sa-0010 ACT+VERIFY |
| P1 | Fix empty INBOX on broker auto-advance |
| P1 | Audit/re-closeout 67 STALE broker |
| P2 | Receipt schema structured fields |
| P2 | INCIDENT-005 fix batch — ASF confirm |

---

### B.5 — One-page “never again” card

```text
COUNT:     receipts only · honest_done on monitor
PROVE:     AGENT DONE in log tail · broker JSON · receipt path
TEMPLATE:  RECIPE · VALIDATION · EVIDENCE · BUILT — every VERIFY
WAIT:      estimate 4–6 min · tail log · never 180s chat hostage
LANE:      Worker builds · Brain routes · Brain refuses INBOX
CRITIC:    INPUT CLASS first · no disk from GPT without ASF yes
STOP:      broker_reject · WORKER_TURN_OPEN · kill flag — Unstick first
```

---

### B.6 — Honest self-check (claims verified at lock)

| Claim | Verified? |
|-------|-----------|
| 78/1000 honest | ✅ monitor API |
| sa-0001..0009 complete | ✅ receipts + REGISTRY + road broker PASS |
| sa-0010 incomplete | ✅ no receipt · Q20 ACT pending |
| 67 STALE global | ✅ validate-monitor-honesty |
| Auto-run paused | ✅ monitor |

**Caveat:** Road broker PASS for sa-0001..0009 does **not** clear **67 STALE** elsewhere until audited.

**Next best move:** `run inbox` to finish sa-0010 (likely verify-only ACT + VERIFY) → **78 → 79** honest.

---

## Part C — Read chain

| Role | Read |
|------|------|
| Worker | Part B + INCIDENT-007 + `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` |
| Brain | Part A index + INCIDENT-004 |
| Maintainer | Part A + INCIDENT-005 + Part B §B.4 |
| Founder | Part A.3 + Part B.5 never-again card |

---

**END COMPENDIUM**
