"""Resolve traversal seeds from text, explicit target, or D1 index."""
from __future__ import annotations

import re
from typing import Any


def _paths_from_text(text: str) -> list[str]:
    found = re.findall(r"[\w./-]+\.(?:py|sh|md|json|js|ts)", text, re.I)
    out: list[str] = []
    for p in found:
        if p not in out:
            out.append(p)
    return out


def resolve_seeds(
    *,
    text: str,
    target: str,
    target_type: str,
    d1: dict[str, Any] | None,
    d3: dict[str, Any],
) -> list[dict[str, str]]:
    seeds: list[dict[str, str]] = []

    if target:
        seeds.append({"type": target_type or "file", "value": target})

    for path in _paths_from_text(text):
        seeds.append({"type": "file", "value": path})

    if d1 and text:
        symbols = d1.get("symbols") or {}
        norm = text.lower()
        for name in list(symbols.keys())[:200]:
            if name.lower() in norm or name in text:
                seeds.append({"type": "symbol", "value": name})

    if not seeds:
        stats = d3.get("graph_stats") or {}
        if stats.get("file_edges", 0) > 0:
            sample = (d3.get("file_graph") or [{}])[0]
            if sample.get("from"):
                seeds.append({"type": "file", "value": sample["from"]})

    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, str]] = []
    for s in seeds:
        key = (s["type"], s["value"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(s)
    return deduped[:8]
