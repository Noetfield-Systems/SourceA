#!/usr/bin/env python3
"""Chat Unify ORD — Phase 2 atoms + claim graph.

Rules atomizer always · optional OpenRouter structured enrich on classify.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOMS_VERSION = "1.4.0"

PATH_RE = re.compile(
    r"(?:`([^`]+\.(?:md|json|py|sh|ts|tsx|html|css))`|"
    r"(?:^|\s)((?:scripts|docs|brain-os|infra|data|apps)/[\w./_-]+\.(?:md|json|py|sh)))",
    re.I | re.M,
)
API_RE = re.compile(r"\b(api/[a-z0-9_/-]+)\b", re.I)

ATOMIZER_SYSTEM = """You extract structured claim atoms from AI agent output.

Return ONLY valid JSON (no markdown):
{
  "atoms": [
    {
      "id": "a1",
      "text": "short claim line",
      "kind": "CLAIM|FACT|ACTION|ASSUMPTION|INSTRUCTION",
      "certainty": "high|medium|low",
      "object": "what it refers to",
      "action_verb": "verb or empty"
    }
  ]
}

Max 24 atoms. Plain English text fields. No jargon."""


def _ai_json_call(*, system: str, user: str, timeout_sec: int = 22) -> tuple[dict | None, str]:
    try:
        from ai_unify_api_v1 import dispatch_raw, pick_provider  # noqa: WPS433
    except ImportError:
        return None, "none"
    if pick_provider("auto") == "none":
        return None, "none"

    def _run() -> dict:
        return dispatch_raw(
            system=system,
            user=user[:10000],
            provider="auto",
            light_gate=True,
            source="chat-ord-atoms",
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            row = pool.submit(_run).result(timeout=timeout_sec)
    except (FutTimeout, Exception):
        return None, "timeout"
    raw = (row.get("response") or "").strip()
    if not row.get("ok") or not raw:
        return None, row.get("provider") or "failed"
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None, row.get("provider") or "ai"
    try:
        return json.loads(m.group(0)), row.get("provider") or "ai"
    except json.JSONDecodeError:
        return None, row.get("provider") or "ai"


def _kind_from_bucket(kind: str) -> str:
    k = (kind or "CLAIM").upper()
    if k == "FACT":
        return "FACT"
    if k == "INSTRUCTION":
        return "INSTRUCTION"
    if k == "ASSUMPTION":
        return "ASSUMPTION"
    if k == "NOISE":
        return "NOISE"
    return "CLAIM"


def build_atoms_rules(*, parsed: dict, buckets: dict) -> list[dict]:
    """Rules atomizer from classify buckets + parse segments."""
    atoms: list[dict] = []
    idx = 0

    def _add(text: str, kind: str, certainty: str = "medium") -> None:
        nonlocal idx
        from chat_ord_claim_rules_v1 import is_table_noise_line  # noqa: WPS433

        t = (text or "").strip()[:400]
        if not t or len(t) < 4 or is_table_noise_line(t):
            return
        idx += 1
        low = t.lower()
        action_verb = ""
        if kind in ("ACTION", "INSTRUCTION") or re.search(
            r"\b(run|execute|deploy|fix|add|create|build|ship|merge|move)\b", low
        ):
            m = re.search(
                r"\b(run|execute|deploy|fix|add|create|build|ship|merge|move|restart|curl)\b",
                low,
            )
            action_verb = m.group(1) if m else "act"
        atoms.append(
            {
                "id": f"a{idx}",
                "text": t,
                "kind": kind,
                "certainty": certainty,
                "object": t[:80],
                "action_verb": action_verb,
                "source_tag": "UNKNOWN",
                "disk_status": "n/a",
                "disk_ref": None,
            }
        )

    for line in parsed.get("actions") or []:
        _add(line, "ACTION", "medium")
    for line in parsed.get("assumptions") or []:
        _add(line, "ASSUMPTION", "low")
    for line in parsed.get("decisions") or []:
        _add(line, "CLAIM", "medium")
    for kind, lines in (buckets or {}).items():
        ck = _kind_from_bucket(kind)
        if ck == "NOISE":
            continue
        for line in lines or []:
            cert = "high" if ck == "FACT" else "medium" if ck == "CLAIM" else "low"
            _add(line, ck, cert)

    # Dedupe by text prefix
    seen: set[str] = set()
    deduped: list[dict] = []
    for a in atoms:
        key = a["text"][:100].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(a)
    for i, a in enumerate(deduped[:32], start=1):
        a["id"] = f"a{i}"
    from chat_ord_claim_rules_v1 import sanitize_atoms, tag_atoms_claim_types  # noqa: WPS433

    return tag_atoms_claim_types(sanitize_atoms(deduped[:32]))


def enrich_atoms_ai(*, draft: str, atoms: list[dict], use_ai: bool) -> tuple[list[dict], str]:
    if not use_ai or not atoms:
        return atoms, "rules"
    sample = json.dumps({"atoms": atoms[:12]}, ensure_ascii=False)[:3000]
    user = f"Draft excerpt:\n{draft[:5000]}\n\nExisting atoms (refine/add, max 24):\n{sample}"
    data, prov = _ai_json_call(system=ATOMIZER_SYSTEM, user=user)
    if not data or not isinstance(data.get("atoms"), list):
        return atoms, "rules"
    merged: list[dict] = []
    for i, row in enumerate(data["atoms"][:24], start=1):
        if not isinstance(row, dict) or not (row.get("text") or "").strip():
            continue
        merged.append(
            {
                "id": f"a{i}",
                "text": str(row.get("text", ""))[:400],
                "kind": _kind_from_bucket(str(row.get("kind", "CLAIM"))),
                "certainty": str(row.get("certainty") or "medium").lower()[:6],
                "object": str(row.get("object") or row.get("text", ""))[:120],
                "action_verb": str(row.get("action_verb") or "")[:40],
                "source_tag": "UNKNOWN",
                "disk_status": "n/a",
                "disk_ref": None,
            }
        )
    return merged or atoms, prov if merged else "rules"


def build_claim_graph(*, atoms: list[dict], issues: list[str], draft: str = "") -> dict:
    nodes = [
        {
            "id": a["id"],
            "label": a["text"][:100],
            "kind": a.get("kind"),
            "disk_status": a.get("disk_status"),
            "source_tag": a.get("source_tag"),
        }
        for a in atoms
    ]
    edges: list[dict] = []
    low = draft.lower()
    pass_atoms = [
        a
        for a in atoms
        if a.get("disk_status") not in ("skip", "opinion")
        and re.search(r"\bpass\b", a["text"], re.I)
    ]
    fail_atoms = [
        a
        for a in atoms
        if a.get("disk_status") not in ("skip", "opinion")
        and re.search(r"\bfail\b", a["text"], re.I)
    ]
    for pa in pass_atoms:
        for fa in fail_atoms:
            edges.append({"from": pa["id"], "to": fa["id"], "type": "contradicts", "reason": "pass_vs_fail"})

    if re.search(r"\bpass\b", low) and re.search(r"\bfail\b", low) and not edges:
        if len(atoms) >= 2:
            edges.append({"from": atoms[0]["id"], "to": atoms[1]["id"], "type": "contradicts", "reason": "text_pass_fail"})

    action_atoms = [a for a in atoms if a.get("kind") in ("ACTION", "INSTRUCTION")]
    claim_atoms = [a for a in atoms if a.get("kind") in ("CLAIM", "FACT")]
    for act in action_atoms[:3]:
        for cl in claim_atoms[:3]:
            if act["id"] != cl["id"] and act.get("disk_status") == "mismatch":
                edges.append({"from": cl["id"], "to": act["id"], "type": "depends", "reason": "mismatch_to_action"})

    seen_e: set[tuple] = set()
    uniq: list[dict] = []
    for e in edges:
        key = (e["from"], e["to"], e["type"])
        if key in seen_e:
            continue
        seen_e.add(key)
        uniq.append(e)

    # Refresh node labels with post-verify disk_status
    id_map = {a["id"]: a for a in atoms}
    for node in nodes:
        row = id_map.get(node["id"]) or {}
        node["disk_status"] = row.get("disk_status")
        node["source_tag"] = row.get("source_tag")
        node["verify_reason"] = row.get("verify_reason")

    return {"nodes": nodes, "edges": uniq[:48]}


def verify_atoms_on_disk(*, atoms: list[dict], disk: dict) -> list[dict]:
    from chat_ord_claim_rules_v1 import verify_atoms_on_disk as _verify  # noqa: WPS433

    return _verify(atoms=atoms, disk=disk)


def tag_atom_sources(*, atoms: list[dict], draft: str, issues: list[str]) -> list[dict]:
    low = draft.lower()
    out: list[dict] = []
    for a in atoms:
        row = dict(a)
        text = row["text"]
        tl = text.lower()
        tag = "AGENT"
        if row.get("disk_status") == "mismatch" or any("DISK:" in i for i in issues):
            if row.get("disk_status") in ("mismatch", "verified"):
                tag = "DISK"
        elif row.get("disk_status") == "opinion":
            tag = "AGENT"
        elif row.get("claim_type") == "LIVE_HTTP":
            tag = "AGENT"
        elif API_RE.search(text) and row.get("disk_status") != "verified":
            tag = "MODEL"
        elif re.search(r"\b(openrouter|claude|gpt|gemini|model)\b", tl):
            tag = "ROUTER"
        elif re.search(r"\b(i (fixed|updated|changed|committed|ran))\b", tl):
            tag = "EXECUTION"
        elif re.search(r"\b(wired|ssot|zero drift|validator pass)\b", tl):
            tag = "AGENT"
        elif re.search(r"\b(curl|bash|python3|git commit)\b", low):
            tag = "EXECUTION"
        row["source_tag"] = tag
        out.append(row)
    return out


def atom_stats(atoms: list[dict], graph: dict) -> dict:
    from chat_ord_claim_rules_v1 import atom_stats as _stats  # noqa: WPS433

    return _stats(atoms, graph)


def format_atoms_summary(atoms: list[dict], stats: dict) -> str:
    lines = [
        "Semantic atoms (rules v1)",
        f"· total: {stats.get('atom_count', 0)} · checkable: {stats.get('checkable_count', 0)}",
        f"· verified: {stats.get('verified', 0)} · unverified: {stats.get('unverified', 0)}",
        f"· mismatch: {stats.get('disk_mismatch', 0)} · opinion: {stats.get('opinion_count', 0)}",
        f"· skipped fragments: {stats.get('skipped_fragments', 0)}",
        "",
        "Sample atoms",
    ]
    for a in atoms[:5]:
        ds = a.get("disk_status", "n/a")
        ct = a.get("claim_type", "?")
        lines.append(f"· [{ct}|{ds}] {a['text'][:90]}")
    return "\n".join(lines)


def format_graph_summary(graph: dict, stats: dict) -> str:
    edges = (graph or {}).get("edges") or []
    contra = [e for e in edges if e.get("type") == "contradicts"]
    lines = [
        "Claim graph",
        f"· nodes: {len((graph or {}).get('nodes', []))} · edges: {stats.get('edge_count', 0)}",
        f"· contradictions: {stats.get('contradictions', 0)}",
        "",
        "Contradiction edges",
    ]
    if contra:
        for e in contra[:4]:
            lines.append(f"· {e.get('from')} → {e.get('to')} ({e.get('reason', 'contradicts')})")
    else:
        lines.append("· none detected")
    return "\n".join(lines)
