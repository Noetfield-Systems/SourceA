"""Rule-based goal classification — no LLM (D4 law)."""
from __future__ import annotations

import re
from typing import Any

GOAL_CLASSES = (
    "fix",
    "build",
    "refactor",
    "debug",
    "audit",
    "explain",
    "validate",
    "ship",
    "explore",
    "other",
)

# (goal_class, weight, patterns)
_SIGNALS: list[tuple[str, float, tuple[str, ...]]] = [
    ("fix", 1.0, ("fix", "bug", "broken", "error", "fail", "failing", "crash", "repair", "resolve", "issue")),
    ("build", 1.0, ("build", "implement", "create", "add", "write", "develop", "scaffold", "ship d", "d4", "d5")),
    ("refactor", 1.0, ("refactor", "restructure", "reorganize", "simplify", "dedupe", "clean up", "cleanup")),
    ("debug", 0.95, ("debug", "trace", "investigate", "diagnose", "root cause", "why does", "why is")),
    ("audit", 0.9, ("audit", "review", "scan", "alignment", "align", "maturity", "system status")),
    ("explain", 0.85, ("explain", "what is", "how does", "describe", "document", "meaning")),
    ("validate", 0.95, ("validate", "verify", "test", "smoke", "green", "pass", "validator")),
    ("ship", 0.9, ("ship", "deploy", "release", "publish", "merge", "pull request", " pr ")),
    ("explore", 0.8, ("explore", "find", "search", "where is", "locate", "show me", "list ")),
]


def _normalize(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return f" {t} "


def score_goal_classes(text: str) -> dict[str, float]:
    norm = _normalize(text)
    scores: dict[str, float] = {g: 0.0 for g in GOAL_CLASSES}
    for goal, weight, patterns in _SIGNALS:
        for pat in patterns:
            if pat in norm:
                scores[goal] += weight
    if scores.get("build", 0) and re.search(r"\bd[0-9]+\b", norm):
        scores["build"] += 0.5
    if scores.get("fix", 0) and scores.get("validate", 0):
        scores["fix"] += 0.25
    top = max(scores.values()) if scores else 0.0
    if top <= 0:
        scores["other"] = 1.0
    return scores


def classify_goal(text: str) -> dict[str, Any]:
    scores = score_goal_classes(text)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    best_class, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    total = sum(scores.values()) or 1.0
    confidence = round(min(1.0, best_score / max(total * 0.55, 0.01)), 3)
    if best_class == "other" and best_score <= 1.0:
        confidence = round(0.35, 3)
    return {
        "goal_class": best_class,
        "confidence": confidence,
        "scores": {k: round(v, 3) for k, v in scores.items() if v > 0},
        "runner_up": ranked[1][0] if second_score > 0 and second_score >= best_score * 0.75 else None,
        "runner_up_score": round(second_score, 3) if second_score > 0 else 0.0,
    }
