"""Ambiguity + missing-context detection for user goals."""
from __future__ import annotations

import re
from typing import Any

_AMBIGUITY_CODES = (
    "too_short",
    "vague_target",
    "multi_goal",
    "missing_scope",
    "contradictory_verbs",
    "unclear_priority",
)

_SCOPE_GOALS = frozenset({"fix", "refactor", "debug", "validate", "build"})
_PATH_HINT = re.compile(r"[\w./-]+\.(py|sh|md|json|tsx?|jsx?)\b")
_MODULE_HINT = re.compile(r"\b(?:pre_llm|scripts|runtime)\.[\w.]+\b")
_STEP_HINT = re.compile(r"\bD[0-9]{1,2}\b", re.I)


def detect_ambiguity(*, text: str, classification: dict[str, Any]) -> dict[str, Any]:
    raw = (text or "").strip()
    norm = raw.lower()
    words = [w for w in re.split(r"\W+", norm) if w]
    flags: list[dict[str, Any]] = []

    if len(raw) < 8 or len(words) < 2:
        flags.append({"code": "too_short", "severity": "high", "detail": "Input too short to classify reliably"})

    if re.search(r"\b(it|this|that|them)\b", norm) and not (_PATH_HINT.search(raw) or _MODULE_HINT.search(raw)):
        flags.append({"code": "vague_target", "severity": "medium", "detail": "Pronoun target without file/module anchor"})

    scores = classification.get("scores") or {}
    active = [(k, v) for k, v in scores.items() if k != "other" and v > 0]
    if len(active) >= 2:
        top, second = sorted(active, key=lambda kv: -kv[1])[:2]
        if second[1] >= top[1] * 0.75:
            flags.append(
                {
                    "code": "multi_goal",
                    "severity": "medium",
                    "detail": f"Competing goals: {top[0]} vs {second[0]}",
                    "candidates": [top[0], second[0]],
                }
            )

    goal = classification.get("goal_class") or "other"
    if goal in _SCOPE_GOALS and not (_PATH_HINT.search(raw) or _MODULE_HINT.search(raw) or _STEP_HINT.search(raw)):
        flags.append({"code": "missing_scope", "severity": "medium", "detail": "No file/module/step scope detected"})

    fix_s = scores.get("fix", 0)
    build_s = scores.get("build", 0)
    ship_s = scores.get("ship", 0)
    if fix_s > 0 and build_s > 0 and abs(fix_s - build_s) < 0.5:
        flags.append({"code": "contradictory_verbs", "severity": "low", "detail": "Both fix and build signals present"})

    if " and also " in norm or " then " in norm:
        if classification.get("runner_up"):
            flags.append(
                {
                    "code": "unclear_priority",
                    "severity": "low",
                    "detail": "Multi-clause request — primary goal may be ambiguous",
                }
            )

    severity_rank = {"high": 3, "medium": 2, "low": 1}
    flags.sort(key=lambda f: -severity_rank.get(f.get("severity", ""), 0))
    return {
        "ambiguity_flags": flags,
        "ambiguity_score": round(min(1.0, len(flags) * 0.22), 3),
        "needs_clarification": any(f.get("severity") == "high" for f in flags)
            or sum(1 for f in flags if f.get("severity") == "medium") >= 2,
    }
