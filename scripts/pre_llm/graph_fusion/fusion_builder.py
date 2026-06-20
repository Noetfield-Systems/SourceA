"""Fuse D1 AST + call + import + execution + error edges into one graph."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.code_intelligence.index_builder import run_full_index
from pre_llm.code_intelligence.store import SCHEMA as D1_SCHEMA
from pre_llm.graph_fusion.store import FUSION_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _nid(kind: str, key: str) -> str:
    return f"{kind}:{key}"


def _read_execution_signals(limit: int = 40) -> list[dict]:
    try:
        from execution_intelligence.reader import read_execution_memory  # noqa: WPS433

        rows = read_execution_memory()
        return rows[-limit:] if rows else []
    except Exception:
        return []


def _module_id(rel_path: str) -> str:
    p = Path(rel_path)
    if p.suffix == ".py":
        parts = list(p.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) if parts else rel_path
    return rel_path


def build_fusion_graph(*, d1: dict[str, Any], execution_rows: list[dict]) -> dict[str, Any]:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    edge_seen: set[tuple[str, str, str]] = set()

    def add_edge(frm: str, to: str, etype: str, **meta: Any) -> None:
        key = (frm, to, etype)
        if key in edge_seen:
            return
        edge_seen.add(key)
        edges.append({"from": frm, "to": to, "type": etype, **meta})

    def add_node(nid: str, ntype: str, **meta: Any) -> None:
        if nid not in nodes:
            nodes[nid] = {"id": nid, "type": ntype, **meta}

    for f in d1.get("files") or []:
        rel = f.get("path") or ""
        if not rel:
            continue
        fid = _nid("file", rel)
        add_node(fid, "file", path=rel, language=f.get("language"), ast_hash=f.get("ast_hash") or "")
        if f.get("language") == "python" and not f.get("ast_hash"):
            err_id = _nid("error", rel)
            add_node(err_id, "error", path=rel, reason="ast_parse_missing")
            add_edge(fid, err_id, "error", source="d1_ast")

    modules_seen: set[str] = set()
    for edge in d1.get("imports_graph") or []:
        src_mod = _module_id(edge.get("from") or "")
        tgt_mod = edge.get("to") or ""
        if not src_mod or not tgt_mod:
            continue
        mid_src = _nid("module", src_mod)
        mid_tgt = _nid("module", tgt_mod)
        add_node(mid_src, "module", name=src_mod)
        add_node(mid_tgt, "module", name=tgt_mod)
        modules_seen.update((src_mod, tgt_mod))
        add_edge(mid_src, mid_tgt, "import", import_type=edge.get("type") or "import")

    for rel in {f.get("path") for f in d1.get("files") or [] if f.get("path")}:
        mod = _module_id(rel)
        if mod in modules_seen or rel.endswith(".py"):
            mid = _nid("module", mod)
            add_node(mid, "module", name=mod)
            add_edge(_nid("file", rel), mid, "defines_module")

    symbols = d1.get("symbols") or {}
    for name, sym in symbols.items():
        sid = _nid("symbol", name)
        add_node(
            sid,
            sym.get("type") or "symbol",
            name=name,
            file=sym.get("file"),
            qualified_name=sym.get("qualified_name") or name,
        )
        fpath = sym.get("file")
        if fpath:
            add_edge(_nid("file", fpath), sid, "defines", line=sym.get("line_start"))
        for ref in sym.get("references") or []:
            caller_file = ref.get("file") or ""
            if caller_file:
                add_edge(
                    _nid("file", caller_file),
                    sid,
                    "call",
                    line=ref.get("line"),
                    callee=ref.get("callee"),
                    scope=ref.get("scope"),
                )

    for row in execution_rows:
        task_id = str(row.get("task_id") or row.get("id") or "")
        action = str(row.get("action_id") or row.get("action") or "")
        if not task_id and not action:
            continue
        eid = _nid("execution", task_id or action)
        add_node(
            eid,
            "execution",
            task_id=task_id,
            action_id=action,
            status=row.get("status"),
            at=row.get("at") or row.get("timestamp"),
        )
        for name in symbols:
            if name and (name in action or name in task_id):
                add_edge(eid, _nid("symbol", name), "execution", action_id=action)

    node_list = sorted(nodes.values(), key=lambda n: n["id"])
    by_type: dict[str, int] = {}
    for n in node_list:
        by_type[n["type"]] = by_type.get(n["type"], 0) + 1
    edge_by_type: dict[str, int] = {}
    for e in edges:
        edge_by_type[e["type"]] = edge_by_type.get(e["type"], 0) + 1

    return {
        "schema": SCHEMA,
        "generated_at": _now(),
        "repo_root": d1.get("repo_root"),
        "d1_ref": {
            "schema": d1.get("schema") or D1_SCHEMA,
            "generated_at": d1.get("generated_at"),
        },
        "nodes": node_list,
        "edges": edges,
        "fusion_stats": {
            "nodes": len(node_list),
            "edges": len(edges),
            "nodes_by_type": by_type,
            "edges_by_type": edge_by_type,
            "execution_signals": len(execution_rows),
        },
        "fusion_ready": len(node_list) > 0 and len(edges) > 0,
    }


def run_fusion(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    tid = task_id or "graph-fusion:default"
    if not force_refresh:
        cached = load_canonical()
        if cached and cached.get("fusion_ready") and FUSION_SSOT_PATH.is_file():
            return {"ok": True, **cached}

    d1 = run_full_index(repo_root=repo_root, task_id=f"fusion-{tid}", force_refresh=force_refresh)
    if not d1.get("ok"):
        return {"ok": False, "error": "D1 index required", "d1": d1}

    stats = d1.get("index_stats") or {}
    if stats.get("symbols", 0) < 1 or stats.get("edges", 0) < 1:
        return {"ok": False, "error": "D1 index empty — bootstrap D1 first", "d1_stats": stats}

    execution_rows = _read_execution_signals()
    canonical = build_fusion_graph(d1=d1, execution_rows=execution_rows)
    write_canonical(canonical=canonical, task_id=tid)
    return {"ok": True, **canonical}
