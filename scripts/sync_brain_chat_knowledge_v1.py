#!/usr/bin/env python3
"""Bundle Brain Intelligence corpus v3 → worker JSON + SQLite DB."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_db_v1 import rebuild_db  # noqa: E402

MANIFEST_PATH = ROOT / "data/CHATBOT_KNOWLEDGE_MANIFEST.json"
INDEX_PATH = ROOT / "data/brain-live-source-index-v1.json"
BUNDLE_OUT = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"
HUB_BUNDLE_OUT = ROOT / "data/brain-chat-knowledge-bundle-v1.json"
DB_PATH = ROOT / "data/chatbot-knowledge/brain_knowledge_v1.sqlite"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8")) if INDEX_PATH.is_file() else {}

    if args.check_only:
        ok = DB_PATH.is_file() and index.get("meets_target", False)
        payload = {
            "ok": ok,
            "db": str(DB_PATH.relative_to(ROOT)),
            "live_sources": index.get("source_file_count", 0),
        }
        print(json.dumps(payload, indent=2) if args.json else json.dumps(payload))
        return 0 if ok else 1

    db_result = rebuild_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM knowledge_chunks WHERE active=1").fetchall()
    conn.close()

    chunks = []
    rule_chunks = 0
    for r in rows:
        kind = r["kind"]
        if kind in ("rule", "rules") or r["lane"] == "rules":
            rule_chunks += 1
        chunks.append(
            {
                "id": r["id"],
                "lane": r["lane"],
                "source_path": r["source_path"],
                "www_url": r["www_url"],
                "content": r["content"],
                "content_hash": r["content_hash"],
                "pinned": bool(r["pinned"]),
                "kind": kind,
            }
        )

    total_chars = sum(len(c["content"]) for c in chunks)
    lanes_count: dict[str, int] = {}
    for c in chunks:
        lanes_count[c["lane"]] = lanes_count.get(c["lane"], 0) + 1

    live_files = index.get("source_file_count", db_result.get("source_files", 0))
    unique_sources = len({c["source_path"] for c in chunks if c.get("source_path")})

    bundle = {
        "schema": "sourcea-brain-knowledge-bundle-v5",
        "bundle_version": manifest.get("knowledge_bundle_version", "3.0.0"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "source_files": db_result.get("source_files", 0),
        "live_source_files": unique_sources,
        "rule_chunks": rule_chunks,
        "lanes": lanes_count,
        "retrieval": "brain_intelligence_v5",
        "pipeline": "rules_first_bm25_vector_live_tools",
        "vector": {
            "provider": "semantic_hash_v1",
            "dimensions": 96,
            "mode": "runtime_projection",
        },
        "chunks": chunks,
    }

    # refresh index meets_112 from actual corpus
    if INDEX_PATH.is_file():
        idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        idx["source_file_count"] = unique_sources
        idx["meets_target"] = unique_sources >= 112
        idx["chunk_count"] = len(chunks)
        INDEX_PATH.write_text(json.dumps(idx, indent=2) + "\n", encoding="utf-8")

    BUNDLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE_OUT.write_text(json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf-8")
    HUB_BUNDLE_OUT.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    payload = {
        "ok": True,
        "bundle_version": bundle["bundle_version"],
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "source_files": db_result.get("source_files"),
        "live_source_files": unique_sources,
        "rule_chunks": rule_chunks,
        "lanes": lanes_count,
        "retrieval": bundle["retrieval"],
        "worker_bundle": str(BUNDLE_OUT.relative_to(ROOT)),
        "db": str(DB_PATH.relative_to(ROOT)),
        "meets_112": unique_sources >= 112,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"sync OK v5 — {len(chunks)} chunks · {live_files} live sources · "
            f"{rule_chunks} rule chunks → {BUNDLE_OUT.name}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
