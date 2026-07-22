# Essay — No Model Without a Packet

**Field:** pre-llm-world-model  
**Version:** 1.0 — first unified page (book seed)  
**Merged from:** `MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md`  
**For roles:** WTM builder · gate operator · hub planner  
**Law:** `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` · `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`

---

## The sentence

**No model call until intent, retrieval, ranking, and plan are assembled and validated.**

That is not a wish. It is how production agent systems work. They call it context engineering, compiled context, or pre-inference governance. Sina already named the steps in Phase D. What is missing is one door in code.

---

## The mistake we stop making

The gap is not that we did not think enough. The gap is that `agent_loop` still reaches OpenRouter with hub JSON and chat, while `validate_packet()` sits ready and returns `gate_eligible: false` on an honest stub. We built the spine, the schema, and D1–D4 on disk. We did not yet **force** the path.

---

## Two layers of memory

**Substrate** persists: `~/.sina/*`, code graphs, dependency edges, intent SSOT. It is the world between calls.

**Projection** is per task: one `llm_context_packet_v1.json`, assembled for this job, validated, handed to the model, then discarded. The model is not the brain. It is the **executor** on a pre-built world model.

D15 is not another feature on the roadmap. It is the **compiler** from substrate to projection.

---

## The pipeline (our names, their names)

```text
D4  intent      — what is this task?
D5  retrieval   — what evidence matters?
D9  ranking     — what matters most?
D10 plan        — what order of work?
D14 compression — what fits the budget?
D15 assembly    — one packet, provenance, gate bit
D15.1 dispatch  — the only door to OpenRouter (hub)
```

Industry stacks match: retrieve → rerank → compress → validate → generate. Plan-aware compression (PAACE) means D14 runs **after** D10, not from raw chat.

---

## Three modes (how we ship without breaking work)

| Mode | What happens |
|------|----------------|
| **OFF** | Today. Models run. We build D5. |
| **SHADOW** | Assemble, log `gate_eligible` and missing sections, still call model. Learn. |
| **ENFORCE** | Block hub OpenRouter when packet is not gate-eligible. |

We gate **hub planners** first — agent loop planner, live maintainer, advisor. We do **not** gate Cursor’s executing agent on day one. Execution stays on the spine.

---

## One door

All hub OpenRouter traffic goes through `model_dispatch.py`: assemble → `validate_packet()` → dispatch or block. Shadow first. Enforce when D14 and D15 are wired and D9/D10 can fill ranking and plan with rule-based graph scores — no LLM required for the first version.

---

## What success looks like

**Before:** Agent loop sends a large opaque prompt.  
**After:** Hub shows “Packet 87% ready — missing: retrieval, plan.” The model receives one page of ranked, planned context.

Maturity moves from 4/10 (strong spine, thin pre-LLM) toward 7/10 (structure forces think-before-act). The question stops being “did we think?” and becomes “did the system assemble and validate?”

---

## Next move

Ship **D5** the same way we shipped D4: SSOT, API, validator, wire `packet.retrieval`. Then shadow `model_dispatch`. Then enforce one planner path with one receipt: `validate-model-gate-enforced-v1.sh`.

---

## Footnotes (purity — read originals)

- Claude analyst attachment: `archive/attachments/wtm/CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md`
- Golden research + URLs: `archive/attachments/wtm/GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md`
- Lessons (append-only): `archive/attachments/wtm/SINA_AGENT_LESSONS_PRE_LLM_GATE_v1.md`
