#!/usr/bin/env python3
"""Apple Health mini app — personal wellness goals linked to program roadmaps."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
STATE_DIR = Path.home() / ".sina" / "apple-health"
GOALS_PATH = STATE_DIR / "goals.json"
SLEEP_SIGNAL_PATH = STATE_DIR / "sleep-signal-v1.json"
AUTO_ARM_FLAG = STATE_DIR / "auto-arm-sleep-v1.flag"
HUB_MINI = "http://127.0.0.1:13025/"
APPLE_HEALTH_VERSION = "2.0.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_goals() -> dict:
    return {
        "schema": "apple-health-goals-v1",
        "updated_at": _now(),
        "goals": [
            {
                "id": "movement",
                "title": "Daily movement",
                "target": "10,000 steps",
                "metric": "steps",
                "status": "active",
                "linked_plan_id": "P0-RUNRECEIPT",
            },
            {
                "id": "sleep",
                "title": "Sleep consistency",
                "target": "7+ hours",
                "metric": "sleep",
                "status": "active",
                "linked_plan_id": None,
            },
            {
                "id": "recovery",
                "title": "Recovery between ship sprints",
                "target": "1 rest block / week",
                "metric": "habit",
                "status": "active",
                "linked_plan_id": "MERGEPACK-L1",
            },
        ],
        "notes": "Sync with iPhone Health app via Shortcuts; hub stores intent only — no medical API.",
    }


def load_goals() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not GOALS_PATH.is_file():
        data = _default_goals()
        save_goals(data)
        return data
    return json.loads(GOALS_PATH.read_text(encoding="utf-8"))


def save_goals(data: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    GOALS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_sleep_signal() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not SLEEP_SIGNAL_PATH.is_file():
        return {"schema": "apple-health-sleep-signal-v1", "state": "awake", "updated_at": None}
    try:
        return json.loads(SLEEP_SIGNAL_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema": "apple-health-sleep-signal-v1", "state": "unknown", "updated_at": None}


def save_sleep_signal(*, state: str, source: str = "shortcut", extra: dict | None = None) -> dict:
    row = {
        "schema": "apple-health-sleep-signal-v1",
        "state": state,
        "source": source,
        "updated_at": _now(),
        **(extra or {}),
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SLEEP_SIGNAL_PATH.write_text(json.dumps(row, indent=2), encoding="utf-8")
    return row


def open_health_app() -> dict:
    """Open Apple Health on Mac if installed."""
    try:
        subprocess.run(["open", "-a", "Health"], check=False)
        return {"ok": True, "message": "Opened Health app (Mac)"}
    except OSError as e:
        return {"ok": False, "error": str(e)}


def apple_health_payload(*, rescan: bool = False) -> dict:
    goals_data = load_goals()
    parallel: list[dict] = []
    try:
        from roadmaps_goals import roadmaps_goals_payload  # noqa: WPS433

        parallel = (roadmaps_goals_payload().get("parallel_plans") or [])[:8]
    except Exception:
        pass
    port = int(__import__("os").environ.get("APPLE_HEALTH_PORT", "13025"))
    ui_contract: dict = {}
    try:
        from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433

        ui_contract = build_ui_contract("apple_health", port=port)
    except Exception:
        ui_contract = {"ui_mode": "founder_glance", "version": APPLE_HEALTH_VERSION}
    return {
        "ok": True,
        "app": "apple-health",
        "version": APPLE_HEALTH_VERSION,
        "ui_contract": ui_contract,
        "standalone": True,
        "title": "Apple Health",
        "tagline": "Wellness goals · sleep · this Mac only",
        "mini_app_url": f"http://127.0.0.1:{port}/",
        "standalone_url": f"http://127.0.0.1:{port}/",
        "data_dir": str(STATE_DIR),
        "goals": goals_data.get("goals") or [],
        "notes": goals_data.get("notes", ""),
        "parallel_plans": parallel,
        "shortcuts_hint": "iPhone: Shortcuts → Sleep Focus / Health → POST /api/apple-health action=sleep_start|sleep_end",
        "sleep_signal": load_sleep_signal(),
        "auto_arm_sleep": AUTO_ARM_FLAG.is_file(),
        "open_health": open_health_app(),
    }


def handle_action(body: dict | None = None) -> dict:
    body = body or {}
    action = (body.get("action") or "status").strip().lower()
    if action == "open_health":
        return open_health_app()
    if action == "add_goal":
        data = load_goals()
        goals = list(data.get("goals") or [])
        goals.append(
            {
                "id": body.get("id") or f"goal-{len(goals) + 1}",
                "title": body.get("title") or "New goal",
                "target": body.get("target") or "",
                "metric": body.get("metric") or "custom",
                "status": "active",
                "linked_plan_id": body.get("linked_plan_id"),
            }
        )
        data["goals"] = goals
        save_goals(data)
        return {"ok": True, "message": "Goal added", "goals": goals}
    if action == "save_goals":
        data = load_goals()
        if body.get("goals"):
            data["goals"] = body["goals"]
        save_goals(data)
        return {"ok": True, "message": "Goals saved"}
    if action == "sleep_start":
        row = save_sleep_signal(
            state="asleep",
            source=body.get("source") or "apple_health",
            extra={
                k: body[k]
                for k in ("sleep_hours", "in_bed", "steps_today", "heart_rate")
                if body.get(k) is not None
            },
        )
        out = {"ok": True, "message": "Sleep signal recorded", "sleep_signal": row}
        if AUTO_ARM_FLAG.is_file():
            try:
                from apple_health_sleep_bridge_v1 import apply_sleep_from_health  # noqa: WPS433

                out["arm_sleep"] = apply_sleep_from_health()
            except Exception as exc:
                out["arm_sleep"] = {"ok": False, "error": str(exc)}
        return out
    if action == "sleep_end":
        row = save_sleep_signal(state="awake", source=body.get("source") or "apple_health")
        try:
            from apple_health_sleep_bridge_v1 import apply_wake_from_health  # noqa: WPS433

            wake = apply_wake_from_health()
        except Exception as exc:
            wake = {"ok": False, "error": str(exc)}
        return {"ok": True, "message": "Wake signal recorded", "sleep_signal": row, "wake": wake}
    if action == "health_sample":
        row = save_sleep_signal(
            state=body.get("state") or "awake",
            source=body.get("source") or "health_sample",
            extra={
                k: body[k]
                for k in ("sleep_hours", "in_bed", "steps_today", "heart_rate")
                if body.get(k) is not None
            },
        )
        return {"ok": True, "sleep_signal": row}
    if action == "enable_auto_arm":
        AUTO_ARM_FLAG.touch()
        return {"ok": True, "message": "Auto arm sleep ON — sleep_start will arm overnight"}
    if action == "disable_auto_arm":
        AUTO_ARM_FLAG.unlink(missing_ok=True)
        return {"ok": True, "message": "Auto arm sleep OFF — manual arm sleep only"}
    return apple_health_payload()
