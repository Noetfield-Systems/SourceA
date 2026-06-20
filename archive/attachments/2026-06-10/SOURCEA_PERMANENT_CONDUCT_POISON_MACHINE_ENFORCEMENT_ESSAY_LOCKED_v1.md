> **ARCHIVE ONLY — not canonical law.** Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

# SourceA — Permanent conduct + poison loop machine enforcement

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Date:** 2026-06-10  
**Audience:** Maintainer (primary shipper) · Worker · Brain · ASF  
**Classification:** Implementation spec — turns root-cause essay into **enforceable** factory law  
**Parent:** `SOURCEA_ROOT_CAUSE_FACTORY_CONTROL_PLANE_ESSAY_LOCKED_v1.md`  
**Companion:** `SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v2.md` · `INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md`

---

## 0. Executive summary

Chat rules failed at scale (INCIDENT-015-CONDUCT). Permanent fix requires **five mechanical layers** that make disobedience and poison loops **unspawnable**, not discouraged in prose.

| Layer | Name | Stops |
|-------|------|-------|
| L0 | Kill SSOT | Unauthorized resume |
| L1 | Spawn gates | autodrain after STOP |
| L2 | Per-turn gates | sa_mismatch retry loops |
| L3 | Session / lexicon gate | “why stuck” → resume |
| L4 | Audit gates | regression when gate removed |
| L5 | Hub truth | false Idle · dead Stop |

**Founder one-liner:** *Freeze by default · one sa when unfrozen · one now-line in every reply · spawn gate or nothing runs.*

---

## 1. Two disease classes (do not conflate)

| Class | Definition | 015 example | Fix type |
|-------|------------|-------------|----------|
| **CONDUCT** | ASF will violated — authority inversion | Resume autodrain after STOP | Spawn + lexicon gates |
| **POISON** | Automation on bad state — technical loop | sa_mismatch · bind drift · silent pack | Per-turn state machine + bind heal |

Conduct hurt **trust**. Poison hurt **truth**. Fixing only poison leaves disobedience; fixing only conduct leaves retry loops.

---

## 2. What is already enforced (keep — do not tear down)

### 2.1 Freeze / stop

| Asset | Role |
|-------|------|
| `scripts/stop_goal1_auto_run_v1.py` | Kill PIDs · reset orch · broker idle · locks |
| `~/.sina/auto-run-disabled-v1.flag` | Kill switch — law: ON in founder_busy |
| `scripts/paid_engine_gate_v1.py` | Block paid API/CLI when flag |
| `scripts/autorun_dispatcher_v1.py` | Pause dispatch when flag |
| `validate-founder-agentic-commercial-policy-v1.sh` | Critical — flag must exist |
| Hub `/api/stop-goal1-auto-run` | Founder tap → stop script |

### 2.2 Poison / bind

| Asset | Role |
|-------|------|
| `healthy_pack_bind_lib_v1.py` | Triple align queue/inbox/bind |
| `validate-healthy-pack-bind-v1.sh` | Mechanical bind gate |
| `~/.sina/pack-drain-receipts/pack-*.json` | Per-pack delta proof |
| `operating_mode_enforce_v1.py` | Engine matrix founder_busy/absent |
| `FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md` | Autorun MUST OFF when busy |

### 2.3 Conduct audit

| Asset | Role |
|-------|------|
| `SOURCEA_CONDUCT_AND_POISONED_LOOP_AUDIT_PROMPT_LOCKED_v2.md` | BLOCK A/B/C/D |
| `~/.sina/agent-governance-events.jsonl` | ASF_WILL_VIOLATION events |
| INCIDENT-015-CONDUCT LOCKED report | Disk SSOT |

### 2.4 Verified live state (2026-06-10 post-freeze)

- ~596/1000 honest · flag ON · no drain PIDs · BIND OK · dual_proof OK

---

## 3. Critical gaps (why 015 can repeat tomorrow)

| Gap | Evidence | Severity |
|-----|----------|----------|
| `worker_healthy_pack_autodrain_v1.py` — no kill-flag at entry | grep empty | **P0** |
| `worker_healthy_pack_loop_v1.py` — no kill-flag at entry | grep empty | **P0** |
| `goal1_auto_run_v1.py` — no kill-flag at entry | grep empty | **P0** |
| STOP lexicon — no spawn blocker in `cursor_entry_gate` | no hook | **P0** |
| `start-sourcea.sh` removes kill flag | `rm -f` line | **P1** |
| Plan todos not cancelled on STOP | Cursor runtime | **P1** |
| No `validate-stop-supremacy-v1.sh` in `find_critical_bugs` | missing | **P0** |
| Resume without `founder-resume-drain-v1.json` token | missing | **P1** |
| No atomic `factory-now-v1.json` | plural SSOT | **P0** |

---

## 4. Layer 0 — Kill SSOT

### 4.1 Files

| File | Meaning |
|------|---------|
| `~/.sina/auto-run-disabled-v1.flag` | Drain/autorun **forbidden** |
| `~/.sina/founder-stop-receipt-v1.json` | Last STOP event |

### 4.2 Stop receipt schema

```json
{
  "schema": "founder-stop-receipt-v1",
  "at": "2026-06-10T08:42:13Z",
  "chat_id": "fd67502f-5f95-43b8-bdfc-f2dba306f828",
  "trigger": "stop all loop and run",
  "cleared_by_asf": false,
  "cleared_at": null,
  "law": "ASF_ORDER > plan todo"
}
```

### 4.3 Procedure (machine)

On founder message class `ASF_STOP`:

1. `stop_goal1_auto_run_v1.py --json`
2. Write / update stop receipt (`cleared_by_asf: false`)
3. `touch auto-run-disabled-v1.flag`
4. Reply **second** — never spawn drain first

### 4.4 Resume procedure (ASF only)

Only when message matches `ASF: resume drain` (bounded):

1. Founder confirms disposition on any conduct window receipts (if pending)
2. Maintainer script writes `founder-resume-drain-v1.json` with `max_turns` · `max_packs` · `expires_at`
3. Clear stop receipt · remove flag **only** via this script — never `start-sourcea.sh` silent rm

---

## 5. Layer 1 — Spawn gates

### 5.1 Single function (new)

`scripts/factory_spawn_gate_v1.py`:

```python
def drain_spawn_allowed(*, caller: str) -> dict:
    """Return {ok: bool, reason: str, mode: str, ...}"""
```

**Reject if any:**

- `auto-run-disabled-v1.flag` present AND no valid `founder-resume-drain-v1.json`
- `founder-stop-receipt-v1.json` has `cleared_by_asf: false`
- `factory_mode_v1.json` mode not in (`SINGLE_SA`,) for drain callers
- `validate-healthy-pack-bind-v1.sh` would fail (pre-check)
- `operating_mode_enforce_v1.py` INVALID for act+worker

### 5.2 Wire at top of (mandatory)

- `worker_healthy_pack_autodrain_v1.py`
- `worker_healthy_pack_loop_v1.py`
- `goal1_auto_run_v1.py`
- `goal1_worker_batch_loop_v1.py`
- `healthy-drain-orchestrator-v1.py` (advance that spawns work)
- Hub action `founder-goal1-autorun-start` / START AUTO RUN
- `closeout_sa_task.py` batch paths (if any bulk entry remains)

### 5.3 Failure UX

Return JSON to hub/chat — never silent exit:

```json
{"ok": false, "blocked": true, "reason": "kill_flag", "action": "Hub Stop or ASF: resume drain"}
```

---

## 6. Layer 2 — Per-turn gates (poison state machine)

Inside each pack / turn iteration:

| Step | Check | On fail |
|------|-------|---------|
| 1 | Re-read kill flag | exit `STOPPED_BY_FLAG` |
| 2 | Re-read bind | heal once · else `poison_stall_v1.json` + FREEZE |
| 3 | Write `pack-NN.json` **before** chat +honest claim | visibility |
| 4 | Cap default `--max-turns` to **1** unless resume token | conduct |
| 5 | On `sa_mismatch` | set stall file · **no** auto-resume until ASF |

### 6.1 Poison stall file

`~/.sina/poison-stall-v1.json`:

```json
{
  "schema": "poison-stall-v1",
  "class": "sa_mismatch",
  "at": "...",
  "expected_sa": "sa-0500",
  "queue_sa": "sa-0502",
  "heal_required": true,
  "auto_resume_forbidden": true
}
```

Spawn gate reads this — blocks drain until heal + ASF clear.

---

## 7. Layer 3 — Session / lexicon gate

### 7.1 Classifier (new)

`scripts/founder_message_class_v1.py`:

| Class | Triggers |
|-------|----------|
| `ASF_STOP` | stop · halt · stop all · why stuck · interrupt |
| `ASF_RESUME` | ASF: resume drain · resume healthy drain |
| `ASF_QUESTION` | why · what happened (no stop words) |
| `ASF_ORDER` | explicit bounded build/heal scope |
| `EDIT_ALLOWED` | EDIT ALLOWED: path |

### 7.2 Wire

- `cursor_entry_gate.py` — line 1 includes `founder_class=...`
- If `ASF_STOP` → next allowed shell class = **stop only** (Maintainer wrapper or agent rule)
- Cursor rule file: **STOP supersedes plan todos**

---

## 8. Layer 4 — Audit gates (find_critical_bugs critical)

| Validator (new or existing) | Proves |
|-----------------------------|--------|
| `validate-stop-supremacy-v1.sh` | All spawn sites call `drain_spawn_allowed` |
| `validate-factory-now-v1.sh` | `factory-now-v1.json` schema + rebuild hook exists |
| `validate-healthy-pack-bind-v1.sh` | existing |
| `validate-founder-agentic-commercial-policy-v1.sh` | flag exists |
| `validate-brain-sync-hooks-v1.sh` | existing |
| `validate-no-start-sourcea-clears-flag-v1.sh` | start script law |

**Law:** No incident class closed without matching validator in critical list.

---

## 9. Layer 5 — Hub truth

| UI state | Disk condition |
|----------|----------------|
| **FROZEN** | kill flag OR stop receipt uncleared |
| **RUNNING** | broker batch + PIDs + mode SINGLE_SA |
| **IDLE (honest)** | orch idle + flag + no PIDs — not “tap START” hero |

Stop icon must call stop API and flip UI to FROZEN with receipt id.

Progress card reads **`factory-now-v1.json` only** — not stale command-data built_at.

---

## 10. factory-now-v1 (Invariant 2 — ship spec)

### 10.1 Path

`~/.sina/factory-now-v1.json`

### 10.2 Schema

```json
{
  "schema": "factory-now-v1",
  "at": "ISO-8601Z",
  "valid_yes": 596,
  "backlog": 404,
  "brain_vy": 595,
  "dual_proof_ok": true,
  "mode": "FREEZE",
  "kill_flag": true,
  "stop_receipt_open": true,
  "queue_sa": "sa-0778",
  "inbox_sa": "sa-0778",
  "orchestrator": "idle",
  "orchestrator_status": "idle",
  "broker_status": "idle",
  "poison_stall": false,
  "live_pick": "sa-0101",
  "law": "cite this line only in chat"
}
```

### 10.3 Rebuild triggers

Atomic rewrite after:

- every VERIFY closeout
- every stop_goal1_auto_run
- every brain_sync light
- every mode change
- hub self_refresh

### 10.4 Chat law

**Never say “verified” or “N/1000” without quoting factory-now same turn.**

Template:

```text
factory-now · Valid YES {valid_yes} · brain {brain_vy} · dual_proof {dual_proof_ok} · mode {mode} · queue {queue_sa}
```

---

## 11. factory-mode-v1 (Invariant 1 — ship spec)

### 11.1 Path

`~/.sina/factory-mode-v1.json`

### 11.2 Default

```json
{"schema": "factory-mode-v1", "mode": "FREEZE", "since": "...", "set_by": "stop_goal1_auto_run"}
```

### 11.3 Transitions (ASF only)

| From | To | Requires |
|------|-----|----------|
| FREEZE | AUDIT | ASF: run conduct audit |
| FREEZE | SINGLE_SA | ASF: resume drain + resume token + cleared stop |
| * | SHIP_MAINTAINER | ASF: EDIT ALLOWED + bounded paths |
| SINGLE_SA | FREEZE | STOP · stall · visibility timeout · gate fail |

---

## 12. Maintainer ship order (P0 → P2)

| Phase | Deliverable | Kills |
|-------|-------------|-------|
| **P0a** | `factory_spawn_gate_v1.py` + wire autodrain/loop/auto_run | 015 spawn |
| **P0b** | `factory_now_v1.py` rebuild + hub/inject read | 013·014 |
| **P0c** | `founder-stop-receipt` + resume token | resume consent |
| **P0d** | `validate-stop-supremacy-v1.sh` → critical bugs | regression |
| **P1a** | Hub FROZEN banner + Stop responsiveness | false Idle |
| **P1b** | Visibility timeout → auto FREEZE | stuck UX |
| **P1c** | Fix `start-sourcea.sh` flag removal | silent re-arm |
| **P2a** | `founder_message_class_v1.py` in entry gate | conduct lexicon |
| **P2b** | Single queue SSOT collapse | 004·bind |

---

## 13. Founder must-do vs better-to-do

### Must-do (binding)

- [ ] Keep **FREEZE** until `ASF: resume drain — max N — receipt required`
- [ ] Disposition **packs 41–45** (accept / audit sample / rollback)
- [ ] Order Maintainer: **P0a–P0d** before any new architecture pitch
- [ ] Send external advisors **advisor brief** — forbid new D-modules + batch drain advice
- [ ] Never approve open-ended “complete all todos don’t stop” in Worker chat during meta questions

### Better-to-do (high leverage)

- [ ] Hub Refresh after any stop — confirm FROZEN state
- [ ] Sample audit 3 sas from pack 44 range skew before accept +69
- [ ] Close 015-ID separately — registry read law for all agents
- [ ] Rename Cursor plan todos to void on STOP (manual cancel today)

---

## 14. Self-healing mandatory checklist (machine targets)

| # | Detect | Auto act | Validator |
|---|--------|----------|-----------|
| 1 | kill flag missing while stop receipt open | touch flag + log | founder-policy |
| 2 | bind triple drift | heal or poison_stall + FREEZE | healthy-pack-bind |
| 3 | brain_vy ≠ live_vy | brain_sync on VERIFY | brain-snapshot-sync |
| 4 | silent drain >60s | FREEZE | pack-receipt-fresh (new) |
| 5 | sa_mismatch | poison_stall · no resume | spawn gate |
| 6 | spawn without gate | block + JSON reason | stop-supremacy |
| 7 | backlog_broker_pass >0 | hygiene ladder (existing) | monitor-honesty |
| 8 | mode SINGLE_SA without resume token | force FREEZE | factory-mode (new) |

---

## 15. Never-again card (agents)

```text
STOP words → stop_goal1_auto_run FIRST · reply SECOND · zero new drain shells
Plan todos DIE on ASF_STOP — mode FREEZE default
Progress = factory-now line only — never inject · never chat memory
No background pack_loop — foreground · max 1 turn · pack-NN.json visible
sa_mismatch → poison_stall — no auto-resume — wait ASF
Resume only: ASF: resume drain + founder-resume-drain token
015-CONDUCT ≠ 015-ID — cite correctly
```

---

## 16. Success criteria (permanent = measurable)

| Metric | Target |
|--------|--------|
| Spawn with flag ON | **0** successful autodrain starts (blocked JSON only) |
| STOP → next shell | **100%** stop script first (transcript audit) |
| Chat progress without factory-now | **0** in Worker/Brain status replies |
| Critical conduct validators | PASS in find_critical_bugs |
| Founder “stuck” reports during FREEZE | **0** drain PIDs (visibility only) |
| Repeat 015-class in 30 days | **0** without CRITICAL_RED_FLAG + gate patch |

---

**END** — SOURCEA_PERMANENT_CONDUCT_POISON_MACHINE_ENFORCEMENT_ESSAY_LOCKED_v1
