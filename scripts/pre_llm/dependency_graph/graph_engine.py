"""Build file/call/module graphs + impact index from D2 fusion substrate."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.code_intelligence.store import load_canonical as load_d1
from pre_llm.graph_fusion.fusion_builder import run_fusion
from pre_llm.graph_fusion.store import SCHEMA as D2_SCHEMA
from pre_llm.dependency_graph.store import DEP_GRAPH_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _module_for_file(rel: str) -> str:
    p = Path(rel)
    if p.suffix == ".py":
        parts = list(p.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) if parts else rel
    return rel


def _module_index(files: list[dict]) -> dict[str, str]:
    """Map module id (and aliases) → repo-relative file path."""
    index: dict[str, str] = {}
    for f in files:
        rel = f.get("path") or ""
        if not rel.endswith(".py"):
            continue
        mid = _module_for_file(rel)
        index[mid] = rel
        if mid.startswith("scripts."):
            index[mid[len("scripts.") :]] = rel
        guess = mid.replace(".", "/") + ".py"
        index.setdefault(guess.replace("/", ".").replace(".py", ""), rel)
    return index


def _file_for_module(module: str, mod_index: dict[str, str]) -> str | None:
    if module in mod_index:
        return mod_index[module]
    if not module.startswith("scripts."):
        hit = mod_index.get(f"scripts.{module}")
        if hit:
            return hit
    guess = module.replace(".", "/") + ".py"
    return mod_index.get(guess.replace("/", ".").replace(".py", ""))


def _build_reverse(adj: dict[str, list[str]]) -> dict[str, list[str]]:
    rev: dict[str, list[str]] = defaultdict(list)
    for src, tgts in adj.items():
        for tgt in tgts:
            rev[tgt].append(src)
    return {k: sorted(set(v)) for k, v in rev.items()}


def _transitive_closure(start: str, rev_adj: dict[str, list[str]], limit: int = 500) -> list[str]:
    seen: set[str] = set()
    frontier = [start]
    while frontier and len(seen) < limit:
        cur = frontier.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for parent in rev_adj.get(cur, []):
            if parent not in seen:
                frontier.append(parent)
    seen.discard(start)
    return sorted(seen)


def build_dependency_graph(*, fusion: dict[str, Any], d1: dict[str, Any]) -> dict[str, Any]:
    files = d1.get("files") or []
    file_paths = {f.get("path") for f in files if f.get("path")}
    mod_index = _module_index(files)

    module_edges: list[dict] = []
    module_adj: dict[str, list[str]] = defaultdict(list)
    for e in d1.get("module_graph") or []:
        src = e.get("from") or ""
        tgt = e.get("to") or ""
        if not src or not tgt:
            continue
        if _file_for_module(tgt, mod_index) is None:
            continue
        module_edges.append({"from": src, "to": tgt, "type": e.get("type") or "import"})
        if tgt not in module_adj[src]:
            module_adj[src].append(tgt)

    file_edges: list[dict] = []
    file_adj: dict[str, list[str]] = defaultdict(list)
    seen_file: set[tuple[str, str]] = set()
    for e in d1.get("imports_graph") or []:
        src_f = e.get("from") or ""
        tgt_mod = e.get("to") or ""
        if src_f not in file_paths:
            continue
        tgt_f = _file_for_module(tgt_mod, mod_index)
        if not tgt_f or tgt_f == src_f:
            continue
        key = (src_f, tgt_f)
        if key in seen_file:
            continue
        seen_file.add(key)
        file_edges.append(
            {"from": src_f, "to": tgt_f, "type": e.get("type") or "import", "import_target": tgt_mod}
        )
        if tgt_f not in file_adj[src_f]:
            file_adj[src_f].append(tgt_f)

    call_edges: list[dict] = []
    call_adj: dict[str, list[str]] = defaultdict(list)
    for e in fusion.get("edges") or []:
        if e.get("type") != "call":
            continue
        frm, to = e.get("from") or "", e.get("to") or ""
        if not frm.startswith("file:") or not to.startswith("symbol:"):
            continue
        caller = frm.replace("file:", "", 1)
        sym = to.replace("symbol:", "", 1)
        row = {
            "from": caller,
            "to": sym,
            "type": "call",
            "line": e.get("line"),
            "callee": e.get("callee"),
        }
        call_edges.append(row)
        if sym not in call_adj[caller]:
            call_adj[caller].append(sym)

    module_rev = _build_reverse(module_adj)
    file_rev = _build_reverse(file_adj)
    call_rev = _build_reverse(call_adj)

    symbols = d1.get("symbols") or {}
    symbol_callers: dict[str, list[str]] = defaultdict(list)
    for sym_name, meta in symbols.items():
        for ref in meta.get("references") or []:
            fpath = ref.get("file") or ""
            if fpath:
                symbol_callers[sym_name].append(fpath)
    for k in symbol_callers:
        symbol_callers[k] = sorted(set(symbol_callers[k]))

    return {
        "schema": SCHEMA,
        "generated_at": _now(),
        "repo_root": fusion.get("repo_root") or d1.get("repo_root"),
        "d2_ref": {
            "schema": fusion.get("schema") or D2_SCHEMA,
            "generated_at": fusion.get("generated_at"),
        },
        "module_graph": module_edges,
        "file_graph": file_edges,
        "call_graph": call_edges,
        "impact_index": {
            "module_dependents": module_rev,
            "file_dependents": file_rev,
            "symbol_callers": dict(symbol_callers),
            "call_dependents": call_rev,
        },
        "graph_stats": {
            "modules": len({e["from"] for e in module_edges} | {e["to"] for e in module_edges}),
            "module_edges": len(module_edges),
            "file_edges": len(file_edges),
            "call_edges": len(call_edges),
            "symbols_indexed": len(symbol_callers),
        },
        "dependency_ready": len(module_edges) > 0 and len(file_edges) > 0 and len(call_edges) > 0,
    }


def simulate_impact(*, target_type: str, target: str, canonical: dict[str, Any]) -> dict[str, Any]:
    idx = canonical.get("impact_index") or {}
    t = target_type.strip().lower()
    if t == "module":
        rev = idx.get("module_dependents") or {}
        direct = sorted(set(rev.get(target, [])))
        transitive = _transitive_closure(target, rev)
    elif t == "file":
        rev = idx.get("file_dependents") or {}
        direct = sorted(set(rev.get(target, [])))
        transitive = _transitive_closure(target, rev)
    elif t == "symbol":
        direct = sorted(set((idx.get("symbol_callers") or {}).get(target, [])))
        rev = idx.get("call_dependents") or {}
        transitive = _transitive_closure(target, rev)
    else:
        return {"ok": False, "error": f"unknown target_type: {target_type}"}

    return {
        "ok": True,
        "query": "impact",
        "target_type": t,
        "target": target,
        "direct_dependent_count": len(direct),
        "direct_dependents": direct[:80],
        "transitive_dependent_count": len(transitive),
        "transitive_dependents": transitive[:120],
    }


def run_dependency_graph(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    tid = task_id or "dependency-graph:default"
    if not force_refresh:
        cached = load_canonical()
        if cached and cached.get("dependency_ready") and DEP_GRAPH_SSOT_PATH.is_file():
            return {"ok": True, **cached}

    fusion = run_fusion(repo_root=repo_root, task_id=f"dep-{tid}", force_refresh=force_refresh)
    if not fusion.get("ok"):
        return {"ok": False, "error": "D2 fusion required", "fusion": fusion}

    d1 = load_d1()
    if not d1:
        return {"ok": False, "error": "D1 canonical missing"}

    canonical = build_dependency_graph(fusion=fusion, d1=d1)
    if not canonical.get("dependency_ready"):
        return {"ok": False, "error": "dependency graph empty", "stats": canonical.get("graph_stats")}

    write_canonical(canonical=canonical, task_id=tid)
    return {"ok": True, **canonical}
