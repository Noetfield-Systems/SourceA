# Forge MVP Blueprint — LOCKED v0.1

**Version:** 0.1.0 · **Saved:** 2026-06-20T17:14:30Z · **Authority:** ASF · forge mvp blueprint  
**Path:** `docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md`  
**Machine SSOT:** `data/forge-mvp-router-rules-v0.1.json` · `data/schemas/forge-task-graph-v0.1.json`

---

## One law

> **Forge = LLM router + execution sandbox + trace loop.**  
> Revenue and product value come from the **loop**, not from picking a single model.

Mac = control panel only. All build muscle runs on **Railway FBE / FORGE cloud** (`CLOUD_ONLY`).

---

## What companies actually run (2026 pattern)

Comparable motion (Cursor · Replit Agent · Cognition-style · Vercel AI SDK shops):

| Layer | Real stack |
|-------|------------|
| Core inference | OpenAI (control) · Claude (code) · Gemini (context) |
| Cheap scale | OpenRouter → DeepSeek · Llama · Mixtral for bulk / parallel |
| Router | Task-kind rules + cost caps (LangGraph-style DAG dispatch) |
| Execution | Node / Python FastAPI sandbox on cloud (not Mac body) |
| Observability | JSONL traces · per-request cost · eval / critic pass-fail |

SourceA wires this through **FBE factory_3** · bay `forge-bay` · template `forge-app-factory-v1`.

---

## Forge execution loop (7 stages)

```text
INPUT (raw prompt)
  → 1 REASONING     intent · constraints · entities · risk (no routing yet)
  → 2 PLANNING      TASK GRAPH DAG (forge-task-graph-v0.1)
  → 3 ROUTING       assign model lane per task (forge-mvp-router-rules-v0.1)
  → 4 EXECUTION     workers: code · patch · API · files (cloud sandbox)
  → 5 VERIFICATION  critic: intent match · runs · UI · cost cap
  → 6 AGGREGATION   merge task outputs → artifact + preview URL
  → 7 META LOOP     on fail: replan · reroute · retry (cap 2)
```

**Value is in:** (1) task decomposition, (2) routing intelligence, (3) verification loop — not in branding a model.

---

## MVP model table (use now)

| Role | Route key | Provider | Model (MVP) |
|------|-----------|----------|-------------|
| Bulk / parallel | `openrouter_bulk` | OpenRouter | DeepSeek V3 · Llama 3.1 70B |
| Code quality | `claude_code` | Anthropic | Claude Sonnet 4 |
| Control / critic | `gpt_control` | OpenAI | GPT-4.1 mini |
| Long context / research | `gemini_context` | Google | Gemini 2.0 Flash |
| Run / deploy | `sandbox` | FBE cloud | forge-bay pipeline |

Full rules: `data/forge-mvp-router-rules-v0.1.json`

---

## Task graph schema

Planning layer emits JSON matching `data/schemas/forge-task-graph-v0.1.json`.

Minimal example (1 prompt → landing + pricing):

```json
{
  "schema": "forge-task-graph-v0.1",
  "version": "0.1.0",
  "run_id": "forge-run-demo",
  "prompt": {
    "raw": "Landing page with pricing table and CTA",
    "intent": "ship_minimal_marketing_page"
  },
  "tasks": [
    {"id": "T1", "kind": "research", "route_hint": "gemini_context"},
    {"id": "T2", "kind": "code_gen", "depends_on": ["T1"], "route_hint": "claude_code"},
    {"id": "T3", "kind": "ui_gen", "depends_on": ["T2"], "route_hint": "openrouter_bulk"},
    {"id": "T4", "kind": "validate", "depends_on": ["T3"], "route_hint": "sandbox"},
    {"id": "T5", "kind": "deploy", "depends_on": ["T4"], "route_hint": "sandbox"},
    {"id": "T6", "kind": "evaluate", "depends_on": ["T5"], "route_hint": "gpt_control"}
  ],
  "edges": [
    {"from": "T1", "to": "T2"},
    {"from": "T2", "to": "T3"},
    {"from": "T3", "to": "T4"},
    {"from": "T4", "to": "T5"},
    {"from": "T5", "to": "T6"}
  ]
}
```

---

## Router rules (dispatch only — no thinking)

| Task kind | Route |
|-----------|-------|
| research | Gemini |
| code_gen · patch | Claude |
| ui_gen | OpenRouter cheap |
| validate · deploy | FBE sandbox |
| evaluate · aggregate | GPT critic |

Competitor-1000 workstream hints (from pick scripts):

| Workstream | Default route |
|------------|---------------|
| ws-ux | OpenRouter bulk |
| ws-pricing | Gemini (evidence capture) |
| ws-run | Claude (run detail UI) |
| ws-onboard | GPT (flow / checklist) |
| ws-integrate | Claude (API / adapter) |

---

## Sandbox execution API (cloud — already on disk)

| Surface | Path |
|---------|------|
| Hub POST | `POST http://127.0.0.1:13020/api/fbe/run-forge/v1` |
| Cloud worker | `POST {FBE_CLOUD_WORKER_URL}/api/fbe/run-forge/v1` |
| Body | `{ "bay_slug": "forge-bay", "template_id": "forge-app-factory-v1", "tenant": "forge", "work_order_id": "<plan-id>", "execution_mode": "CLOUD_ONLY" }` |
| Config SSOT | `data/fbe_cloud_worker_config_v1.json` |
| Factory spec | `data/factory-specs/forge-app-factory-v1.json` |
| Execution contract | `data/fbe_execution_contract_v1.json` |

**Forge pipeline steps (W5):**

Refinery: `forge-orient-v1` → `forge-scaffold-v1` → `forge-inbox-gate-v1`  
Assembly: `forge-deploy-pack-v1` → `forge-verify-job-v1`

Runner: `scripts/fbe_forge_runner_v1.py` · dispatch helper: `scripts/portfolio_competitor_forge_dispatch_v1.py`

---

## Trace system (MVP receipts)

| File | Purpose |
|------|---------|
| `receipts/bays/forge-bay/refinery/ledger.jsonl` | Step-level refinery trace |
| `receipts/bays/forge-bay/assembly/ledger.jsonl` | Assembly trace |
| `~/.sina/fbe-forge-run-receipt-v1.json` | Last forge run |
| `~/.sina/fbe-forge-verify-receipt-v1.json` | Verify PASS/FAIL |
| `~/.sina/fbe-cloud-adapter-receipt-v1.json` | Cloud dispatch receipt |
| `data/schemas/run-receipt-output-v1.json` | Output schema (G0–G3) |

MVP adds (next implement slice): `receipts/bays/forge-bay/trace/cost.jsonl` · `eval.jsonl` per run_id.

---

## Critic prompts (verification layer)

**Intent match (T6 evaluate):**

```text
Given original intent: {intent}
And artifact summary: {artifact_summary}
And preview URL: {preview_url}
Answer: PASS or FAIL
If FAIL: one concrete fix task for the DAG replanner.
Do not rename product concepts — use buyer-visible words only.
```

**Cost gate:**

```text
Run cost USD: {cost} · cap: {cap}
If over cap: FAIL with reroute to openrouter_bulk for non-critical tasks.
```

---

## One prompt → one app → preview URL (demo pipeline)

### Step 0 — Mac (observe only)

```bash
bash ~/Desktop/SourceA/scripts/plan-competitor-mkt-run.sh pick sourcea 1
# or any stack: virlux | witnessbc | noetfield | trustfield
```

### Step 1 — Dry-run FORGE envelope

```bash
bash ~/Desktop/SourceA/scripts/plan-competitor-mkt-run.sh dispatch-forge sourcea --dry-run
```

### Step 2 — Live cloud dispatch

Set worker URL (once, in `~/.sourcea-secrets` or shell):

```bash
export FBE_CLOUD_WORKER_URL="https://sourcea-fbe-runner-production.up.railway.app"
export FBE_INTERNAL_SECRET="<from secrets>"
python3 ~/Desktop/SourceA/scripts/portfolio_competitor_forge_dispatch_v1.py \
  --stack sourcea --mode railway_fbe --json
```

### Step 3 — Verify receipt

```bash
python3 ~/Desktop/SourceA/scripts/fbe_verify_forge_v1.py --bay forge-bay --json
bash ~/Desktop/SourceA/scripts/validate-fbe-w5-v1.sh
```

### Step 4 — Glance

- Hub: `GET http://127.0.0.1:13020/api/fbe/forge/v1?bay_slug=forge-bay`
- Proof class: G0–G3 · `deliveryMode: prove_only` until founder promotes tier

**Demo success criteria:** one `work_order_id` · forge run receipt `ok: true` · verify receipt `ok: true` · artifact path under `receipts/bays/forge-bay/` · honest `mock_only` label if not live URL yet.

---

## Revenue loop (why buyers pay)

```text
user prompt → generate app → run in sandbox → deploy preview → iterate
```

Each iteration = metered cost + delivered artifact. Forge bills the **loop**, not token vanity.

---

## NOT in MVP (explicit defer)

- Local models on Mac
- Custom LLM training
- Multi-agent chat without DAG
- Heavy infra redesign
- Mac-body docker Cloud Forge Run (Mac Law blocks under freeze)

---

## Wiring map (portfolio competitor 1000)

| Stack | Tenant | Pick |
|-------|--------|------|
| SourceA | forge | `pick-sourcea-competitor-mkt-plan.py` |
| WitnessBC | witnessbc | `pick-witnessbc-competitor-mkt-plan.py` |
| Noetfield | noetfield | `pick-noetfield-competitor-mkt-plan.py` |
| TrustField | trustfield | `pick-trustfield-competitor-mkt-plan.py` |
| VIRLUX | virlux | `pick-virlux-competitor-mkt-plan.py` |

Manifest: `data/portfolio-competitor-1000-manifest-v1.json` · 5000 plans · generator v2.

---

## Next implement slices (shipped v0.1 — 2026-06-20)

| Step | Status | Script |
|------|--------|--------|
| 1 Baseline gate | **DONE** | `scripts/validate-forge-mvp-baseline-v1.sh` |
| 2 Cloud env loader | **DONE** | `scripts/forge_cloud_env_load_v1.py` |
| 3 Trace JSONL | **DONE** | `fbe_forge_lib_v1.py` + `fbe_forge_runner_v1.py` |
| 4 Task graph emitter | **DONE** | `scripts/forge_task_graph_emit_v01.py` |
| 5 Dispatch payload | **DONE** | `portfolio_competitor_forge_dispatch_v1.py` + `cloud_adapter_v1.py` |
| 6 Router executor | **DONE** | `scripts/forge_router_execute_v01.py` |
| 7 Critic replan | **DONE** | `scripts/forge_critic_loop_v01.py` |
| 8 Preview URL Hub | **DONE** | `fbe_forge_deploy_pack_v1.py` + `fbe_hub_projection_v1.py` |
| 9 Hub one-tap | **DONE** | `POST /api/fbe/forge-competitor-run/v1` + `forge_competitor_run_v1.py` |
| 10 Closeout fleet | **DONE** | `forge_competitor_closeout_v1.py` + `validate-forge-mvp-fleet-v1.sh` |

Verify fleet:

```bash
bash ~/Desktop/SourceA/scripts/validate-forge-mvp-fleet-v1.sh
bash ~/Desktop/SourceA/scripts/validate-forge-mvp-hub-action-v1.sh
```

---

## Verify this blueprint

```bash
bash ~/Desktop/SourceA/scripts/validate-doc-datetime-header-v1.sh docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md
bash ~/Desktop/SourceA/scripts/plan-competitor-mkt-run.sh validate
python3 -c "import json; json.load(open('data/forge-mvp-router-rules-v0.1.json')); json.load(open('data/schemas/forge-task-graph-v0.1.json')); print('schemas ok')"
```

---

**Plain test:** If a founder cannot go from one pick → cloud dispatch → receipt PASS without opening Terminal for factory muscle, the MVP is not done yet.
