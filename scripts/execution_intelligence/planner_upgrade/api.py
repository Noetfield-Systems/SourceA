"""Planner Upgrade v1 — API + SSOT context store."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from execution_intelligence.planner_upgrade.planner_adapter import build_recommendation
from execution_intelligence.planner_upgrade.planner_context import (
    DECISIONS_V1_PATH,
    PATTERNS_V1_PATH,
    SIGNALS_V1_PATH,
    load_decisions_readonly,
    load_patterns_readonly,
    load_signals_readonly,
)

STATE_DIR = Path.home() / ".sina"
PLANNER_CONTEXT_PATH = STATE_DIR / "planner_context_v1.json"
PLANNER_STATE_PATH = STATE_DIR / "planner-upgrade-v1-state.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _input_fingerprint() -> dict:
    return {
        "patterns_mtime": PATTERNS_V1_PATH.stat().st_mtime if PATTERNS_V1_PATH.is_file() else 0.0,
        "decisions_mtime": DECISIONS_V1_PATH.stat().st_mtime if DECISIONS_V1_PATH.is_file() else 0.0,
        "signals_mtime": SIGNALS_V1_PATH.stat().st_mtime if SIGNALS_V1_PATH.is_file() else 0.0,
        "patterns_count": len(load_patterns_readonly()),
        "decisions_count": len(load_decisions_readonly()),
        "signals_count": len(load_signals_readonly()),
    }


def _load_state() -> dict:
    if not PLANNER_STATE_PATH.is_file():
        return {}
    try:
        return json.loads(PLANNER_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PLANNER_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _write_context(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PLANNER_CONTEXT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def run_planner_upgrade(*, candidate_actions: list[str] | None = None, force: bool = False) -> dict:
    fp = _input_fingerprint()
    prev = _load_state()
    unchanged = (
        not force
        and prev.get("patterns_mtime") == fp["patterns_mtime"]
        and prev.get("decisions_mtime") == fp["decisions_mtime"]
        and prev.get("signals_mtime") == fp["signals_mtime"]
        and PLANNER_CONTEXT_PATH.is_file()
    )
    if unchanged and not candidate_actions:
        try:
            cached = json.loads(PLANNER_CONTEXT_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cached = {}
        return {"ok": True, "skipped": True, "reason": "inputs unchanged", **cached}

    recommendation = build_recommendation(candidate_actions=candidate_actions)
    summary = {
        "candidate_count": len(recommendation["context_package"]["candidate_actions"]),
        "recommended_count": len(recommendation["recommended_actions"]),
        "avoid_count": len(recommendation["avoid_actions"]),
        "signals_consumed": recommendation["signals_consumed"],
        "top_action": (recommendation["ranked_actions"][0]["action_id"] if recommendation["ranked_actions"] else None),
        "top_score": (recommendation["ranked_actions"][0]["score"] if recommendation["ranked_actions"] else None),
    }

    store = {
        "ok": True,
        "schema": "planner-context-v1",
        "updated_at": _now(),
        "path": str(PLANNER_CONTEXT_PATH),
        "inputs_fingerprint": fp,
        "planner_context_summary": summary,
        "outcome_evaluations": recommendation["outcome_evaluations"],
        "confidence_scores": recommendation["outcome_evaluations"],
        "recommendation": {
            "recommended_actions": recommendation["recommended_actions"],
            "avoid_actions": recommendation["avoid_actions"],
            "ranked_actions": recommendation["ranked_actions"],
        },
        "action_contexts": recommendation["context_package"]["action_contexts"],
    }
    _write_context(store)
    _save_state({"updated_at": store["updated_at"], **fp})
    return {**store, "skipped": False}


def planner_upgrade_v1_payload(*, candidate_actions: list[str] | None = None) -> dict:
    result = run_planner_upgrade(candidate_actions=candidate_actions)
    rec = result.get("recommendation") or {}
    return {
        "ok": True,
        "schema": "planner-upgrade-v1",
        "path": str(PLANNER_CONTEXT_PATH),
        "skipped": result.get("skipped", False),
        "updated_at": result.get("updated_at"),
        "ranked_actions": rec.get("ranked_actions") or [],
        "recommended_actions": rec.get("recommended_actions") or [],
        "avoid_actions": rec.get("avoid_actions") or [],
        "confidence_scores": result.get("confidence_scores") or [],
        "planner_context_summary": result.get("planner_context_summary") or {},
        "outcome_evaluations": result.get("outcome_evaluations") or [],
    }
