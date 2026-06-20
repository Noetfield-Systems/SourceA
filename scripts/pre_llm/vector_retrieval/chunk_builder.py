"""AST-aware + doc chunks for D5 (v1 — text from D1 paths/symbols + markdown excerpts)."""
from __future__ import annotations

import re
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[3]

DOC_GLOBS = [
    "knowledge-library/**/*.md",
    "archive/attachments/wtm/*.md",
    "*_LOCKED_v*.md",
]

MAX_DOC_BYTES = 24_000
MAX_FILE_CHUNKS = 350
MAX_DOC_CHUNKS = 450
MAX_CHUNKS = MAX_FILE_CHUNKS + MAX_DOC_CHUNKS


def _read_excerpt(path: Path, limit: int = 2000) -> str:
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_DOC_BYTES:
            raw = raw[:MAX_DOC_BYTES]
        return raw.decode("utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def chunks_from_d1(d1: dict) -> list[dict]:
    out: list[dict] = []
    repo = d1.get("repo_root") or ""
    for f in d1.get("files") or []:
        path = f.get("path") or ""
        if not path:
            continue
        syms = f.get("symbols") or []
        sym_text = ", ".join(syms[:40]) if syms else ""
        text = f"file:{path}\nexports:{sym_text}\nlang:{f.get('language') or ''}"
        if len(out) >= MAX_FILE_CHUNKS:
            break
        out.append(
            {
                "chunk_id": f"file:{path}",
                "kind": "ast_file",
                "path": path,
                "repo_root": repo,
                "text": text.strip(),
                "symbols": syms[:20],
            }
        )
    raw_syms = d1.get("symbols") or []
    if isinstance(raw_syms, dict):
        sym_iter = list(raw_syms.values())[:400]
    else:
        sym_iter = list(raw_syms)[:400]
    for sym in sym_iter:
        if isinstance(sym, dict):
            name = sym.get("qualified_name") or sym.get("name") or ""
            fpath = sym.get("file") or sym.get("path") or ""
        else:
            name = str(sym)
            fpath = ""
        if not name or len(out) >= MAX_FILE_CHUNKS:
            continue
        out.append(
            {
                "chunk_id": f"sym:{name}",
                "kind": "ast_symbol",
                "path": fpath,
                "repo_root": repo,
                "text": f"symbol:{name}\nfile:{fpath}",
                "symbols": [name],
            }
        )
    return out


def chunks_from_docs(root: Path | None = None) -> list[dict]:
    base = root or SOURCE_A
    out: list[dict] = []
    seen: set[str] = set()
    for pattern in DOC_GLOBS:
        for path in sorted(base.glob(pattern)):
            if not path.is_file():
                continue
            rel = str(path.relative_to(base))
            if rel in seen:
                continue
            seen.add(rel)
            body = _read_excerpt(path)
            if not body.strip():
                continue
            title = ""
            for line in body.splitlines()[:8]:
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                    break
            out.append(
                {
                    "chunk_id": f"doc:{rel}",
                    "kind": "doc",
                    "path": rel,
                    "repo_root": str(base),
                    "text": f"doc:{rel}\ntitle:{title}\n{body[:1800]}",
                    "symbols": [],
                }
            )
            if len(out) >= MAX_DOC_CHUNKS:
                return out
    return out


def build_all_chunks(*, d1: dict, repo_root: Path | None = None) -> list[dict]:
    return chunks_from_d1(d1) + chunks_from_docs(repo_root)
