# LLM Context Packet — Schema Contract (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED (design-first gate)  
**sequence_id:** SA-2026-06-05-PACKET-SCHEMA-001  
**Canonical location:** `~/Desktop/SourceA/LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md`  
**SSOT path:** `~/.sina/llm_context_packet_v1.json`  
**Code:** `scripts/pre_llm/context_packet/schema.py`  
**Authority:** Subordinate to `WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md`

---

## 1. Why this exists first

Every D4–D16 module assembles **fields for one packet**. Without this contract, modules have no shared target and model calls keep bypassing structure (raw hub JSON → OpenRouter).

**Gate law (Month 3):** `agent_loop` and Live agents **must not** call a model unless `validate_packet()` passes on a fresh packet for the task.

---

## 2. Top-level envelope

```json
{
  "schema": "llm-context-packet-v1",
  "packet_version": "1.0",
  "generated_at": "ISO-8601 UTC",
  "task_id": "string",
  "repo_root": "absolute path",
  "readiness": {
    "score": 0.0,
    "required_fields_ok": false,
    "producer_steps": []
  },
  "intent": { },
  "workspace": { },
  "code": { },
  "dependencies": { },
  "retrieval": { },
  "reasoning": { },
  "ranking": { },
  "plan": { },
  "tools": { },
  "validation": { },
  "diff": { },
  "compression": { },
  "memory": { },
  "constraints": { },
  "compressed_context": { },
  "provenance": { }
}
```

**D15 assembler extensions (optional, not gate-required):**

- `input_text` — raw task string passed to `assemble_packet()` (cache key + D14/D4 chain)
- `retrieval.task_grounding` — bounded grounding block from `task_grounding.py`

---

## 3. Field → producer map (D-steps)

| Packet field | Producer step(s) | Required for gate |
|--------------|------------------|-------------------|
| `intent` | **D4** Intent Engine | yes |
| `workspace` | L1 / hub session (bridge) | no |
| `code.files`, `code.symbols` | **D1** + **D2** | yes |
| `dependencies` | **D3** | yes |
| `retrieval.chunks` | **D5**, **D6**, **D7** | yes (when semantic path active) |
| `retrieval.queries` | **D7** | no until D7 ships |
| `retrieval.task_grounding` | **D15** assembler | no (D15 extension) |
| `reasoning.paths` | **D8** | no until D8 ships |
| `ranking.ranked_evidence` | **D9** | yes |
| `plan.graph` | **D10** (semantic SSOT — not C6) | yes |
| `tools.selection` | **D11** | no |
| `validation.checks` | **D12** | no |
| `diff.changes` | **D13** | no |
| `compression.budget` | **D14** | yes |
| `memory.slots` | **D6** + **D16** | no until D6/D16 |
| `compressed_context.narrative` | **D14** | yes |
| `constraints` | policy / governance | yes |
| `provenance` | **D15** assembler | yes |

**Built today (can populate now):** full D1–D16 substrates via `hydrate_from_disk_substrate()` + D15 `assemble_packet()`.

---

## 4. Minimum gate (v1 — before full D16)

Packet is **dispatch-eligible** when:

1. `schema == llm-context-packet-v1`
2. `intent.goal_class` present (D4)
3. `code.files` non-empty (D1/D2)
4. `dependencies.impact_ready == true` (D3)
5. `ranking.ranked_evidence` non-empty (D9)
6. `plan.graph.nodes` non-empty (D10)
7. `compression.budget.tokens_used <= compression.budget.token_limit` (D14)
8. `compressed_context.narrative` non-empty (D14)
9. `provenance.producer_steps` lists all steps that contributed

Until D4–D10 ship, use `readiness.required_fields_ok: false` — gate blocks model call.

---

## 5. What must NOT be in the packet

- Raw full hub `command-data.json`
- Unbounded file contents (use chunk refs + paths)
- Post-execution B4 planner bias as plan authority
- C6 runtime tool-chain as `plan.graph` SSOT

---

## 6. Validators

| Script | When |
|--------|------|
| `validate-llm-context-packet-schema-v1.sh` | Schema contract + empty template (now) |
| `validate-llm-context-packet-v1.sh` | Full assembled packet (D15) |
| `validate-packet-memory-merge-v1.sh` | D16 writeback |

---

*Design first. Build D4–D15 toward this shape. Gate in Month 3.*
