"""Build symbol table — function/class/method → file mapping."""
from __future__ import annotations

from typing import Any


def extract_symbols(parsed_modules: dict[str, dict]) -> dict[str, dict]:
    """Canonical symbols dict keyed by simple name (collisions keep richest entry)."""
    symbols: dict[str, dict] = {}
    class_methods: dict[str, list[str]] = {}

    for rel_path, mod in parsed_modules.items():
        for sym in mod.get("symbols") or []:
            kind = sym.get("kind") or "symbol"
            name = sym.get("name") or ""
            qn = sym.get("qualified_name") or name
            if not name:
                continue

            if kind == "class":
                class_methods.setdefault(name, [])
                symbols[name] = {
                    "type": "class",
                    "file": rel_path,
                    "qualified_name": qn,
                    "references": symbols.get(name, {}).get("references", []),
                    "methods": class_methods[name],
                    "line_start": sym.get("line_start"),
                }
            elif kind in ("function", "async_function"):
                if "." in qn:
                    owner = qn.rsplit(".", 1)[0].split(".")[-1]
                    class_methods.setdefault(owner, [])
                    if name not in class_methods[owner]:
                        class_methods[owner].append(name)
                    if owner in symbols and symbols[owner].get("type") == "class":
                        symbols[owner]["methods"] = sorted(class_methods[owner])
                else:
                    symbols[name] = {
                        "type": "function" if kind == "function" else "async_function",
                        "file": rel_path,
                        "qualified_name": qn,
                        "references": symbols.get(name, {}).get("references", []),
                        "methods": [],
                        "line_start": sym.get("line_start"),
                    }

    return symbols


def file_symbol_names(parsed_modules: dict[str, dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for rel_path, mod in parsed_modules.items():
        names = sorted({s.get("name") for s in mod.get("symbols") or [] if s.get("name")})
        out[rel_path] = names
    return out
