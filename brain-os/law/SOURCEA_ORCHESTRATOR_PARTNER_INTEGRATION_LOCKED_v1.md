# SourceA Orchestrator Partner Integration — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-15  
**Topic:** Policy layer above durable orchestrators — **partner, not competitor**  
**Authority:** `SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` · `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v1.md` §4  
**Competitor context:** `archive/attachments/commercial/SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md`

**Scope:** SourceA + portfolio engineering · partner sales · embed agreements  
**Out of scope:** W1 demo film (other repo) · hub UI · Sina Command edits

---

## Positioning sentence

> **Temporal executes your workflows. LangGraph builds your agents. SourceA decides whether the run is admissible** — then signs the receipt.

Do **not** pitch SourceA as a Temporal replacement. Pitch as **L6 governance layer** mounted above any L3/L4 stack.

---

## Layer stack (production pattern 2026)

```text
┌─────────────────────────────────────────────────────────────┐
│ L6 SOURCEA — boot gate · model_dispatch · receipts          │
│   critic_boot · session gate · validators · trust ledger    │
├─────────────────────────────────────────────────────────────┤
│ L5 ENTERPRISE EXECUTION — approve → orchestrate → audit     │
│   (Hubler-class — Order Guardian · task orders on disk)     │
├─────────────────────────────────────────────────────────────┤
│ L4 LANGGRAPH / MAF — reasoning · tools · HITL                       │
│   subgraph inside Temporal activities                               │
├─────────────────────────────────────────────────────────────┤
│ L3 TEMPORAL / INNGEST / KESTRA — durable workflow spine     │
│   crash recovery · retries · multi-day waits                │
├─────────────────────────────────────────────────────────────┤
│ L2 INFRA — K8s · Fly · Mac founder stack                    │
└─────────────────────────────────────────────────────────────┘
```

**Industry reference:** [LangGraph vs Temporal](https://www.langchain.com/resources/langgraph-vs-temporal) — outer durability + inner agent graph. SourceA wraps **both** at session and dispatch boundaries.

---

## Integration modes

| Mode | Who | SourceA touchpoint | Orchestrator |
|------|-----|-------------------|--------------|
| **A — Session boot** | Any agent chat / worker | `critic_boot_v1.py` PASS before work | N/A — pre-flight |
| **B — Planner gate** | Hub / agent loop planner | `model_dispatch.dispatch_chat()` SHADOW/ENFORCE | Before LLM call |
| **C — Activity wrapper** | Temporal worker | SourceA gate activity before side-effect activity | Temporal workflow |
| **D — Graph node** | LangGraph | Gate node → conditional edge ALLOW/BLOCK | LangGraph StateGraph |
| **E — n8n glue** | Founder ops | Receipt ingest · intelligence wire | Kestra/n8n cron |

**Minimum viable partner story:** Mode A + B today on disk. Mode C + D = integration blueprint for embed buyers.

---

## Mode C — Temporal partner pattern

```text
Workflow: CopilotGovernedJob
  1. Activity: sourcea_critic_boot()     → PASS | BLOCK
  2. if BLOCK → Activity: notify_compliance() → end
  3. Activity: langgraph_agent_step()   → tool calls (inner graph)
  4. Activity: sourcea_sign_receipt()   → ~/.sina receipt path
  5. Activity: downstream_side_effect() → only if receipt ok
```

**Contract (embed API shape — future SDK):**

```json
{
  "action": "admit_transition",
  "task_id": "wf-123",
  "agent_id": "AGENT-AUTO-MONO",
  "intent_summary": "export board pack",
  "policy_version": "SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md",
  "orchestrator": "temporal",
  "workflow_id": "copilot-governed-job"
}
```

**Response:**

```json
{
  "verdict": "PASS",
  "gate_id": "ASG-20260615-…",
  "receipt_path": "~/.sina/critic-boot-v1.json",
  "blockers": []
}
```

**Today on disk:** CLI `python3 scripts/critic_boot_v1.py --json` + `agent_session_gate_run_v1.py` — wrap as Temporal Activity via subprocess or HTTP sidecar.

---

## Mode D — LangGraph partner pattern

```text
Nodes:
  boot_gate → (PASS) → retrieve_context → llm_reason → tool_exec → receipt_write
            → (BLOCK) → human_escalation → END
```

**Rule:** LangGraph owns **reasoning topology**. SourceA owns **admissibility** at `boot_gate` and **dispatch** at `llm_reason` via `model_dispatch`.

**Anti-pattern:** Reimplementing Temporal durability inside LangGraph checkpoints only — use Temporal for outer workflow when run > 1 hour or cross-service.

---

## Mode B — Already shipped

| File | Role |
|------|------|
| `scripts/model_dispatch.py` | Single OpenRouter choke — SHADOW/ENFORCE |
| `scripts/critic_boot_v1.py` | Layer 1 — 4 checks PASS/BLOCK |
| `scripts/agent_session_gate_run_v1.py` | Session receipt chain |
| `scripts/ai_unify_api_v1.py` | Layer 2 semantic critique (Chat Unify) |

Gate mode: `~/.sina/gate_mode_v1.txt` → `off` | `shadow` | `enforce`

---

## Partner pitch (Buyer 2 embed)

> You already run Temporal + LangGraph. Your agents survive crashes — but they still ship on **stale policy** and **fake-green** receipts. Mount SourceA as a **15-line admission check** before every material activity. Same validators, same receipt format, your orchestrator unchanged.

**Not:** "Migrate to SourceA workflow engine."  
**Yes:** "Add SourceA PEP at the activity boundary."

---

## Who buys this integration story

| Buyer | Fit |
|-------|-----|
| Platform eng eval (SourceA Buyer 2) | **Primary** — embed agreement |
| AAA agency on Temporal | Medium — Mac Guard + gate wrapper |
| Enterprise Copilot (Noetfield) | Compliance receipt — orchestrator agnostic |
| Temporal-only shop | **Partner** — sell admission layer, not rip-and-replace |

---

## Competitive clarity

| Vendor | Relationship to SourceA |
|--------|----------------------|
| **Temporal** | Partner — outer durability |
| **LangGraph** | Partner — inner agent graph |
| **Inngest** | Partner — lighter TS alternative |
| **Notenic** | Competitor — same L6, different packaging |
| **Zenity** | Competitor on Copilot — different layer (agent security vs policy re-brief) |

---

## Implementation roadmap (SourceA only)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **P0** | Disk gate — `critic_boot` + `model_dispatch` | **Shipped** |
| **P1** | HTTP admit API (`/api/admit-v1`) for sidecar embed | Not built |
| **P2** | Temporal Activity sample in `demo/temporal-sourcea-gate/` | Not built |
| **P2b** | MAF sim activity in `apps/factory-runtime-spike/` (`--embed maf`) | **Spike shipped** |
| **P3** | LangGraph gate node sample | Not built |
| **P4** | pip package `sourcea-gate` (read-only admit + receipt) | Not built — SW4 |

**Law:** No P1–P4 until NW1 outreach sent (frozen zone FM-1) unless ASF orders.

---

## References

| Ref | URL |
|-----|-----|
| Temporal | https://temporal.io/ |
| LangGraph vs Temporal | https://www.langchain.com/resources/langgraph-vs-temporal |
| Temporal + LangGraph production | https://devopsvibe.io/en/blog/temporal-langgraph-reliable-agents |
| Inngest agent comparison | https://wetheflywheel.com/en/comparisons/temporal-vs-inngest/ |
| Notenic (L6 peer) | https://notenic.ai/ |
| Constellation map | `SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md` |

---

## Void phrases (partner docs)

- "SourceA replaces Temporal"  
- "Kubernetes for AI agents" in Temporal sales calls — reserve for SourceA company pitch only  
- Mixing Noetfield Copilot vocabulary into embed SDK docs

---

**W1 demo film:** owned by **other repo** — not this document.
