"""Compute weighted action ranking from mapped influence signals."""
from __future__ import annotations

POSITIVE = frozenset({"prefer", "reinforce"})
NEGATIVE = frozenset({"avoid", "deprioritize"})


def build_ranking(mapped_signals: list[dict]) -> list[dict]:
    """Higher score = stronger future preference (influence only — not planning)."""
    by_action: dict[str, dict] = {}

    for sig in mapped_signals:
        action = sig.get("action_id") or ""
        if not action:
            continue
        st = sig.get("signal_type") or ""
        weight = float(sig.get("weight") or 0)
        row = by_action.setdefault(
            action,
            {
                "action_id": action,
                "score": 0.0,
                "prefer_weight": 0.0,
                "avoid_weight": 0.0,
                "reinforce_weight": 0.0,
                "deprioritize_weight": 0.0,
                "signal_types": [],
            },
        )
        if st in POSITIVE:
            row["score"] += weight * 100
            if st == "prefer":
                row["prefer_weight"] = max(row["prefer_weight"], weight)
            else:
                row["reinforce_weight"] = max(row["reinforce_weight"], weight)
        elif st in NEGATIVE:
            row["score"] -= weight * 100
            if st == "avoid":
                row["avoid_weight"] = max(row["avoid_weight"], weight)
            else:
                row["deprioritize_weight"] = max(row["deprioritize_weight"], weight)
        if st and st not in row["signal_types"]:
            row["signal_types"].append(st)

    ranking = list(by_action.values())
    for row in ranking:
        row["score"] = round(row["score"], 2)
        for key in ("prefer_weight", "avoid_weight", "reinforce_weight", "deprioritize_weight"):
            row[key] = round(row[key], 3)
        row["net_influence"] = round(
            row["prefer_weight"] + row["reinforce_weight"] - row["avoid_weight"] - row["deprioritize_weight"],
            3,
        )

    ranking.sort(key=lambda r: (-r["score"], r["action_id"]))
    return ranking


def actions_by_type(mapped_signals: list[dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {t: [] for t in ("prefer", "avoid", "reinforce", "deprioritize")}
    for sig in mapped_signals:
        st = sig.get("signal_type") or ""
        action = sig.get("action_id") or ""
        if st in grouped and action and action not in grouped[st]:
            grouped[st].append(action)
    for key in grouped:
        grouped[key] = sorted(grouped[key])
    return grouped
