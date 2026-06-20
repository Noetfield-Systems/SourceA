"""Generate structured why statements from causal signals."""
from __future__ import annotations

CauseType = str  # success_cause | failure_cause | fix_cause | constraint


def build_why_summary(
    *,
    cause_type: CauseType,
    action_id: str,
    cause_signal: str,
    effect_signal: str,
) -> str:
    if cause_type == "success_cause":
        return f"'{action_id}' succeeded because {cause_signal} produced {effect_signal}."
    if cause_type == "failure_cause":
        return f"'{action_id}' failed because {cause_signal} led to {effect_signal}."
    if cause_type == "fix_cause":
        return f"'{action_id}' recovered: {cause_signal} was resolved by {effect_signal}."
    if cause_type == "constraint":
        return f"'{action_id}' was blocked by constraint: {cause_signal} → {effect_signal}."
    return f"'{action_id}': {cause_signal} → {effect_signal}."


def confidence_from_pattern(pattern: dict | None, *, base: float = 0.45) -> float:
    if not pattern:
        return round(base, 3)
    freq = pattern.get("frequency") or 1
    pat_conf = float(pattern.get("confidence") or 0.5)
    return round(min(0.99, base + pat_conf * 0.35 + min(freq, 8) * 0.02), 3)
