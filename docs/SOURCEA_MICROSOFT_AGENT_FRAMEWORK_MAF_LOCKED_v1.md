# SourceA — Microsoft Agent Framework (MAF) — LOCKED v1

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-06-24T22:00:00Z  
**Authority:** Advisor brief · founder directive · `docs/SOURCEA_RUNTIME_STACK_HYBRID_LOCKED_v1.md`  
**Parents:** `brain-os/law/SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md` · `apps/factory-runtime-spike/`

---

## 0. One law

> **MAF is a tertiary L4 embed inside Temporal activities — never the outer orchestrator, never the proof engine. SourceA PASS/BLOCK validators and signed receipts stay outside MAF.**

**GA:** Microsoft Agent Framework reached **1.0 GA on 2026-04-03** — converges **AutoGen** (conversational multi-agent) and **Semantic Kernel** (enterprise orchestration, plugins, reliability).

**Official:** https://learn.microsoft.com/en-us/agent-framework/overview/ · https://github.com/microsoft/agent-framework

---

## 1. What MAF is (locked summary)

| Pillar | Role |
|--------|------|
| **Agents** | LLM entities — reasoning, tool calling (MCP), memory/context, middleware |
| **Workflows** | Graph orchestration — branching, checkpointing, human-in-the-loop, hand-off patterns |
| **Production** | OpenTelemetry, durability, .NET + Python unified APIs, Azure AI Foundry hosting |

**Design principles:** production-first · open ecosystem (OpenAI, Anthropic, Copilot, MCP, A2A) · explicit graph control vs pure AutoGen conversation.

---

## 2. SourceA layer placement

```text
┌─────────────────────────────────────────────────────────────┐
│ L6 SOURCEA — critic_boot · validators PASS/BLOCK · receipt  │
├─────────────────────────────────────────────────────────────┤
│ L3 TEMPORAL — FactoryJobWorkflow (durable outer spine)       │
├─────────────────────────────────────────────────────────────┤
│ L4a LANGGRAPH — primary agent graph in activities (spike)    │
│ L4b MAF — tertiary embed: M365/Copilot/codegen specialist    │
│      nodes inside ONE activity only                          │
└─────────────────────────────────────────────────────────────┘
```

**Positioning sentence (unchanged):**

> Temporal executes workflows. LangGraph builds agents. SourceA decides admissibility — then signs the receipt.

MAF does **not** replace LangGraph or Temporal on disk.

---

## 3. Framework verdict (2026-06-24)

| Framework | SourceA role | Verdict |
|-----------|--------------|---------|
| **LangGraph + Temporal** | Runtime + Proof spine | **Primary** |
| **CrewAI** | Fast role crews in activities | **Secondary** |
| **MAF (ex-AutoGen/SK)** | M365/Copilot/codegen specialist activity | **Tertiary** |
| **MAF alone** | Outer orchestrator | **Forbidden** |
| **LangGraph vs MAF** | LangGraph = general factory gate graph; MAF = Microsoft-stack specialist subgraph | **Complementary** |

### vs related stacks

| Compare | Verdict for SourceA |
|---------|---------------------|
| **vs AutoGen** | MAF is successor — use MAF for new Microsoft-stack embeds, not greenfield AutoGen |
| **vs Semantic Kernel** | SK v1 supported; new Microsoft agent work → MAF |
| **vs LangGraph** | LangGraph stays primary gate graph; MAF optional inner node for Azure/M365 buyers |
| **vs CrewAI** | CrewAI = speed prototype; MAF = enterprise telemetry + Copilot integration |

---

## 4. Where MAF helps SourceA

| Use case | Lane | MAF fit |
|----------|------|---------|
| **Noetfield Copilot Governance** | Enterprise ~20% | Strong — M365 metadata, Copilot rollout, board PDF workflows |
| **Noetfield Intelligence** | SME ~80% | Weak primary — buyers want outcomes, not Microsoft SDK |
| **Factory codegen debate** | Internal spike | Medium — sandboxed specialist activity |
| **Proof Engine moat** | L6 | **No** — validators remain code/rules, not MAF middleware alone |

---

## 5. Canonical hybrid pattern (Mode C + MAF activity)

```text
Temporal: FactoryJobWorkflowV1
  1. Activity: sourcea_critic_boot_stub()     → PASS | BLOCK
  2. Activity: maf_workflow_phase()           → draft plan + checkpoint_id
  3. Activity: sourcea_validate_gate()        → PASS | BLOCK  ← moat
  4. Activity: emit_receipt()                 → signed JSON
```

**Spike implementation:** `apps/factory-runtime-spike/factory_runtime_spike/maf_workflow_v1.py` (deterministic sim — no cloud keys on Mac).

**Run (Mac — dry, no MAF SDK required):**

```bash
cd ~/Desktop/SourceA
python3 apps/factory-runtime-spike/factory_runtime_spike/dry_run_v1.py \
  --fixture pureflow --embed maf --json
```

**Receipt field:** `runtime_embed: "maf-hybrid-v1"` · `agent_framework: "maf-sim-v1"`

---

## 6. Sequencing law

| Priority | Action | MAF |
|----------|--------|-----|
| **P0** | Revenue / first Diagnostic | No |
| **P1** | LangGraph spike receipt | No |
| **P1b** | MAF sim embed in spike (`--embed maf`) | **This lock** |
| **P2** | Temporal worker cloud | Optional MAF activity |
| **P3** | Real `agent-framework` pip + Azure Foundry | After paid Copilot-governance job |

**Red lines:**

- Do not pitch MAF to SME buyers.
- Do not replace LangGraph gate with MAF workflow for factory spine.
- No Mac validator marathon to prove MAF SDK install.

---

## 7. Public vs internal vocabulary

| Say to buyers | Say internally |
|---------------|----------------|
| Governed automation with receipts | MAF activity inside Temporal |
| Board-grade Copilot evidence | MAF + TLE export path (Noetfield governance) |
| Proof-backed system | LangGraph validate + MAF draft optional |

---

## 8. Lock statement

> **As of 2026-06-24T22:00:00Z, Microsoft Agent Framework (MAF) is a locked tertiary partner for SourceA — specialist L4 embed inside Temporal activities for Microsoft/Azure/Copilot-class work. LangGraph + Temporal remain primary. SourceA validators and receipts remain outside MAF. Spike code proves the hybrid chain on Mac without MAF cloud dependencies.**

**Paths:**

- This lock: `docs/SOURCEA_MICROSOFT_AGENT_FRAMEWORK_MAF_LOCKED_v1.md`
- Runtime hybrid: `docs/SOURCEA_RUNTIME_STACK_HYBRID_LOCKED_v1.md`
- Spike: `apps/factory-runtime-spike/README.md`
- Factory pattern: `docs/SOURCEA_MAF_FACTORY_JOB_PATTERN_v1.md`
- Registry: `data/sourcea-runtime-embed-registry-v1.json`

---

*Internal engineering · June 2026*
