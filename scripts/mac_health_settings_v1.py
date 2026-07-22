#!/usr/bin/env python3
"""Mac Health Guard — founder-tunable auto-guard, Cursor, and Chrome settings."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mac_health_edition_v1 import SINA

PANIC_PATH = SINA / "config" / "mac-health-panic-v1.json"
PREVENTION_PATH = SINA / "config" / "mac-health-prevention-v1.json"
SETTINGS_META_PATH = SINA / "config" / "mac-health-settings-meta-v1.json"
QUIET_FLAG = SINA / "mac-health-quiet-v1.flag"
PULSE_SEC = 8

DEFAULTS: dict[str, Any] = {
    "schema_version": "mac-health-settings-v1",
    "notifications": {
        "enabled": False,
        "sounds_enabled": False,
        "modal_on_auto_stop_only": True,
    },
    "auto_guard": {
        "enabled": True,
        "cursor_cpu_start_streak": 280,
        "pulses_before_stop": 24,
        "queue_zombies_start_streak": 12,
        "panic_cooldown_sec": 900,
        "warn_every_n_pulses": 4,
        "warn_modal_at_pulses": [18, 21, 23],
        "cpu_system_warn_pct": [50, 62, 74, 86],
        "cursor_cpu_warn_pct": [150, 190, 230, 270],
        "cpu_warn_cooldown_sec": 300,
    },
    "cursor": {
        "auto_restart_on_unattended_panic": False,
        "auto_restart_peak_pct": 450,
        "auto_restart_sum_pct": 550,
        "ui_hot_banner_peak_pct": 280,
        "ui_hot_banner_sum_pct": 350,
    },
    "chrome": {
        "quit_on_cool_down_mode": "when_mac_hot",
        "quit_on_wake_cool_down_mode": "when_mac_hot",
        "when_mac_hot": {
            "min_system_cpu_pct": 78,
            "min_load_per_core": 0.85,
            "min_ram_pct": 88,
            "min_chrome_cpu_sum_pct": 50,
            "wake_min_system_cpu_pct": 55,
            "wake_min_load_per_core": 0.65,
            "wake_min_chrome_cpu_sum_pct": 45,
        },
    },
    "prevention": {
        "enabled": True,
        "auto_apply_background": True,
        "cursor_busy_warn_pct": 120,
        "freeze_factory_only_when_unhealthy": True,
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _deep_merge(base: dict, patch: dict) -> dict:
    out = deepcopy(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _chrome_mode_from_disk(
    chrome_extra: dict[str, Any],
    bool_key: str,
    mode_key: str,
    default: str,
) -> str:
    """Legacy bool true=always, false=when_mac_hot (not never — Mac still gets care)."""
    if mode_key in chrome_extra and chrome_extra[mode_key] in ("never", "when_mac_hot", "always"):
        return str(chrome_extra[mode_key])
    if bool_key in chrome_extra:
        return "always" if chrome_extra[bool_key] else "when_mac_hot"
    return default


def _chrome_mode_label(mode: str) -> str:
    if mode == "always":
        return "always closes Chrome"
    if mode == "never":
        return "never closes Chrome (manual only)"
    return "closes Chrome only when Mac is hot"


def notifications_enabled() -> bool:
    """Master kill switch — no osascript alerts when False or quiet flag set."""
    if QUIET_FLAG.is_file():
        return False
    try:
        notes = load_settings().get("notifications") or {}
        return bool(notes.get("enabled", False))
    except Exception:
        return False


def load_settings() -> dict[str, Any]:
    """Merge defaults with on-disk panic + prevention configs."""
    settings = deepcopy(DEFAULTS)
    panic = _read_json(PANIC_PATH)
    prev = _read_json(PREVENTION_PATH)
    unattended = panic.get("unattended") or {}
    prevention = prev.get("prevention") or prev
    thresholds = prevention.get("thresholds") or {}
    chrome_extra = prevention.get("chrome") or panic.get("chrome") or {}

    settings["auto_guard"].update(
        {
            "enabled": bool(unattended.get("auto_panic_on_runaway", settings["auto_guard"]["enabled"])),
            "cursor_cpu_start_streak": int(
                unattended.get("cursor_cpu_panic", settings["auto_guard"]["cursor_cpu_start_streak"])
            ),
            "pulses_before_stop": int(
                unattended.get(
                    "consecutive_unhealthy_pulses", settings["auto_guard"]["pulses_before_stop"]
                )
            ),
            "queue_zombies_start_streak": int(
                unattended.get("queue_zombies_panic", settings["auto_guard"]["queue_zombies_start_streak"])
            ),
            "panic_cooldown_sec": int(
                unattended.get("panic_cooldown_sec", settings["auto_guard"]["panic_cooldown_sec"])
            ),
            "warn_modal_at_pulses": list(
                unattended.get("warn_modal_streaks", settings["auto_guard"]["warn_modal_at_pulses"])
            ),
        }
    )
    warn_streaks = unattended.get("warn_streaks")
    if isinstance(warn_streaks, list) and len(warn_streaks) >= 2:
        settings["auto_guard"]["warn_every_n_pulses"] = max(
            1, int(warn_streaks[1]) - int(warn_streaks[0])
        )
    cpu_warn = panic.get("cpu_warn") or {}
    if cpu_warn:
        settings["auto_guard"]["cpu_system_warn_pct"] = list(
            cpu_warn.get("system_cpu_pct", settings["auto_guard"]["cpu_system_warn_pct"])
        )
        settings["auto_guard"]["cursor_cpu_warn_pct"] = list(
            cpu_warn.get("cursor_cpu_sum_pct", settings["auto_guard"]["cursor_cpu_warn_pct"])
        )
        settings["auto_guard"]["cpu_warn_cooldown_sec"] = int(
            cpu_warn.get("cooldown_sec", settings["auto_guard"]["cpu_warn_cooldown_sec"])
        )
        settings["notifications"]["sounds_enabled"] = bool(
            cpu_warn.get("enabled", settings["notifications"]["sounds_enabled"])
        )
    if QUIET_FLAG.is_file():
        settings["notifications"]["enabled"] = False
        settings["notifications"]["sounds_enabled"] = False

    settings["cursor"].update(
        {
            "auto_restart_on_unattended_panic": bool(
                unattended.get(
                    "auto_restart_cursor_unattended",
                    settings["cursor"]["auto_restart_on_unattended_panic"],
                )
            ),
            "auto_restart_peak_pct": int(
                unattended.get("cursor_restart_peak", settings["cursor"]["auto_restart_peak_pct"])
            ),
            "auto_restart_sum_pct": int(
                unattended.get("cursor_restart_sum", settings["cursor"]["auto_restart_sum_pct"])
            ),
            "ui_hot_banner_peak_pct": int(
                unattended.get(
                    "ui_cursor_hot_peak", settings["cursor"]["ui_hot_banner_peak_pct"]
                )
            ),
            "ui_hot_banner_sum_pct": int(
                unattended.get("ui_cursor_hot_sum", settings["cursor"]["ui_hot_banner_sum_pct"])
            ),
        }
    )

    settings["chrome"].update(
        {
            "quit_on_cool_down_mode": _chrome_mode_from_disk(
                chrome_extra, "quit_on_cool_down", "quit_on_cool_down_mode", "when_mac_hot"
            ),
            "quit_on_wake_cool_down_mode": _chrome_mode_from_disk(
                chrome_extra, "quit_on_wake_cool_down", "quit_on_wake_cool_down_mode", "when_mac_hot"
            ),
            "when_mac_hot": {
                **(DEFAULTS["chrome"].get("when_mac_hot") or {}),
                **(chrome_extra.get("when_mac_hot") or {}),
            },
        }
    )

    settings["prevention"].update(
        {
            "enabled": bool(prevention.get("enabled", settings["prevention"]["enabled"])),
            "auto_apply_background": bool(
                prevention.get("auto_apply", settings["prevention"]["auto_apply_background"])
            ),
            "cursor_busy_warn_pct": int(
                thresholds.get("cursor_cpu_sum_warn", settings["prevention"]["cursor_busy_warn_pct"])
            ),
        }
    )
    return settings


def save_settings(patch: dict[str, Any]) -> dict[str, Any]:
    """Apply founder patch → write panic + prevention JSON on disk."""
    current = load_settings()
    merged = _deep_merge(current, patch)
    ag = merged["auto_guard"]
    cur = merged["cursor"]
    ch = merged["chrome"]
    prev = merged["prevention"]

    warn_step = max(1, int(ag.get("warn_every_n_pulses") or 2))
    max_pulse = int(ag.get("pulses_before_stop") or 24)
    warn_streaks = list(range(warn_step, max_pulse, warn_step))
    if not warn_streaks:
        warn_streaks = [min(warn_step, max(1, max_pulse - 1))]

    panic_doc = _read_json(PANIC_PATH)
    panic_doc.setdefault("hotkey", {"enabled": True, "label": "⌃⌥⌘S"})
    panic_doc["unattended"] = {
        "auto_panic_on_runaway": bool(ag.get("enabled")),
        "auto_restart_cursor_unattended": bool(cur.get("auto_restart_on_unattended_panic")),
        "consecutive_unhealthy_pulses": int(ag.get("pulses_before_stop")),
        "cursor_cpu_panic": int(ag.get("cursor_cpu_start_streak")),
        "queue_zombies_panic": int(ag.get("queue_zombies_start_streak")),
        "warn_streaks": warn_streaks,
        "warn_modal_streaks": list(ag.get("warn_modal_at_pulses") or [18, 21, 23]),
        "cursor_restart_peak": int(cur.get("auto_restart_peak_pct")),
        "cursor_restart_sum": int(cur.get("auto_restart_sum_pct")),
        "ui_cursor_hot_peak": int(cur.get("ui_hot_banner_peak_pct")),
        "ui_cursor_hot_sum": int(cur.get("ui_hot_banner_sum_pct")),
        "panic_cooldown_sec": int(ag.get("panic_cooldown_sec")),
    }
    panic_doc["chrome"] = {
        "quit_on_cool_down_mode": str(ch.get("quit_on_cool_down_mode") or "when_mac_hot"),
        "quit_on_wake_cool_down_mode": str(ch.get("quit_on_wake_cool_down_mode") or "when_mac_hot"),
        "when_mac_hot": {
            **(DEFAULTS["chrome"].get("when_mac_hot") or {}),
            **(ch.get("when_mac_hot") or {}),
        },
    }
    panic_doc["cpu_warn"] = {
        "enabled": bool(merged.get("notifications", {}).get("sounds_enabled", False)),
        "system_cpu_pct": list(ag.get("cpu_system_warn_pct") or [50, 62, 74, 86]),
        "cursor_cpu_sum_pct": list(ag.get("cursor_cpu_warn_pct") or [150, 190, 230, 270]),
        "cooldown_sec": int(ag.get("cpu_warn_cooldown_sec") or 300),
    }
    _write_json(PANIC_PATH, panic_doc)

    prev_doc = _read_json(PREVENTION_PATH)
    prev_block = prev_doc.get("prevention") or {}
    prev_block.update(
        {
            "enabled": bool(prev.get("enabled")),
            "auto_apply": bool(prev.get("auto_apply_background")),
            "cooldown_sec": prev_block.get("cooldown_sec", 90),
            "wake_window_min": prev_block.get("wake_window_min", 45),
            "thresholds": {
                **(prev_block.get("thresholds") or {}),
                "cursor_cpu_sum_warn": int(prev.get("cursor_busy_warn_pct")),
            },
            "chrome": {
                "quit_on_cool_down_mode": str(ch.get("quit_on_cool_down_mode") or "when_mac_hot"),
                "quit_on_wake_cool_down_mode": str(
                    ch.get("quit_on_wake_cool_down_mode") or "when_mac_hot"
                ),
                "when_mac_hot": {
                    **(DEFAULTS["chrome"].get("when_mac_hot") or {}),
                    **(ch.get("when_mac_hot") or {}),
                },
            },
        }
    )
    prev_doc["prevention"] = prev_block
    _write_json(PREVENTION_PATH, prev_doc)

    meta = {
        "updated_at": _now(),
        "updated_by": "mac-health-settings-ui",
        "paths": {
            "panic": str(PANIC_PATH),
            "prevention": str(PREVENTION_PATH),
        },
    }
    _write_json(SETTINGS_META_PATH, meta)
    return load_settings()


def reset_settings() -> dict[str, Any]:
    """Restore shipped defaults."""
    return save_settings(deepcopy(DEFAULTS))


def _chrome_cpu_sum() -> float:
    try:
        import subprocess

        proc = subprocess.run(
            ["ps", "-axo", "pcpu,comm"],
            capture_output=True,
            text=True,
            timeout=6.0,
        )
        total = 0.0
        for line in (proc.stdout or "").splitlines()[1:]:
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            comm = parts[1]
            if "chrome" not in comm.lower() and "Google Chrome" not in comm:
                continue
            try:
                total += float(parts[0])
            except ValueError:
                continue
        return round(total, 1)
    except (OSError, subprocess.TimeoutExpired):
        return 0.0


def _mac_is_hot_for_chrome(
    mp: dict[str, Any] | None,
    *,
    wake: bool = False,
) -> tuple[bool, str]:
    ch = load_settings().get("chrome") or {}
    hot = ch.get("when_mac_hot") or DEFAULTS["chrome"]["when_mac_hot"]
    if mp is None:
        try:
            from mac_health_cpu_relief_v1 import snapshot_pressure  # noqa: WPS433

            mp = snapshot_pressure()
        except Exception:
            mp = {}
    if mp.get("ram_used_pct") is None or mp.get("cpu_cores") is None:
        try:
            from mac_health_guard import _machine_pressure  # noqa: WPS433

            mp = {**_machine_pressure(), **mp}
        except Exception:
            pass
    cores = max(int(mp.get("cpu_cores") or mp.get("cores") or 1), 1)
    cpu_pct = float(mp.get("cpu_pct") or 0)
    ram_pct = float(mp.get("ram_used_pct") or 0)
    load_per_core = float(mp.get("load_1min") or 0) / cores
    chrome_cpu = _chrome_cpu_sum()

    if wake:
        if cpu_pct >= float(hot.get("wake_min_system_cpu_pct") or 48):
            return True, f"wake · body CPU {cpu_pct:.0f}%"
        if load_per_core >= float(hot.get("wake_min_load_per_core") or 0.55):
            return True, f"wake · load {load_per_core:.1f}/core"
        if chrome_cpu >= float(hot.get("wake_min_chrome_cpu_sum_pct") or 35):
            return True, f"wake · Chrome {chrome_cpu:.0f}% CPU"
        return False, f"Mac calm after wake (CPU {cpu_pct:.0f}%) — Chrome kept open"

    if cpu_pct >= float(hot.get("min_system_cpu_pct") or 72):
        return True, f"body CPU {cpu_pct:.0f}%"
    if load_per_core >= float(hot.get("min_load_per_core") or 0.72):
        return True, f"load {load_per_core:.1f}/core"
    if ram_pct >= float(hot.get("min_ram_pct") or 86):
        return True, f"RAM {ram_pct:.0f}%"
    if chrome_cpu >= float(hot.get("min_chrome_cpu_sum_pct") or 40):
        return True, f"Chrome {chrome_cpu:.0f}% CPU"
    return False, f"Mac OK (CPU {cpu_pct:.0f}%) — Chrome kept open"


def chrome_quit_decision(context: str, mp: dict[str, Any] | None = None) -> tuple[bool, str]:
    """context: cool_down | wake_cool_down | manual → (quit?, detail)"""
    ch = load_settings().get("chrome") or {}
    if context == "manual":
        return True, "manual Close Chrome"
    mode_key = "quit_on_wake_cool_down_mode" if context == "wake_cool_down" else "quit_on_cool_down_mode"
    mode = str(ch.get(mode_key) or "when_mac_hot")
    if mode == "never":
        return False, "Chrome kept open (Settings: never on Cool Down)"
    if mode == "always":
        return True, "Chrome close enabled (always)"
    hot, reason = _mac_is_hot_for_chrome(mp, wake=context == "wake_cool_down")
    if hot:
        return True, f"Mac needs care — {reason} — closing Chrome"
    return False, reason


def chrome_quit_allowed(context: str, mp: dict[str, Any] | None = None) -> bool:
    """context: cool_down | wake_cool_down | manual"""
    return chrome_quit_decision(context, mp)[0]


def build_field_schema() -> list[dict[str, Any]]:
    return [
        {
            "group": "auto_guard",
            "title": "Auto guard (background stop)",
            "help": "Runs every 8 seconds. Only stops factory/hub scripts — not Cursor unless you enable it below.",
            "fields": [
                {
                    "key": "enabled",
                    "label": "Auto guard ON",
                    "type": "bool",
                    "help": "Master switch for unattended background stop.",
                },
                {
                    "key": "cursor_cpu_start_streak",
                    "label": "Cursor CPU % to start counting",
                    "type": "number",
                    "min": 100,
                    "max": 600,
                    "step": 10,
                    "help": "Sum of all Cursor processes. 74% and 200% are safe — default 280%.",
                },
                {
                    "key": "pulses_before_stop",
                    "label": "Pulses before background stop",
                    "type": "number",
                    "min": 4,
                    "max": 60,
                    "step": 1,
                    "help": f"Each pulse = {PULSE_SEC}s. 24 pulses ≈ 192 seconds (~3 min).",
                },
                {
                    "key": "queue_zombies_start_streak",
                    "label": "Queue zombies to start counting",
                    "type": "number",
                    "min": 2,
                    "max": 50,
                    "step": 1,
                    "help": "Leaked factory queue builders — alternative trigger.",
                },
                {
                    "key": "warn_every_n_pulses",
                    "label": "Warn every N pulses",
                    "type": "number",
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "help": "Notification rhythm while streak builds. 1 = every pulse (~8s).",
                },
                {
                    "key": "cpu_warn_cooldown_sec",
                    "label": "CPU alarm cooldown (seconds)",
                    "type": "number",
                    "min": 30,
                    "max": 600,
                    "step": 15,
                    "help": "Minimum gap between repeated system/Cursor CPU notifications.",
                },
                {
                    "key": "panic_cooldown_sec",
                    "label": "Cooldown after auto-stop (seconds)",
                    "type": "number",
                    "min": 120,
                    "max": 3600,
                    "step": 60,
                    "help": "Minimum time before another auto-stop can run.",
                },
            ],
        },
        {
            "group": "cursor",
            "title": "Cursor kill / restart switch",
            "help": "Default: auto-stop never quits Cursor. Manual Restart Cursor button always available in Cool Down.",
            "fields": [
                {
                    "key": "auto_restart_on_unattended_panic",
                    "label": "Auto-quit Cursor on unattended panic",
                    "type": "bool",
                    "help": "OFF recommended. When ON, quit+reopen only if peak/sum thresholds exceeded.",
                },
                {
                    "key": "auto_restart_peak_pct",
                    "label": "Auto-restart renderer peak %",
                    "type": "number",
                    "min": 150,
                    "max": 800,
                    "step": 10,
                    "help": "Only if auto-quit Cursor is ON.",
                },
                {
                    "key": "auto_restart_sum_pct",
                    "label": "Auto-restart Cursor CPU sum %",
                    "type": "number",
                    "min": 200,
                    "max": 900,
                    "step": 10,
                    "help": "Only if auto-quit Cursor is ON.",
                },
                {
                    "key": "ui_hot_banner_peak_pct",
                    "label": "UI hot banner — peak %",
                    "type": "number",
                    "min": 100,
                    "max": 600,
                    "step": 10,
                    "help": "When to show optional Restart Cursor banner (not auto-kill).",
                },
                {
                    "key": "ui_hot_banner_sum_pct",
                    "label": "UI hot banner — sum %",
                    "type": "number",
                    "min": 150,
                    "max": 800,
                    "step": 10,
                    "help": "When to show optional Restart Cursor banner.",
                },
            ],
        },
        {
            "group": "chrome",
            "title": "Chrome in Cool Down",
            "help": "Smart default: close Chrome only when Mac is actually hot — not on every tap.",
            "fields": [
                {
                    "key": "quit_on_cool_down_mode",
                    "label": "Cool Down now — Chrome",
                    "type": "select",
                    "options": [
                        {"value": "when_mac_hot", "label": "When Mac is hot (recommended)"},
                        {"value": "always", "label": "Always close"},
                        {"value": "never", "label": "Never (manual only)"},
                    ],
                    "help": "Hot = body CPU ≥78%, load ≥0.85/core, RAM ≥88%, or Chrome ≥50% CPU.",
                },
                {
                    "key": "quit_on_wake_cool_down_mode",
                    "label": "Wake Cool Down — Chrome",
                    "type": "select",
                    "options": [
                        {"value": "when_mac_hot", "label": "When Mac is hot (recommended)"},
                        {"value": "always", "label": "Always close"},
                        {"value": "never", "label": "Never (manual only)"},
                    ],
                    "help": "After sleep — closes Chrome only if wake pressure is real.",
                },
            ],
        },
        {
            "group": "prevention",
            "title": "Background prevention",
            "help": "Gentle automatic actions before auto-guard. Factory freeze only when unhealthy (not watch).",
            "fields": [
                {
                    "key": "enabled",
                    "label": "Prevention ON",
                    "type": "bool",
                },
                {
                    "key": "auto_apply_background",
                    "label": "Auto-apply prevention",
                    "type": "bool",
                    "help": "Freeze factory / pause n8n when unhealthy — 90s cooldown.",
                },
                {
                    "key": "cursor_busy_warn_pct",
                    "label": "Cursor busy label starts at %",
                    "type": "number",
                    "min": 60,
                    "max": 300,
                    "step": 10,
                    "help": "UI text only — does not trigger auto-stop.",
                },
            ],
        },
    ]


def build_auto_guard_explainer(settings: dict[str, Any] | None = None) -> dict[str, Any]:
    s = settings or load_settings()
    ag = s.get("auto_guard") or {}
    cur = s.get("cursor") or {}
    ch = s.get("chrome") or {}
    pulses = int(ag.get("pulses_before_stop") or 24)
    cursor_start = int(ag.get("cursor_cpu_start_streak") or 280)
    eta_sec = pulses * PULSE_SEC
    warn_step = int(ag.get("warn_every_n_pulses") or 2)

    steps = [
        {
            "order": 1,
            "title": "Every 8 seconds",
            "detail": "Mac Health reads CPU, RAM, Cursor load, queue zombies.",
        },
        {
            "order": 2,
            "title": f"Below {cursor_start}% Cursor CPU",
            "detail": "Nothing happens — keep working. Normal agent chats often run 60–200%.",
        },
        {
            "order": 3,
            "title": f"At or above {cursor_start}% Cursor CPU (health not healthy)",
            "detail": f"Streak counter +1 each pulse. Resets to 0 if CPU drops.",
        },
        {
            "order": 4,
            "title": f"Warnings every {warn_step} pulse(s)",
            "detail": "macOS notifications while streak builds · Cursor stays open · Cool Down anytime.",
        },
        {
            "order": 5,
            "title": "System CPU alarms",
            "detail": (
                f"Body CPU tiers {ag.get('cpu_system_warn_pct')} · "
                f"Cursor CPU tiers {ag.get('cursor_cpu_warn_pct')} · "
                f"cooldown {ag.get('cpu_warn_cooldown_sec', 75)}s."
            ),
        },
        {
            "order": 6,
            "title": f"After {pulses} consecutive pulses (~{eta_sec}s)",
            "detail": "Background stop: factory freeze, hub, pipeline — Cursor stays open by default.",
        },
        {
            "order": 7,
            "title": "Cursor auto-quit",
            "detail": (
                "OFF (recommended). "
                + (
                    f"ON only if peak ≥{cur.get('auto_restart_peak_pct')}% "
                    f"or sum ≥{cur.get('auto_restart_sum_pct')}%."
                    if cur.get("auto_restart_on_unattended_panic")
                    else "Disabled — use manual Restart Cursor in Cool Down if frozen."
                )
            ),
        },
        {
            "order": 8,
            "title": "Chrome on Cool Down",
            "detail": (
                f"Cool Down now: {_chrome_mode_label(str(ch.get('quit_on_cool_down_mode') or 'when_mac_hot'))} · "
                f"Wake Cool Down: {_chrome_mode_label(str(ch.get('quit_on_wake_cool_down_mode') or 'when_mac_hot'))} · "
                "manual Close Chrome always available."
            ),
        },
    ]
    return {
        "schema": "mac-health-auto-guard-explainer-v1",
        "pulse_sec": PULSE_SEC,
        "steps": steps,
        "summary": (
            f"Auto guard {'ON' if ag.get('enabled') else 'OFF'} · "
            f"start at Cursor {cursor_start}% · "
            f"{pulses} pulses (~{eta_sec}s) · "
            f"Cursor auto-quit {'ON' if cur.get('auto_restart_on_unattended_panic') else 'OFF'}"
        ),
        "config_paths": {
            "panic": str(PANIC_PATH),
            "prevention": str(PREVENTION_PATH),
        },
    }


def handle_settings_action(body: dict[str, Any]) -> dict[str, Any]:
    action = (body.get("action") or "settings").strip().lower()
    if action == "settings_reset":
        values = reset_settings()
        return {
            "ok": True,
            "action": action,
            "values": values,
            "schema": build_field_schema(),
            "explainer": build_auto_guard_explainer(values),
            "defaults": DEFAULTS,
        }
    if action == "settings_save":
        patch = body.get("settings") or body.get("patch") or {}
        if not isinstance(patch, dict):
            return {"ok": False, "error": "settings must be an object"}
        values = save_settings(patch)
        return {
            "ok": True,
            "action": action,
            "values": values,
            "schema": build_field_schema(),
            "explainer": build_auto_guard_explainer(values),
        }
    values = load_settings()
    return {
        "ok": True,
        "action": "settings",
        "values": values,
        "schema": build_field_schema(),
        "explainer": build_auto_guard_explainer(values),
        "defaults": DEFAULTS,
    }
