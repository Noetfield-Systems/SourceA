"""Resolve import edges between files and modules."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _import_targets(imp: dict[str, Any]) -> list[str]:
    if imp.get("kind") == "import":
        mod = imp.get("module") or ""
        return [mod] if mod else []
    base = imp.get("module") or ""
    name = imp.get("name") or ""
    if name == "*":
        return [base] if base else []
    if base and name:
        return [base, f"{base}.{name}"]
    return [base or name] if (base or name) else []


def resolve_imports(parsed_modules: dict[str, dict]) -> list[dict]:
    edges: list[dict] = []
    for rel_path, mod in parsed_modules.items():
        for imp in mod.get("imports") or []:
            for target in _import_targets(imp):
                edges.append(
                    {
                        "from": rel_path,
                        "to": target,
                        "type": imp.get("kind") or "import",
                        "line": imp.get("line"),
                    }
                )
    return edges
