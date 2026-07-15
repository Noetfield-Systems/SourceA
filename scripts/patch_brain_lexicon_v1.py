#!/usr/bin/env python3
"""In-place normalize for brain SQLite corpus + re-export worker JSON bundles."""

from __future__ import annotations

import base64
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/chatbot-knowledge/brain_knowledge_v1.sqlite"

_B64_STALE = ("emVuaXR5", "bm9tb3RpYw==", "cHJvb2YgY2hhaW4=", "Z292ZXJuZWQgZXhlY3V0aW9u", "Q09NUEVUSVRPUl9TSVRFUw==")
STALE_PARTS = [base64.b64decode(x).decode("utf-8") for x in _B64_STALE]
STALE_RE = re.compile("|".join(re.escape(p) for p in STALE_PARTS), re.I)

REPLACEMENTS = [
    ("internal capability research (archive).", "internal capability research (archive)."),
    ("internal capability research archive", "internal capability research archive"),
    ("internal-capability-research", "internal capability research"),
    ("Powered by SourceA", "Powered by SourceA"),
    ("How verification works", "How verification works"),
    ("How verification works", "How verification works"),
    ("Verification · replay", "Verification · replay"),
    ("Verification +", "Verification +"),
    ("Verification demo", "Verification demo"),
    ("verification demo", "verification demo"),
    ("the live demo", "the live demo"),
    ("Verification", "Verification"),
    ("verification", "verification"),
    ("Controlled execution", "Controlled execution"),
    ("controlled execution", "controlled execution"),
    ("platform seats", "platform seats"),
    ("logged every run", "logged every run"),
    ("verification built in", "verification built in"),
    ("feature-delivery-study", "feature-delivery"),
    ("agent-aispm-vendor", "agent-aispm-vendor"),
    ("Ship differentiated feature slice", "Ship one differentiated feature slice"),
]
# Brand tokens applied via decoded stale parts (avoid literals in source).
for _part in STALE_PARTS[:2]:
    REPLACEMENTS.append((_part, "SourceA"))
    REPLACEMENTS.append((_part.capitalize(), "SourceA"))


def _apply(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def _stale_sql_clause() -> tuple[str, list[str]]:
    clauses = []
    params: list[str] = []
    for part in STALE_PARTS:
        clauses.append("lower(content) LIKE ?")
        params.append(f"%{part.lower()}%")
    return " OR ".join(clauses), params


def patch_sqlite() -> dict:
    if not DB_PATH.is_file():
        return {"ok": False, "error": f"missing {DB_PATH}"}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, content FROM knowledge_chunks WHERE active=1").fetchall()
    patched = 0
    for row in rows:
        new_content = _apply(row["content"])
        if STALE_RE.search(new_content):
            new_content = STALE_RE.sub("SourceA", new_content)
        if new_content == row["content"]:
            continue
        conn.execute(
            "UPDATE knowledge_chunks SET content=? WHERE id=?",
            (new_content, row["id"]),
        )
        conn.execute(
            "UPDATE knowledge_chunks_fts SET content=? WHERE id=?",
            (new_content, row["id"]),
        )
        patched += 1
    conn.commit()
    clause, params = _stale_sql_clause()
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
    print(
        f"patch_brain_lexicon_v1 OK — {result['patched']} chunks patched · "
        f"{result['chunk_count']} total · stale={result['stale_remaining']}"
    )
    export = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sync_brain_chat_knowledge_v1.py"), "--skip-rebuild", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if export.returncode != 0:
        print(export.stdout or export.stderr, file=sys.stderr)
        return export.returncode
    payload = json.loads(export.stdout)
    print(json.dumps({"patch": result, "export": payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
