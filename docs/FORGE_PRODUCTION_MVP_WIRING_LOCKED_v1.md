# Forge Production MVP Wiring — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-25T02:51:34Z · **Authority:** ASF · Forge-first execution system  
**Path:** `docs/FORGE_PRODUCTION_MVP_WIRING_LOCKED_v1.md`  
**Parent:** `docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md` · `SOURCEA_FORGE_GOVERNANCE_KERNEL_V2_LOCKED_v1.md`  
**Advisor alignment:** Forge = execution system · Cursor = IDE only · no v6/v7/v8 conceptual layers in production path

---

## One law

> **Forge Production MVP = one real queue · one real worker · one real governance gate · one real state store · one real API.**  
> Cursor observes and edits code; **Forge runs tasks.**

Mac = control panel only (`CLOUD_ONLY` muscle). All queue consumers and task execution run on **Railway / FBE cloud**.

---

## Strategic decision (locked)

| Path | Status |
|------|--------|
| **Correct — build product** | Forge = runtime + API + worker + governance + state |
| **Wrong — infinite abstraction** | v6/v7/v8 civilization · multi-nation simulation · recursive self-writing without queue receipts |

**Relationship to existing blueprint:** `FORGE_MVP_BLUEPRINT_LOCKED_v1.md` covers the **LLM DAG router** (plan → route → sandbox → critic). This doc covers the **execution OS layer underneath** — queue intake, governance gate, worker execution, canonical state. Router DAG mounts **on top** of this loop in a later slice; do not merge the two into one conceptual stack.

---

## Phase 0 — Freeze architecture

### Governance kernel (lock v2 production · v3 advisory)

| Layer | Law | Runtime |
|-------|-----|---------|
| **v2 (production gate)** | `SOURCEA_FORGE_GOVERNANCE_KERNEL_V2_LOCKED_v1.md` | `scripts/forge_governance_kernel_v1.py` (`GOVERNANCE_VERSION=v2`) |
| **v3 (legal arbitration)** | `SOURCEA_FORGE_GOVERNANCE_KERNEL_V3_LOCKED_v1.md` | `scripts/forge_governance_legal_v3.py` — **conflict-only**; not on hot path for MVP |
| Economy | v2 companion | `scripts/forge_economy_v1.py` · `~/.sina/forge-economy-v1.json` |
| Violations | shared | `~/.sina/forge-governance-violations-v1.jsonl` |
| Latest decision | shared | `~/.sina/forge-governance-latest-v1.json` |

**MVP hot path:** `govern(task)` → ALLOW | DENY | MODIFY (v2). Escalate to v3 only when rule conflict is detected.

### Prompt OS compiler (real module · no autonomous dispatch)

| Version | Script | Role in MVP |
|---------|--------|-------------|
| v1 core | `scripts/forge_prompt_os_compiler_v1.py` | Schema + compile primitives |
| v2 adaptive | `scripts/forge_prompt_os_compiler_v2.py` | Outcome recording |
| v3 runtime | `scripts/forge_prompt_os_compiler_v3.py` | **Importable module only** — called by worker after governance ALLOW |

**Receipt:** `~/.sina/forge-prompt-os-compiler-latest-v1.json`  
**Law:** `SOURCEA_FORGE_PROMPT_OS_COMPILER_V3_LOCKED_v1.md`

`autonomous_execute` and `compile_and_dispatch_hint` from v3 are **disabled by default** in production MVP. Worker invokes `compile_prompt` explicitly per task.

### Self-building mode (off by default)

| Resource | Address |
|----------|---------|
| Script | `scripts/forge_self_build_v1.py` |
| Law | `SOURCEA_FORGE_SELF_BUILD_STACK_LOCKED_v1.md` |
| Receipt | `~/.sina/forge-self-build-latest-v1.json` |

**Default:** `dry_run=true`. Manual trigger only: founder flag `FORGE_SELF_BUILD_ARMED=1` + explicit CLI. Never on cron or queue consumer boot.

---

## Phase 1 — Three production services

### A) `forge-core-api`

**Job:** Task intake · agent execution dispatch · state read/write HTTP surface.

| Endpoint (MVP) | Method | Purpose |
|----------------|--------|---------|
| `/health` | GET | Liveness |
| `/tasks` | POST | Enqueue task (validates schema → Redis) |
| `/tasks/:id` | GET | Task status + result pointer |
| `/state/:run_id` | GET | Canonical run snapshot |
| `/agents` | GET | Registry read |
| `/governance/check` | POST | Dry-run govern (debug only; worker uses internal call) |

**Deploy target:** Railway service `forge-core-api` (Node Hono or Python FastAPI — pick one per implement slice; Hono preferred for shared TS types with worker).

### B) `forge-worker`

**Job:** Queue consumer · governance gate · task execution · state update.

| Concern | Choice |
|---------|--------|
| Queue | **BullMQ** on Redis (MVP) · CF Queues deferred |
| Consumer | Single worker process per Railway replica (scale horizontally later) |
| Execution stub (slice 1) | Write receipt JSON + mark task `completed` |
| Execution real (slice 2) | Delegate to FBE `POST /api/fbe/run-forge/v1` |

**Deploy target:** Railway service `forge-worker` (separate process from API).

### C) `forge-governance`

**Job:** Thin HTTP + library wrapper around existing kernel — rule check · cost debit · permission · audit log.

| Surface | Behavior |
|---------|----------|
| `POST /govern` | Wrap `forge_governance_kernel_v1.govern()` |
| Audit | Append `~/.sina/forge-governance-violations-v1.jsonl` |
| Cost | Debit via `forge_economy_v1.py` when `dry_run=false` |

**MVP:** Can ship as Python subpackage inside `apps/forge-governance/` calling existing scripts via subprocess or import — no rewrite of kernel logic.

---

## Phase 2 — Single truth system

Canonical package root (shared types + disk layout contract):

```text
apps/forge-core/
  state/           # run snapshots · task outcomes (schema SSOT)
  registry/        # agents · tools · roles
  tasks/           # task envelope schema · queue job shape
  agents/          # agent registry contract
  governance/      # decision schema · ALLOW/DENY types
  package.json     # @sourcea/forge-core
  src/
    index.ts       # re-exports
    schemas/       # Zod: ForgeTask, ForgeRunState, GovernDecision
```

**Runtime state paths (MVP — file-backed; Supabase slice 3):**

| Path | Purpose |
|------|---------|
| `~/.sina/forge-core/state/` | Per-run JSON snapshots |
| `~/.sina/forge-core/tasks/` | Task ledger (append) |
| `~/.sina/forge-core/registry/agents.json` | Agent registry |
| `receipts/forge-core/ledger.jsonl` | Cross-run audit trace |

**Rule:** API and worker both read/write through `apps/forge-core` schemas — no ad-hoc task shapes in service code.

---

## Phase 3 — Paused layers (explicit defer)

Do **not** wire these into the production MVP loop:

| Layer | Script / doc | Reason |
|-------|--------------|--------|
| v6 world simulation | `scripts/forge_world_state_v1.py` | Stub only · not production geopolitics |
| v7/v8 consciousness | `scripts/forge_reality_consciousness_v8.py` | Conceptual · no queue value |
| Multi-civilization | `SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md` | Terminal narrative only |
| Recursive self-writing | `forge_self_build_v1.py` without founder arm | Unbounded · no governance receipt |
| Cursor-as-orchestrator | Chat memory as task queue | Violates golden rule — state is canonical |

**Terminal UI stays:** `apps/forge-terminal-v1/` · `apps/forge-terminal-connect-v1/` — observe + submit tasks via API; not the execution body.

---

## MVP runtime loop (canonical)

```typescript
// apps/forge-worker/src/loop.ts — behavioral contract
while (true) {
  const task = await queue.pull();           // BullMQ: forge-tasks
  const decision = await governance.check(task);

  if (decision.allow) {
    const compiled = await compiler.compile(task);  // optional per task.kind
    const result = await worker.execute(task, compiled);
    await state.update(task.run_id, result);
    await queue.ack(task);
  } else {
    await audit.log(task, decision);
    await queue.nack(task, { deadLetter: false });
  }
}
```

**Success criteria (slice 1):** One `POST /tasks` → Redis job → worker ALLOW → `~/.sina/forge-core/state/<run_id>.json` written → `GET /tasks/:id` returns `status: completed` with receipt path.

---

## Repo layout (implement target)

```text
apps/
  forge-core/                 # shared schemas + state contract
  forge-core-api/             # HTTP intake + state API
  forge-worker/               # BullMQ consumer + execute loop
  forge-governance/           # govern() service wrapper

infra/
  forge-mvp/
    docker-compose.yml        # Redis only (local dev)
    railway.toml              # multi-service deploy hints

data/schemas/
  forge-task-v1.json          # machine SSOT (emit from Zod)
  forge-run-state-v1.json
  forge-govern-decision-v1.json

scripts/
  forge_mvp_loop_smoke_v1.py  # submit → poll → assert receipt (≤90s)
  validate-forge-production-mvp-v1.sh
```

**Existing scripts reused (no rewrite):**

| Concern | Existing |
|---------|----------|
| Governance | `forge_governance_kernel_v1.py` |
| Economy | `forge_economy_v1.py` |
| Compiler | `forge_prompt_os_compiler_v3.py` (`compile_prompt` only) |
| Cloud execute | `portfolio_competitor_forge_dispatch_v1.py` · FBE runner |
| Trace | `fbe_forge_lib_v1.py` ledger pattern |

---

## Queue system (BullMQ + Redis)

| Setting | Value |
|---------|-------|
| Queue name | `forge-tasks` |
| Job name | `forge.task.execute` |
| Payload | `ForgeTask` schema from `apps/forge-core` |
| Retry | 3 attempts · exponential backoff |
| DLQ | `forge-tasks-dlq` after exhaust |
| Idempotency | `task.id` = UUID v4 · dedupe key `run_id` |

**Local dev only:**

```bash
docker compose -f infra/forge-mvp/docker-compose.yml up -d redis
export REDIS_URL=redis://127.0.0.1:6379
```

**Production:** Railway Redis add-on or Upstash — never Mac-body queue consumer under founder session freeze.

---

## Task envelope (minimal schema)

```json
{
  "schema": "forge-task-v1",
  "id": "task-uuid",
  "run_id": "run-uuid",
  "kind": "execute_stub | fbe_forge | compile_only",
  "agent_id": "forge-worker-1",
  "role": "builder",
  "payload": {
    "prompt": "optional",
    "work_order_id": "optional-fbe-ref"
  },
  "created_at": "2026-06-25T02:51:34Z"
}
```

Governance checks: `role` permissions · action cost · reputation tier (v2).

---

## Implement slices (ordered)

| # | Slice | Status | Deliverable |
|---|-------|--------|---------------|
| 0 | Freeze doc | **DONE** | This file |
| 1 | `apps/forge-core` schemas | NEXT | Zod + JSON SSOT |
| 2 | Redis + BullMQ wiring | NEXT | `infra/forge-mvp/docker-compose.yml` |
| 3 | `forge-core-api` POST/GET tasks | NEXT | Working enqueue |
| 4 | `forge-worker` stub loop | NEXT | ALLOW → state write |
| 5 | `forge-governance` wrapper | NEXT | v2 govern on hot path |
| 6 | Smoke script | NEXT | `forge_mvp_loop_smoke_v1.py` PASS |
| 7 | FBE delegate | DEFER | `kind: fbe_forge` in worker |
| 8 | Router DAG mount | DEFER | `FORGE_MVP_BLUEPRINT` stage 3–7 on queue |
| 9 | Supabase state | DEFER | Replace file state for multi-tenant |

---

## Mac vs cloud boundary

| Surface | Mac | Cloud |
|---------|-----|-------|
| Submit task (observe) | Hub or `curl` to Railway API | `forge-core-api` |
| Queue consumer | **Forbidden** | `forge-worker` |
| Governance kernel test | `dry_run=true` read-only | production debits |
| Smoke script | ≤90s one-shot | full loop against Railway URL |
| Terminal UI | `apps/forge-terminal-connect-v1/` | calls cloud API |

**Law:** `mac-control-plane.mdc` · `FORGE_MVP_BLUEPRINT` § Mac observe only.

---

## Verify this wiring

```bash
bash scripts/validate-doc-datetime-header-v1.sh docs/FORGE_PRODUCTION_MVP_WIRING_LOCKED_v1.md
# After slice 6 ships:
bash scripts/validate-forge-production-mvp-v1.sh
python3 scripts/forge_mvp_loop_smoke_v1.py --base-url "$FORGE_CORE_API_URL" --json
```

---

## Plain test

Founder can: submit one task → see governance ALLOW/DENY receipt → see state file or API response → **without** Cursor chat being the queue and **without** v6/v8 scripts on the hot path.

If the loop does not run on cloud with a real Redis job, the Production MVP is not done — regardless of terminal UI or compiler version number.
