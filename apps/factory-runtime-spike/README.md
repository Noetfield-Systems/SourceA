# Factory Runtime Spike — Temporal + LangGraph + MAF embed

**Saved:** 2026-06-24T22:00:00Z  
**Authority:** `docs/SOURCEA_RUNTIME_STACK_HYBRID_LOCKED_v1.md` · `docs/SOURCEA_MICROSOFT_AGENT_FRAMEWORK_MAF_LOCKED_v1.md`  
**Status:** Spike / reference — not production FBE replacement

## Purpose

Minimal **Intent → LangGraph gate → PASS/BLOCK → receipt** chain for one PureFlow-class factory job.

Optional **MAF hybrid** embed: critic boot → MAF workflow sim → SourceA validate gate → receipt.

- **`dry_run_v1.py`** — Mac-safe proof without Temporal server (sequential activity simulation).
- **`worker_v1.py`** — Temporal worker when `TEMPORAL_HOST` is set (cloud / CI).

## Quick start (dry-run)

```bash
cd ~/Desktop/SourceA
pip install -r apps/factory-runtime-spike/requirements.txt
python3 apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py --fixture pureflow --json
```

**MAF hybrid embed (deterministic sim — no MAF SDK):**

```bash
python3 apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py \
  --fixture pureflow --embed maf --json
```

**Forge advisor embed (Mac-safe dry_run):**

```bash
python3 apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py \
  --embed advisor --prompt "Ship PureFlow landing proof" --json
```

Receipt: `~/.sina/factory-runtime-spike-receipt-v1.json`

## Temporal worker (optional)

```bash
export TEMPORAL_HOST=127.0.0.1:7233
export TEMPORAL_TASK_QUEUE=sourcea-factory-spike-v1
python3 apps/factory-runtime-spike/factory_runtime_spike/worker_v1.py
```

In another terminal (with `temporal` CLI + server running):

```bash
python3 apps/factory-runtime-spike/factory_runtime_spike/start_workflow_v1.py --fixture pureflow --json
```

## Layout

| File | Role |
|------|------|
| `langgraph_gate_v1.py` | StateGraph: intake → plan → validate → receipt |
| `maf_workflow_v1.py` | MAF factory graph: offer_engineer → fan-out assets → fan-in → checkpoint → observability |
| `critic_boot_stub_v1.py` | SourceA pre-flight PASS/BLOCK stub |
| `activities_v1.py` | Activity bodies (shared by dry-run + Temporal) |
| `workflow_v1.py` | Temporal `FactoryJobWorkflow` |
| `dry_run_v1.py` | Local proof runner |
| `worker_v1.py` | Temporal worker |
| `start_workflow_v1.py` | Start workflow client |

## Law

- Factory isolated under `apps/factory-runtime-spike/` — no cross-imports from other factories.
- No Mac validator marathon — dry-run only on founder session.
