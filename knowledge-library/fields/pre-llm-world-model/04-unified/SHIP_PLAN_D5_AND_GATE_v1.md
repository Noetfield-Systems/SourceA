# Ship Plan — D5 + Gate Shadow (v1)

**Field:** pre-llm-world-model  
**Current strategic step:** D5  
**Playbook:** Same as D4 (SSOT → module → API → validator → packet wire)

---

## D5 file map

| File | Role |
|------|------|
| `scripts/pre_llm/vector_retrieval/store.py` | `~/.sina/vector_index_v1.json` |
| `scripts/pre_llm/vector_retrieval/chunk_builder.py` | AST-aware chunks from D1 + doc chunks |
| `scripts/pre_llm/vector_retrieval/index_builder.py` | Full index rebuild |
| `scripts/pre_llm/vector_retrieval/query_engine.py` | Token overlap search (v1 — no Ollama) |
| `scripts/pre_llm/vector_retrieval/retrieval_engine.py` | Orchestrate build + query |
| `scripts/pre_llm/vector_retrieval/api.py` | Hub payload |
| `scripts/validate-vector-retrieval-v1.sh` | Receipt |
| `scripts/sina-command-server.py` | `GET /api/vector-retrieval-v1` |

---

## D5 acceptance

1. Index builds from SourceA + D1 symbols  
2. Query `build D5` returns ≥1 chunk with path metadata  
3. `retrieval_ready: true` on canonical snapshot  
4. Validator script exits 0  
5. `hydrate_from_disk_substrate` fills `packet.retrieval.chunks` when index exists  

---

## D15.1 shadow (after D5 PASS)

| File | Role |
|------|------|
| `scripts/model_dispatch.py` | `gate_mode` OFF/SHADOW/ENFORCE · log shadow |
| `~/.sina/gate_shadow_v1.jsonl` | Replay envelope |
| `scripts/validate-model-gate-shadow-v1.sh` | Shadow receipt |

**Wire:** `agent_loop._planner_chat` calls `model_dispatch.chat()` — SHADOW logs, does not block until ENFORCE.

---

## After D5 → D16 order (locked)

```text
D5  → D6 → D7 → D8 → D9 → D10 → D11 → D12 → D13 → D14 → D15 → D15.1 → D15.2 → D16
      ↑ shadow gate starts after D5
                              ↑ enforce after D14+D15
```
