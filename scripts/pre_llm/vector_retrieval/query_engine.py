"""D5 v1 retrieval — token overlap (no external embed API)."""
from __future__ import annotations

import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_./-]+", (text or "").lower())


def score_query(query_tokens: list[str], chunk_text: str, *, chunk_kind: str = "") -> float:
    if not query_tokens:
        return 0.0
    doc_tokens = tokenize(chunk_text)
    if not doc_tokens:
        return 0.0
    q = Counter(query_tokens)
    d = Counter(doc_tokens)
    dot = sum(q[t] * d.get(t, 0) for t in q)
    if dot <= 0:
        return 0.0
    q_norm = math.sqrt(sum(v * v for v in q.values()))
    d_norm = math.sqrt(sum(v * v for v in d.values()))
    if q_norm == 0 or d_norm == 0:
        return 0.0
    base = dot / (q_norm * d_norm)
    if chunk_kind == "ast_symbol":
        base *= 1.08
    if chunk_kind == "doc" and any(t in chunk_text.lower() for t in query_tokens[:6]):
        base *= 1.05
    return round(base, 6)


def search_chunks(
    chunks: list[dict],
    query: str,
    *,
    top_k: int = 8,
    min_score: float = 0.008,
    hybrid: bool = False,
) -> list[dict]:
    from pre_llm.vector_retrieval.embedding_provider import hybrid_score  # noqa: WPS433

    qtok = tokenize(query)
    scored: list[tuple[float, dict]] = []
    for ch in chunks:
        token_s = score_query(qtok, ch.get("text") or "", chunk_kind=ch.get("kind") or "")
        s = hybrid_score(token_score=token_s, query=query, chunk_text=ch.get("text") or "") if hybrid else token_s
        if s >= min_score:
            scored.append((s, ch))
    scored.sort(key=lambda x: (-x[0], x[1].get("chunk_id") or ""))
    out: list[dict] = []
    for s, ch in scored[:top_k]:
        out.append({**ch, "score": s})
    return out
