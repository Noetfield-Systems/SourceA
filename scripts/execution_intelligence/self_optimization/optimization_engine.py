"""Generate optimization candidates — suggestions only, never executed."""
from __future__ import annotations


def generate_candidates(
    *,
    performance: list[dict],
    strategies: list[dict],
    trends: list[dict],
    signals: list[dict],
) -> list[dict]:
    signal_by_action = {}
    for sig in signals:
        act = sig.get("action_id") or ""
        if act:
            signal_by_action.setdefault(act, []).append(sig)

    candidates: list[dict] = []
    strategy_by_action = {s["action_id"]: s for s in strategies}

    for row in performance:
        action_id = row["action_id"]
        strategy = strategy_by_action.get(action_id) or {}
        label = strategy.get("label", "neutral")
        trend = strategy.get("trend", "flat")

        if row["success_rate"] >= 0.7 and row["stability_score"] >= 0.5:
            candidates.append(
                {
                    "optimization_type": "increase_preference_weight",
                    "target": action_id,
                    "reason": f"High success ({row['success_rate']:.2f}) and stability ({row['stability_score']:.2f})",
                    "confidence": min(1.0, row["success_rate"] * 0.8 + row["stability_score"] * 0.2),
                }
            )
            candidates.append(
                {
                    "optimization_type": "prioritize_action",
                    "target": action_id,
                    "reason": f"Strategy label={label}; trend={trend}",
                    "confidence": strategy.get("confidence", 0.5),
                }
            )

        if row["failure_rate"] >= 0.4 or label == "failing":
            candidates.append(
                {
                    "optimization_type": "decrease_preference_weight",
                    "target": action_id,
                    "reason": f"Elevated failure rate ({row['failure_rate']:.2f})",
                    "confidence": min(1.0, row["failure_rate"]),
                }
            )
            candidates.append(
                {
                    "optimization_type": "deprioritize_action",
                    "target": action_id,
                    "reason": f"Failing strategy evidence; stability={row['stability_score']:.2f}",
                    "confidence": min(1.0, row["failure_rate"] * 0.9),
                }
            )

        if trend == "improving":
            candidates.append(
                {
                    "optimization_type": "raise_confidence_threshold",
                    "target": action_id,
                    "reason": "Performance trend improving — tighten confidence for sustained gains",
                    "confidence": strategy.get("confidence", 0.5),
                }
            )
        elif trend == "degrading":
            candidates.append(
                {
                    "optimization_type": "lower_confidence_threshold",
                    "target": action_id,
                    "reason": "Performance degrading — relax threshold to probe recovery paths",
                    "confidence": min(1.0, 0.5 + row["failure_rate"] * 0.3),
                }
            )

        for sig in signal_by_action.get(action_id, []):
            if sig.get("signal_type") == "avoid" and row["success_rate"] < 0.5:
                candidates.append(
                    {
                        "optimization_type": "deprioritize_action",
                        "target": action_id,
                        "reason": f"Avoid signal active: {(sig.get('reason') or '')[:80]}",
                        "confidence": float(sig.get("weight") or 0.5),
                    }
                )

    perf_trend = next((t for t in trends if t.get("trend_type") == "performance"), {})
    if perf_trend.get("direction") == "down":
        candidates.append(
            {
                "optimization_type": "lower_confidence_threshold",
                "target": "system",
                "reason": "Overall performance trend declining",
                "confidence": float(perf_trend.get("strength") or 0.5),
            }
        )
    elif perf_trend.get("direction") == "up":
        candidates.append(
            {
                "optimization_type": "raise_confidence_threshold",
                "target": "system",
                "reason": "Overall performance trend improving",
                "confidence": float(perf_trend.get("strength") or 0.5),
            }
        )

    # Deduplicate by type+target keeping highest confidence
    best: dict[tuple[str, str], dict] = {}
    for cand in candidates:
        key = (cand["optimization_type"], cand["target"])
        if key not in best or cand["confidence"] > best[key]["confidence"]:
            best[key] = cand

    out = list(best.values())
    out.sort(key=lambda c: (-c["confidence"], c["target"]))
    return out
