#!/usr/bin/env python3
"""Brain retrieval engine — rules-first + BM25 hybrid + confidence scoring."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_lib_v1 import classify_intent, infer_page_context, search_chunks  # noqa: E402

RULE_KINDS = {"rule", "rules"}
MIN_CONFIDENCE_FLOOR = 0.15


def split_corpus(chunks: list[dict]) -> tuple[list[dict], list[dict]]:
    rules = [c for c in chunks if c.get("kind") in RULE_KINDS or c.get("lane") == "rules"]
    knowledge = [c for c in chunks if c not in rules]
    return rules, knowledge


def dedupe_hits(hits: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for h in hits:
        key = h.get("source_path") or h.get("id") or h.get("content", "")[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


def compute_confidence(hits: list[dict]) -> dict:
    if not hits:
        return {"score": 0.0, "level": "low", "hits": 0}
    scores = [float(h.get("score") or 0) for h in hits]
    top = max(scores) if scores else 0.0
    avg = sum(scores) / len(scores) if scores else 0.0
    # normalize roughly to 0-1
    norm = min(1.0, top / 8.0)
    level = "high" if norm >= 0.55 else "medium" if norm >= 0.25 else "low"
    return {
        "score": round(norm, 3),
        "level": level,
        "hits": len(hits),
        "top_score": round(top, 3),
        "avg_score": round(avg, 3),
    }


def retrieve(
    chunks: list[dict],
    query: str,
    *,
    k_rules: int = 4,
    k_knowledge: int = 8,
    lane: str | None = None,
    page_path: str = "",
    sa_page: str = "",
    page_ctx: dict | None = None,
) -> dict:
    rules, knowledge = split_corpus(chunks)
    intent = lane or classify_intent(query)
    ctx = page_ctx or infer_page_context(page_path, sa_page)

    rule_hits = search_chunks(rules, query, k=k_rules, lane="rules", page_ctx=ctx) if rules else []
    if not rule_hits and rules:
        rule_hits = [r for r in rules if r.get("pinned")][:k_rules]

    know_hits = search_chunks(knowledge, query, k=k_knowledge, lane=intent, page_ctx=ctx) if knowledge else []
    if not know_hits and knowledge:
        know_hits = [c for c in knowledge if c.get("pinned")][:3]

    merged = dedupe_hits(rule_hits + know_hits)
    confidence = compute_confidence(merged)
    sources = sorted({h.get("source_path") for h in merged if h.get("source_path")})

    return {
        "intent": intent,
        "page_path": ctx.get("page_path"),
        "page_lane": ctx.get("page_lane"),
        "hits": merged,
        "rules_applied": len(rule_hits),
        "knowledge_hits": len(know_hits),
        "sources_consulted": len(sources),
        "source_paths": sources[:20],
        "chunk_ids": [h.get("id") for h in merged if h.get("id")][:20],
        "confidence": confidence,
    }


def assemble_prompt(base_core: str, retrieval: dict) -> tuple[str, list[dict]]:
    hits = retrieval.get("hits") or []
    if not hits:
        return base_core, []

    rules_block = []
    know_block = []
    for h in hits:
        cite = f" ({h['www_url']})" if h.get("www_url") else ""
        block = f"### {h.get('source_path')}{cite}\n{h.get('content', '')}"
        if h.get("kind") in RULE_KINDS or h.get("lane") == "rules":
            rules_block.append(block)
        else:
            know_block.append(block)

    citations = [
        {
            "source_path": h.get("source_path"),
            "www_url": h.get("www_url"),
            "lane": h.get("lane"),
            "score": h.get("score"),
            "kind": h.get("kind", "doc"),
        }
        for h in hits
    ]

    conf = retrieval.get("confidence") or {}
    prompt = f"""{base_core}

BRAIN RETRIEVAL ({retrieval.get('sources_consulted', 0)} live sources · confidence {conf.get('level', 'unknown')} · intent {retrieval.get('intent')})
Answer ONLY from the blocks below + your core identity. If blocks lack detail, say so and link a relevant /sourcea/ page.

PUBLIC RULES (mandatory — never violate):
{chr(10).join(rules_block) if rules_block else '- Follow agentic-first and grounded-only rules.'}

LIVE KNOWLEDGE (cite URLs when used):
{chr(10).join(know_block) if know_block else '- No specific page matched — use rules + suggest Forge Terminal demo.'}
"""
    return prompt.strip(), citations
