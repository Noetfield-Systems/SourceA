# Worker auto-run stall, timing waste & factory gate mismatch (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-09-INCIDENT-008  
**Classification:** MANDATORY READ — **every SourceA Worker** · auto-run executor · Maintainer  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_WORKER_AUTORUN_STALL_AND_TIMING_INCIDENT_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-09 (founder screenshots + “WHY DID YOU STUCK?” · “WRITE FULL REPORT”)  
**Related:** INCIDENT-003 · INCIDENT-006 · INCIDENT-007 · `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md`  
**Agent reports:** AR-63960a328c · AR-a7ba632c8b · AR-098180dd31

---

## 1. Executive summary

A SourceA Worker auto-run session for **sa-0009** (Q16–Q18 CHECK→ACT→VERIFY) exposed **three classes of failure**:

1. **Executor timing waste** — agent blocked chat on **180s blind poll** instead of estimating **~3 min** for three headless turns and tailing the batch log once.
2. **Factory gate / agent prompt mismatch** — new **CLOSEOUT_TEMPLATE** law (INCIDENT-007) enforced on broker **before** headless agent wrapper included **RECIPE · VALIDATION · EVIDENCE · BUILT** lines → VERIFY broker **reject** halted auto-run at turn 3 despite disk closeout.
3. **Legacy log confusion** — founder screenshot showed top-of-log **`agent` not found** (`WORKER_BATCH_HALT` **2026-06-09T02:30Z**) — **stale**; fixed earlier (`~/.local/bin/agent` present for 10:41Z run).

**Outcome:** sa-0009 **closed logged** (receipt + REGISTRY `done` · validators PASS · **78/1000** honest). Broker VERIFY submit **rejected once** (`CLOSEOUT_TEMPLATE_MISSING`); auto-run **correctly stopped** on `broker_reject`. Wrapper patched for future VERIFY turns.

**One-line law for all future Workers:**

> **Estimate turn time (CHECK ~60s · ACT ~30s · VERIFY ~90–150s) → tail log once → never block chat on long Await. Law logged must match agent wrapper the same ship.**

---

## 2. Timeline (2026-06-09 UTC) — accurate disk order

| Time | Event | Evidence |
|------|-------|----------|
| 02:30 | **Stale halt** — `WORKER_BATCH_HALT` `worker_chat_preflight` `[Errno 2] No such file or directory: 'agent'` | Top of `~/.sina/goal1-worker-batch-latest.log` (screenshot) — **not** current run |
| 10:27 | Hub STOP mid-turn 7 — orphan **`WORKER_TURN_OPEN` sa-0009** | `worker_turn_state_v1.json` |
| 10:35–10:40 | INBOX corrupt `sa-BIND` · empty prompt | `worker-prompt-inbox-v1.json` |
| 10:40 | **Unstick** closed stale turn · **deliver** sa-0009 CHECK | `worker_stuck_recovery_v1.py` |
| 10:41 | Auto-run START · gatekeeper PASS | `AUTO-RUN START turns=30 queue=16/30 sa=sa-0009 role=check` |
| 10:42:03 | Turn 1 CHECK done · broker OK · orchestrator `role_mismatch expected=act got=check` (non-fatal) | batch log JSON |
| 10:42:37 | Turn 2 ACT done · broker OK · INBOX deliver **chars: 0** for meta | batch log |
| 10:45:15 | Turn 3 VERIFY agent done · **broker FAIL** `CLOSEOUT_TEMPLATE_MISSING` | batch log |
| 10:45:16 | Auto-run **stopped** `broker_reject` · receipt + REGISTRY sa-0009 **done** logged | `receipts/sa-0009-receipt.json` |
| 10:45+ | Wrapper patched · auto-run STOP · hub refresh | `start_goal1_worker_turn_v1.py` |

---

## 3. Root causes (ranked)

| # | Cause | Class | Owner |
|---|--------|-------|-------|
| 1 | **Law shipped without agent wrapper update** — broker required 4-line template; headless prompt had YAML only | Gate/law drift | Maintainer / executor |
| 2 | **180s chat Await** instead of log tail after ~3 min estimate | Executor anti-pattern | Cursor agent (INCIDENT-003) |
| 3 | **Hub STOP without turn close** → `WORKER_TURN_OPEN` blocks all drains | Ops | Hub stop path + Unstick |
| 4 | **Broker auto-deliver** sets INBOX meta but **prompt chars: 0** on ACT/VERIFY | Code bug | `goal1_lane_broker` / deliver path |
| 5 | **Dual advance** — orchestrator `role_mismatch` wait + broker `auto_advance` still moves queue | Race | orchestrator + broker |
| 6 | **`brain_validate_goal1_v1.py` after every auto-run turn** | Unnecessary latency | `goal1_auto_run_v1.py` |
| 7 | **30-turn spawn** when one sa needs **3 turns** | Scope waste | Hub start default |
| 8 | **Stale log top** (`agent` not found) read as current failure | UX / INCIDENT-003 | Founder screenshot vs log tail |
| 9 | **67 STALE broker** receipts from prior sessions still on monitor | Honesty debt | INCIDENT-006/007 |

---

## 4. sa-0009 round — recipe · validation · evidence · built

### 4.1 Recipe (3 files)

| Field | Value |
|-------|-------|
| **Title** | Run `validate-governance-drift-v1.sh`; drift items must be 0 |
| **Prompt** | `brain-os/plan-registry/sourcea-1000/prompts/phase-s0-ssot-alignment/T0/sa-0009.md` |
| **Verify** | `cd scripts && bash validate-governance-drift-v1.sh && python3 find_critical_bugs.py` |

### 4.2 Validation

| Check | Result |
|-------|--------|
| CHECK validators | PASS · drift **0** · score **100** |
| ACT | no-op · validators PASS |
| VERIFY validators | PASS · build · FCB critical **0** · pack 1000 |
| Broker VERIFY submit | **FAIL** `CLOSEOUT_TEMPLATE_MISSING` (then auto-run halt) |
| `validate-registry-honest-gate-v1` | PASS · **78/1000** |

### 4.3 Evidence

| Artifact | Status |
|----------|--------|
| `receipts/sa-0009-receipt.json` | DONE |
| `REGISTRY.json` sa-0009 | `done` |
| `SOURCEA-PRIORITY.md` row | added 2026-06-09 |
| Broker events VERIFY | **reject** on template — monitor may still show STALE for broker column |

### 4.4 Built

**No new implementation** — verify-only closeout (governance drift validator already green logged).

---

## 5. Unnecessary Worker activity — do NOT repeat

| Activity | Typical cost | Verdict |
|----------|-------------|---------|
| Chat **Await 120–180s** with no log read | Blocks founder thread | **BANNED** — estimate + one `tail` |
| `brain_validate_goal1` **per turn** | 5–15s × N turns | **Defer** to batch end or founder tap |
| Re-read **entire** batch log from line 1 | Shows stale `agent` halt | **Tail -30** only |
| Spawn **30 turns** for one sa | Hours of scope | **3 turns** per sa default |
| **Deliver** with empty INBOX prompt | Agent runs blind; broker drift | Fix deliver before next run |
| Claim **broker_ok** when JSON shows `ok: false` | INCIDENT-006/007 | **FAIL** the status reply |

---

## 6. Timing estimates (use before every auto-run)

| Role | Typical headless `agent -p -f` | Plan for |
|------|-------------------------------|----------|
| CHECK | 45–90s | 90s |
| ACT (no-op) | 20–45s | 45s |
| ACT (implement) | 2–8 min | task size |
| VERIFY + closeout | 90–180s | 150s |

**One sa (CHECK+ACT+VERIFY):** budget **~4–6 min** · poll batch log **once at 3 min**, then every **45s** until `AGENT DONE` or `broker_reject`.

**Never** hold the founder chat hostage for the full runtime.

---

## 7. Mandatory Worker playbook (next time do better)

### 7.1 Before START AUTO RUN

```text
1. Unstick if gatekeeper shows WORKER_TURN_OPEN
2. python3 scripts/worker_factory_evidence_gate_v1.py --json  → must PASS
3. python3 scripts/gatekeeper_v1.py --no-broker  → must PASS
4. tail -5 ~/.sina/goal1-worker-batch-latest.log  → note LAST timestamp (ignore top-of-file stale halts)
5. which agent  → must resolve (~/.local/bin/agent)
```

### 7.2 During run (executor only)

```text
6. Estimate: 3 turns × ~90s ≈ 4.5 min for one sa
7. After ~3 min: tail -20 batch log — look for AGENT DONE | broker_reject | factory_evidence_gate
8. On broker_reject: read error field — do NOT claim success
9. On success: cite RECIPE · VALIDATION · EVIDENCE · BUILT from disk
```

### 7.3 End reply template (copy every closeout)

```text
RECIPE: <title> · <prompt path> · <verify cmd>
VALIDATION: validators <list> · broker <PASS|FAIL|STALE> · roles <check/act/verify>
EVIDENCE: receipt <path> · PRIORITY <y/n> · disk delta <line>
BUILT: <yes: file> OR <no: verify-only> OR <none: CHECK only>
```

### 7.4 Founder sees screenshot `agent` not found

- **Check log timestamp** — if hours before current START line, it is **archive noise**.
- **Proof of current run:** latest `AUTO-RUN START` + `AGENT START` + `which agent` in status reply.

---

## 8. Remediation shipped (this session)

| Fix | File / artifact |
|-----|-----------------|
| INCIDENT-007 audit locked | `SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md` |
| Factory evidence law + gate | `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` · `worker_factory_evidence_gate_v1.py` |
| VERIFY wrapper includes 4 closeout lines | `start_goal1_worker_turn_v1.py` |
| Auto-run halts on `broker_reject` | `goal1_auto_run_v1.py` |
| `receipt_on_disk` ban | removed from `start_goal1_worker_turn_v1.py` |
| Orchestrator `role_mismatch` gate | `healthy-drain-orchestrator-v1.py` |
| Unstick + deliver path documented | §7.1 |

### 8.1 Still open (next Maintainer slice)

- Broker deliver **empty prompt** on ACT/VERIFY auto-advance  
- `brain_validate_goal1` once-per-batch not per-turn  
- Re-closeout **67 STALE broker** rows (INCIDENT-007)  
- Hub START default **3 turns per sa** option  

---

## 9. Acceptance checks (future Workers — copy/paste proof)

Before reporting “round complete”:

1. `tail -3 ~/.sina/goal1-worker-batch-latest.log` contains **`AGENT DONE sa-XXXX`** for VERIFY  
2. `receipts/sa-XXXX-receipt.json` exists **after** broker PASS **or** explicit broker_reject explained  
3. `validate-monitor-honesty-v1.sh` — cite **STALE broker** count  
4. Reply includes §7.3 four lines  
5. Log timestamp cited — **not** top-of-file stale halt  

---

## 10. Read chain

| Role | Read |
|------|------|
| Worker | This doc · INCIDENT-007 · `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` |
| Executor / auto-run | §6 timing · §7 playbook · §5 banned activities |
| Founder | §4 sa-0009 proof table · §7.4 screenshot law |

---

**END INCIDENT-008**
