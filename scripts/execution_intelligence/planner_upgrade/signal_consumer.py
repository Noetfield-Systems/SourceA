"""Convert feedback signals into planner weights (read-only)."""
from __future__ import annotations

SIGNAL_WEIGHTS = {
    "prefer": 30.0,
    "reinforce": 25.0,
    "avoid": -40.0,
    "deprioritize": -20.0,
}


def consume_signals(signals: list[dict]) -> dict[str, dict]:
    """
    Per action_id:
      prefer_weight, avoid_weight, reinforce_weight, deprioritize_weight,
      signal_score (sum of typed contributions)
    """
    by_action: dict[str, dict] = {}

    for sig in signals:
        action = sig.get("action_id") or ""
        st = sig.get("signal_type") or ""
        if not action or st not in SIGNAL_WEIGHTS:
            continue
        weight = float(sig.get("weight") or 0)
        row = by_action.setdefault(
            action,
            {
                "prefer_weight": 0.0,
                "avoid_weight": 0.0,
                "reinforce_weight": 0.0,
                "deprioritize_weight": 0.0,
                "signal_score": 0.0,
                "active_signals": [],
            },
        )
        contribution = SIGNAL_WEIGHTS[st] * weight
        row["signal_score"] += contribution
        key = f"{st}_weight"
        row[key] = max(row[key], weight)
        row["active_signals"].append(
            {
                "signal_id": sig.get("signal_id"),
                "signal_type": st,
                "weight": weight,
                "reason": sig.get("reason") or "",
            }
        )

    for row in by_action.values():
        row["signal_score"] = round(row["signal_score"], 2)
        for key in ("prefer_weight", "avoid_weight", "reinforce_weight", "deprioritize_weight"):
            row[key] = round(row[key], 3)
    return by_action
