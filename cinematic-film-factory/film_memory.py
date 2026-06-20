#!/usr/bin/env python3
"""Cinematic factory — film memory + rule evolution engine."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RULES_BASE = ROOT / "data" / "cinematic-rules-engine-v1.json"
EVOLVED = SINA / "cinematic-film-rules-evolved-v1.json"
INCIDENTS = SINA / "cinematic-film-memory-incidents-v1.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_rules() -> dict[str, Any]:
    base = _read_json(RULES_BASE)
    evolved = _read_json(EVOLVED)
    if not evolved:
        return base
    merged = dict(base)
    merged_rules = dict(base.get("rules", {}))
    for key, patch in evolved.get("rule_patches", {}).items():
        merged_rules[key] = {**merged_rules.get(key, {}), **patch}
    merged["rules"] = merged_rules
    if evolved.get("ffmpeg_grade"):
        merged["ffmpeg_grade"] = {**merged.get("ffmpeg_grade", {}), **evolved["ffmpeg_grade"]}
    return merged


def record_incident(
    *,
    lane: str,
    video_id: str,
    beats: dict[str, float],
    critic_verdict: str,
    issues: list[str],
    probe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    INCIDENTS.parent.mkdir(parents=True, exist_ok=True)
    block = beats.get("block", 0)
    receipt = beats.get("receipt", 0)
    dwell = receipt - block if receipt and block else 0

    incident: dict[str, Any] = {
        "at": _now(),
        "video_id": video_id,
        "lane": lane,
        "critic_verdict": critic_verdict,
        "dropoff_point": "block_scene" if critic_verdict != "PASS" else None,
        "watch_time_loss_pct": 42 if critic_verdict != "PASS" else 0,
        "confusion_zone": "receipt_hash too fast" if dwell < 4 else None,
        "trust_peak": "block event",
        "failure_reason": issues[0] if issues else None,
        "next_fix": None,
        "beats": beats,
        "probe": probe or {},
    }

    if dwell < 4 and "block" in str(issues).lower():
        incident["next_fix"] = "increase hold from 3s → 6s"
    elif critic_verdict != "PASS":
        incident["next_fix"] = "Screen Studio truth capture or extend block dwell per rules engine"

    with INCIDENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(incident, ensure_ascii=False) + "\n")

    return incident


def evolve_rules_from_incident(incident: dict[str, Any]) -> dict[str, Any] | None:
    fix = incident.get("next_fix") or ""
    patches: dict[str, Any] = {}
    if "increase hold" in fix.lower():
        patches["block_event"] = {"hold_seconds_min": 6.0, "hold_seconds_max": 9.0}
    if incident.get("confusion_zone") == "receipt_hash too fast":
        patches["proof_event"] = {"hold_seconds_min": 5.0, "zoom_factor": 1.1}

    if not patches:
        return None

    evolved = _read_json(EVOLVED) or {"schema": "cinematic-rules-evolved-v1", "rule_patches": {}}
    evolved.setdefault("rule_patches", {})
    for k, v in patches.items():
        evolved["rule_patches"][k] = {**evolved["rule_patches"].get(k, {}), **v}
    evolved["updated_at"] = _now()
    evolved["last_incident"] = incident.get("video_id")
    EVOLVED.parent.mkdir(parents=True, exist_ok=True)
    EVOLVED.write_text(json.dumps(evolved, indent=2) + "\n", encoding="utf-8")
    return evolved
