"""Derive behavioral influence signals from patterns + decisions (read-only inputs)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from execution_intelligence.pattern_engine.helpers import action_from_pattern

SIGNAL_TYPES = ("prefer", "avoid", "reinforce", "deprioritize")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _action_from_decision(decision: dict) -> str:
    if decision.get("action_id"):
        return str(decision["action_id"])
    why = decision.get("why_summary") or ""
    if why.startswith("'") and "'" in why[1:]:
        return why[1 : why.index("'", 1)]
    return ""


def _signal(
    signal_type: str,
    action_id: str,
    weight: float,
    reason: str,
    *,
    pattern_id: str = "",
    decision_id: str = "",
) -> dict:
    return {
        "signal_id": str(uuid.uuid4()),
        "signal_type": signal_type,
        "action_id": action_id,
        "weight": round(max(0.0, min(1.0, weight)), 3),
        "reason": reason,
        "source_pattern_id": pattern_id,
        "source_decision_id": decision_id,
        "created_at": _now(),
    }


def _signals_from_pattern(pattern: dict) -> list[dict]:
    action = action_from_pattern(pattern)
    if not action:
        return []

    pid = pattern.get("pattern_id") or ""
    ptype = pattern.get("type") or ""
    freq = int(pattern.get("frequency") or 0)
    conf = float(pattern.get("confidence") or 0)
    sig = pattern.get("signature") or ""
    out: list[dict] = []

    if ptype == "success":
        if freq >= 2:
            out.append(
                _signal(
                    "prefer",
                    action,
                    0.5 + min(freq * 0.08, 0.4),
                    f"Repeated successful outcomes ({freq}x) — {sig}",
                    pattern_id=pid,
                )
            )
        elif freq >= 1:
            out.append(
                _signal(
                    "prefer",
                    action,
                    0.35 + conf * 0.25,
                    f"Successful outcome pattern — {sig}",
                    pattern_id=pid,
                )
            )
        if conf >= 0.7:
            out.append(
                _signal(
                    "reinforce",
                    action,
                    conf,
                    f"High-confidence success pattern ({conf:.2f}) — {sig}",
                    pattern_id=pid,
                )
            )

    if ptype == "failure":
        if freq >= 2:
            out.append(
                _signal(
                    "avoid",
                    action,
                    0.6 + min(freq * 0.08, 0.35),
                    f"Repeated failures ({freq}x) — {sig}",
                    pattern_id=pid,
                )
            )
        else:
            out.append(
                _signal(
                    "avoid",
                    action,
                    0.45 + conf * 0.2,
                    f"Failure pattern detected — {sig}",
                    pattern_id=pid,
                )
            )

    if ptype == "repetition":
        out.append(
            _signal(
                "deprioritize",
                action,
                0.45 + conf * 0.2,
                f"Unstable repetition ({freq}x) — {sig}",
                pattern_id=pid,
            )
        )

    if conf < 0.55 and ptype in ("success", "failure"):
        out.append(
            _signal(
                "deprioritize",
                action,
                max(0.25, 0.6 - conf),
                f"Low-confidence pattern ({conf:.2f}) — {sig}",
                pattern_id=pid,
            )
        )

    return out


def _signals_from_decision(decision: dict) -> list[dict]:
    action = _action_from_decision(decision)
    if not action:
        return []

    did = decision.get("decision_id") or ""
    pid = decision.get("pattern_id") or ""
    cause = decision.get("cause_type") or ""
    conf = float(decision.get("confidence") or 0)
    why = (decision.get("why_summary") or "")[:160]
    out: list[dict] = []

    if cause == "success_cause":
        if conf >= 0.7:
            out.append(_signal("reinforce", action, conf, why, pattern_id=pid, decision_id=did))
        else:
            out.append(_signal("prefer", action, 0.4 + conf * 0.3, why, pattern_id=pid, decision_id=did))
    elif cause == "failure_cause":
        out.append(_signal("avoid", action, 0.55 + conf * 0.25, why, pattern_id=pid, decision_id=did))
    elif cause == "fix_cause":
        out.append(_signal("reinforce", action, conf * 0.9, why, pattern_id=pid, decision_id=did))
    elif cause == "constraint":
        out.append(_signal("deprioritize", action, 0.6, why, pattern_id=pid, decision_id=did))

    return out


def generate_signals(patterns: list[dict], decisions: list[dict]) -> list[dict]:
    """Raw signals before influence mapping."""
    signals: list[dict] = []
    for pattern in patterns:
        signals.extend(_signals_from_pattern(pattern))
    for decision in decisions:
        signals.extend(_signals_from_decision(decision))
    return signals
