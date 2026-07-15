# Worker full-round evidence enforcement (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-09-LAW-WORKER-FACTORY-EVIDENCE-v1  
**Classification:** MANDATORY — **every SourceA Worker** chat · headless auto-run · Maintainer executor on Worker path  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md`  
**Related:** INCIDENT-006 · INCIDENT-007 · `REGISTRY_DRAIN_RAIL_LOCKED_v1.md` · `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`  
**Mechanical gate:** `scripts/worker_factory_evidence_gate_v1.py` · `scripts/validate-worker-factory-evidence-v1.sh`  
**Cursor rule:** `.cursor/rules/098-worker-full-round-evidence.mdc`

---

## 1. One-line law

> **No Worker turn ships without recipe logged, factory gate PASS, role-correct broker submit, and closeout reply citing RECIPE · VALIDATION · EVIDENCE · BUILT. Receipt alone never counts when broker is STALE or `sa_mismatch`.**

---

## 2. Factory model (non-negotiable)

```text
RECIPE (3 files) → CHECK → ACT (only if CHECK gap) → VERIFY → broker PASS each step → evidence
```

| Layer | SSOT | PASS means |
|-------|------|------------|
| **Recipe** | REGISTRY `title` + `prompts/.../sa-XXXX.md` + REGISTRY `verify` | All three exist; INBOX `bound: sa_id=… role=…` matches queue head |
| **Validation** | Machine validators + broker factory | Validators exit 0; broker ≠ STALE; no `sa_mismatch`; no `receipt_on_disk` recovery |
| **Evidence** | `receipts/sa-XXXX-receipt.json` (VERIFY only) + disk delta | Written **after** broker VERIFY `WORKER_SUBMIT` PASS; PRIORITY row on closeout |
| **Built** | Git/disk delta | Agent states **built** vs **verify-only closeout** — never claim build when CHECK said already logged |

---

## 3. Mandatory Worker reply template (every turn end)

```text
RECIPE: <title> · <prompt path> · <verify cmd>
VALIDATION: validators <list PASS/FAIL> · broker <PASS|STALE|FAIL|pending> · roles ran <check/act/verify>
EVIDENCE: receipt <path or pending> · PRIORITY row <y/n> · disk delta <one line>
BUILT: <yes: path/line> OR <no: verify-only closeout> OR <none: CHECK only>
```

Plus YAML block:

```yaml
status: WORKER_ROUND_REPORT
round_type: check | act | verify
sa_focus: sa-XXXX
validate:
  spine: PASS|FAIL
  critical_bugs: N
summary: one line
```

**Forbidden:** `round_type: implement` / `audit` without mapping to check/act/verify · `broker_ok` chat claims without broker JSON · skipping template on VERIFY closeout.

---

## 4. Hard blocks (mechanical — gate FAIL)

| # | Condition | Gate reason | Founder fix |
|---|-----------|-------------|-------------|
| 1 | `worker_turn_state_v1.json` **open** and ≠ queue head sa | `WORKER_TURN_OPEN` | Hub **Unstick Worker** |
| 2 | INBOX `pending` false or empty prompt | `INBOX_NOT_READY` | Hub Deliver / auto-run prepare after unstick |
| 3 | INBOX meta `sa_id` not `sa-####` (e.g. `sa-BIND`) | `INBOX_META_INVALID` | Unstick + deliver |
| 4 | INBOX `bound:` header ≠ meta sa/role | `INBOX_BIND_DRIFT` | Re-deliver |
| 5 | Orchestrator `awaiting_worker` + force deliver | `AWAITING_WORKER` | Finish turn or reset |
| 6 | Broker submit `sa_mismatch` | `BROKER_SA_MISMATCH` | Turn snapshot + role gate (never mask) |
| 7 | Monitor **STALE broker** on closeout sa | `BROKER_STALE_RECEIPT` | Re-run full CHECK→ACT→VERIFY |
| 8 | CHECK → VERIFY skip when CHECK said **GAP FOUND** | `ACT_SKIPPED_ILLEGAL` | Orchestrator role_mismatch gate |
| 9 | `receipt_on_disk` / fake `broker_ok` recovery | `FAKE_BROKER_RECOVERY` | **Banned** in code |
| 10 | Auto-run while prepare returns `WORKER_BUSY` | `AUTORUN_FACTORY_BLOCKED` | Unstick first |

---

## 5. Enforcement map (every Worker entry)

| Entry | Enforcement |
|-------|-------------|
| `cursor_entry_gate.py --role worker` | Hash this law · `run_factory_gate(strict=True)` |
| `gatekeeper_v1.py` | Factory gate before `SAFE TO EXECUTE` |
| `healthy-drain-orchestrator-v1.py` `deliver_current` | Factory gate (inbox + turn) |
| `start_goal1_worker_turn_v1.py` | Factory gate after gatekeeper |
| `goal1_auto_run_v1.py` | Factory gate each turn; halt on `broker_reject` |
| `goal1_lane_broker.py` `worker_submit` | `sa_mismatch` reject · snapshot bind · no receipt_on_disk |
| `prompt_feasibility_gate.py --role worker` | Already blocks live-eval inject |
| `validate-worker-factory-evidence-v1.sh` | CI / Maintainer proof |
| `.cursor/rules/098-worker-full-round-evidence.mdc` | Agent read-first |

---

## 6. Full round acceptance (before “sa closed”)

1. `validate-monitor-honesty-v1.sh` — cite **STALE broker** count in reply  
2. Batch log — `AGENT DONE` + **no `sa_mismatch`** on that sa  
3. `goal1-lane-broker-events.jsonl` — `WORKER_SUBMIT` per role on same `sa_id`  
4. Reply includes §3 template all four lines  
5. VERIFY only: `receipts/sa-XXXX-receipt.json` + REGISTRY `done` + broker monitor ≠ STALE  

---

## 7. Auto-run policy (post INCIDENT-007)

- **Do not** restart auto-run until one **manual** `run inbox` VERIFY shows broker PASS + template complete.  
- `~/.sina/auto-run-disabled-v1.flag` — legacy batch kill; unified path still requires factory gate PASS.  
- Hub STOP mid-turn **must** run Unstick or orphan turn blocks all drains.

---

## 8. Read chain

| Role | Read |
|------|------|
| Worker | This doc · INCIDENT-007 · `REGISTRY_DRAIN_RAIL_LOCKED_v1.md` |
| Maintainer | This doc · `validate-worker-factory-evidence-v1.sh` |
| Brain | INCIDENT-007 summary only — Worker executes factory |

---

**END WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1**
