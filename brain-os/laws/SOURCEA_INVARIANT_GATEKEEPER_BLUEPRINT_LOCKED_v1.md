# Invariant + Gatekeeper — 7-day SSOT blueprint (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**sequence_id:** SA-2026-06-08-INVARIANT-GK-001  
**Authority:** ASF  
**Pointer:** `SOURCEA_INVARIANT_GATEKEEPER_REPORT_LOCKED_v1.md`  
**Mechanism:** `scripts/gatekeeper_v1.py` · `scripts/sourcea_execute_v1.py`

---

## 1. The invariant (MUST)

```text
No execution unless:
  ACTIVE_NOW  ∧  QUEUE  ∧  GOAL_HIERARCHY  ∧  EXECUTION_LAW  = aligned
```

**Violation → HARD STOP → EXECUTION DENIED** — no LLM override.

---

## 2. Authority stack (frozen)

| Level | SSOT | Editor |
|-------|------|--------|
| L0 | `GOAL_HIERARCHY_LOCKED_v1.md` · `SOURCEA_EXECUTION_LAW_LOCKED_v1.md` | ASF only |
| L1 | `ACTIVE_NOW.md` | ASF · Hub Action |
| L2 | `~/.sina/healthy-queue-30-active.json` + `healthy-queue-state-v1.json` | queue scripts only |
| L3 | Executor (`worker` · `cli` · `api`) | Gatekeeper PASS only |
| L4 | `scripts/validate-*.sh` · receipts | bash only |

**MUST NOT:** chat · LLM · manual JSON edit for L0–L2 truth.

---

## 3. Role rename (MUST use function names)

| Function | Component | Decides execution? |
|----------|-----------|-------------------|
| **Strategist** | Brain chat | No — route + paste only |
| **Executor** | Worker · CLI · API | No — runs after PASS |
| **Gatekeeper** | `gatekeeper_v1.py` | **Yes** — deterministic only |

**MUST NOT:** “Old Brain” / “New Brain” as authority labels.

---

## 4. Gatekeeper contract (MUST)

**Command:**

```bash
python3 scripts/gatekeeper_v1.py [--role R] [--engine E] [--sa ID]
```

**PASS output:**

```text
STATUS: PASS
Goal: …
Sprint: …
Queue: …
sa_id: …
SAFE TO EXECUTE
```

**FAIL output:**

```text
STATUS: FAIL
Reason:
  - …
EXECUTION DENIED
```

**MUST:**

- Compare structured fields only  
- **MUST NOT** use LLM reasoning  
- **MUST NOT** interpret founder intent  
- Write `~/.sina/gatekeeper-receipt-v1.json` on PASS  

**Checks (in order):**

1. L0 law files exist  
2. `ACTIVE_NOW.md` parses  
3. Queue SSOT readable · not commercial default  
4. ACTIVE_NOW `sa_id` / pos == queue state  
5. `PHASE_ORDER` Pre-LLM before commercial  
6. `execution_law_enforce_v1.py` allowed  
7. `operating_mode_enforce_v1.py` if `--role` + `--engine`  
8. Broker expected_sa/pos == queue (optional `--no-broker`)  

---

## 5. Single execute entry (MUST)

```bash
python3 scripts/sourcea_execute_v1.py [--engine auto|worker|cli|api] [--dry-run]
```

**Flow:**

```text
gatekeeper_v1 → IF PASS → executor → receipt → state advance (existing scripts)
```

**MUST call Gatekeeper first:**

- `start_goal1_worker_turn_v1.py`  
- `claude_code_agent_v1.py`  
- `claude_api_agent_v1.py`  
- `autorun_dispatcher_v1.py`  
- Hub execute Actions (when wired)  

---

## 6. Receipt schema (MUST)

```json
{
  "sa_id": "sa-0153",
  "goal": "…",
  "active_now_match": true,
  "queue_match": true,
  "hierarchy_match": true,
  "execution_law": "YES",
  "gatekeeper_status": "PASS",
  "engine_used": "worker",
  "validation_passed": "YES"
}
```

**DONE** only when `validation_passed: YES` from bash validators.

---

## 7. Seven-day build map (aligned to disk reality)

| Day | Deliverable | Status on disk |
|-----|-------------|----------------|
| D1 | Freeze L0–L4 stack in law files | **SHIPPED** — GOAL_HIERARCHY · EXECUTION_LAW · OPERATING_MODEL |
| D2 | Unified `gatekeeper_v1.py` | **SHIPPED** |
| D3 | `sourcea_execute_v1.py` entry | **SHIPPED** — wraps existing executors |
| D4 | ACTIVE_NOW CPU register + parser | **SHIPPED** — `active_now_v1.py` |
| D5 | Queue machine-only SSOT | **SHIPPED** — `healthy_queue_ssot_lib.py` · advance scripts |
| D6 | Receipt envelope + validator chain | **PARTIAL** — `execution_law_enforce.receipt_envelope` · extend per sa |
| D7 | All paths call Gatekeeper first | **IN PROGRESS** — agents wired this sprint |

**MUST NOT:** greenfield rewrite · new agent personalities · delete existing validators.

---

## 8. Founder mode (from OPERATING_MODEL — binding)

| Mode | Executor default | Gatekeeper autorun rule |
|------|------------------|-------------------------|
| `founder_busy` | Worker ACT | autorun FAIL |
| `founder_absent` | CLI ACT · API CHECK | autorun MAY pass |

---

## 9. CI (MUST pass)

```bash
bash scripts/validate-gatekeeper-v1.sh
bash scripts/validate-founder-busy-operating-model-v1.sh
bash scripts/validate-execution-law-v1.sh
```

---

## 10. Forbidden (MUST NOT)

- Execute without `gatekeeper_v1.py` PASS  
- LLM as pass/fail validator  
- Chat edit of queue JSON  
- Skip Gatekeeper on “urgent” tasks  
- Swap model without invariant layer  

---

*End SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1*
