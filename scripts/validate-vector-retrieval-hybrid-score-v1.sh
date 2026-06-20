#!/usr/bin/env bash
# sa-0613 — vector_retrieval query_engine hybrid_score smoke
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pre_llm.vector_retrieval.embedding_provider import hybrid_score, provider_payload
from pre_llm.vector_retrieval.query_engine import search_chunks

ep = provider_payload()
assert ep.get("hybrid"), ep

score = hybrid_score(
    token_score=0.42,
    query="pre-LLM gate D5 vector retrieval",
    chunk_text="vector retrieval hybrid_score blends token overlap with hash embeddings",
)
assert 0.0 < score <= 1.0, score

chunks = [
    {"chunk_id": "doc-1", "text": "D5 vector retrieval hybrid_score gate pre-LLM", "kind": "doc"},
    {"chunk_id": "doc-2", "text": "unrelated governance entry gate receipts", "kind": "doc"},
]
hits = search_chunks(chunks, "hybrid_score vector gate D5", top_k=2, hybrid=True)
assert hits, "search_chunks hybrid returned no hits"
assert hits[0].get("chunk_id") == "doc-1", hits
assert float(hits[0].get("score") or 0) > float(hits[-1].get("score") or 0), hits

print(f"OK: validate-vector-retrieval-hybrid-score-v1 · score={score} hits={len(hits)}")
PY
