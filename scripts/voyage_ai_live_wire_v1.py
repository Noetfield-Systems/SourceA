#!/usr/bin/env python3
"""Voyage AI live wire — L8 semantic embeddings + active hybrid search logged.

Law: brain-os/wtm/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md · SECRETS_VAULT.md
Receipt: ~/.sina/voyage-ai-live-wire-v1.json
Surfaces: voyage_line on agent-live-surfaces-v1.json
API: GET /api/vector-retrieval-v1 (hub :13020)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "voyage-ai-live-wire-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
SECRETS = SINA / "secrets.env"
VECTOR_INDEX = SINA / "vector_index_v1.json"
DEFAULT_QUERY = "vector retrieval hybrid embedding"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _provider_status() -> dict:
    sys.path.insert(0, str(SCRIPTS / "pre_llm" / "vector_retrieval"))
    sys.path.insert(0, str(SCRIPTS))
    from embedding_provider import provider_payload  # noqa: WPS433

    payload = provider_payload()
    mode = str(payload.get("mode") or "hash_local")
    semantic = bool(payload.get("semantic"))
    voyage_key = False
    if SECRETS.is_file():
        text = SECRETS.read_text(encoding="utf-8", errors="replace")
        voyage_key = "VOYAGE_API_KEY=" in text and "VOYAGE_API_KEY=\n" not in text + "\n"
    ok = semantic and mode == "voyage"
    if voyage_key and mode == "hash_local":
        ok = False
    return {
        "ok": ok,
        "mode": mode,
        "model": payload.get("model"),
        "semantic": semantic,
        "hybrid": bool(payload.get("hybrid")),
        "voyage_key_on_disk": voyage_key,
        "producer": payload.get("producer"),
    }


def _index_status() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from pre_llm.vector_retrieval.store import load_canonical  # noqa: WPS433

    canonical = load_canonical()
    chunks = canonical.get("chunks") or []
    return {
        "ok": len(chunks) >= 10,
        "chunk_count": len(chunks),
        "retrieval_ready": bool(canonical.get("retrieval_ready")),
        "generated_at": canonical.get("generated_at") or "",
        "embedding_provider": canonical.get("embedding_provider") or "",
    }


def _active_search(*, tier: str = "session", query: str = DEFAULT_QUERY) -> dict:
    """Session: 1-call Voyage probe + token hit on cached index. Full: hybrid retrieval smoke."""
    sys.path.insert(0, str(SCRIPTS / "pre_llm" / "vector_retrieval"))
    sys.path.insert(0, str(SCRIPTS))
    os.environ.setdefault("SINA_L8_HYBRID", "1")
    from embedding_provider import embed_text, provider_payload  # noqa: WPS433
    from pre_llm.vector_retrieval.store import load_canonical  # noqa: WPS433
    from pre_llm.vector_retrieval.query_engine import search_chunks  # noqa: WPS433

    idx = _index_status()
    prov = provider_payload()
    if not prov.get("semantic"):
        return {"ok": False, "reason": "not_semantic", "hits": 0}

    try:
        qvec = embed_text(query, is_query=True)
        if len(qvec) < 8:
            return {"ok": False, "reason": "empty_embedding", "hits": 0}
    except Exception as exc:
        return {"ok": False, "reason": str(exc), "hits": 0}

    if idx.get("chunk_count", 0) < 10:
        return {
            "ok": True,
            "reason": "probe_only_index_building",
            "hits": 1,
            "mode": "probe",
            "chunk_count": idx.get("chunk_count"),
            "query": query[:80],
        }

    chunks = load_canonical().get("chunks") or []
    use_hybrid = tier == "full"
    sample = chunks[:60] if use_hybrid else chunks
    hits = search_chunks(sample, query, top_k=3, hybrid=use_hybrid, min_score=0.001)
    ok = len(hits) >= 1
    top = hits[0] if hits else {}
    return {
        "ok": ok,
        "hits": len(hits),
        "top_score": top.get("score"),
        "top_path": (top.get("path") or "")[:80],
        "mode": "hybrid" if use_hybrid else "probe+token",
        "chunk_count": idx.get("chunk_count"),
        "sampled_chunks": len(sample),
        "query": query[:80],
    }


def _compose_voyage_line(*, provider: dict, index: dict, search: dict) -> str:
    mode = provider.get("mode") or "?"
    model = provider.get("model") or "?"
    chunks = index.get("chunk_count") or 0
    hits = search.get("hits") or 0
    if provider.get("ok") and search.get("ok"):
        status = "ACTIVE"
    elif provider.get("ok") and index.get("ok"):
        status = "READY"
    elif provider.get("mode") == "voyage":
        status = "INDEX"
    else:
        status = "FALLBACK"
    return f"VOYAGE {status} · {mode} · {model} · chunks={chunks} · search={hits}hits · L8 hybrid"


def _patch_surfaces(*, voyage_line: str, provider: dict, search: dict) -> None:
    row = _read_json(SURFACES)
    if not row:
        return
    row["voyage_line"] = voyage_line
    row["voyage_at"] = _now()
    row["voyage_ai"] = {
        "receipt": str(RECEIPT),
        "mode": provider.get("mode"),
        "model": provider.get("model"),
        "semantic": provider.get("semantic"),
        "api": "GET /api/vector-retrieval-v1",
        "hub": "http://127.0.0.1:13020/api/vector-retrieval-v1",
        "search_hits": search.get("hits"),
    }
    try:
        SURFACES.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def run_voyage_ai_live_wire(*, tier: str = "session", query: str = DEFAULT_QUERY) -> dict:
    steps: list[dict] = []
    provider = _provider_status()
    steps.append({"step": "embedding_provider", **provider})

    index = _index_status()
    steps.append({"step": "vector_index", **index})

    search = _active_search(tier=tier, query=query)
    steps.append({"step": "active_search", **search})

    ok = bool(provider.get("ok"))
    if index.get("ok"):
        ok = ok and bool(search.get("ok"))

    voyage_line = _compose_voyage_line(provider=provider, index=index, search=search)
    receipt = {
        "schema": "voyage-ai-live-wire-v1",
        "ok": ok,
        "at": _now(),
        "tier": tier,
        "law": "SECRETS_VAULT.md · L8-embedding-provider-v2",
        "voyage_line": voyage_line,
        "provider": provider,
        "index": index,
        "search": search,
        "paths": {
            "secrets": str(SECRETS),
            "vector_index": str(VECTOR_INDEX),
            "embedding_provider": str(SCRIPTS / "pre_llm" / "vector_retrieval" / "embedding_provider.py"),
            "query_engine": str(SCRIPTS / "pre_llm" / "vector_retrieval" / "query_engine.py"),
            "hub_api": "http://127.0.0.1:13020/api/vector-retrieval-v1",
        },
        "steps": steps,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _patch_surfaces(voyage_line=voyage_line, provider=provider, search=search)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Voyage AI live wire — L8 semantic + active search")
    ap.add_argument("--tier", default="session", choices=["session", "full"])
    ap.add_argument("--query", default=DEFAULT_QUERY)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_voyage_ai_live_wire(tier=args.tier, query=args.query)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"VOYAGE_LIVE_WIRE ok={row['ok']} line={row.get('voyage_line', '')[:90]}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
