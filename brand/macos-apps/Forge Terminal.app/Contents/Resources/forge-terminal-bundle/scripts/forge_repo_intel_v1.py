#!/usr/bin/env python3
"""Forge Repo Intelligence v1 — import-aware dependency graph."""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

IMPORT_RE = re.compile(
    r"""^(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)""",
    re.MULTILINE,
)


def _py_imports(path: Path, root: Path) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    rel = path.relative_to(root).as_posix()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return edges
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                edges.append((rel, alias.name.split(".")[0] + ".py"))
        elif isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module.replace(".", "/") + ".py"
            edges.append((rel, mod))
    return edges


def _js_ts_imports(path: Path, root: Path) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return edges
    for m in re.finditer(r"""from\s+['"](\.\.?/[^'"]+)['"]""", text):
        target = m.group(1)
        if target.startswith("."):
            target = str((path.parent / target).resolve().relative_to(root))
        edges.append((rel, target))
    return edges


def build_repo_graph(
    *,
    workspace: Path,
    files: list[str] | None = None,
    max_files: int = 120,
) -> dict[str, Any]:
    """Build import-aware repo graph: nodes, edges, symbols."""
    root = workspace.expanduser().resolve()
    if not root.is_dir():
        return {"nodes": [], "edges": [], "symbols": []}

    if files:
        paths = [root / f for f in files if (root / f).is_file()]
    else:
        paths = []
        for ext in ("*.py", "*.ts", "*.tsx", "*.js"):
            paths.extend(root.rglob(ext))
        paths = [p for p in paths if ".git" not in p.parts and "node_modules" not in p.parts][:max_files]

    nodes: set[str] = set()
    edges: list[list[str]] = []
    symbols: list[str] = []

    for path in paths:
        rel = path.relative_to(root).as_posix()
        nodes.add(rel)
        if path.suffix == ".py":
            for fr, to in _py_imports(path, root):
                nodes.add(fr)
                nodes.add(to)
                edges.append([fr, to])
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        symbols.append(f"{rel}:{node.name}")
            except (OSError, SyntaxError):
                pass
        elif path.suffix in (".ts", ".tsx", ".js"):
            for fr, to in _js_ts_imports(path, root):
                nodes.add(fr)
                nodes.add(to)
                edges.append([fr, to])

    return {
        "nodes": sorted(nodes)[:200],
        "edges": edges[:300],
        "symbols": symbols[:100],
    }
