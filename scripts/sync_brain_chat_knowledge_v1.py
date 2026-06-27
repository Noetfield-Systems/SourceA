#!/usr/bin/env python3
"""Bundle full Brain knowledge corpus → worker JSON + SQLite DB."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_db_v1 import rebuild_db  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "CHATBOT_KNOWLEDGE_MANIFEST.json"
BUNDLE_OUT = ROOT / "cloud" / "workers" / "sourcea-brain-chat-v1" / "src" / "knowledge-bundle.json"
HUB_BUNDLE_OUT = ROOT / "data" / "brain-chat-knowledge-bundle-v1.json"
DB_PATH = ROOT / "data" / "chatbot-knowledge" / "brain_knowledge_v1.sqlite"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    if args.check_only:
        ok = DB_PATH.is_file()
        payload = {"ok": ok, "db": str(DB_PATH.relative_to(ROOT))}
        print(json.dumps(payload, indent=2) if args.json else ("OK" if ok else "MISSING DB"))
        return 0 if ok else 1

    db_result = rebuild_db()
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM knowledge_chunks WHERE active=1").fetchall()
    conn.close()

    chunks = []
    for r in rows:
        chunks.append(
            {
                "id": r["id"],
                "lane": r["lane"],
                "source_path": r["source_path"],
                "www_url": r["www_url"],
                "content": r["content"],
                "content_hash": r["content_hash"],
                "pinned": bool(r["pinned"]),
                "kind": r["kind"],
            }
        )

    total_chars = sum(len(c["content"]) for c in chunks)
    lanes_count: dict[str, int] = {}
    for c in chunks:
        lanes_count[c["lane"]] = lanes_count.get(c["lane"], 0) + 1

    bundle = {
        "schema": "sourcea-brain-knowledge-bundle-v2",
        "bundle_version": manifest.get("knowledge_bundle_version", "2.0.0"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "source_files": db_result.get("source_files", 0),
        "lanes": lanes_count,
        "retrieval": "bm25_hybrid_v1",
        "chunks": chunks,
    }

    BUNDLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    # Compact JSON for worker size
    BUNDLE_OUT.write_text(json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf-8")
    HUB_BUNDLE_OUT.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    payload = {
        "ok": True,
        "bundle_version": bundle["bundle_version"],
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "source_files": db_result.get("source_files"),
        "lanes": lanes_count,
        "worker_bundle": str(BUNDLE_OUT.relative_to(ROOT)),
        "db": str(DB_PATH.relative_to(ROOT)),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"sync OK — {len(chunks)} chunks · {total_chars:,} chars · "
            f"{db_result.get('source_files')} files → {BUNDLE_OUT.name}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
