#!/usr/bin/env python3
"""Brain Intelligence Pipeline — retrieval-first, rule-aware, 112+ live sources."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_retrieval_engine_v1 import assemble_prompt, retrieve  # noqa: E402

DB_PATH = ROOT / "data/chatbot-knowledge/brain_knowledge_v1.sqlite"
BUNDLE_PATH = ROOT / "data/brain-chat-knowledge-bundle-v1.json"
INDEX_PATH = ROOT / "data/brain-live-source-index-v1.json"

BRAIN_CORE = """You are Brain on sourcea.app — the public guide for SourceA + Forge.

You are NOT a hardcoded chatbot. You are a retrieval-first advisor:
- LIVE SOURCES and PUBLIC RULES are injected below every turn
- Answer from retrieved evidence with citations
- Rule-aware: agentic-first, never lead with price, never deny factories when catalog says they exist
- If evidence is thin, say so honestly and route to /sourcea/forge/terminal or the best matching page
- Operate with high confidence by using evidence, not by calling yourself "highest confidence."

Tone: sharp, honest, plain English. Match the user's energy. No governance jargon to strangers."""


def load_chunks() -> list[dict]:
    if DB_PATH.is_file():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM knowledge_chunks WHERE active=1").fetchall()
        conn.close()
        chunks = [dict(r) for r in rows]
        for c in chunks:
            c["pinned"] = bool(c.get("pinned"))
        return chunks
    if BUNDLE_PATH.is_file():
        bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
        return bundle.get("chunks") or []
    return []


def run(message: str, *, product: str = "") -> dict:
    chunks = load_chunks()
    index_meta = {}
    if INDEX_PATH.is_file():
        index_meta = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    retrieval = retrieve(chunks, message)
    core = BRAIN_CORE
    if (product or "").strip().lower() == "forge_terminal":
        core += "\n\nProduct mode: Forge Terminal public demo — four labeled sections, under 400 words."
    prompt, citations = assemble_prompt(core, retrieval)

    return {
        "schema": "brain-intelligence-pipeline-v1",
        "ok": True,
        "prompt": prompt,
        "citations": citations,
        "intent": retrieval.get("intent"),
        "confidence": retrieval.get("confidence"),
        "sources_consulted": retrieval.get("sources_consulted"),
        "source_file_count": index_meta.get("source_file_count"),
        "chunk_count": len(chunks),
        "rules_applied": retrieval.get("rules_applied"),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--message", "-m", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = run(args.message)
    if args.json:
        # truncate prompt in json output for readability
        display = {**out, "prompt_preview": out["prompt"][:500] + "…"}
        del display["prompt"]
        print(json.dumps(display, indent=2))
    else:
        print(out["prompt"][:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
