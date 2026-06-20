#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
from pre_llm.vector_retrieval.api import vector_retrieval_v1_payload
from pre_llm.vector_retrieval.store import VECTOR_SSOT_PATH

QUERY = "pre-LLM gate D5 vector retrieval intent packet"
live = vector_retrieval_v1_payload(text=QUERY, task_id="validate-d5", force_refresh=True, top_k=5)
assert live.get("ok"), live
assert VECTOR_SSOT_PATH.is_file(), "vector_index_v1.json missing"
assert live.get("chunk_count", 0) >= 10, f"too few chunks: {live.get('chunk_count')}"
hits = live.get("hits") or []
assert len(hits) >= 1, "no retrieval hits"
assert live.get("retrieval_ready"), "retrieval_ready false"
assert live.get("mode") == "hybrid" or live.get("hybrid_retrieval"), "L8 hybrid mode expected"
from pre_llm.vector_retrieval.embedding_provider import provider_payload
ep = provider_payload()
assert ep.get("hybrid"), ep
pr = live.get("packet_retrieval") or {}
assert len(pr.get("chunks") or []) >= 1, "packet_retrieval.chunks empty"
print("PASS vector retrieval v1", "chunks", live.get("chunk_count"), "hits", len(hits), "mode", live.get("mode"))
PY
