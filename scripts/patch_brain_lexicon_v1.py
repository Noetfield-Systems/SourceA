#!/usr/bin/env python3
"""Patch brain SQLite from neutral scrub pairs — delegates to lexicon normalize logic."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/chatbot-knowledge/brain_knowledge_v1.sqlite"
SCRUB = ROOT / "scripts" / "sourcea_lexicon_normalize_repo_v1.py"


def _apply_fn():
    spec = importlib.util.spec_from_file_location("thread_scrub", SCRUB)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod._apply, mod._pairs


def patch_sqlite() -> dict:
    apply_text, pairs = _apply_fn()
    if not DB_PATH.is_file():
        return {"ok": False, "error": f"missing {DB_PATH}"}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, content FROM knowledge_chunks WHERE active=1").fetchall()
    patched = 0
    needles = [p[0].lower() for p in pairs() if p[0]]
    for row in rows:
        new_content = apply_text(row["content"])
        if new_content == row["content"]:
            continue
        conn.execute("UPDATE knowledge_chunks SET content=? WHERE id=?", (new_content, row["id"]))
        conn.execute("UPDATE knowledge_chunks_fts SET content=? WHERE id=?", (new_content, row["id"]))
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
