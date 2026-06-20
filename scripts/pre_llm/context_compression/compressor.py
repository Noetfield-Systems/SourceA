"""Hierarchical compression of ranked evidence — no re-rank, no LLM."""
from __future__ import annotations

from typing import Any

from pre_llm.context_compression.token_estimator import estimate_tokens, trim_to_token_budget


def _plan_headlines(d10: dict[str, Any], *, limit: int = 5) -> list[str]:
    nodes = sorted(
        (d10.get("graph") or {}).get("nodes") or [],
        key=lambda n: int(n.get("order") or 99),
    )
    lines: list[str] = []
    for n in nodes[:limit]:
        title = (n.get("title") or n.get("id") or "").strip()
        if title:
            lines.append(f"- {title}")
    return lines


def _validation_headline(d12: dict[str, Any]) -> str:
    fails = int(d12.get("fail_count") or 0)
    checks = int(d12.get("check_count") or 0)
    if d12.get("validation_ready") and fails == 0:
        return f"Validation: PASS ({checks} checks, 0 fails)"
    return f"Validation: not ready (fails={fails})"


def _diff_headlines(d13: dict[str, Any], *, limit: int = 4) -> list[str]:
    high = (d13.get("impact_map") or {}).get("high_impact_paths") or []
    lines: list[str] = []
    for path in high[:limit]:
        lines.append(f"- high-impact change: {path}")
    if not lines:
        for c in (d13.get("changes") or [])[:limit]:
            p = c.get("path") or ""
            if p:
                lines.append(f"- {c.get('kind', 'change')}: {p}")
    return lines


def compress_substrates(
    *,
    input_text: str,
    token_limit: int,
    d4: dict[str, Any],
    d9: dict[str, Any],
    d10: dict[str, Any],
    d12: dict[str, Any],
    d13: dict[str, Any],
) -> dict[str, Any]:
    goal = d4.get("goal_class") or "other"
    ranked = list(d9.get("ranked_evidence") or [])
    ranked.sort(key=lambda r: int(r.get("rank") or 999))

    layers: list[dict[str, Any]] = []
    packed: list[dict[str, Any]] = []
    tokens_used = 0

    intent_block = f"Goal: {goal}\nTask: {input_text[:200]}"
    intent_tokens = estimate_tokens(intent_block)
    tokens_used += intent_tokens
    layers.append(
        {
            "layer": "intent",
            "tokens": intent_tokens,
            "items_in": 1,
            "items_out": 1,
            "summary": intent_block[:240],
        }
    )

    plan_lines = _plan_headlines(d10)
    plan_block = "Plan:\n" + "\n".join(plan_lines) if plan_lines else "Plan: (none)"
    plan_tokens = estimate_tokens(plan_block)
    tokens_used += plan_tokens
    layers.append(
        {
            "layer": "plan",
            "tokens": plan_tokens,
            "items_in": len((d10.get("graph") or {}).get("nodes") or []),
            "items_out": len(plan_lines),
            "summary": plan_block[:320],
        }
    )

    evidence_budget = max(256, int(token_limit * 0.55) - tokens_used)
    evidence_lines: list[str] = []
    for row in ranked:
        summary = (row.get("summary") or "")[:180]
        path = row.get("path") or row.get("evidence_id") or ""
        line = f"- [{row.get('source_step')}] {path}: {summary}"
        line_tokens = estimate_tokens(line)
        if sum(estimate_tokens(x) for x in evidence_lines) + line_tokens > evidence_budget:
            break
        evidence_lines.append(line)
        packed.append(
            {
                "rank": row.get("rank"),
                "evidence_id": row.get("evidence_id"),
                "path": row.get("path"),
                "source_step": row.get("source_step"),
                "summary": summary,
                "score": row.get("score"),
                "tokens": line_tokens,
            }
        )
    evidence_block = "Evidence:\n" + "\n".join(evidence_lines) if evidence_lines else "Evidence: (none)"
    evidence_tokens = estimate_tokens(evidence_block)
    tokens_used += evidence_tokens
    layers.append(
        {
            "layer": "ranking",
            "tokens": evidence_tokens,
            "items_in": len(ranked),
            "items_out": len(packed),
            "summary": evidence_block[:400],
        }
    )

    diff_lines = _diff_headlines(d13)
    diff_block = "Changes:\n" + "\n".join(diff_lines) if diff_lines else ""
    diff_tokens = estimate_tokens(diff_block) if diff_block else 0
    if diff_tokens:
        tokens_used += diff_tokens
        layers.append(
            {
                "layer": "diff",
                "tokens": diff_tokens,
                "items_in": len(d13.get("changes") or []),
                "items_out": len(diff_lines),
                "summary": diff_block[:320],
            }
        )

    val_line = _validation_headline(d12)
    val_tokens = estimate_tokens(val_line)
    tokens_used += val_tokens
    layers.append(
        {
            "layer": "validation",
            "tokens": val_tokens,
            "items_in": int(d12.get("check_count") or 0),
            "items_out": 1,
            "summary": val_line,
        }
    )

    narrative_parts = [intent_block, plan_block, evidence_block]
    if diff_block:
        narrative_parts.append(diff_block)
    narrative_parts.append(val_line)
    narrative = "\n\n".join(p for p in narrative_parts if p.strip())
    narrative = trim_to_token_budget(narrative, token_limit)
    narrative_tokens = estimate_tokens(narrative)
    tokens_used = max(tokens_used, narrative_tokens)

    raw_tokens = sum(
        estimate_tokens((r.get("summary") or "") + (r.get("path") or ""))
        for r in ranked[: len(packed) + 4]
    )
    tokens_saved = max(0, raw_tokens - tokens_used)

    budget = {
        "token_limit": token_limit,
        "tokens_used": tokens_used,
        "tokens_saved": tokens_saved,
        "within_budget": tokens_used <= token_limit,
        "evidence_in": len(ranked),
        "evidence_out": len(packed),
    }

    return {
        "budget": budget,
        "layers": layers,
        "packed_evidence": packed,
        "narrative": narrative,
        "compression_ready": bool(narrative.strip()) and token_limit > 0 and budget["within_budget"],
    }
