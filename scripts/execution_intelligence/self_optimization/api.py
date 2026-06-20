"""Self-Optimization Loop v1 — observe, measure, compare, suggest (no auto-execute)."""
from __future__ import annotations

from datetime import datetime, timezone

from execution_intelligence.self_optimization.optimization_engine import generate_candidates
from execution_intelligence.self_optimization.optimization_memory import (
    SSOT_PATH,
    input_fingerprint,
    load_inputs,
    load_snapshot,
    mark_built,
    should_skip,
    write_snapshot,
)
from execution_intelligence.self_optimization.performance_tracker import track_performance
from execution_intelligence.self_optimization.recommendation_generator import generate_recommendations
from execution_intelligence.self_optimization.strategy_analyzer import analyze_strategies
from execution_intelligence.self_optimization.trend_detector import detect_trends

SCHEMA = "self-optimization-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summaries(performance: list[dict], strategies: list[dict], trends: list[dict], recommendations: list[dict]) -> dict:
    best = performance[0] if performance else {}
    worst = min(performance, key=lambda p: p["success_rate"]) if performance else {}
    improving = [s for s in strategies if s.get("trend") == "improving"]
    degrading = [s for s in strategies if s.get("trend") == "degrading"]
    return {
        "performance_summary": {
            "actions_tracked": len(performance),
            "best_action": best.get("action_id"),
            "best_success_rate": best.get("success_rate"),
            "worst_action": worst.get("action_id"),
            "worst_success_rate": worst.get("success_rate"),
            "avg_stability": round(sum(p["stability_score"] for p in performance) / max(len(performance), 1), 3),
        },
        "trend_summary": {
            "trends_detected": len(trends),
            "improving_strategies": len(improving),
            "degrading_strategies": len(degrading),
            "trends": trends,
        },
        "strategy_summary": {
            "total": len(strategies),
            "successful": len([s for s in strategies if s.get("label") == "successful"]),
            "failing": len([s for s in strategies if s.get("label") == "failing"]),
            "best_strategy": strategies[0] if strategies else None,
            "worst_strategy": strategies[-1] if strategies else None,
            "strategies": strategies,
        },
        "recommendation_count": len(recommendations),
        "top_recommendation": recommendations[0] if recommendations else None,
    }


def run_self_optimization(*, force: bool = False) -> dict:
    if should_skip(force=force):
        cached = load_snapshot()
        if cached:
            return {**cached, "ok": True, "skipped": True, "reason": "inputs unchanged"}

    inputs = load_inputs()
    performance = track_performance(
        memory=inputs["memory"],
        patterns=inputs["patterns"],
        decisions=inputs["decisions"],
        signals=inputs["signals"],
        planner=inputs["planner"],
    )
    strategies = analyze_strategies(memory=inputs["memory"], performance=performance)
    trends = detect_trends(
        memory=inputs["memory"],
        patterns=inputs["patterns"],
        decisions=inputs["decisions"],
        planner=inputs["planner"],
        context=inputs["context"],
    )
    candidates = generate_candidates(
        performance=performance,
        strategies=strategies,
        trends=trends,
        signals=inputs["signals"],
    )
    recommendations = generate_recommendations(candidates)
    summaries = _summaries(performance, strategies, trends, recommendations)

    store = {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(SSOT_PATH),
        "inputs_fingerprint": input_fingerprint(),
        "performance": performance,
        "strategies": strategies,
        "trends": trends,
        "optimization_candidates": candidates,
        "recommendations": recommendations,
        **summaries,
        "skipped": False,
    }
    write_snapshot(store)
    mark_built(store)
    return store


def self_optimization_v1_payload() -> dict:
    result = run_self_optimization()
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(SSOT_PATH),
        "skipped": result.get("skipped", False),
        "generated_at": result.get("generated_at"),
        "performance_summary": result.get("performance_summary") or {},
        "trend_summary": result.get("trend_summary") or {},
        "strategy_summary": result.get("strategy_summary") or {},
        "optimization_recommendations": result.get("recommendations") or [],
        "performance": result.get("performance") or [],
        "trends": result.get("trends") or [],
        "strategies": (result.get("strategy_summary") or {}).get("strategies") or result.get("strategies") or [],
    }
