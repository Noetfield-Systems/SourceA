# SourceA Runtime Stack — Hybrid (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-06-24T18:00:00Z  
**Authority:** Advisor convergence · founder directive · disk honesty  
**Parents:** `docs/SOURCEA_REVENUE_ENGINE_V1_LOCKED_v1.md` · `brain-os/law/SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` · `data/fbe_execution_contract_v1.json`  
**Spike:** `apps/factory-runtime-spike/`

---

## 0. One law

> **Temporal durably orchestrates. LangGraph governs agent steps. Validators PASS/BLOCK. Receipts ship. Buyers hear outcomes — not workflow vocabulary.**

**External (buyers):** proof-backed business systems in 48 hours.  
**Internal (engineering):** Deterministic Business Operating System — Factory · Runtime · Proof.

---

## 1. Disk honesty (2026-06-24)

| Layer | Positioning on site | Production code today |
|-------|-------------------|------------------------|
| Temporal | ✅ Named (stack / portfolio) | 🟡 **Spike** — `apps/factory-runtime-spike/` |
| LangGraph | ✅ Named | 🟡 **Spike** — gate graph in spike |
| FBE / Cloud Forge Run | Internal motor | ✅ **Live** — current factory execution |
| Proof pack / validators | Public proof story | ✅ **Live** — scripts + gates |
| CrewAI / AutoGen | Not primary | ❌ Optional future **activity** embeds only |

**Law:** Do not tell prospects “we run on Temporal” until at least one client job completes through the hybrid path with a receipt on disk. Until then: “governed execution with PASS/BLOCK receipts.”

---

## 2. Layer map

```
┌─────────────────────────────────────────────────────────────┐
│  TEMPORAL — durable outer workflow (replay-safe orchestration) │
│  FactoryJobWorkflow: intake → plan → validate → receipt → out  │
└───────────────────────────┬─────────────────────────────────┘
                            │ Activities (non-deterministic I/O)
┌───────────────────────────▼─────────────────────────────────┐
│  LANGGRAPH — agent graph inside activities                     │
│  intake → plan → validate_gate → receipt                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  VALIDATORS — code/rules PASS/BLOCK (minimize LLM in gate)   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  PROOF — signed receipt JSON · replay · deploy artifact        │
└─────────────────────────────────────────────────────────────┘
```

**Optional embeds (not spine):**

| Tool | Layer | Use |
|------|-------|-----|
| **CrewAI** | Activity | Fast role crews — offer copy, report template drafts |
| **AutoGen / MAF** | Activity | Sandboxed codegen loops only |
| **n8n** | Delivery | Noetfield Intelligence client automations |

---

## 3. Chain (canonical)

**Intent → Temporal workflow → LangGraph activity → validators → gates → receipt → deployable output**

| Step | Owner | Deterministic? |
|------|-------|----------------|
| Workflow structure | Temporal | ✅ Replay-safe |
| LLM plan / copy | Activity (LangGraph node) | ❌ Probabilistic — isolated |
| Policy gate | Validator script | ✅ PASS/BLOCK |
| Receipt write | Activity | ✅ Signed artifact |
| Deploy | Activity | ❌ Side effect — retried by Temporal |

---

## 4. Hybrid patterns (locked)

### 4.1 Primary — LangGraph inside Temporal activities

- **Workflow** defines job phases (PureFlow-class: intake → assets → validate → receipt).
- Each heavy step is an **Activity**; planning/validation subgraph runs in **LangGraph** inside the activity.
- Temporal event history + receipt JSON = forensic proof.

### 4.2 Two-layer

| Layer | Responsibility |
|-------|----------------|
| Temporal | Long-running jobs, retries, human signals (approve deploy), audit history |
| LangGraph | Branching, loops, checkpoints within a phase |

### 4.3 When to add CrewAI

Inside a LangGraph node when **speed > control** for a subtask (e.g. generate three offer variants). Outer gate still **BLOCK**s if validator fails.

### 4.4 When to add AutoGen / MAF

Code-generation, M365/Copilot, or debate subtasks only — **inside one Temporal activity**. Never the outer orchestrator.

**Spike:** `dry_run_v1.py --embed maf` · `maf_workflow_v1.py` (deterministic sim).  
**Lock:** `docs/SOURCEA_MICROSOFT_AGENT_FRAMEWORK_MAF_LOCKED_v1.md` · registry `data/sourcea-runtime-embed-registry-v1.json`

---

## 5. Framework verdict (2026)

| Framework | SourceA role | Verdict |
|-----------|--------------|---------|
| **LangGraph + Temporal** | Runtime + Proof spine | **Primary** |
| **CrewAI** | Factory fast prototype inside activities | **Secondary** |
| **AutoGen / MAF** | Code/debate/M365 specialist nodes | **Tertiary** — spike `--embed maf` |
| **LangGraph alone** | Local dev / demos only | Pre-production |
| **CrewAI alone** | Vertical MVP sketch | Pre-governance |

---

## 6. Public vs internal vocabulary

| Say to buyers | Say internally |
|---------------|----------------|
| Proof-backed system | Deterministic validation |
| PASS / BLOCK before ship | Policy gate |
| Receipt you can replay | Temporal event history + receipt schema |
| 48-hour acquisition system | Factory job workflow |
| Show the receipt | LangGraph checkpoint + validator output |

---

## 7. Sequencing law (revenue first)

| Priority | Action | Gate |
|----------|--------|------|
| **P0** | Revenue Engine outreach → first paid client | `SOURCEA_REVENUE_ENGINE_V1_LOCKED_v1.md` |
| **P1** | Spike: one factory job dry-run PASS receipt | `apps/factory-runtime-spike/` |
| **P1b** | MAF sim embed dry-run (`--embed maf`) | `docs/SOURCEA_MICROSOFT_AGENT_FRAMEWORK_MAF_LOCKED_v1.md` |
| **P2** | Wire spike to cloud worker (Temporal server) | After P0 or explicit ship window |
| **P3** | CrewAI inside plan activity | After 2+ client jobs same vertical |
| **P4** | Revenue Engine as Temporal workflow | After 10 manual CRM sends |

**Red line:** No Temporal Cloud spend or validator marathon on Mac founder session for “green theater.”

---

## 8. Spike reference job

**Job ID pattern:** `factory-job-pureflow-spike-v1`  
**Input:** bounded prompt (vertical, audience, proof artifact name)  
**Output:** receipt JSON aligned with `fbe-execution-receipt-v1` fields  

**Run (Mac — dry, no server):**

```bash
cd ~/Desktop/SourceA
pip install -r apps/factory-runtime-spike/requirements.txt
python3 apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py \
  --fixture pureflow --json
```

**MAF hybrid embed (Mac — dry, no MAF SDK):**

```bash
python3 apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py \
  --fixture pureflow --embed maf --json
```

**Run (cloud — Temporal worker):**

```bash
# Requires TEMPORAL_HOST + task queue — Railway / CI only
python3 apps/factory-runtime-spike/factory_runtime_spike/worker_v1.py
```

**Receipt path:** `~/.sina/factory-runtime-spike-receipt-v1.json` (dry-run default)

---

## 9. Relation to FBE

| System | Role |
|--------|------|
| **FBE / Cloud Forge Run** | Current production motor — keep until hybrid path proves one paid job |
| **factory-runtime-spike** | Target shape reference — migrate one template at a time |
| **Portfolio positioning** | “Temporal meets Stripe” — partner narrative, not claim of full migration |

---

## 10. Lock statement

> **As of 2026-06-24T18:00:00Z, SourceA’s target runtime is Temporal (durable orchestration) + LangGraph (governed agent graph) + code validators (PASS/BLOCK) + receipt output. FBE remains the live motor until a hybrid factory job produces a client-facing receipt. CrewAI and AutoGen are optional activity embeds — not the spine. Sales and distribution remain P0 over platform polish.**

**Paths:**  
- This lock: `docs/SOURCEA_RUNTIME_STACK_HYBRID_LOCKED_v1.md`  
- MAF lock: `docs/SOURCEA_MICROSOFT_AGENT_FRAMEWORK_MAF_LOCKED_v1.md`  
- Spike: `apps/factory-runtime-spike/README.md`  
- Revenue: `docs/SOURCEA_REVENUE_ENGINE_V1_LOCKED_v1.md`

---

*Runtime hybrid v1 · internal only · June 2026*
