"""Python AST parser — functions, classes, calls (v1 scope)."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any


def _qualify(parts: list[str]) -> str:
    return ".".join(p for p in parts if p)


class _AstVisitor(ast.NodeVisitor):
    def __init__(self, rel_path: str) -> None:
        self.rel_path = rel_path
        self.symbols: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self._scope: list[str] = []
        self._complexity = 0

    def generic_visit(self, node: ast.AST) -> None:
        self._complexity += 1
        super().generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append({"kind": "import", "module": alias.name, "line": node.lineno})
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            self.imports.append(
                {
                    "kind": "from",
                    "module": module,
                    "name": alias.name,
                    "line": node.lineno,
                    "level": node.level,
                }
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._add_symbol("function", node.name, node.lineno, getattr(node, "end_lineno", node.lineno))
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._add_symbol("async_function", node.name, node.lineno, getattr(node, "end_lineno", node.lineno))
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._add_symbol("class", node.name, node.lineno, getattr(node, "end_lineno", node.lineno))
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_Call(self, node: ast.Call) -> None:
        callee = _callee_name(node.func)
        if callee:
            self.calls.append(
                {
                    "callee": callee,
                    "line": node.lineno,
                    "scope": _qualify(self._scope),
                }
            )
        self.generic_visit(node)

    def _add_symbol(self, kind: str, name: str, start: int, end: int) -> None:
        self.symbols.append(
            {
                "kind": kind,
                "name": name,
                "qualified_name": _qualify(self._scope + [name]),
                "line_start": start,
                "line_end": end,
            }
        )


def _callee_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _callee_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


def _ast_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def parse_python_file(repo_root: Path, rel_path: str) -> dict[str, Any]:
    full = repo_root / rel_path
    try:
        source = full.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return {"ok": False, "path": rel_path, "error": str(exc)}

    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as exc:
        return {"ok": False, "path": rel_path, "error": exc.msg, "line": exc.lineno}

    visitor = _AstVisitor(rel_path)
    visitor.visit(tree)

    return {
        "ok": True,
        "path": rel_path,
        "language": "python",
        "ast_hash": _ast_hash(source),
        "complexity": float(visitor._complexity),
        "symbols": visitor.symbols,
        "imports": visitor.imports,
        "calls": visitor.calls,
    }


def parse_python_files(repo_root: Path, lang_files: list[dict]) -> dict[str, dict]:
    modules: dict[str, dict] = {}
    for entry in lang_files:
        if entry.get("language") != "python":
            continue
        parsed = parse_python_file(repo_root, entry["path"])
        if parsed.get("ok"):
            modules[entry["path"]] = parsed
    return modules
