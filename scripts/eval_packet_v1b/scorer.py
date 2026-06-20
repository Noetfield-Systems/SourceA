"""Rubric scoring for Eval-1b — scaffold proxy and live reply grading.

Plan-eval-1b path citations (sa-0136): full repo paths required — basename-only
``runner.py`` / ``scorer.py`` must not count when multiple eval harness files exist.
"""
from __future__ import annotations

import re
from typing import Any

# plan-eval-1b — basename-only citations are ambiguous (sa-0136)
PLAN_EVAL_1B_PATHS: tuple[str, ...] = (
    "scripts/eval_packet_v1b/runner.py",
    "scripts/eval_packet_v1/runner.py",
    "scripts/eval_packet_v1b/scorer.py",
)
_BASENAME_ONLY_FORBIDDEN: frozenset[str] = frozenset(PLAN_EVAL_1B_PATHS)

_TOOL_CALL_RE = re.compile(
    r"<longcat_tool_call>[\s\S]*?</longcat_tool_call>|<tool_call>[\s\S]*?</tool_call>",
    re.IGNORECASE,
)


def sanitize_live_reply(reply: str) -> str:
    """Strip tool-call XML so failed tool attempts do not zero the packet arm score."""
    text = reply or ""
    text = _TOOL_CALL_RE.sub("", text)
    text = re.sub(r"<longcat_[^>]+>[^<]*</longcat_[^>]+>", "", text, flags=re.IGNORECASE)
    return text.strip()


def _flatten_packet_text(packet: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("schema", "generated_at", "path"):
                    continue
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, str) and obj.strip():
            parts.append(obj)

    walk(packet)
    return "\n".join(parts).lower()


def keyword_hit_rate(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    low = (text or "").lower()
    hits = sum(1 for kw in keywords if kw.lower() in low)
    return hits / len(keywords)


def _path_cited(path: str, text: str) -> bool:
    """True when reply cites a specific repo path (not ambiguous basename-only)."""
    low = (text or "").lower()
    p = (path or "").strip().lower()
    if not p or not low:
        return False
    if p in low or f"`{p}`" in low:
        return True
    parts = p.split("/")
    if len(parts) >= 2 and "/".join(parts[-2:]) in low:
        return True
    if len(parts) >= 3 and "/".join(parts[-3:]) in low:
        return True
    return False


def expected_path_hits(text: str, paths: list[str]) -> int:
    if not paths:
        return 0
    low = (text or "").lower()
    basenames: dict[str, int] = {}
    for p in paths:
        base = p.split("/")[-1].lower()
        basenames[base] = basenames.get(base, 0) + 1
    hits = 0
    for p in paths:
        if _path_cited(p, low):
            hits += 1
            continue
        base = p.split("/")[-1].lower()
        if p in _BASENAME_ONLY_FORBIDDEN:
            continue
        if basenames.get(base, 0) == 1 and re.search(rf"(?<![\w./-]){re.escape(base)}(?![\w.-])", low):
            hits += 1
    return hits


def cross_check_plan_eval_1b_path_citations() -> list[str]:
    """Harden plan-eval-1b path citation rules (sa-0136)."""
    errors: list[str] = []
    paths = list(PLAN_EVAL_1B_PATHS)
    weak = "Use runner.py for the eval harness."
    if expected_path_hits(weak, paths) != 0:
        errors.append("basename-only runner.py must not count")
    one = "See scripts/eval_packet_v1b/runner.py for live_pilot A/B."
    if expected_path_hits(one, paths) != 1:
        errors.append(f"full runner path expected 1 hit, got {expected_path_hits(one, paths)}")
    two = (
        "Compare `scripts/eval_packet_v1b/runner.py` vs "
        "`scripts/eval_packet_v1/runner.py`; scoring in eval_packet_v1b/scorer.py."
    )
    if expected_path_hits(two, paths) != 3:
        errors.append(f"three-path citation expected 3 hits, got {expected_path_hits(two, paths)}")
    scorer_only = "Tune scorer.py composite weights for live A/B."
    if expected_path_hits(scorer_only, paths) != 0:
        errors.append("basename-only scorer.py must not count for plan-eval-1b")
    scorer_full = "Weights live in scripts/eval_packet_v1b/scorer.py."
    if expected_path_hits(scorer_full, paths) != 1:
        errors.append("full scorer path expected 1 hit")
    return errors


def scaffold_arm_score(*, arm: str, prompt: str, packet: dict | None, keywords: list[str]) -> dict[str, Any]:
    if arm == "raw":
        text = prompt
        readiness = 0.0
        sections = 0
    else:
        pkt = packet or {}
        text = _flatten_packet_text(pkt)
        val = pkt.get("_validation") or {}
        readiness = float(val.get("readiness_score") or 0) / 100.0
        raw_sections = val.get("populated_sections") or 0
        sections = len(raw_sections) if isinstance(raw_sections, list) else int(raw_sections or 0)
    kw_rate = keyword_hit_rate(text, keywords)
    grounding = min(1.0, len(re.findall(r"[\w./-]+\.(py|md|json|sh)", text)) / 5.0)
    actionability = min(1.0, sections / 8.0) if arm == "packet" else 0.05
    composite = round(0.45 * kw_rate + 0.30 * readiness + 0.15 * grounding + 0.10 * actionability, 4)
    return {
        "arm": arm,
        "keyword_hit_rate": round(kw_rate, 4),
        "readiness_norm": round(readiness, 4),
        "grounding": round(grounding, 4),
        "actionability": round(actionability, 4),
        "composite": composite,
    }


def live_reply_score(
    reply: str,
    keywords: list[str],
    *,
    expected_paths: list[str] | None = None,
) -> dict[str, Any]:
    text = sanitize_live_reply(reply)
    paths = list(expected_paths or [])
    kw_rate = keyword_hit_rate(text, keywords)
    structured = 1.0 if re.search(r"(?m)^\s*(\d+[\).\]]|[-*])", text) else 0.0
    cites_code = 1.0 if re.search(r"`[^`]+`|\.py\b|\.md\b|scripts/", text) else 0.0
    path_hits = expected_path_hits(text, paths)
    path_rate = (path_hits / len(paths)) if paths else 0.0
    composite = round(
        0.40 * kw_rate + 0.20 * structured + 0.15 * cites_code + 0.25 * path_rate,
        4,
    )
    return {
        "keyword_hit_rate": round(kw_rate, 4),
        "structured": structured,
        "cites_code": cites_code,
        "expected_path_hits": path_hits,
        "expected_path_rate": round(path_rate, 4),
        "composite": composite,
        "reply_preview": text[:240],
    }


def live_packet_wins(
    raw_score: dict[str, Any],
    pkt_score: dict[str, Any],
    *,
    ok_raw: bool,
    ok_pkt: bool,
) -> bool:
    if not ok_pkt:
        return False
    if not ok_raw:
        return True
    if pkt_score["composite"] > raw_score["composite"]:
        return True
    if pkt_score["composite"] < raw_score["composite"]:
        return False
    pkt_paths = pkt_score.get("expected_path_hits") or 0
    raw_paths = raw_score.get("expected_path_hits") or 0
    return pkt_paths >= raw_paths and pkt_paths > 0
