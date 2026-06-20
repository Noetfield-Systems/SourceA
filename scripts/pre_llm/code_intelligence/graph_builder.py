"""Module graph + symbol reference graph."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _module_id(rel_path: str) -> str:
    p = Path(rel_path)
    if p.suffix == ".py":
        parts = list(p.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) if parts else rel_path
    return rel_path


def _normalize_symbol(name: str) -> str:
    return name.strip().split(".")[-1]


def build_module_graph(imports_graph: list[dict]) -> list[dict]:
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for edge in imports_graph:
        src = _module_id(edge["from"])
        tgt = edge["to"]
        key = (src, tgt, edge.get("type") or "import")
        if key in seen:
            continue
        seen.add(key)
        edges.append({"from": src, "to": tgt, "type": key[2]})
    return edges


def attach_symbol_references(
    symbols: dict[str, dict],
    parsed_modules: dict[str, dict],
) -> dict[str, dict]:
    """Populate references[] from lightweight call nodes."""
    refs: dict[str, list[dict]] = {name: list(meta.get("references") or []) for name, meta in symbols.items()}

    for rel_path, mod in parsed_modules.items():
        for call in mod.get("calls") or []:
            callee = call.get("callee") or ""
            target = _normalize_symbol(callee)
            if target not in symbols:
                continue
            entry = {
                "file": rel_path,
                "line": call.get("line"),
                "callee": callee,
                "scope": call.get("scope"),
            }
            bucket = refs.setdefault(target, [])
            if entry not in bucket:
                bucket.append(entry)

    out = dict(symbols)
    for name, meta in out.items():
        meta = dict(meta)
        meta["references"] = refs.get(name, [])[:100]
        out[name] = meta
    return out
