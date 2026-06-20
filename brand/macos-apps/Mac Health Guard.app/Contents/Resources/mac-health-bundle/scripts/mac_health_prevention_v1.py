#!/usr/bin/env python3
"""Mac Health — proactive CPU/RAM prevention (before SICK, not after).

Auto-applies on live pulse when load spikes (especially post-wake):
  · factory freeze flag · hub stack stop · n8n pause · safe script kill · pipeline sweep

Never kills Cursor/WindowServer/Spotlight — surfaces Restart Cursor when Cursor is the hog.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
CONFIG_PATH = SINA / "config" / "mac-health-prevention-v1.json"
RECEIPT_PATH = SINA / "mac-health" / "prevention-latest-v1.json"
HISTORY_PATH = SINA / "mac-health" / "prevention-history-v1.jsonl"
ZOMBIE_SWEEP_PATH = SINA / "mac-health" / "last-zombie-sweep-v1.json"
ZOMBIE_SWEEP_COOLDOWN_SEC = 30
FREEZE_FLAG = SINA / "auto-run-disabled-v1.flag"
PEAK_DECAY_PATH = SINA / "mac-health" / "cursor-peak-decay-v1.json"
PEAK_DECAY_SEC = 120.0
DEFAULT_COOLDOWN_SEC = 90


def _stale_shell_hints(ghost_count: int) -> list[str]:
    """Read-only hints for hung background shells (never kill Hub/Heart)."""
    if ghost_count < 1:
        return []
    hints: list[str] = []
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid,command"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        for line in (proc.stdout or "").splitlines()[1:]:
            low = line.lower()
            if "railway login" in low or ("railway" in low and "browserless" in low):
                hints.append("Stale Railway login shell — safe to dismiss in Cursor")
            elif "head -5" in low and "railway" in low:
                hints.append("Hung terminal pipe from deploy setup — not active work")
            if len(hints) >= 3:
                break
    except Exception:
        pass
    if ghost_count >= 2 and not hints:
        hints.append(f"{ghost_count} ghost terminals — open More → Cool down if Mac feels stuck")
    return hints


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_config() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "enabled": True,
        "auto_apply": True,
        "cooldown_sec": DEFAULT_COOLDOWN_SEC,
        "wake_window_min": 45,
        "thresholds": {
            "load_per_core_warn": 0.45,
            "load_per_core_act": 0.65,
            "wake_cpu_pct_act": 35,
            "cursor_cpu_sum_warn": 120,
            "cursor_rss_mb_warn": 6000,
            "cursor_rss_mb_act": 8000,
            "ram_pct_act": 88,
        },
        "actions": {
            "freeze_factory_on_pressure": True,
            "kill_hub_on_pressure": True,
            "pause_n8n_on_pressure": True,
            "pipeline_sweep_on_zombies": True,
            "cool_down_on_wake_storm": True,
            "kill_scripts_min_cpu_wake": 12,
            "kill_scripts_min_cpu_normal": 28,
            "cursor_trim_on_pressure": True,
            "cursor_trim_only_under_control_plane": True,
        },
    }
    if CONFIG_PATH.is_file():
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            prev = raw.get("prevention") or raw
            for k, v in prev.items():
                if isinstance(v, dict) and k in defaults and isinstance(defaults[k], dict):
                    defaults[k].update(v)
                else:
                    defaults[k] = v
        except (OSError, json.JSONDecodeError):
            pass
    return defaults


def _uptime_minutes() -> float:
    try:
        out = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5.0).stdout
        m = re.search(r"up\s+(?:(\d+)\s+days?,?\s*)?(?:(\d+):(\d+)|(\d+)\s+mins?)", out)
        if not m:
            return 9999.0
        days = int(m.group(1) or 0)
        if m.group(4):
            return float(days * 24 * 60 + int(m.group(4)))
        hours, mins = int(m.group(2)), int(m.group(3))
        return float(days * 24 * 60 + hours * 60 + mins)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return 9999.0


def _cursor_pressure() -> dict[str, Any]:
    try:
        out = subprocess.run(
            ["ps", "-axo", "pid,pcpu,rss,comm"],
            capture_output=True,
            text=True,
            timeout=8.0,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {"cpu_sum": 0.0, "rss_mb": 0.0, "processes": 0, "peak_cpu": 0.0, "renderer_peak": 0.0}
    cpu_sum = 0.0
    rss_kb = 0
    count = 0
    peak_cpu = 0.0
    renderer_peak = 0.0
    for line in out.splitlines()[1:]:
        if "Cursor" not in line and "cursor" not in line.lower():
            continue
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        try:
            pcpu = float(parts[1])
            cpu_sum += pcpu
            peak_cpu = max(peak_cpu, pcpu)
            rss_kb += int(parts[2])
            count += 1
            comm = parts[3]
            if "Renderer" in comm:
                renderer_peak = max(renderer_peak, pcpu)
        except ValueError:
            continue
    return {
        "cpu_sum": round(cpu_sum, 1),
        "rss_mb": round(rss_kb / 1024, 1),
        "processes": count,
        "peak_cpu": round(peak_cpu, 1),
        "renderer_peak": round(renderer_peak, 1),
    }


def _cursor_pressure_decayed() -> dict[str, Any]:
    """Hold renderer peak for PEAK_DECAY_SEC so brief agent spikes do not nag."""
    raw = _cursor_pressure()
    now = time.time()
    instant = float(raw.get("renderer_peak") or 0)
    state: dict[str, Any] = {}
    if PEAK_DECAY_PATH.is_file():
        try:
            state = json.loads(PEAK_DECAY_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}
    stored = float(state.get("renderer_peak") or 0)
    stored_at = float(state.get("at") or 0)
    if instant >= stored:
        effective = instant
        state = {"renderer_peak": instant, "at": now}
    elif now - stored_at <= PEAK_DECAY_SEC:
        effective = max(instant, stored)
    else:
        effective = instant
        state = {"renderer_peak": instant, "at": now}
    PEAK_DECAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PEAK_DECAY_PATH.write_text(json.dumps(state), encoding="utf-8")
    raw["renderer_peak_instant"] = raw.get("renderer_peak")
    raw["renderer_peak"] = round(effective, 1)
    return raw


def _playwright_pressure() -> dict[str, Any]:
    """Detect stuck Cursor agent headless Chrome (common heat source)."""
    try:
        out = subprocess.run(
            ["ps", "-axo", "pcpu,rss,command"],
            capture_output=True,
            text=True,
            timeout=5.0,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {"processes": 0, "cpu_sum": 0.0, "rss_mb": 0.0, "stuck": False}
    cpu_sum = 0.0
    rss_kb = 0
    count = 0
    for line in out.splitlines()[1:]:
        low = line.lower()
        if "chrome-headless-shell" not in line and "playwright" not in low:
            continue
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        try:
            cpu_sum += float(parts[0])
            rss_kb += int(parts[1])
            count += 1
        except ValueError:
            continue
    stuck = count > 0 and cpu_sum >= 45.0
    return {
        "processes": count,
        "cpu_sum": round(cpu_sum, 1),
        "rss_mb": round(rss_kb / 1024, 1),
        "stuck": stuck,
    }


def _last_apply_age_sec() -> float | None:
    if not RECEIPT_PATH.is_file():
        return None
    try:
        rec = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        at = rec.get("at")
        if not at:
            return None
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def analyze_prevention(mp: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify body state + recommend control actions (no side effects)."""
    cfg = _load_config()
    if mp is None:
        from mac_health_guard import _machine_pressure  # noqa: WPS433

        mp = _machine_pressure()

    cores = max(int(mp.get("cpu_cores") or 1), 1)
    load = float(mp.get("load_1min") or 0)
    load_per_core = load / cores
    cpu_pct = float(mp.get("cpu_pct") or 0)
    ram_pct = float(mp.get("ram_used_pct") or 0)
    qz = int(mp.get("queue_zombies") or 0)
    ghosts = int(mp.get("ghost_terminals") or 0)
    uptime_min = _uptime_minutes()
    cursor = _cursor_pressure_decayed()
    playwright = _playwright_pressure()
    thr = cfg.get("thresholds") or {}

    wake_storm = uptime_min <= float(cfg.get("wake_window_min") or 45)
    wake_cpu_act = float(thr.get("wake_cpu_pct_act") or 35)
    load_warn = load_per_core >= float(thr.get("load_per_core_warn") or 0.45)
    load_act = load_per_core >= float(thr.get("load_per_core_act") or 0.65)
    cursor_hot = cursor["cpu_sum"] >= float(thr.get("cursor_cpu_sum_warn") or 60)
    cursor_ram = cursor["rss_mb"] >= float(thr.get("cursor_rss_mb_warn") or 4500)
    rss_mb = float(cursor["rss_mb"])
    if rss_mb >= 6144:
        cursor_ram_tier = "high"
    elif rss_mb >= 4096:
        cursor_ram_tier = "watch"
    else:
        cursor_ram_tier = "ok"
    renderer_peak = float(cursor.get("renderer_peak") or 0)
    # Cursor busy (60–200% CPU) is NORMAL while founder works in agent chats — not an emergency.
    cursor_emergency = renderer_peak >= 180 or cursor["cpu_sum"] >= 250 or (
        renderer_peak >= 150 and cpu_pct >= 70 and load_per_core >= 0.85
    )
    cursor_actually_hot = cursor_emergency
    ram_act = ram_pct >= float(thr.get("ram_pct_act") or 82)
    wake_pressure = (
        load_warn
        or cursor_actually_hot
        or cpu_pct >= wake_cpu_act
        or qz >= 2
        or ghosts >= 1
    )

    modes: list[str] = []
    if wake_storm and wake_pressure:
        modes.append("wake_storm")
    if cursor_actually_hot:
        modes.append("cursor_hot")
    elif cursor_hot or cursor_ram:
        modes.append("cursor_busy")
    if qz >= 4:
        modes.append("factory_leak")
    if ghosts >= 2:
        modes.append("ghost_terminals")
    if ram_act:
        modes.append("ram_pressure")
    if load_act and not modes:
        modes.append("load_high")
    if playwright.get("stuck"):
        modes.append("playwright_stuck")
    bomb = mp.get("sina_log_bomb") or {}
    if bomb.get("critical"):
        modes.append("log_bomb")
    elif bomb.get("level") == "warn":
        modes.append("log_warn")
    if mp.get("hub_online") and not mp.get("hub_health_ok"):
        modes.append("hub_sick")
    if int(mp.get("stuck_log_reader_count") or 0) >= 1:
        modes.append("stuck_log_readers")
    factory_storm = (mp.get("factory_storm") or {}).get("factory_storm")
    if factory_storm:
        modes.append("factory_storm")
    film_render = mp.get("film_render") or {}
    if film_render.get("violation"):
        modes.append("film_render_violation")
    elif film_render.get("active") and float(film_render.get("cpu_sum") or 0) >= 30:
        modes.append("film_render_hot")

    if not modes and not load_warn:
        health = "healthy"
    elif (
        ram_act
        or qz >= 12
        or (wake_storm and wake_pressure)
        or cursor_actually_hot
        or bomb.get("critical")
        or factory_storm
        or (load_act and ("factory_leak" in modes or qz >= 2 or ghosts >= 2))
    ):
        health = "unhealthy"
    else:
        health = "watch"

    founder_action = "Keep working — body is balanced."
    tap_action = None
    if "wake_storm" in modes:
        chrome_note = " · Chrome if Mac hot"
        try:
            from mac_health_settings_v1 import load_settings  # noqa: WPS433

            ch = load_settings().get("chrome") or {}
            mode = str(ch.get("quit_on_wake_cool_down_mode") or "when_mac_hot")
            if mode == "always":
                chrome_note = " · Chrome"
            elif mode == "never":
                chrome_note = " · Chrome kept open"
        except Exception:
            pass
        founder_action = (
            f"Wake storm ({uptime_min:.0f} min since boot) — tap Wake Cool Down: "
            f"freeze factory + clear hub · pipeline · ghosts{chrome_note} · n8n."
        )
        tap_action = "cpu_wake_cool_down"
        if cursor_actually_hot:
            rss_gb = float(cursor["rss_mb"]) / 1024
            founder_action += (
                f" Cursor {cursor['cpu_sum']:.0f}% CPU · {rss_gb:.1f} GB — Restart Cursor after."
            )
    elif cursor_actually_hot:
        rss_gb = float(cursor["rss_mb"]) / 1024
        founder_action = (
            f"Cursor emergency — {cursor['cpu_sum']:.0f}% CPU · {rss_gb:.1f} GB — "
            "Mac frozen? Restart Cursor once. Otherwise stop background agents only."
        )
        tap_action = "cpu_restart_cursor"
    elif "playwright_stuck" in modes:
        founder_action = (
            f"Stuck agent browser ({playwright['cpu_sum']:.0f}% CPU · "
            f"{playwright['processes']} proc) — Terminal: pkill -f chrome-headless-shell"
        )
        tap_action = None
    elif "film_render_violation" in modes:
        fr = mp.get("film_render") or {}
        founder_action = (
            f"Film capture running while FROZEN ({fr.get('processes', 0)} proc · "
            f"{fr.get('cpu_sum', 0):.0f}% CPU) — kill-active in Mac Health"
        )
        tap_action = None
    elif "film_render_hot" in modes:
        fr = mp.get("film_render") or {}
        founder_action = (
            f"Commercial film render active ({fr.get('processes', 0)} proc · "
            f"{fr.get('rss_mb', 0):.0f} MB RAM) — Playwright capture heats Mac"
        )
        tap_action = None
    elif "cursor_busy" in modes:
        rss_gb = float(cursor["rss_mb"]) / 1024
        founder_action = (
            f"Cursor busy ({cursor['cpu_sum']:.0f}% CPU · {rss_gb:.1f} GB) — "
            "normal while you work in agent chats. Cursor stays open — no auto-stop at this level."
        )
        tap_action = None
    elif load_act:
        founder_action = "Load high — Cool Down ran or will run automatically."
        tap_action = "cpu_cool_down"

    return {
        "schema": "mac-health-prevention-v1",
        "at": _now(),
        "enabled": bool(cfg.get("enabled")),
        "auto_apply": bool(cfg.get("auto_apply")),
        "health": health,
        "modes": modes,
        "wake_storm": wake_storm,
        "uptime_min": round(uptime_min, 1),
        "load_per_core": round(load_per_core, 2),
        "cpu_pct": cpu_pct,
        "ram_pct": ram_pct,
        "cursor": cursor,
        "cursor_ram_tier": cursor_ram_tier,
        "playwright": playwright,
        "queue_zombies": qz,
        "ghost_terminals": ghosts,
        "stale_shell_hints": _stale_shell_hints(ghosts),
        "factory_frozen": FREEZE_FLAG.is_file(),
        "founder_line": founder_action,
        "next_tap_action": tap_action,
        "cooldown_sec_remaining": max(
            0,
            int(float(cfg.get("cooldown_sec") or DEFAULT_COOLDOWN_SEC) - ( _last_apply_age_sec() or 9999)),
        )
        if _last_apply_age_sec() is not None
        else 0,
    }


def _append_history(row: dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def _prevention_step_detail(key: str, step: dict[str, Any]) -> str:
    if step.get("detail"):
        return str(step["detail"])
    if step.get("summary"):
        return str(step["summary"])
    if key == "scripts":
        kc = int(step.get("killed_count") or 0)
        return (
            f"killed {kc} allowlisted script{'s' if kc != 1 else ''}"
            if kc
            else "no allowlisted scripts above CPU floor"
        )
    if key == "pipeline":
        return (
            f"killed {int(step.get('killed') or 0)} queue zombies "
            f"({int(step.get('before') or 0)} → {int(step.get('after') or 0)})"
        )
    if key == "ghosts":
        closed = int(step.get("closed") or 0)
        patched = int(step.get("patched") or 0)
        return f"closed {closed} ghost terminal{'s' if closed != 1 else ''} · patched {patched}"
    return key


def _prevention_step_effective(key: str, step: dict[str, Any]) -> bool:
    if not isinstance(step, dict):
        return False
    if key == "factory_freeze":
        detail = str(step.get("detail") or "")
        return "auto-run disabled" in detail
    if key == "n8n":
        return bool(step.get("had_n8n")) and not bool(step.get("still_running"))
    if key == "scripts":
        return int(step.get("killed_count") or 0) > 0
    if key == "pipeline":
        return int(step.get("killed") or 0) > 0
    if key == "ghosts":
        return int(step.get("closed") or 0) > 0 or int(step.get("patched") or 0) > 0
    if key == "hub":
        return bool(step.get("killed") or step.get("ok"))
    return bool(step.get("ok"))


def apply_prevention(
    mp: dict[str, Any] | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Apply gentle automatic controls. Respects cooldown unless force."""
    cfg = _load_config()
    analysis = analyze_prevention(mp)
    if not cfg.get("auto_apply") and not force:
        return {**analysis, "applied": False, "reason": "auto_apply_off"}
    try:
        from mac_health_ram_pressure_v1 import founder_stop_heavy_processing  # noqa: WPS433

        if founder_stop_heavy_processing() and not force:
            return {**analysis, "applied": False, "reason": "founder_stop_heavy_processing"}
    except Exception:
        pass
    if not cfg.get("enabled"):
        return {**analysis, "applied": False, "reason": "disabled"}

    age = _last_apply_age_sec()
    cooldown = float(cfg.get("cooldown_sec") or DEFAULT_COOLDOWN_SEC)
    if not force and age is not None and age < cooldown:
        return {
            **analysis,
            "applied": False,
            "reason": "cooldown",
            "cooldown_sec_remaining": int(cooldown - age),
        }

    health = analysis.get("health")
    if not force and health == "healthy":
        return {**analysis, "applied": False, "reason": "healthy"}

    actions_cfg = cfg.get("actions") or {}
    steps: dict[str, Any] = {}
    wake = bool(analysis.get("wake_storm"))

    if actions_cfg.get("freeze_factory_on_pressure") and analysis.get("health") == "unhealthy":
        if not FREEZE_FLAG.is_file():
            FREEZE_FLAG.write_text(
                f"mac-health-prevention-v1 · {_now()} · load_per_core={analysis.get('load_per_core')}\n",
                encoding="utf-8",
            )
            steps["factory_freeze"] = {"ok": True, "detail": "auto-run disabled — factory paused"}
        else:
            steps["factory_freeze"] = {"ok": True, "detail": "already frozen"}

    if "ram_pressure" in (analysis.get("modes") or []) and actions_cfg.get("bootout_autorun_on_ram", True):
        try:
            from mac_health_ram_pressure_v1 import bootout_autorun  # noqa: WPS433

            steps["autorun_bootout"] = bootout_autorun()
        except Exception as exc:
            steps["autorun_bootout"] = {"ok": False, "error": str(exc)[:80]}

    if "ram_pressure" in (analysis.get("modes") or []) and actions_cfg.get("kill_forbidden_body_on_ram", True):
        try:
            from mac_pipeline_validator_pressure_v1 import run_pressure_probe  # noqa: WPS433

            steps["forbidden_body"] = run_pressure_probe(side_effects=True)
        except Exception as exc:
            steps["forbidden_body"] = {"ok": False, "error": str(exc)[:80]}

    if actions_cfg.get("kill_hub_on_pressure") and force and (
        wake or float(analysis.get("load_per_core") or 0) >= float((cfg.get("thresholds") or {}).get("load_per_core_act") or 0.65)
    ):
        from mac_health_cpu_relief_v1 import kill_legacy_hub_stack  # noqa: WPS433

        steps["hub"] = kill_legacy_hub_stack()

    if actions_cfg.get("pause_n8n_on_pressure") and analysis.get("health") == "unhealthy":
        from mac_health_cpu_relief_v1 import pause_n8n  # noqa: WPS433

        steps["n8n"] = pause_n8n()

    min_cpu = float(
        actions_cfg.get("kill_scripts_min_cpu_wake" if wake else "kill_scripts_min_cpu_normal") or (12 if wake else 28)
    )
    if float(analysis.get("ram_pct") or 0) >= 90:
        min_cpu = min(min_cpu, float(actions_cfg.get("kill_scripts_min_cpu_ram_critical") or 8))
    from mac_health_cpu_relief_v1 import kill_safe_cpu_hogs  # noqa: WPS433

    steps["scripts"] = kill_safe_cpu_hogs(min_cpu=min_cpu)

    if actions_cfg.get("pipeline_sweep_on_zombies"):
        from mac_health_guard import pipeline_queue_sweep, pipeline_queue_zombie_pids  # noqa: WPS433

        if pipeline_queue_zombie_pids():
            steps["pipeline"] = pipeline_queue_sweep()

    if int(analysis.get("ghost_terminals") or 0) >= 2:
        from mac_health_guard import cart_fleet_sweep  # noqa: WPS433

        steps["ghosts"] = cart_fleet_sweep()

    modes = analysis.get("modes") or []
    if "log_bomb" in modes or "stuck_log_readers" in modes:
        from mac_health_log_shield_v1 import kill_stuck_log_readers, truncate_runaway_logs  # noqa: WPS433

        if "stuck_log_readers" in modes:
            steps["log_readers"] = kill_stuck_log_readers()
        if "log_bomb" in modes:
            steps["log_truncate"] = truncate_runaway_logs()

    if ("cursor_busy" in modes or "cursor_hot" in modes) and actions_cfg.get("cursor_trim_on_pressure", True):
        try:
            from cursor_session_relief_v1 import probe_cursor_session, trim_cursor_caches  # noqa: WPS433

            thr = cfg.get("thresholds") or {}
            probe = probe_cursor_session()
            rss_mb = float(probe.get("total_mb") or 0)
            act_mb = float(thr.get("cursor_rss_mb_act") or 8000)
            if rss_mb >= act_mb and actions_cfg.get("cursor_restart_nudge", True):
                steps["cursor_nudge"] = {
                    "ok": True,
                    "detail": f"Cursor {rss_mb:.0f} MB — run founder-mac-reset --hard",
                    "rss_mb": rss_mb,
                }
            steps["cursor_trim"] = trim_cursor_caches()
        except Exception:
            pass

    step_lines = []
    for key, step in steps.items():
        if isinstance(step, dict):
            step_lines.append(f"{key}: {_prevention_step_detail(key, step)}")

    effective = any(_prevention_step_effective(k, v) for k, v in steps.items())
    if not effective:
        return {
            **analysis,
            "applied": False,
            "reason": "no_op",
            "steps": steps,
            "step_lines": step_lines,
            "summary": " · ".join(step_lines) if step_lines else "No automatic actions needed",
            "factory_frozen": FREEZE_FLAG.is_file(),
        }

    receipt = {
        **analysis,
        "applied": True,
        "at": _now(),
        "steps": steps,
        "step_lines": step_lines,
        "summary": " · ".join(step_lines) if step_lines else "No automatic actions needed",
        "factory_frozen": FREEZE_FLAG.is_file(),
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _append_history({"at": receipt["at"], "health": health, "modes": analysis.get("modes"), "summary": receipt["summary"]})
    return receipt


def apply_wake_cool_down(
    mp: dict[str, Any] | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Full wake cool down — freeze + complete factory relief stack."""
    cfg = _load_config()
    analysis = analyze_prevention(mp)
    if not cfg.get("enabled"):
        return {**analysis, "applied": False, "reason": "disabled", "wake_cool_down": True}

    if "wake_storm" not in (analysis.get("modes") or []) and not force:
        return {**analysis, "applied": False, "reason": "not_wake_storm", "wake_cool_down": True}

    age = _last_apply_age_sec()
    cooldown = float(cfg.get("cooldown_sec") or DEFAULT_COOLDOWN_SEC)
    if not force and age is not None and age < cooldown:
        return {
            **analysis,
            "applied": False,
            "reason": "cooldown",
            "wake_cool_down": True,
            "cooldown_sec_remaining": int(cooldown - age),
        }

    from mac_health_cpu_relief_v1 import run_wake_cool_down  # noqa: WPS433

    relief = run_wake_cool_down()
    receipt = {
        **analysis,
        "applied": True,
        "wake_cool_down": True,
        "at": _now(),
        "relief": relief,
        "steps": relief.get("steps") or {},
        "step_lines": relief.get("step_lines") or [],
        "summary": relief.get("summary") or "Wake cool down complete",
        "factory_frozen": FREEZE_FLAG.is_file(),
        "cursor_still_hot": relief.get("cursor_still_hot"),
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _append_history(
        {
            "at": receipt["at"],
            "health": analysis.get("health"),
            "modes": analysis.get("modes"),
            "summary": receipt["summary"],
            "wake_cool_down": True,
        }
    )
    return receipt


def _last_zombie_sweep_age_sec() -> float | None:
    if not ZOMBIE_SWEEP_PATH.is_file():
        return None
    try:
        rec = json.loads(ZOMBIE_SWEEP_PATH.read_text(encoding="utf-8"))
        at = rec.get("at")
        if not at:
            return None
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def auto_sweep_queue_zombies(mp: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Always-on zombie sweep on live pulse — runs even when health is healthy."""
    try:
        from mac_health_ram_pressure_v1 import founder_stop_heavy_processing  # noqa: WPS433

        if founder_stop_heavy_processing():
            return None
    except Exception:
        pass
    cfg = _load_config()
    if not cfg.get("enabled"):
        return None
    actions_cfg = cfg.get("actions") or {}
    if not actions_cfg.get("pipeline_sweep_on_zombies", True):
        return None
    analysis = analyze_prevention(mp)
    from mac_health_guard import pipeline_queue_sweep, pipeline_queue_zombie_pids  # noqa: WPS433

    fresh_pids = pipeline_queue_zombie_pids()
    qz = len(fresh_pids)
    if qz < 1:
        return None
    age = _last_zombie_sweep_age_sec()
    if age is not None and age < ZOMBIE_SWEEP_COOLDOWN_SEC:
        return {**analysis, "applied": False, "reason": "zombie_cooldown", "queue_zombies": qz}

    sweep = pipeline_queue_sweep()
    killed = int(sweep.get("killed") or 0)
    before = int(sweep.get("before") or 0)
    after = int(sweep.get("after") or 0)
    if killed == 0 and after >= before:
        return {**analysis, "applied": False, "reason": "sweep_no_op", "queue_zombies": after}
    receipt = {
        **analysis,
        "queue_zombies": after,
        "applied": True,
        "zombie_sweep_only": True,
        "at": _now(),
        "steps": {"pipeline": sweep},
        "step_lines": [
            f"pipeline: killed {killed} queue zombie{'s' if killed != 1 else ''} "
            f"({sweep.get('before', 0)} → {sweep.get('after', 0)})"
        ],
        "summary": (
            f"Auto pipeline sweep · killed {killed} · "
            f"{sweep.get('before', 0)} → {sweep.get('after', 0)} zombies"
        ),
    }
    ZOMBIE_SWEEP_PATH.parent.mkdir(parents=True, exist_ok=True)
    ZOMBIE_SWEEP_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if killed > 0 or qz >= 2:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        _append_history(
            {
                "at": receipt["at"],
                "health": analysis.get("health"),
                "modes": analysis.get("modes"),
                "summary": receipt["summary"],
                "zombie_sweep_only": True,
            }
        )
    return receipt


def maybe_auto_prevent(mp: dict[str, Any] | None = None) -> dict[str, Any]:
    """Called from live pulse — auto zombie sweep + apply if auto_apply and unhealthy."""
    try:
        from mac_health_ram_pressure_v1 import founder_stop_heavy_processing  # noqa: WPS433

        if founder_stop_heavy_processing():
            analysis = analyze_prevention(mp)
            return {**analysis, "applied": False, "reason": "founder_stop_heavy_processing"}
    except Exception:
        pass
    cfg = _load_config()
    analysis = analyze_prevention(mp)
    zombie = auto_sweep_queue_zombies(mp)
    if zombie and zombie.get("applied"):
        if analysis.get("health") == "healthy":
            return zombie
        if (zombie.get("steps") or {}).get("pipeline", {}).get("killed", 0) > 0:
            analysis = {**analysis, "zombie_sweep": zombie}
    if not cfg.get("enabled") or not cfg.get("auto_apply"):
        return {**analysis, "applied": False, "reason": "auto_apply_off"}
    if analysis.get("health") == "healthy":
        return {**analysis, "applied": False, "reason": "healthy"}
    # Wake cool down kills hub — founder tap only (INCIDENT-035); auto path uses gentle prevention.
    return apply_prevention(mp)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac Health prevention control")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--wake-cool-down", action="store_true", help="Apply wake cool down stack")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.wake_cool_down:
        row = apply_wake_cool_down(force=args.force)
    elif args.apply:
        row = apply_prevention(force=args.force)
    else:
        row = analyze_prevention()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("health"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
