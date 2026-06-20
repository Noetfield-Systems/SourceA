"""Aggregate pipeline → canonical D1 index."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from pre_llm.code_intelligence.ast_parser import parse_python_files
from pre_llm.code_intelligence.file_discovery import discover_files
from pre_llm.code_intelligence.graph_builder import attach_symbol_references, build_module_graph
from pre_llm.code_intelligence.import_resolver import resolve_imports
from pre_llm.code_intelligence.language_detector import detect_languages
from pre_llm.code_intelligence.repo_walker import walk_repo
from pre_llm.code_intelligence.store import CODE_INTEL_SSOT_PATH, SCHEMA, load_canonical, write_canonical
from pre_llm.code_intelligence.symbol_extractor import extract_symbols, file_symbol_names

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_CODE_INTEL_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _file_exports(parsed: dict) -> list[str]:
    names: list[str] = []
    for sym in parsed.get("symbols") or []:
        name = sym.get("name") or ""
        qn = sym.get("qualified_name") or name
        if name and "." not in qn and not name.startswith("_"):
            names.append(name)
    return sorted(names)


def _import_names(parsed: dict) -> list[str]:
    out: list[str] = []
    for imp in parsed.get("imports") or []:
        if imp.get("kind") == "import":
            mod = imp.get("module")
            if mod:
                out.append(mod)
        else:
            base = imp.get("module") or ""
            name = imp.get("name") or ""
            if base and name and name != "*":
                out.append(f"{base}.{name}")
            elif base:
                out.append(base)
    return sorted(set(out))


def run_full_index(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    root = _repo_root(repo_root)
    if not root.is_dir():
        return {"ok": False, "error": f"repo root not found: {root}"}

    tid = task_id or f"code-intel:{root.name}"
    if not force_refresh:
        cached = load_canonical()
        if cached and cached.get("repo_root") == str(root) and CODE_INTEL_SSOT_PATH.is_file():
            return {"ok": True, **cached}

    raw_paths = walk_repo(root)
    discovered = discover_files(root, raw_paths)
    lang_files = detect_languages(discovered)
    parsed_modules = parse_python_files(root, lang_files)
    symbols = extract_symbols(parsed_modules)
    imports_graph = resolve_imports(parsed_modules)
    symbols = attach_symbol_references(symbols, parsed_modules)
    module_graph = build_module_graph(imports_graph)
    sym_by_file = file_symbol_names(parsed_modules)

    files_out: list[dict] = []
    for entry in lang_files:
        rel = entry["path"]
        lang = entry["language"]
        row = {
            "path": rel,
            "language": lang,
            "ast_hash": "",
            "symbols": sym_by_file.get(rel, []) if lang == "python" else [],
            "imports": [],
            "exports": [],
            "complexity": 0.0,
        }
        if rel in parsed_modules:
            parsed = parsed_modules[rel]
            row["ast_hash"] = parsed.get("ast_hash") or ""
            row["imports"] = _import_names(parsed)
            row["exports"] = _file_exports(parsed)
            row["complexity"] = parsed.get("complexity") or 0.0
        files_out.append(row)

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "repo_root": str(root),
        "files": files_out,
        "symbols": symbols,
        "imports_graph": imports_graph,
        "module_graph": module_graph,
        "index_stats": {
            "files": len(files_out),
            "python_files": len(parsed_modules),
            "symbols": len(symbols),
            "edges": len(imports_graph),
            "module_edges": len(module_graph),
        },
        "query_layer_ready": len(symbols) > 0 and len(parsed_modules) > 0,
    }

    write_canonical(canonical=canonical, task_id=tid)
    return {"ok": True, **canonical}
