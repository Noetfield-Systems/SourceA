#!/usr/bin/env python3
"""Patch brain SQLite using lexicon normalization pairs."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/chatbot-knowledge/brain_knowledge_v1.sqlite"
LEXICON = ROOT / "scripts" / "sourcea_lexicon_normalize_v1.py"


def _apply_fn():
    spec = importlib.util.spec_from_file_location("lexicon", LEXICON)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod._apply, mod._pairs, mod._catchalls


def patch_sqlite() -> dict:
    apply_text, pairs, catchalls = _apply_fn()
    if not DB_PATH.is_file():
        return {"ok": False, "error": f"missing {DB_PATH}"}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, content FROM knowledge_chunks WHERE active=1").fetchall()
    patched = 0
    needles = [p[0].lower() for p in pairs() + catchalls() if p[0]]
    for row in rows:
        new_content = apply_text(row["content"])
        if new_content == row["content"]:
            continue
        conn.execute("UPDATE knowledge_chunks SET content=? WHERE id=?", (new_content, row["id"]))
        conn.execute("UPDATE knowledge_chunks_fts SET content=? WHERE id=?", (new_content, row["id"]))
        patched += 1
    meta_rows = conn.execute(
        "SELECT id, source_path, www_url FROM knowledge_chunks WHERE active=1"
    ).fetchall()
    for row in meta_rows:
        sp = apply_text(row["source_path"] or "")
        wu = apply_text(row["www_url"] or "")
        new_id = apply_text(row["id"])
        if sp != row["source_path"] or wu != row["www_url"] or new_id != row["id"]:
            conn.execute(
                "UPDATE knowledge_chunks SET id=?, source_path=?, www_url=? WHERE id=?",
                (new_id, sp, wu, row["id"]),
            )
            patched += 1
    conn.commit()
    clause = " OR ".join("lower(content) LIKE ?" for _ in needles)
    params = [f"%{n}%" for n in needles]
    remaining = conn.execute(
        f"SELECT COUNT(*) FROM knowledge_chunks WHERE active=1 AND ({clause})",
        params,
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM knowledge_chunks WHERE active=1").fetchone()[0]
    conn.close()
    return {"ok": remaining == 0, "patched": patched, "chunk_count": total, "stale_remaining": remaining}


def main() -> int:
    result = patch_sqlite()
    if not result.get("ok"):
        print(json.dumps(result, indent=2))
        return 1
    export = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sync_brain_chat_knowledge_v1.py"), "--skip-rebuild", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if export.returncode != 0:
        print(export.stdout or export.stderr, file=sys.stderr)
        return export.returncode
    print(json.dumps({"patch": result, "export": json.loads(export.stdout)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
