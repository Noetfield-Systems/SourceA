"""Expand query symbols from D1 code intelligence — read-only."""
from __future__ import annotations

import re
from typing import Any


def _norm(text: str) -> str:
    return (text or "").lower()


def expand_symbols(*, text: str, d1: dict[str, Any] | None) -> list[str]:
    if not d1:
        return []

    raw = text or ""
    norm = _norm(raw)
    symbols_map = d1.get("symbols") or {}
    if isinstance(symbols_map, dict):
        symbol_names = list(symbols_map.keys())
    else:
        symbol_names = [
            s.get("name") or s.get("id") or ""
            for s in (symbols_map if isinstance(symbols_map, list) else [])
            if isinstance(s, dict)
        ]

    hits: list[tuple[int, str]] = []
    for name in symbol_names:
        if not name or len(name) < 3:
            continue
        nlow = name.lower()
        if nlow in norm or name in raw:
            hits.append((3, name))
            continue
        # CamelCase token overlap
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", name)
        if parts and any(p.lower() in norm for p in parts if len(p) > 2):
            hits.append((2, name))

    files = d1.get("files") or []
    for f in files[:200]:
        path = f.get("path") if isinstance(f, dict) else str(f)
        if not path:
            continue
        base = path.rsplit("/", 1)[-1]
        stem = base.rsplit(".", 1)[0]
        if stem and (stem.lower() in norm or base in raw):
            hits.append((2, stem))

    hits.sort(key=lambda x: (-x[0], x[1]))
    out: list[str] = []
    for _, name in hits:
        if name not in out:
            out.append(name)
    return out[:16]
