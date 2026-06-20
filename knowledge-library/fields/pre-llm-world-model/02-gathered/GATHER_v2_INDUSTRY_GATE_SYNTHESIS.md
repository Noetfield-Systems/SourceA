# Gathered — Industry gate synthesis (v2)

**Sources:** Golden research report expanded turn · EXT-002 · user research paste  
**Thread:** WTM-D6  
**Prior:** `GATHER_v1_GATE_RESEARCH.md`

---

## Mantra (industry = WTM)

> No model call until intent, retrieval, ranking, and plan are assembled and validated.

Production names: context engineering, compiled context, pre-inference governance.

---

## Compiler stages → packet (ContextOS pattern)

| Stage | Step | Output |
|-------|------|--------|
| Intent | D4 | `packet.intent` |
| Evidence | D5,D6,D7 | `packet.retrieval` |
| Salience | D9 | `packet.ranking` |
| Action graph | D10 | `packet.plan` |
| Budget | D14 | `compression` + `compressed_context` |
| Manifest | D15 | `provenance` + `gate_eligible` |

---

## D5+D7 retrieval stack (production standard)

1. Hybrid — dense vector + sparse/BM25 (paths, symbols)
2. Fuse — RRF default
3. Rerank — top 20–50 (D9 rule-based first)
4. Cap — per-corpus + token budget
5. Retrieval plan JSON per task — not ad-hoc search

Nic Chin: hybrid + rerank 61% → 96.8% recall.

---

## Replay envelope fields

`packet_id`, `task_id`, `readiness_score`, `gate_eligible`, `missing_for_gate`, `producer_steps`, `retrieval_query_id`, `policy_version`, `trace_id` → `~/.sina/gate_shadow_v1.jsonl`

---

## Top 5 golden ideas

1. Harness > prompt  
2. Retrieval plan is code (declarative, diffable)  
3. Plan before compress (PAACE)  
4. Golden-set CI gate (RAGAS)  
5. Minimum sufficient context (AgentSwarm packets)

---

## Status vs this gather

| Item | Status |
|------|--------|
| D5 vector index | Shipped |
| D15.1 shadow | Shipped |
| `retrieval` in GATE_REQUIRED_SECTIONS | Open |
| Golden set `~/.sina/golden/pre_llm_v1/` | Pending |
| D6 | Current step |
