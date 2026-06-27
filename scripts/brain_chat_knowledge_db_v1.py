#!/usr/bin/env python3
"""SQLite FTS5 knowledge database for Brain chat — full corpus search on hub."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_lib_v1 import (  # noqa: E402
    PINNED_STEMS,
    chunk_text,
    classify_intent,
    make_chunk,
    search_chunks,
)

DB_PATH = ROOT / "data" / "chatbot-knowledge" / "brain_knowledge_v1.sqlite"
KNOWLEDGE_DIRS = [
    ROOT / "data" / "chatbot-knowledge" / "manual",
    ROOT / "data" / "chatbot-knowledge" / "distilled",
    ROOT / "data" / "chatbot-knowledge" / "crawled" / "www",
    ROOT / "data" / "chatbot-knowledge" / "crawled" / "json",
    ROOT / "data" / "chatbot-knowledge" / "crawled" / "docs",
]

FM_RE = __import__("re").compile(r"^---\n([\s\S]*?)\n---\n([\s\S]*)", __import__("re").M)


def parse_fm(text: str) -> tuple[dict, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS knowledge_sync_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            chunk_count INTEGER,
            source_files INTEGER,
            ok INTEGER
        );
        CREATE TABLE IF NOT EXISTS knowledge_chunks (
            id TEXT PRIMARY KEY,
            lane TEXT,
            source_path TEXT,
            www_url TEXT,
            content TEXT NOT NULL,
            content_hash TEXT,
            pinned INTEGER DEFAULT 0,
            kind TEXT DEFAULT 'doc',
            active INTEGER DEFAULT 1
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts
        USING fts5(id UNINDEXED, lane, content, source_path, tokenize='porter');
        """
    )


def load_md_chunks() -> list[dict]:
    chunks: list[dict] = []
    files = 0
    for d in KNOWLEDGE_DIRS:
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            files += 1
            text = md.read_text(encoding="utf-8", errors="replace")
            meta, body = parse_fm(text)
            if meta.get("public", "true") != "true":
                continue
            lane = meta.get("lane", "core")
            source = meta.get("source_path", md.relative_to(ROOT).as_posix())
            www_url = meta.get("www_url")
            pinned = md.stem in PINNED_STEMS
            for i, sec in enumerate(chunk_text(body)):
                if len(sec.strip()) < 40:
                    continue
                chunks.append(
                    make_chunk(
                        chunk_id=f"{md.stem}-{i}",
                        lane=lane,
                        source_path=source,
                        content=sec,
                        www_url=www_url,
                        pinned=pinned,
                        kind=meta.get("kind", "doc"),
                    )
                )
    return chunks, files


def rebuild_db() -> dict:
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    conn.execute("DELETE FROM knowledge_chunks")
    conn.execute("DELETE FROM knowledge_chunks_fts")
    chunks, files = load_md_chunks()
    for c in chunks:
        conn.execute(
            """INSERT INTO knowledge_chunks
               (id, lane, source_path, www_url, content, content_hash, pinned, kind, active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                c["id"],
                c["lane"],
                c["source_path"],
                c.get("www_url"),
                c["content"],
                c["content_hash"],
                1 if c.get("pinned") else 0,
                c.get("kind", "doc"),
            ),
        )
        conn.execute(
            "INSERT INTO knowledge_chunks_fts (id, lane, content, source_path) VALUES (?, ?, ?, ?)",
            (c["id"], c["lane"], c["content"], c["source_path"]),
        )
    finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute(
        "INSERT INTO knowledge_sync_runs (started_at, finished_at, chunk_count, source_files, ok) VALUES (?, ?, ?, ?, 1)",
        (started, finished, len(chunks), files),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "chunk_count": len(chunks), "source_files": files, "db": str(DB_PATH.relative_to(ROOT))}


def query_db(text: str, k: int = 8) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # FTS pre-filter then BM25 rerank
    rows = conn.execute(
        """SELECT c.* FROM knowledge_chunks c
           JOIN knowledge_chunks_fts f ON c.id = f.id
           WHERE knowledge_chunks_fts MATCH ?
           AND c.active = 1 LIMIT ?""",
        (text.replace('"', ""), max(k * 4, 24)),
    ).fetchall()
    conn.close()
    chunks = [dict(r) for r in rows]
    if not chunks:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        chunks = [dict(r) for r in conn.execute("SELECT * FROM knowledge_chunks WHERE active=1").fetchall()]
        conn.close()
    for c in chunks:
        c["pinned"] = bool(c.get("pinned"))
    intent = classify_intent(text)
    return search_chunks(chunks, text, k=k, lane=intent)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--search", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.rebuild:
        payload = rebuild_db()
    elif args.search:
        payload = {"ok": True, "query": args.search, "hits": query_db(args.search)}
    else:
        payload = {"ok": DB_PATH.is_file(), "db": str(DB_PATH.relative_to(ROOT))}

    print(json.dumps(payload, indent=2) if args.json else json.dumps(payload))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
