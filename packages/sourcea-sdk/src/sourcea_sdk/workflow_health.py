"""Workflow heartbeat scoring and Kaizen receipt emission."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sourcea_sdk.receipt import write_improvement_receipt_v2

_SPEND_BY_VALUE_CLASS = {
    "revenue_path": 0.0,
    "proof_asset": 0.0,
    "risk_reduction": 0.0,
    "hygiene": 0.0,
    "none": 0.0,
}


def _now(dt: datetime | None = None) -> datetime:
    return dt or datetime.now(timezone.utc)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def cron_interval_minutes(expression: str | None) -> int | None:
    expr = (expression or "").strip()
    if not expr:
        return None
    if expr == "0 * * * *":
        return 60
    if expr == "0 0 * * *":
        return 24 * 60
    if expr == "0 3 * * 0":
        return 7 * 24 * 60
    if expr == "*/10 * * * *":
        return 10
    if expr == "*/15 * * * *":
        return 15
    if expr == "*/30 * * * *":
        return 30
    if expr == "*/5 * * * *":
        return 5
    match = re.fullmatch(r"\*/(\d+)\s+\*\s+\*\s+\*\s+\*", expr)
    if match:
        return int(match.group(1))
    return None


def file_age_minutes(path: Path, *, now: datetime | None = None) -> float | None:
    if not path.is_file():
        return None
    current = _now(now)
    age_seconds = current.timestamp() - path.stat().st_mtime
    return max(0.0, age_seconds / 60.0)


def score_slo_target(
    *,
    workflow_id: str,
    lane: str,
    targets: dict[str, Any] | None,
    observed: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(targets, dict) or not targets:
        return {
            "workflow_id": workflow_id,
            "lane": lane,
            "state": "skipped",
            "explicit_miss": False,
            "score": None,
            "slo": None,
            "observed": observed,
            "scorecard": {},
            "misses": ["missing_optional_slo"],
            "evidence": evidence,
        }

    scorecard: dict[str, dict[str, Any]] = {}
    misses: list[str] = []
    degraded = False

    def _cmp(metric: str, target_key: str, observed_key: str, *, lower_is_better: bool) -> None:
        nonlocal degraded
        target = targets.get(target_key)
        value = observed.get(observed_key)
        if target is None:
            degraded = True
            misses.append(f"missing_optional_target:{metric}")
            scorecard[metric] = {"target": None, "observed": value, "pass": None}
            return
        if value is None:
            degraded = True
            misses.append(f"missing_observation:{metric}")
            scorecard[metric] = {"target": target, "observed": None, "pass": None}
            return
        passed = value <= target if lower_is_better else value >= target
        scorecard[metric] = {"target": target, "observed": value, "pass": passed}
        if not passed:
            misses.append(f"{metric}_target_missed")

    _cmp("freshness", "freshness_target_minutes", "freshness_minutes", lower_is_better=True)
    _cmp("success_rate", "success_rate_target", "success_rate", lower_is_better=False)
    _cmp("latency", "latency_target_minutes", "latency_minutes", lower_is_better=True)

    explicit_miss = any(m.endswith("_target_missed") for m in misses)
    if explicit_miss:
        state = "missed"
    elif degraded:
        state = "degraded"
    else:
        state = "healthy"

    score_values = [1.0 if row.get("pass") else 0.0 for row in scorecard.values() if row.get("pass") is not None]
    score = round(sum(score_values) / len(score_values), 3) if score_values else None
    return {
        "workflow_id": workflow_id,
        "lane": lane,
        "state": state,
        "explicit_miss": explicit_miss,
        "score": score,
        "slo": targets,
        "observed": observed,
        "scorecard": scorecard,
        "misses": misses,
        "evidence": evidence,
    }


def build_heartbeat_loop(
    *,
    workflow_id: str,
    lane: str,
    targets: dict[str, Any] | None,
    observed: dict[str, Any],
    evidence: list[dict[str, Any]],
    last_run_at: str | None = None,
    sink_invariant_ok: bool = True,
    cost_window_usd: float = 0.0,
    cost_per_complete_usd: float = 0.0,
    spend_by_value_class: dict[str, float] | None = None,
    throttled_roi: bool = False,
) -> dict[str, Any]:
    score = score_slo_target(
        workflow_id=workflow_id,
        lane=lane,
        targets=targets,
        observed=observed,
        evidence=evidence,
    )
    loop = {
        "workflow_id": workflow_id,
        "lane": lane,
        "last_run_at": last_run_at or observed.get("last_run_at") or observed.get("at"),
        "state": score["state"],
        "sink_invariant_ok": sink_invariant_ok,
        "cost_window_usd": round(float(cost_window_usd), 4),
        "cost_per_complete_usd": round(float(cost_per_complete_usd), 4),
        "spend_by_value_class": dict(spend_by_value_class or _SPEND_BY_VALUE_CLASS),
        "throttled_roi": bool(throttled_roi),
        **score,
    }
    return loop


def _normalize_loop(loop: dict[str, Any]) -> dict[str, Any]:
    spend = loop.get("spend_by_value_class")
    if not isinstance(spend, dict):
        spend = dict(_SPEND_BY_VALUE_CLASS)
    else:
        spend = {**_SPEND_BY_VALUE_CLASS, **spend}
    observed = loop.get("observed") if isinstance(loop.get("observed"), dict) else {}
    normalized = {
        "workflow_id": loop.get("workflow_id"),
        "lane": loop.get("lane"),
        "last_run_at": loop.get("last_run_at") or observed.get("last_run_at"),
        "state": loop.get("state") or "skipped",
        "sink_invariant_ok": bool(loop.get("sink_invariant_ok", True)),
        "cost_window_usd": round(float(loop.get("cost_window_usd") or 0.0), 4),
        "cost_per_complete_usd": round(float(loop.get("cost_per_complete_usd") or 0.0), 4),
        "spend_by_value_class": spend,
        "throttled_roi": bool(loop.get("throttled_roi")),
        "explicit_miss": bool(loop.get("explicit_miss")),
        "score": loop.get("score"),
        "slo": loop.get("slo"),
        "observed": observed,
        "scorecard": loop.get("scorecard") or {},
        "misses": loop.get("misses") or [],
        "evidence": loop.get("evidence") or [],
    }
    return normalized


def build_heartbeat_report(
    *,
    loops: list[dict[str, Any]],
    drift: dict[str, Any],
    founder_blocked_total: int = 0,
    date: str | None = None,
    founder_gated_improvements: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_loops = [_normalize_loop(loop) for loop in loops]
    return {
        "schema": "autorun-heartbeat-v2",
        "date": date or _now().strftime("%Y-%m-%d"),
        "loops": normalized_loops,
        "drift": drift,
        "founder_blocked_total": founder_blocked_total,
        "founder_gated_improvements": founder_gated_improvements or [],
        "escalations": [loop["workflow_id"] for loop in normalized_loops if loop.get("explicit_miss")],
    }


def emit_improvement_receipt(
    *,
    report: dict[str, Any],
    repo_root: Path,
    rollback_command: str,
) -> dict[str, Any] | None:
    misses = [loop for loop in report.get("loops") or [] if loop.get("explicit_miss")]
    if not misses:
        return None

    evidence = [
        {
            "workflow_id": loop.get("workflow_id"),
            "lane": loop.get("lane"),
            "state": loop.get("state"),
            "misses": loop.get("misses") or [],
            "observed": loop.get("observed") or {},
            "scorecard": loop.get("scorecard") or {},
        }
        for loop in misses
    ]
    receipt = write_improvement_receipt_v2(
        repo_root=repo_root,
        classification="machine_safe",
        source="failed_check",
        diff_summary="Harden the observed workflow SLOs for " + ", ".join(loop["workflow_id"] for loop in misses),
        expected_effect="Heartbeat will surface missed observe/sync windows explicitly before drift turns hidden.",
        expected_roi={
            "cost_saved_usd": 0,
            "risk_reduced": "earlier detection of stale observe/sync loops and trigger drift",
            "revenue_unblocked": "keeps declared-window receipts current",
            "build_cost_usd": 0,
        },
        rollback_command=rollback_command,
        evidence=evidence,
        extra={
            "workflow_heartbeat": report,
            "missed_workflows": [loop.get("workflow_id") for loop in misses],
        },
    )
    return receipt
