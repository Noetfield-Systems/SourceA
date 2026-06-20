#!/usr/bin/env python3
"""Mac Health — one-tap CPU relief actions (local only)."""
from __future__ import annotations

import os
import re
import signal
import subprocess
import time
from typing import Any

# Scripts safe to kill when hogging CPU — never Cursor/WindowServer/mac-health.
SAFE_KILL_PATTERNS = (
    "align_command_data_ui_v1.py",
    "build_phase_strict_queue_v1.py",
    "find_critical_bugs",
    "governance_meta_audit_v1.py",
    "auto_run_worker_batch",
    "healthy_prompt_turn_v1.py",
    "queue_ssot_unify_v1.py",
    "hub_projection_sync_v1.py",
)

PROTECTED_PATTERNS = (
    "mac-health-guard-server",
    "mac_health_guard",
    "mac_health_live",
    "WindowServer",
    "kernel_task",
    "PerfPowerService",
    "/usr/sbin/screencapture",
    "screencaptureui",
    "Screenshot",
)


def _run(cmd: list[str], *, timeout: float = 12.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 1, str(exc)


def _top_cpu_rows(limit: int = 20) -> list[dict[str, Any]]:
    code, out = _run(["ps", "-axo", "pid,pcpu,comm"], timeout=8.0)
    if code != 0:
        return []
    rows: list[dict[str, Any]] = []
    for line in out.splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid_s, cpu_s, comm = parts
        try:
            rows.append({"pid": int(pid_s), "cpu_pct": float(cpu_s), "comm": comm.strip()[:160]})
        except ValueError:
            continue
    rows.sort(key=lambda r: r["cpu_pct"], reverse=True)
    return rows[:limit]


def _is_protected(comm: str) -> bool:
    low = comm.lower()
    return any(p.lower() in low for p in PROTECTED_PATTERNS)


def _matches_safe_kill(comm: str) -> str | None:
    for pat in SAFE_KILL_PATTERNS:
        if pat in comm:
            return pat
    return None


def kill_safe_cpu_hogs(*, min_cpu: float = 35.0) -> dict[str, Any]:
    """SIGTERM then SIGKILL stuck factory/hub scripts — not apps."""
    killed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for row in _top_cpu_rows(25):
        comm = row["comm"]
        if row["cpu_pct"] < min_cpu:
            continue
        if _is_protected(comm):
            skipped.append({**row, "reason": "protected"})
            continue
        pat = _matches_safe_kill(comm)
        if not pat:
            skipped.append({**row, "reason": "not_allowlisted"})
            continue
        pid = row["pid"]
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.3)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            killed.append({**row, "pattern": pat})
        except (ProcessLookupError, PermissionError) as exc:
            skipped.append({**row, "reason": str(exc)})
    return {"ok": True, "killed": killed, "killed_count": len(killed), "skipped": skipped[:8]}


def quit_chrome() -> dict[str, Any]:
    code, out = _run(
        ["osascript", "-e", 'tell application "Google Chrome" to quit'],
        timeout=15.0,
    )
    time.sleep(0.8)
    code2, _ = _run(["pgrep", "-x", "Google Chrome"], timeout=4.0)
    still = code2 == 0
    return {
        "ok": code == 0 and not still,
        "method": "osascript_quit",
        "detail": out[:200] or ("Chrome still running" if still else "Chrome quit"),
        "still_running": still,
    }


def pause_n8n() -> dict[str, Any]:
    before_code, before_out = _run(["pgrep", "-f", "n8n"], timeout=5.0)
    had = before_code == 0 and bool(before_out.strip())
    for flag in ("-TERM", "-9"):
        _run(["pkill", flag, "-f", "n8n start"], timeout=8.0)
        _run(["pkill", flag, "-f", "@n8n/task-runner"], timeout=8.0)
        _run(["pkill", flag, "-f", "/n8n/bin/n8n"], timeout=8.0)
        time.sleep(0.5)
    after_code, after_out = _run(["pgrep", "-f", "n8n"], timeout=5.0)
    after = after_code == 0 and bool(after_out.strip())
    return {
        "ok": (had and not after) or not had,
        "had_n8n": had,
        "still_running": after,
        "detail": "n8n paused" if not after else "n8n may still be stopping — tap again",
    }


def kill_legacy_hub_stack() -> dict[str, Any]:
    """Stop legacy :13020 hub workers — keep Mac Health + standalone mini-apps."""
    patterns = (
        "sina-command-server",
        "hub_rebuild_worker",
        "auto_run_worker_batch",
        "dashboard_server",
        "build_phase_strict_queue_v1.py",
    )
    killed: list[str] = []
    for pat in patterns:
        code, out = _run(["pgrep", "-f", pat], timeout=4.0)
        if code == 0 and out.strip():
            _run(["pkill", "-TERM", "-f", pat], timeout=6.0)
            time.sleep(0.2)
            code2, _ = _run(["pgrep", "-f", pat], timeout=4.0)
            if code2 == 0:
                _run(["pkill", "-9", "-f", pat], timeout=6.0)
            killed.append(pat)
    time.sleep(0.6)
    still: list[str] = []
    for pat in patterns:
        code, _ = _run(["pgrep", "-f", pat], timeout=4.0)
        if code == 0:
            still.append(pat)
    return {
        "ok": len(still) == 0,
        "killed": killed,
        "still_running": still,
        "detail": "legacy hub stopped" if not still else f"still running: {', '.join(still[:3])}",
    }


def kill_sina_stack() -> dict[str, Any]:
    """Quit Sina desktop apps + hub scripts — not Cursor."""
    patterns = (
        "sina-command-server",
        "hub_rebuild_worker",
        "auto_run_worker_batch",
        "dashboard_server",
        "mac-health-guard-server",
        "n8n-integration-server",
        "chat-unify-server",
        "apple-health-server",
    )
    killed: list[str] = []
    for pat in patterns:
        code, out = _run(["pgrep", "-f", pat], timeout=4.0)
        if code == 0 and out.strip():
            _run(["pkill", "-TERM", "-f", pat], timeout=6.0)
            killed.append(pat)
    for app in ("Mac Health Guard", "N8N Integration", "Chat Unify", "Apple Health"):
        _run(["osascript", "-e", f'tell application "{app}" to quit'], timeout=10.0)
    _run(["pkill", "-TERM", "-f", "n8n start"], timeout=6.0)
    time.sleep(0.8)
    still: list[str] = []
    for pat in patterns:
        code, _ = _run(["pgrep", "-f", pat], timeout=4.0)
        if code == 0:
            still.append(pat)
    return {
        "ok": len(still) == 0,
        "killed": killed,
        "still_running": still,
        "detail": "Sina stack stopped" if not still else f"still running: {', '.join(still[:3])}",
    }


def restart_cursor() -> dict[str, Any]:
    try:
        from cursor_session_relief_v1 import restart_cursor as _session_restart  # noqa: WPS433

        return _session_restart(force=True)
    except Exception:
        pass
    steps: list[dict[str, Any]] = []
    code, out = _run(
        ["osascript", "-e", 'tell application "Cursor" to quit saving yes'],
        timeout=25.0,
    )
    steps.append({"step": "osascript_quit", "ok": code == 0, "detail": (out or "quit sent")[:160]})
    time.sleep(2.0)
    for pat in (
        "Cursor.app/Contents/MacOS/Cursor",
        "Cursor Helper (Renderer)",
        "Cursor Helper (GPU)",
    ):
        _run(["pkill", "-TERM", "-f", pat], timeout=8.0)
    time.sleep(1.0)
    _run(["pkill", "-9", "-f", "Cursor.app/Contents/MacOS/Cursor"], timeout=8.0)
    time.sleep(0.8)
    code2, remaining = _run(["pgrep", "-f", "Cursor.app/Contents/MacOS/Cursor"], timeout=5.0)
    still = code2 == 0 and bool(remaining.strip())
    steps.append({"step": "force_stop", "ok": not still, "detail": "stopped" if not still else remaining[:120]})
    open_code, open_out = _run(["open", "-a", "Cursor"], timeout=15.0)
    steps.append({"step": "reopen", "ok": open_code == 0, "detail": (open_out or "Cursor launching")[:160]})
    return {
        "ok": open_code == 0,
        "method": "quit_save_reopen_legacy",
        "steps": steps,
        "still_running": still,
        "detail": "Cursor restarting — reopen your chat when the window returns"
        if open_code == 0
        else (open_out[:200] or "Could not reopen Cursor"),
        "warning": "Save work first; unsaved editor buffers may need recovery",
    }


def snapshot_pressure() -> dict[str, Any]:
    load_raw = subprocess.run(
        ["sysctl", "-n", "vm.loadavg"],
        capture_output=True,
        text=True,
        timeout=5.0,
    ).stdout.strip()
    m = re.search(r"\{?\s*([\d.]+)", load_raw)
    load_1 = float(m.group(1)) if m else 0.0
    cores = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True, timeout=5.0).stdout.strip() or "1")
    top = _top_cpu_rows(5)
    return {
        "load_1min": load_1,
        "cores": cores,
        "cpu_pct": round((load_1 / max(cores, 1)) * 100, 1),
        "top_cpu": top,
    }


def _step_summary(key: str, step: dict[str, Any]) -> str | None:
    if not isinstance(step, dict):
        return None
    if key == "safe_hogs":
        n = int(step.get("killed_count") or 0)
        return f"scripts: killed {n}" if n else "scripts: none hot"
    if key == "cart":
        n = int(step.get("patched") or 0)
        return f"ghosts: cleared {n}" if n else "ghosts: none"
    if key == "pipeline":
        n = int(step.get("killed") or 0)
        return f"pipeline: killed {n}" if n else "pipeline: clear"
    if key == "chrome":
        if step.get("skipped"):
            detail = step.get("detail") or "Chrome kept open"
            return f"Chrome: {detail}"[:120]
        if step.get("ok"):
            return "Chrome: closed"
        return "Chrome: not running" if not step.get("still_running") else "Chrome: still open"
    if key == "n8n":
        if step.get("ok"):
            return "n8n: paused" if step.get("had_n8n") else "n8n: was off"
        return "n8n: still running" if step.get("still_running") else "n8n: pause failed"
    if key == "hub_stack":
        if step.get("ok"):
            return "legacy hub: stopped"
        if step.get("killed"):
            return f"legacy hub: stopped {len(step.get('killed') or [])}"
        return "legacy hub: none running"
    if key == "cursor":
        if step.get("ok"):
            return "Cursor: restarting"
        return f"Cursor: {step.get('detail') or 'failed'}"[:80]
    if key == "sina_stack":
        return "Sina stack: stopped" if step.get("ok") else "Sina stack: partial"
    if key == "playwright":
        if step.get("ok"):
            return step.get("detail") or "agent browser: cleared"
        return "agent browser: none found"
    return None


def kill_playwright_browsers() -> dict[str, Any]:
    """Kill stuck Cursor agent headless Chrome — not Cursor itself."""
    patterns = ("chrome-headless-shell", "playwright.*chromium")
    signals = 0
    for pat in patterns:
        try:
            proc = subprocess.run(
                ["pkill", "-f", pat],
                capture_output=True,
                text=True,
                timeout=3.0,
            )
            if proc.returncode == 0:
                signals += 1
        except (OSError, subprocess.TimeoutExpired):
            continue
    return {
        "ok": True,
        "signals": signals,
        "detail": "headless Chrome cleared" if signals else "no headless Chrome running",
    }


def run_wake_cool_down() -> dict[str, Any]:
    """Post-wake full stack: freeze factory + cool down at lower script threshold."""
    from pathlib import Path

    sina = Path.home() / ".sina"
    freeze_flag = sina / "auto-run-disabled-v1.flag"
    before = snapshot_pressure()
    result: dict[str, Any] = {
        "ok": True,
        "action": "wake_cool_down",
        "wake_storm": True,
        "before": before,
        "steps": {},
    }
    if not freeze_flag.is_file():
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        freeze_flag.write_text(
            f"mac-health wake-cool-down · {ts} · load={before.get('load_1min')}\n",
            encoding="utf-8",
        )
        result["steps"]["factory_freeze"] = {"ok": True, "detail": "auto-run disabled — factory paused"}
    else:
        result["steps"]["factory_freeze"] = {"ok": True, "detail": "already frozen"}

    from mac_health_guard import cart_fleet_sweep, pipeline_queue_sweep  # noqa: WPS433

    result["steps"]["hub_stack"] = kill_legacy_hub_stack()
    result["steps"]["pipeline"] = pipeline_queue_sweep(force=True)
    result["steps"]["cart"] = cart_fleet_sweep()
    result["steps"]["safe_hogs"] = kill_safe_cpu_hogs(min_cpu=12.0)
    try:
        from mac_health_settings_v1 import chrome_quit_decision  # noqa: WPS433

        allowed, detail = chrome_quit_decision("wake_cool_down", before)
        if allowed:
            result["steps"]["chrome"] = quit_chrome()
        else:
            result["steps"]["chrome"] = {"ok": True, "skipped": True, "detail": detail}
    except Exception:
        result["steps"]["chrome"] = quit_chrome()
    result["steps"]["n8n"] = pause_n8n()

    time.sleep(1.2)
    after = snapshot_pressure()
    result["after"] = after
    result["improved"] = (after.get("cpu_pct") or 999) < (before.get("cpu_pct") or 0) - 5
    step_lines: list[str] = []
    for key, step in result.get("steps", {}).items():
        line = _step_summary(key, step)
        if line:
            step_lines.append(line)
    result["step_lines"] = step_lines
    parts: list[str] = [
        ln
        for ln in step_lines
        if not ln.endswith(": none")
        and not ln.endswith(": clear")
        and not ln.endswith(": was off")
        and not ln.endswith(": none running")
    ]
    if not parts:
        parts = step_lines[:]
    result["summary"] = (
        "Wake cool down · " + (" · ".join(parts) if parts else "factory frozen — no junk found")
    )
    try:
        from mac_health_prevention_v1 import analyze_prevention  # noqa: WPS433

        prev = analyze_prevention(after)
        cursor = prev.get("cursor") or {}
        if "cursor_hot" in (prev.get("modes") or []):
            result["summary"] += (
                f" · Factory clear ✓ — Cursor still {cursor.get('cpu_sum', '?')}% CPU → Restart Cursor"
            )
            result["cursor_still_hot"] = True
            result["prevention"] = prev
    except Exception:
        pass
    result["founder_line"] = (
        f"Wake cool down · CPU {before.get('cpu_pct')}% → {after.get('cpu_pct')}% · "
        f"load {before.get('load_1min')} → {after.get('load_1min')}"
    )
    return result


def run_cpu_relief(action: str) -> dict[str, Any]:
    """Dispatch one-tap CPU relief. Imports mac_health_guard lazily for cart/pipeline."""
    action = (action or "").strip().lower()
    before = snapshot_pressure()

    result: dict[str, Any] = {"ok": True, "action": action, "before": before, "steps": {}}

    if action in ("cool_down", "cpu_cool_down", "ease_cpu"):
        from mac_health_guard import cart_fleet_sweep, pipeline_queue_sweep  # noqa: WPS433

        result["steps"]["hub_stack"] = kill_legacy_hub_stack()
        result["steps"]["pipeline"] = pipeline_queue_sweep(force=True)
        result["steps"]["cart"] = cart_fleet_sweep()
        result["steps"]["safe_hogs"] = kill_safe_cpu_hogs(min_cpu=25.0)
        try:
            from mac_health_settings_v1 import chrome_quit_decision  # noqa: WPS433

            allowed, detail = chrome_quit_decision("cool_down", before)
            if allowed:
                result["steps"]["chrome"] = quit_chrome()
            else:
                result["steps"]["chrome"] = {
                    "ok": True,
                    "skipped": True,
                    "detail": detail,
                }
        except Exception:
            result["steps"]["chrome"] = quit_chrome()
        result["steps"]["n8n"] = pause_n8n()
        try:
            from cursor_session_relief_v1 import trim_cursor_caches  # noqa: WPS433

            result["steps"]["cursor_trim"] = trim_cursor_caches()
        except Exception as exc:
            result["steps"]["cursor_trim"] = {"ok": False, "error": str(exc)[:120]}
    elif action in ("wake_cool_down", "cpu_wake_cool_down", "wake_cool"):
        return run_wake_cool_down()
    elif action in ("kill_safe_hogs", "cpu_kill_scripts"):
        result["steps"]["safe_hogs"] = kill_safe_cpu_hogs()
    elif action in ("quit_chrome", "cpu_quit_chrome", "close_chrome"):
        result["steps"]["chrome"] = quit_chrome()
    elif action in ("pause_n8n", "cpu_pause_n8n"):
        result["steps"]["n8n"] = pause_n8n()
    elif action in ("clear_ghosts", "cpu_clear_ghosts"):
        from mac_health_guard import cart_fleet_sweep  # noqa: WPS433

        result["steps"]["cart"] = cart_fleet_sweep()
    elif action in ("clear_pipeline", "cpu_clear_pipeline"):
        from mac_health_guard import pipeline_queue_sweep  # noqa: WPS433

        result["steps"]["pipeline"] = pipeline_queue_sweep(force=True)
    elif action in ("restart_cursor", "cpu_restart_cursor"):
        result["steps"]["cursor"] = restart_cursor()
        result["warning"] = result["steps"]["cursor"].get("warning")
    elif action in ("kill_sina_stack", "cpu_kill_sina_stack"):
        result["steps"]["sina_stack"] = kill_sina_stack()
    elif action in ("kill_playwright", "cpu_kill_playwright"):
        result["steps"]["playwright"] = kill_playwright_browsers()
    else:
        return {"ok": False, "error": f"unknown cpu relief action: {action}"}

    time.sleep(1.2)
    after = snapshot_pressure()
    result["after"] = after
    result["improved"] = (after.get("cpu_pct") or 999) < (before.get("cpu_pct") or 0) - 5
    step_lines: list[str] = []
    for key, step in result.get("steps", {}).items():
        line = _step_summary(key, step)
        if line:
            step_lines.append(line)
    result["step_lines"] = step_lines
    parts: list[str] = [ln for ln in step_lines if not ln.endswith(": none") and not ln.endswith(": clear") and not ln.endswith(": was off") and not ln.endswith(": none running")]
    if not parts:
        parts = step_lines[:]
    result["summary"] = " · ".join(parts) if parts else "No heavy relief targets found — tap Restart Cursor for hot agent chat"
    try:
        from mac_health_prevention_v1 import analyze_prevention  # noqa: WPS433

        prev = analyze_prevention(after)
        cursor = prev.get("cursor") or {}
        if "cursor_hot" in (prev.get("modes") or []):
            result["summary"] += (
                f" · Factory clear ✓ — Cursor still {cursor.get('cpu_sum', '?')}% CPU → Restart Cursor"
            )
            result["cursor_still_hot"] = True
            result["prevention"] = prev
    except Exception:
        pass
    result["founder_line"] = (
        f"CPU {before.get('cpu_pct')}% → {after.get('cpu_pct')}% · load {before.get('load_1min')} → {after.get('load_1min')}"
    )
    return result
