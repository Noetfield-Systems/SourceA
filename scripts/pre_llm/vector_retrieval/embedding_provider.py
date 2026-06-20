"""L8 embedding provider — real semantic vectors via Voyage or OpenAI API.

Drop-in replacement for hash_local. Identical function signatures — zero caller changes.

Priority order:
  1. VOYAGE_API_KEY set  → voyage-4-lite  (best quality/cost for SourceA docs)
  2. OPENAI_API_KEY set  → text-embedding-3-small  (stable fallback)
  3. Neither set         → hash_local fallback  (original behavior, no API cost)

Configure via environment:
  export EMBEDDING_PROVIDER=voyage    # or: openai
  export VOYAGE_API_KEY=your-key
  export OPENAI_API_KEY=your-key      # only needed if provider=openai

Unchanged public API (all callers require zero edits):
  embed_text(text)                    → list[float]
  cosine(a, b)                        → float
  hybrid_score(token_score, query, chunk_text) → float
  provider_payload()                  → dict

New helper (optional, for batch efficiency):
  embed_batch(texts)                  → list[list[float]]
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any

# ── Vault hydrate (Tier 3 — ~/.sina/secrets.env) ───────────────────────────

def _hydrate_from_vault() -> None:
    """Load embedding keys from vault when not already in os.environ."""
    names = ("VOYAGE_API_KEY", "OPENAI_API_KEY", "EMBEDDING_PROVIDER", "VOYAGE_MODEL", "OPENAI_MODEL")
    for vault in (
        Path.home() / ".sina" / "secrets.env",
        Path.home() / "Desktop" / "SinaPromptOS" / "secrets.env",
    ):
        if not vault.is_file():
            continue
        for line in vault.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            if key in names and key not in os.environ:
                os.environ[key] = val.strip().strip('"').strip("'")
        break


_hydrate_from_vault()

# ── Config ────────────────────────────────────────────────────────────────────

_PROVIDER    = os.getenv("EMBEDDING_PROVIDER", "").lower().strip()
_VOYAGE_KEY  = os.getenv("VOYAGE_API_KEY", "").strip()
_OPENAI_KEY  = os.getenv("OPENAI_API_KEY", "").strip()
_VOYAGE_URL  = "https://api.voyageai.com/v1/embeddings"
_OPENAI_URL  = "https://api.openai.com/v1/embeddings"
_VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-4-lite")
_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "text-embedding-3-small")
_HASH_DIMS   = 64   # kept for hash fallback parity


def _active_provider() -> str:
    """Resolve active provider from env. Auto-detects if EMBEDDING_PROVIDER not set."""
    if _PROVIDER == "voyage" and _VOYAGE_KEY:
        return "voyage"
    if _PROVIDER == "openai" and _OPENAI_KEY:
        return "openai"
    if _VOYAGE_KEY:
        return "voyage"
    if _OPENAI_KEY:
        return "openai"
    return "hash_local"


# ── HTTP helper (zero external deps) ─────────────────────────────────────────

def _post(url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Embedding API error {exc.code}: {body}") from exc


# ── Hash fallback (original algorithm — unchanged) ────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]{3,}", (text or "").lower())


def _hash_embed(text: str, dims: int = _HASH_DIMS) -> list[float]:
    """Original SHA-256 hash embedding — used only when no API key is configured."""
    vec = [0.0] * dims
    for tok in _tokenize(text):
        h = hashlib.sha256(tok.encode()).digest()
        for i in range(dims):
            vec[i] += (h[i % len(h)] / 255.0) - 0.5
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / norm, 6) for v in vec]


# ── API embedding calls ───────────────────────────────────────────────────────

def _voyage_embed(texts: list[str], *, is_query: bool = False) -> list[list[float]]:
    payload = {
        "input": texts,
        "model": _VOYAGE_MODEL,
        "input_type": "query" if is_query else "document",
    }
    headers = {
        "Authorization": f"Bearer {_VOYAGE_KEY}",
        "Content-Type": "application/json",
    }
    resp = _post(_VOYAGE_URL, payload, headers)
    return [item["embedding"] for item in resp.get("data", [])]


def _openai_embed(texts: list[str]) -> list[list[float]]:
    payload = {"input": texts, "model": _OPENAI_MODEL}
    headers = {
        "Authorization": f"Bearer {_OPENAI_KEY}",
        "Content-Type": "application/json",
    }
    resp = _post(_OPENAI_URL, payload, headers)
    return [item["embedding"] for item in resp.get("data", [])]


# ── LRU cache — avoids redundant API calls for repeated strings ───────────────

@lru_cache(maxsize=2048)
def _cached_embed(text: str, is_query: bool = False) -> tuple[float, ...]:
    """Returns tuple (hashable) for cache key. Converts to list in public API."""
    provider = _active_provider()
    try:
        if provider == "voyage":
            vecs = _voyage_embed([text], is_query=is_query)
            return tuple(vecs[0]) if vecs else tuple(_hash_embed(text))
        if provider == "openai":
            vecs = _openai_embed([text])
            return tuple(vecs[0]) if vecs else tuple(_hash_embed(text))
    except Exception:
        # On any API failure, fall through to hash_local so system stays alive
        pass
    return tuple(_hash_embed(text))


# ── Public API — identical signatures to v1 ───────────────────────────────────

def embed_text(text: str, *, dims: int = _HASH_DIMS, is_query: bool = False) -> list[float]:
    """Embed a single text → list[float].

    dims is ignored for API providers (they return fixed native dimensions).
    Kept as a keyword arg for backward compatibility with any caller passing dims=.
    """
    return list(_cached_embed(text, is_query))


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two embedding vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return round(dot / (na * nb), 6)


def hybrid_score(*, token_score: float, query: str, chunk_text: str) -> float:
    """Combine BM25-style token score with semantic cosine similarity.

    query uses is_query=True (Voyage asymmetric matching).
    chunk_text uses is_query=False (document embedding).
    """
    qe  = embed_text(query,      is_query=True)
    ce  = embed_text(chunk_text, is_query=False)
    sem = cosine(qe, ce)
    return round(0.55 * token_score + 0.45 * sem, 6)


def embed_batch(texts: list[str], *, is_query: bool = False) -> list[list[float]]:
    """Batch embed in a single API call — more efficient than looping embed_text.

    New in v2. Not required by existing callers but available for future index builders.
    """
    if not texts:
        return []
    provider = _active_provider()
    try:
        if provider == "voyage":
            return _voyage_embed(texts, is_query=is_query)
        if provider == "openai":
            return _openai_embed(texts)
    except Exception:
        pass
    return [_hash_embed(t) for t in texts]


def provider_payload() -> dict[str, Any]:
    """Status dict for monitor/audit — same schema as v1, extended."""
    p     = _active_provider()
    model = (
        _VOYAGE_MODEL  if p == "voyage"
        else _OPENAI_MODEL if p == "openai"
        else "hash_local"
    )
    return {
        "ok":       True,           # system always ok — hash_local is safe fallback
        "mode":     p,
        "model":    model,
        "dims":     _HASH_DIMS if p == "hash_local" else "api-native",
        "hybrid":   True,
        "semantic": p != "hash_local",
        "producer": "L8-embedding-provider-v2",
    }
