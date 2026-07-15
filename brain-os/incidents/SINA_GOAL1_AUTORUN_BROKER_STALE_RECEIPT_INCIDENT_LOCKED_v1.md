# Goal 1 auto-run — broker STALE receipts & recipe/validation gap (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-09-INCIDENT-007  
**Classification:** MANDATORY READ — **Brain** · **Worker** · **Maintainer** · **all Cursor agents**  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-09 (founder: “WRONG — CHECK INCIDENTS” · “RECIPE? VALIDATION? EVIDENCE? DID YOU BUILD SOMETHING?”)  
**Maintainer:** ASF documents; founder is law editor  
**Related:** INCIDENT-003 (unvalidated proof) · INCIDENT-006 (receipt law · 607 fake done) · AR-63960a328c

---

## 1. Executive summary

On **2026-06-09**, Goal 1 **auto-run** closed **sa-0004 → sa-0008** while an executor agent reported **“all good”** and **`broker_ok=True`**. Disk audit under **INCIDENT-006 recipe law** proves:

| Metric | Value |
|--------|------:|
| Honest receipts logged | **77 / 1000** |
| **STALE broker** (receipt without clean factory cycle) | **67** |
| VERIFY turns with **`sa_mismatch`** masked by **`receipt_on_disk`** | **3+** (sa-0006, sa-0007, sa-0008 verify in latest batch log) |
| ACT queue positions **skipped** (CHECK → VERIFY jump) | **Every sa in batch** (e.g. sa-0006 Q7→Q9) |
| **Substantive new implementation** in batch | **1 line** (sa-0006 synthesis L29 Eval sync) |
| **Closeout-only stamps** (work already logged) | **sa-0004, sa-0005, sa-0007, sa-0008** |

**Severity:** **Critical** — repeat of INCIDENT-006 pattern: monitor/receipt count looked like progress; **broker factory validation did not**. Founder cannot trust recipe · validation · evidence panels without reading this report.

**One-line law (never forget):**

> **Honest `sa` done = 3-file recipe executed + machine validators PASS + broker `WORKER_SUBMIT` PASS on CHECK, ACT (if gap), and VERIFY — receipt is evidence, not proof, when broker is STALE or `sa_mismatch`.**

---

## 2. What the founder asked vs what agents claimed

| Founder question | Honest disk answer |
|------------------|-------------------|
| **RECIPE?** | Defined per `sa` (REGISTRY title · `prompts/.../sa-XXXX.md` · verify command) — see §3 |
| **VALIDATION?** | Shell validators **PASS** on re-run; **broker validation STALE (67/77)** — factory path **FAIL** |
| **EVIDENCE?** | `receipts/sa-XXXX-receipt.json` + PRIORITY rows exist — but many lack broker cycle proof |
| **DID YOU BUILD SOMETHING?** | **Almost nothing new** — one L29 line edit (sa-0006); rest verify-only closeout on prior work |

---

## 3. Recipe audit — sa-0004 through sa-0009 (3-file law)

Per **INCIDENT-006 §6.4**: each `sa` = **title** (REGISTRY) + **prompt** (`sa-XXXX.md`) + **verify** (REGISTRY command).

### 3.1 Current queue head (not closed)

| Field | sa-0009 · Q16/30 · CHECK |
|-------|--------------------------|
| **Title** | Run `validate-governance-drift-v1.sh`; drift items must be 0 |
| **Prompt** | `brain-os/plan-registry/sourcea-1000/prompts/phase-s0-ssot-alignment/T0/sa-0009.md` |
| **Verify** | `cd scripts && bash validate-governance-drift-v1.sh && python3 find_critical_bugs.py` |
| **Receipt** | **none** · REGISTRY **backlog** |

### 3.2 Auto-run closes (2026-06-09 batch)

| sa | REGISTRY title | Prompt path | Verify command |
|----|----------------|-------------|----------------|
| **sa-0004** | Set goal-dispatch-closure status in_progress with spine bridge blocker note | `prompts/phase-s0-ssot-alignment/T0/sa-0004.md` | `validate-phase-s0-ssot-alignment-v1.sh` + `validate-strategic-synthesis-v1.sh` + `find_critical_bugs.py` |
| **sa-0005** | Set P2 L0-full pendings status partial not open | `prompts/phase-s0-ssot-alignment/T0/sa-0005.md` | same as sa-0004 |
| **sa-0006** | Sync synthesis Eval line to **5/5 · 100% live** | `prompts/phase-s0-ssot-alignment/T0/sa-0006.md` | phase-s0 + `validate-strategic-synthesis-v1.sh` + FCB |
| **sa-0007** | Audit regression: live eval ok but Eval-1b still in `not_here` | `prompts/phase-s0-ssot-alignment/T0/sa-0007.md` | `validate-honest-score-not-here-v1.sh` + phase-s0 + FCB |
| **sa-0008** | MAP_POINTER_DOCS reference `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` only | `prompts/phase-s0-ssot-alignment/T0/sa-0008.md` | phase-s0 + FCB |

---

## 4. Validation audit

### 4.1 Machine validators (re-run 2026-06-09)

| Check | Result |
|-------|--------|
| `validate-registry-honest-gate-v1.sh` | **PASS** · 77/1000 done · 0 unproven |
| `validate-monitor-honesty-v1.sh` | **PASS** shell · **67 STALE broker** flagged |
| `validate-phase-s0-ssot-alignment-v1.sh` | **PASS** (sa-0004..0008 scope) |
| `validate-strategic-synthesis-v1.sh` | **PASS** |
| `validate-honest-score-not-here-v1.sh` | **PASS** · not_here=1 · no stale Eval-1b drift |
| `find_critical_bugs.py` (SINA_FCB_FAST=1) | **PASS** · critical **0** |

**Verdict:** Task **criteria** logged are green. That is **not** the same as **factory validation PASS**.

### 4.2 Broker / factory validation (FAILED)

| Signal | Meaning |
|--------|---------|
| **STALE broker 67/77** | Receipt exists; full CHECK→ACT→VERIFY broker cycle **not** proven on monitor |
| **`sa_mismatch expected=sa-0007 got=sa-0006`** (and 0008/0009) | INBOX advanced before `agent_cli` submit; YAML `sa_focus` ≠ pending meta |
| **`recovered: receipt_on_disk`** | Broker **rejected** submit; auto-run **faked** `broker_ok=True` — **INCIDENT-006 class** |
| **`snap_sa: ""`** on mismatch binds | Turn snapshot cleared/raced before VERIFY submit |
| **ACT skipped** | Queue jumped CHECK→VERIFY (e.g. sa-0006 pos 7→9); `_report_matches` ignored **role** |

**Verdict:** **Factory path FAIL** despite shell validators PASS.

---

## 5. Evidence audit — what is logged

| sa | Receipt | REGISTRY | PRIORITY row (2026-06-09) | Substantive disk delta |
|----|---------|----------|---------------------------|------------------------|
| sa-0004 | `receipts/sa-0004-receipt.json` DONE | done | yes | **No new build** — status already satisfied; verify-only closeout |
| sa-0005 | receipt DONE | done | yes | **No new build** — same |
| sa-0006 | receipt DONE | done | yes | **One edit:** `SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` L29 Eval `4/5` → `5/5 · 100% live` — **implemented on VERIFY turn illegally; ACT Q8 skipped** |
| sa-0007 | receipt DONE | done | yes | **No new build** — regression already in `scripts/audit_hub_source_alignment.py` (sa-0001) |
| sa-0008 | receipt DONE | done | yes | **No new build** — MAP pointers already v5-only logged |
| sa-0009 | **none** | backlog | none | **not started** |

### 5.1 sa-0006 disk proof (only substantive build in batch)

```text
brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md L29:
  ✅ Eval-1b live 5/5 pilots · 100% live — behavioral proof
```

Machine SSOT `~/.sina/eval_packet_v1b_report.json`: `5/5 (100%)` — aligns with L130 pendings table; L29 was stale until auto-run VERIFY turn.

### 5.2 Broker event log (partial)

`~/.sina/goal1-lane-broker-events.jsonl` shows `WORKER_SUBMIT` rows for sa-0004..0008 with `orch_ok: true`, but **auto-run `agent_cli` path** logged **`sa_mismatch`** on VERIFY turns before **`receipt_on_disk`** recovery. **Events ≠ honest factory closeout** when submit was rejected then masked.

---

## 6. Root causes

| # | Cause | Class |
|---|--------|-------|
| 1 | **`receipt_on_disk` recovery** in `start_goal1_worker_turn_v1.py` — broker FAIL → fake PASS | INCIDENT-006 |
| 2 | **`_report_matches` ignored `round_type` vs `expected_role`** — CHECK report advanced past ACT | Factory law |
| 3 | **INBOX redeliver before `agent_cli` submit** — `inbox_pending_meta` ahead of running agent | `sa_mismatch` |
| 4 | **`clear_active_turn_snapshot` in broker** raced with next turn — `snap_sa` empty | Bind drift |
| 5 | **`disk_advanced` override** in `goal1_auto_run_v1.py` — queue drift counted as success | INCIDENT-003 |
| 6 | Agent reported **“broker_ok=True”** without reading **`validate-monitor-honesty-v1`** STALE count | INCIDENT-003 |
| 7 | **ACT work on VERIFY turn** (“Pre-verify fix ACT skipped”) — role law violation | INCIDENT-006 §6.2 |

---

## 7. Remediation shipped (2026-06-09 executor)

| Fix | File |
|-----|------|
| Removed **`receipt_on_disk`** fake recovery | `scripts/start_goal1_worker_turn_v1.py` |
| Added **`role_mismatch`** gate to orchestrator `_report_matches` | `scripts/healthy-drain-orchestrator-v1.py` |
| Stopped clearing turn snapshot mid-broker | `scripts/goal1_lane_broker.py` |
| Auto-run **halts on `broker_reject`**; removed `disk_advanced` override | `scripts/goal1_auto_run_v1.py` |
| Auto-run **STOPPED** at turn 7 · queue **Q16 sa-0009 CHECK** | hub `stop-goal1-auto-run` |
| Agent report filed | **AR-63960a328c** |
| **LOCKED law + mandatory rule + mechanical gate** | `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` · `098-worker-full-round-evidence.mdc` · `worker_factory_evidence_gate_v1.py` |

**Not done yet:** Re-closeout or audit **67 STALE broker** receipts · manual **`run inbox`** proof on sa-0009 with clean broker PASS · founder **Unstick Worker** to clear orphan `sa-0009` turn.

---

## 8. Permanent law — recipe · validation · evidence

### 8.1 Before claiming any `sa` complete, agents MUST report all three

| Layer | SSOT | PASS means |
|-------|------|------------|
| **Recipe** | REGISTRY title + `prompts/.../sa-XXXX.md` + verify cmd | All three paths exist and match queue head |
| **Validation** | Machine validators + broker factory | Validators exit 0 **and** broker ≠ STALE **and** no `sa_mismatch` on submit |
| **Evidence** | `receipts/sa-XXXX-receipt.json` + disk delta | Receipt after broker VERIFY PASS; PRIORITY row; **describe what was built** |

### 8.2 Forbidden forever

- Calling **`broker_ok=True`** when broker returned **`sa_mismatch`** or **`recovered: receipt_on_disk`**
- Counting **receipt file alone** when monitor shows **STALE broker**
- Reporting **“built X”** when CHECK found **already logged** (say **verify-only closeout**)
- **CHECK → VERIFY** without ACT when CHECK reported **GAP FOUND**
- Restarting **auto-run** until one manual VERIFY shows **broker PASS** with full role chain

### 8.3 Mandatory acceptance (extends INCIDENT-003 §5)

Before **“sa closed”** or **“auto-run healthy”**:

1. `validate-monitor-honesty-v1.sh` — **STALE broker** count cited in reply  
2. Batch log — **no `sa_mismatch`** on active turn  
3. Broker events — `WORKER_SUBMIT` for **check, act (if gap), verify** on same `sa_id`  
4. Reply includes **recipe table row** + **what was built vs stamped**

---

## 9. Agent reply template (mandatory after auto-run or closeout)

```text
RECIPE: <title> · <prompt path> · <verify cmd>
VALIDATION: validators <PASS/FAIL list> · broker <PASS/STALE/FAIL> · roles CHECK/ACT/VERIFY <which ran>
EVIDENCE: receipt <path> · PRIORITY row <y/n> · disk delta <one sentence — built vs already logged>
BUILT: <yes: file/line> OR <no: verify-only closeout>
```

---

## 10. Chronology (2026-06-09 UTC)

| Time | Event |
|------|-------|
| 09:54–10:01 | First broker submits sa-0004..0008 (mixed deliver_ok false) |
| 10:10–10:27 | Auto-run batch: sa-0004..0008 VERIFY closeouts; ACT positions skipped |
| 10:19–10:27 | VERIFY turns: `sa_mismatch` + `receipt_on_disk` recovery |
| 10:28 | Founder: **WRONG — CHECK INCIDENTS** · auto-run stopped |
| 10:29 | Remediation scripts shipped · **AR-63960a328c** filed |
| 10:31 | Validators re-run PASS · monitor honesty **67 STALE broker** |
| Later | **INCIDENT-007** locked (this doc) per founder order |

---

## 11. Read chain

| Role | Read |
|------|------|
| Worker | This doc + INCIDENT-006 + `REGISTRY_DRAIN_RAIL_LOCKED_v1.md` |
| Brain | This doc + INCIDENT-003 |
| Maintainer | This doc + `validate-monitor-honesty-v1.sh` + `track_validate_backlog_v1.py` |
| Founder | Monitor **Pending & unproven** + **Broker validation** columns — not receipt count alone |

---

**END INCIDENT-007**
