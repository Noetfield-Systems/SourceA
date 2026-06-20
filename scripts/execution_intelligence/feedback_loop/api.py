"""Feedback Loop v1 — hub API."""
from __future__ import annotations

from execution_intelligence.feedback_loop.loop_engine import (
    SIGNALS_PATH,
    read_signals,
    run_feedback_loop,
)
from execution_intelligence.feedback_loop.priority_adjuster import actions_by_type, build_ranking


def feedback_v1_payload() -> dict:
    result = run_feedback_loop()
    signals = read_signals(limit=500)
    if not signals and result.get("mapped_signals"):
        signals = result["mapped_signals"]

    grouped = actions_by_type(signals)
    ranking = result.get("ranking") or build_ranking(signals)

    by_type: dict[str, list[dict]] = {t: [] for t in ("prefer", "avoid", "reinforce", "deprioritize")}
    for sig in signals:
        st = sig.get("signal_type") or ""
        if st in by_type:
            by_type[st].append(sig)

    return {
        "ok": True,
        "schema": "execution-feedback-v1",
        "path": str(SIGNALS_PATH),
        "skipped": result.get("skipped", False),
        "updated_at": result.get("updated_at"),
        "active_signals": signals,
        "prefer_actions": grouped["prefer"],
        "avoid_actions": grouped["avoid"],
        "reinforcement_signals": by_type["reinforce"],
        "deprioritized_actions": grouped["deprioritize"],
        "weighted_ranking_summary": ranking,
        "signal_counts": {
            "total": len(signals),
            "prefer": len(grouped["prefer"]),
            "avoid": len(grouped["avoid"]),
            "reinforce": len(by_type["reinforce"]),
            "deprioritize": len(grouped["deprioritize"]),
        },
    }
