# Operating Model — pick + engine + mode SSOT (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**sequence_id:** SA-2026-06-08-FOUNDER-BUSY-OM-001  
**Authority:** ASF  
**SSOT pointer:** `FOUNDER_BUSY_OPERATING_MODEL_REPORT_LOCKED_v1.md`  
**Mechanism:** `scripts/operating_mode_enforce_v1.py`  
**Parent:** `GOAL_HIERARCHY_LOCKED_v1.md` · `SOURCEA_EXECUTION_LAW_LOCKED_v1.md` · `ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md`  
**Supersedes:** engine-pick by chat · advisor ROA reorder · “API replaces Worker” · “no Cursor ever” · “zero human in loop”

---

## 1. Scope

This file is **mandatory law** for:

- Brain · Worker · Gatekeeper scripts · Hub · CLI/API agents · autorun · founder (via Hub only)

**Function:** Given situation + role + task → return **allowed engine** or **INVALID**.  
**Output contract:** `VALID` | `INVALID` + `reason` — no planning · no redesign · no lane vote.

---

## 2. Authority stack (executable only)

| Level | SSOT | Governs |
|-------|------|---------|
| L0 | `brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md` | Tier order |
| L1 | `ACTIVE_NOW.md` | Scope this sprint |
| L2 | `~/.sina/healthy-queue-30-active.json` | Queue SSOT |
| L3 | One turn: one `sa_id` · one `queue_role` | Execution unit |
| L4 | `scripts/validate-*.sh` · `receipts/` · `WORKER_ROUND_REPORT` | DONE truth |

All other `.md` files = **reference** until cited by L0–L4 task.

**Gatekeeper (single command):** `python3 scripts/gatekeeper_v1.py`  
**Law:** `SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md`  

Sub-checks (internal only): `active_now_v1` · `execution_law_enforce` · `goal_hierarchy` · `operating_mode_enforce`

---

## 3. ACTIVE_NOW required fields

`ACTIVE_NOW.md` **MUST** contain:

| Field | Key | Values |
|-------|-----|--------|
| Current Goal | `goal` | From GOAL_HIERARCHY |
| Current Sprint | `sprint` | ASF-written |
| Founder Mode | `founder_mode` | `founder_busy` \| `founder_absent` |
| Current Queue | `queue` | Path + phase + sa range |
| Current sa_id | `sa_id` | `sa-XXXX` + role + pos/total |
| Current Blocker | `blocker` | Machine blocker or `none` |
| Forbidden | `forbidden` | Explicit out-of-scope list |

**Default Founder Mode:** `founder_busy` until ASF writes `founder_absent`.

**Parse:** `scripts/active_now_v1.py` — sole parser.

---

## 4. Founder modes (MUST)

### 4.1 `founder_busy`

| Rule | Enforcement |
|------|-------------|
| Autorun **MUST** be OFF | `~/.sina/auto-run-disabled-v1.flag` **OR** ACTIVE_NOW autorun off |
| ACT **MUST** use engine `worker` | `operating_mode_enforce_v1.py --check-engine --role act --engine worker` |
| CLI ACT **MUST NOT** run | `--role act --engine cli` → INVALID unless `worker_stuck_2x` |
| API ACT **MUST NOT** run | `--role act --engine api` → INVALID |
| Execution chain | `Brain paste → founder paste → Worker → validators → advance` |

### 4.2 `founder_absent`

| Rule | Enforcement |
|------|-------------|
| Autorun **MAY** run | Only if flag absent **AND** ACTIVE_NOW = `founder_absent` |
| CHECK **SHOULD** use `api` (Haiku) | Allowed engines per §5 |
| ACT **SHOULD** use `cli` (Sonnet) | Allowed engines per §5 |
| Batch cap | ≤ 5 turns per kick — **MUST NOT** 90s retry spam |

---

## 5. Engine allowlist (MUST enforce)

Engines: `validators` · `worker` · `api` · `cli` · `brain_route`

### 5.1 `founder_busy`

| `queue_role` | Allowed engines | Forbidden engines |
|--------------|-----------------|-------------------|
| `check` | `worker`, `api`, `validators` | — |
| `act` | `worker` | `api`, `cli`* |
| `verify` | `worker`, `validators`, `api` | — |
| `route` / `infra` | `brain_route` | `api`, `cli` for sa build |

\* `cli` allowed only when `worker_stuck_2x=true` on same `sa_id`.

### 5.2 `founder_absent`

| `queue_role` | Allowed engines | Forbidden engines |
|--------------|-----------------|-------------------|
| `check` | `api`, `worker`, `validators` | — |
| `act` | `cli`, `worker` | `api` |
| `verify` | `validators`, `api`, `worker` | — |

### 5.3 Global engine rules (both modes)

| Rule | |
|------|--|
| `api` + `act` | **ALWAYS INVALID** — no file tools |
| `validators` | **ONLY** progress authority for PASS/FAIL |
| AI on CHECK | Report gaps only — **MUST NOT** mark DONE |
| `brain_route` | **MUST NOT** implement `sa-XXXX` logged |

---

## 6. Situation → pick (lookup)

| # | Condition | Mode | CHECK | ACT | VERIFY | Autorun |
|---|-----------|------|-------|-----|--------|---------|
| S1 | Founder at desk, paste available | busy | worker \| api | **worker** | worker + validators | OFF |
| S2 | Founder at desk, bulk CHECK only | busy | api | worker | validators | OFF |
| S3 | Founder away, mechanical sa | absent | api | cli | validators | ON† |
| S4 | Worker failed same sa 2× | either | per §5 | **cli** | validators | per mode |
| S5 | `live_eval_required` + OpenRouter blocked | either | skip slice | disk-only ACT | structural validators | per mode |
| S6 | `sa-05xx` or `phase-s5-commercial-lanes` default | either | **INVALID** | **INVALID** | — | OFF |
| S7 | Queue/broker/ACTIVE_NOW drift | either | **STOP** | **STOP** | — | OFF |
| S8 | Task outside ACTIVE_NOW goal | either | **INVALID** | **INVALID** | — | OFF |
| S9 | Greenfield / full-stack redesign request | either | **INVALID** | **INVALID** | — | OFF |

† ON only if §4.2 autorun conditions met.

**Queue pick order:** `sourcea_pick_lib.PHASE_ORDER` — `phase-s6-wtm-pre-llm` before `phase-s5-commercial-lanes`.

**Queue path:** `healthy_queue_ssot_lib.healthy_queue_path()` — `~/.sina` first.

---

## 7. Queue + phase rules (MUST)

| Rule | |
|------|--|
| Boss queue | `~/.sina/healthy-queue-30-active.json` |
| Repo commercial pack | `healthy-queue-30-active.PARALLEL_COMMERCIAL_QUARANTINED_v1.json` — **MUST NOT** be live default |
| One turn | One `sa_id` · one `queue_role` |
| Advance | **MUST NOT** without validator PASS + receipt |
| Commercial `sa-050x` | **MUST NOT** CLI/autorun default — INCIDENT-004 |

---

## 8. Role assignment (MUST)

| Role | Chat / component | Build sa? | Route? | Gate? |
|------|------------------|-----------|--------|-------|
| ASF | Hub only | No | Yes (scope) | Yes |
| Brain | SourceA Cursor | **No** | **Yes** | Yes |
| Worker | SourceA Cursor | **Yes** | No | No |
| Gatekeeper | Python scripts | No | No | **Yes** |
| API agent | `claude_api_agent_v1.py` | No (CHECK only) | No | No |
| CLI agent | `claude_code_agent_v1.py` | Yes (ACT) | No | No |

---

## 9. Mandatory hooks (MUST call before operate)

| Hook | Callers |
|------|---------|
| `active_now_v1.py --heartbeat` | Brain session · Worker session · CLI · API · orchestrator |
| `operating_mode_enforce_v1.py --check-situation` | Before paste batch · Hub “execute” · session start |
| `operating_mode_enforce_v1.py --check-engine` | Before each CLI/API turn |
| `operating_mode_enforce_v1.py --check-autorun` | `autorun_dispatcher` · `auto_run_worker_batch` · launchd |
| `execution_law_enforce_v1.py` | Every task bind |
| `goal_hierarchy_enforce_v1.py` | Pack generate · session-start validator chain |

**If any hook returns INVALID → execution MUST STOP.**

---

## 10. Receipt schema (MUST)

Every closeout **MUST** include:

```yaml
founder_mode: founder_busy | founder_absent
engine_used: worker | api | cli | validators_only
validation_passed: YES | NO
active_goal: <from ACTIVE_NOW>
active_queue: <from ACTIVE_NOW>
sa_id: <bound sa>
gatekeeper_status: VALID | INVALID
```

**DONE** only when `validation_passed: YES` from bash validators — not from LLM text.

---

## 11. Forbidden (MUST NOT)

- Ask founder to pick main-goal vs commercial when GOAL_HIERARCHY + ACTIVE_NOW apply  
- Promote `phase-s5-commercial-lanes` before `phase-s6-wtm-pre-llm` in pick order  
- Use repo queue as boss when `~/.sina` queue exists  
- Autorun as default in `founder_busy`  
- API for ACT turns  
- CLI Sonnet ACT in `founder_busy` without `worker_stuck_2x`  
- LLM-only VERIFY without `validate-*.sh`  
- Trust chat, screenshots, or advisor text over L0–L4 stack  

---

## 12. Validator (MUST pass in CI)

```bash
bash scripts/validate-founder-busy-operating-model-v1.sh
```

**Gate API:**

```bash
python3 scripts/operating_mode_enforce_v1.py --check-situation --json
python3 scripts/operating_mode_enforce_v1.py --check-engine --role <role> --engine <engine> --json
python3 scripts/operating_mode_enforce_v1.py --check-autorun --json
```

Return: `{"status":"VALID"|"INVALID", "reason":"..."}`

---

## 13. ASF change control

Only ASF **MAY** edit:

- `ACTIVE_NOW.md` — goal · sprint · founder_mode · queue · sa_id · blocker · forbidden  
- Autorun flag policy via Hub Action (executor applies `touch`/`rm` — founder never Terminal)

Agents **MUST NOT** change Founder Mode or scope without ASF order.

---

*End FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1*
