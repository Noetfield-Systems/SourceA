#!/usr/bin/env python3
"""Mac Health — PANIC emergency stop (keyboard / API / unattended).

Instant: factory freeze + agent kill switch.
Then: hub stop · pipeline · ghosts · scripts · Chrome · n8n · inbox clear.

Designed for laggy desktop — no hub UI required. Global hotkey: Control+Option+Command+S.
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
SOURCE_A = Path(__file__).resolve().parents[1]
FREEZE_FLAG = SINA / "auto-run-disabled-v1.flag"
PANIC_FLAG = SINA / "mac-health-emergency-active-v1.flag"
RECEIPT_PATH = SINA / "mac-health" / "emergency-stop-latest-v1.json"
STREAK_PATH = SINA / "mac-health" / "unattended-pulse-streak-v1.json"
CPU_WARN_STATE_PATH = SINA / "mac-health" / "cpu-warn-state-v1.json"
CONFIG_PATH = SINA / "config" / "mac-health-panic-v1.json"
LANDING_TUNNEL_PID = SINA / "sourcea-landing-tunnel-v1.pid"
LANDING_TUNNEL_PORT = 8190
FULL_STOP_TRIGGERS: frozenset[str] = frozenset({"full_stop", "cli-full", "desktop-full"})

# LaunchAgents that respawn killed agents — must pause on panic or STOP has zero effect.
PAUSE_LAUNCH_AGENTS: tuple[str, ...] = (
    "com.sourcea.autorun-worker",
    "com.sourcea.hub",
    "com.sourcea.g7-governance-self-heal",
)

# Per launchd label — pgrep patterns for running instances (bootout alone is not enough).
LAUNCH_AGENT_KILL_PATTERNS: dict[str, tuple[str, ...]] = {
    "com.sourcea.autorun-worker": (
        "autorun_dispatcher_v1",
        "auto_run_worker_batch",
        "fbe_motor_delegate_v1",
        "goal1_worker_batch_loop",
        "anti_staleness_auto_wire_v1",
        "queue_ssot_unify_v1",
        "agent_rules_loop_orchestrator",
    ),
    "com.sourcea.hub": ("sina-command-server", "worker_hub_v1"),
    "com.sourcea.g7-governance-self-heal": (
        "governance_self_heal_daemon",
        "g7_governance",
        "g7-governance",
    ),
}

KILL_PORTS: tuple[int, ...] = (13020, 13030)

# Factory / agent patterns — never Mac Health heart or panic hotkey daemon.
KILL_PATTERNS: tuple[str, ...] = (
    "fbe_motor_delegate_v1",
    "agent_rules_loop_orchestrator",
    "anti_staleness_auto_wire_v1",
    "autorun_dispatcher_v1",
    "auto_run_worker_batch",
    "goal1_worker_batch_loop",
    "healthy_prompt_turn_v1",
    "healthy-drain-orchestrator",
    "brain_run_loop",
    "brain_watch_loop",
    "brain_fast_startup",
    "brain_governance_wire",
    "goal1_lane_broker",
    "build_phase_strict_queue_v1",
    "align_command_data_ui_v1",
    "governance_meta_audit_v1",
    "governance_self_heal_daemon",
    "hub_rebuild_worker",
    "hub_self_refresh",
    "g7_governance",
    "g7-governance",
    "queue_ssot_unify_v1",
    "agentic_layer_pipeline",
    "critic_boot_v1",
    "agent_session_gate_run",
    "cursor_entry_gate",
    "auto_prompt_guard",
    "build-sina-command-panel",
    "sina-command-server",
    "sina-command-api",
    "dashboard_server",
    "worker_hub_v1",
    "factory_control_v1",
    "remote_ops.service",
    "m8_ui.py",
    "m8-dispatch",
    "n8n_glue",
    "n8n start",
    "@n8n/task-runner",
    "/n8n/bin/n8n",
    "cloudflared",
    "publish_sourcea_landing",
    "run-recipe.sh",
    "wrangler deploy",
    "kill-sina-command",
)

PROTECTED_SNIPPETS = (
    "mac-health-guard-server",
    "MacHealthPanicHotkey",
    "Mac Health Panic",
    "MacHealthShell",
    "mac_health_emergency_stop",
    "mac_health_panic_listener",
    "mac_health_live",
    "chat-unify-server",
    "n8n-integration-server",
    "apple-health-server",
    "agent_session_gate_run",
    "agent_memory_mirror_v1",
    # Mac control panel — never orphan-kill (INCIDENT-042)
    "sina-command-server",
    "worker_hub_v1",
    "cloud-workers-server",
    "cloud_workers_hub_v1",
    "mac_cloud_deploy_dispatch",
    "mac_control_dispatch",
    "mac-law-server",
    "routing-panel/server",
    "mac_launchd_tcc_guard",
    "mac_pipeline_validator_pressure",
    "test_mac_control_dispatch_policy",
    "sourcea-python-v1",
)

# Unattended false-positive panics must not kill founder Worker Hub (INCIDENT-035).
HUB_KEEP_ALIVE_SNIPPETS = (
    "sina-command-server",
    "worker_hub_v1",
    "serve-sina-command",
)

HEAL_KEEP_ALIVE_SNIPPETS = (
    "hub_dual_heal_v1",
    "worker_hub_heal_v1",
    "anti_staleness_auto_wire",
    "agent_session_gate_run",
    "agent_maze_pipeline",
    "governance_zero_drift",
    "sourcea_crawl_mirror",
    "validate-",
)


def _protect_landing_tunnel(trigger: str) -> bool:
    """Routine UI stop keeps SourceA landing tunnel alive (UPGR-051)."""
    return trigger not in FULL_STOP_TRIGGERS and not str(trigger).startswith("full")


def _landing_tunnel_pids() -> set[int]:
    pids: set[int] = set()
    if LANDING_TUNNEL_PID.is_file():
        try:
            pids.add(int(LANDING_TUNNEL_PID.read_text(encoding="utf-8").strip()))
        except (OSError, ValueError):
            pass
    try:
        proc = subprocess.run(
            ["lsof", "-ti", f"TCP:{LANDING_TUNNEL_PORT}"],
            capture_output=True,
            text=True,
            timeout=3.0,
        )
        for pid_s in (proc.stdout or "").strip().split():
            if pid_s.isdigit():
                pids.add(int(pid_s))
    except (OSError, subprocess.TimeoutExpired):
        pass
    return pids


def _is_landing_tunnel_row(row: dict[str, Any]) -> bool:
    cmd = row.get("cmdline") or ""
    pid = int(row.get("pid") or 0)
    if pid and pid in _landing_tunnel_pids():
        return True
    if "cloudflared" in cmd and (
        f":{LANDING_TUNNEL_PORT}" in cmd or f"127.0.0.1:{LANDING_TUNNEL_PORT}" in cmd
    ):
        return True
    if "publish_sourcea_landing" in cmd:
        return True
    if "http.server" in cmd and str(LANDING_TUNNEL_PORT) in cmd:
        return True
    return False


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_config() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "hotkey": {"enabled": True, "label": "⌃⌥⌘S"},
        "unattended": {
            "auto_panic_on_runaway": True,
            "auto_restart_cursor_unattended": False,
            "consecutive_unhealthy_pulses": 24,
            "cursor_cpu_panic": 280,
            "queue_zombies_panic": 12,
            "warn_streaks": [6, 12, 18, 22],
            "warn_modal_streaks": [18, 22],
            "warn_min_sec": 120,
            "cursor_restart_peak": 450,
            "cursor_restart_sum": 550,
            "panic_cooldown_sec": 900,
        },
        "cpu_warn": {
            "enabled": True,
            "system_cpu_pct": [50, 62, 74, 86],
            "cursor_cpu_sum_pct": [150, 190, 230, 270],
            "cooldown_sec": 300,
            "global_cooldown_sec": 180,
        },
    }
    if CONFIG_PATH.is_file():
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for k, v in raw.items():
                if isinstance(v, dict) and k in defaults:
                    defaults[k].update(v)
                else:
                    defaults[k] = v
        except (OSError, json.JSONDecodeError):
            pass
    return defaults


def _is_protected_cmd(cmdline: str, *, trigger: str = "api") -> bool:
    if any(p in cmdline for p in PROTECTED_SNIPPETS):
        return True
    if trigger == "unattended" and any(p in cmdline for p in HUB_KEEP_ALIVE_SNIPPETS + HEAL_KEEP_ALIVE_SNIPPETS):
        return True
    if _protect_landing_tunnel(trigger):
        if "publish_sourcea_landing" in cmdline:
            return True
        if "cloudflared" in cmdline and (
            f":{LANDING_TUNNEL_PORT}" in cmdline or f"127.0.0.1:{LANDING_TUNNEL_PORT}" in cmdline
        ):
            return True
    return False


def _pgrep_full(pattern: str, *, trigger: str = "api") -> list[dict[str, Any]]:
    """Enumerate PIDs matching -f pattern (skips protected Mac Health heart)."""
    if any(p in pattern for p in PROTECTED_SNIPPETS):
        return []
    try:
        proc = subprocess.run(
            ["pgrep", "-fl", pattern],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
        if proc.returncode != 0:
            return []
        rows: list[dict[str, Any]] = []
        for line in (proc.stdout or "").splitlines():
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            pid_s, cmd = parts[0], parts[1]
            if _is_protected_cmd(cmd, trigger=trigger):
                continue
            try:
                rows.append({"pid": int(pid_s), "cmdline": cmd[:220], "pattern": pattern})
            except ValueError:
                continue
        return rows
    except (OSError, subprocess.TimeoutExpired):
        return []


def _enumerate_agent_pids(*, trigger: str = "api") -> list[dict[str, Any]]:
    """All factory/agent PIDs before kill — deduped by pid."""
    seen: set[int] = set()
    rows: list[dict[str, Any]] = []
    protect_landing = _protect_landing_tunnel(trigger)
    for pat in KILL_PATTERNS:
        if protect_landing and pat == "cloudflared":
            continue
        for row in _pgrep_full(pat, trigger=trigger):
            pid = int(row["pid"])
            if protect_landing and _is_landing_tunnel_row(row):
                continue
            if pid in seen:
                continue
            seen.add(pid)
            rows.append(row)
    for label, pats in LAUNCH_AGENT_KILL_PATTERNS.items():
        for pat in pats:
            for row in _pgrep_full(pat, trigger=trigger):
                pid = int(row["pid"])
                if pid in seen:
                    continue
                seen.add(pid)
                row["launch_agent"] = label
                rows.append(row)
    return rows


def _kill_pid(pid: int, sig: int, *, dry_run: bool = False) -> bool:
    if dry_run:
        return True
    try:
        os.kill(pid, sig)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _top_heavy_processes(limit: int = 8) -> list[dict[str, Any]]:
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid,pcpu,rss,comm"],
            capture_output=True,
            text=True,
            timeout=8.0,
        )
        if proc.returncode != 0:
            return []
        rows: list[dict[str, Any]] = []
        for line in (proc.stdout or "").splitlines()[1:]:
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            try:
                rows.append(
                    {
                        "pid": int(parts[0]),
                        "cpu_pct": float(parts[1]),
                        "rss_mb": round(int(parts[2]) / 1024, 1),
                        "comm": parts[3].strip()[:120],
                    }
                )
            except ValueError:
                continue
        rows.sort(key=lambda r: (r["cpu_pct"], r["rss_mb"]), reverse=True)
        return rows[:limit]
    except (OSError, subprocess.TimeoutExpired):
        return []


def _system_ram_used_gb() -> float:
    try:
        proc = subprocess.run(
            ["vm_stat"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        page_size = 16384
        m = re.search(r"page size of (\d+)", proc.stdout or "")
        if m:
            page_size = int(m.group(1))
        used_pages = 0
        for key in ("active", "wired", "compressed"):
            m2 = re.search(rf"{key}:\s+(\d+)", proc.stdout or "")
            if m2:
                used_pages += int(m2.group(1))
        return round(used_pages * page_size / (1024**3), 2)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return 0.0


def _pause_launch_agents(*, dry_run: bool = False) -> tuple[list[str], list[dict[str, Any]]]:
    """Stop launchd from respawning hub + autorun, then kill any running instances."""
    uid = os.getuid()
    domain = f"gui/{uid}"
    lines: list[str] = []
    kills: list[dict[str, Any]] = []
    for label in PAUSE_LAUNCH_AGENTS:
        try:
            proc = subprocess.run(
                ["launchctl", "bootout", f"{domain}/{label}"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )
            if dry_run:
                lines.append(f"DRY bootout launchd {label}")
            elif proc.returncode == 0:
                lines.append(f"PAUSED launchd {label}")
            elif "No such process" in (proc.stderr or "") or proc.returncode == 3:
                lines.append(f"launchd {label} already off")
            else:
                lines.append(f"launchd {label} warn rc={proc.returncode}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            lines.append(f"launchd {label} err: {exc}")

    seen: set[int] = set()
    for label, pats in LAUNCH_AGENT_KILL_PATTERNS.items():
        for pat in pats:
            for row in _pgrep_full(pat):
                pid = int(row["pid"])
                if pid in seen:
                    continue
                seen.add(pid)
                row["launch_agent"] = label
                if dry_run:
                    kills.append({**row, "signal": "DRY", "status": "would_kill"})
                    lines.append(f"DRY would kill pid {pid} ({pat})")
                elif _kill_pid(pid, signal.SIGTERM, dry_run=False):
                    kills.append({**row, "signal": "TERM", "status": "sent"})
                    lines.append(f"TERM pid {pid} ({pat})")
    return lines, kills


def _cursor_hot_now() -> dict[str, Any]:
    try:
        from mac_health_prevention_v1 import _cursor_pressure  # noqa: WPS433

        return _cursor_pressure()
    except Exception:
        return {}


def _should_restart_cursor(cursor: dict[str, Any], *, trigger: str = "") -> bool:
    """Never restart Cursor unless true emergency — founder must keep working in Cursor."""
    cfg = _load_config().get("unattended") or {}
    if trigger == "unattended" and not cfg.get("auto_restart_cursor_unattended", False):
        return False
    peak = float(cursor.get("renderer_peak") or cursor.get("peak_cpu") or 0)
    cpu_sum = float(cursor.get("cpu_sum") or 0)
    peak_need = float(cfg.get("cursor_restart_peak") or 450)
    sum_need = float(cfg.get("cursor_restart_sum") or 550)
    # Desktop app: only restart on extreme freeze — otherwise agents-only stop.
    if trigger in ("desktop-app", "desktop-stop"):
        return peak >= max(peak_need, 480) or cpu_sum >= max(sum_need, 580)
    if trigger in ("ui", "api-get", "hotkey", "menubar") or str(trigger).startswith("hotkey"):
        return False
    return peak >= peak_need or cpu_sum >= sum_need


def _kill_port(port: int, *, dry_run: bool = False) -> list[dict[str, Any]]:
    kills: list[dict[str, Any]] = []
    try:
        out = subprocess.run(
            ["lsof", "-ti", f"TCP:{port}"],
            capture_output=True,
            text=True,
            timeout=3.0,
        ).stdout.strip()
        if not out:
            return kills
        for pid_s in out.split():
            try:
                pid = int(pid_s)
            except ValueError:
                continue
            row = {"pid": pid, "pattern": f"port:{port}", "cmdline": f"listener TCP:{port}"}
            if dry_run:
                kills.append({**row, "signal": "DRY", "status": "would_kill"})
            else:
                subprocess.run(["kill", "-9", str(pid)], timeout=2.0)
                kills.append({**row, "signal": "KILL", "status": "killed"})
    except (OSError, subprocess.TimeoutExpired):
        pass
    return kills


def _kill_agent_swarm(*, fast: bool = False, dry_run: bool = False, trigger: str = "api") -> list[dict[str, Any]]:
    """Enumerate matching PIDs, TERM then KILL survivors — honest per-PID receipt."""
    kills: list[dict[str, Any]] = []
    wait = 0.12 if fast else 0.35
    targets = _enumerate_agent_pids(trigger=trigger)

    for row in targets:
        pid = int(row["pid"])
        if dry_run:
            kills.append({**row, "signal": "DRY", "status": "would_kill"})
            continue
        if _kill_pid(pid, signal.SIGTERM, dry_run=False):
            kills.append({**row, "signal": "TERM", "status": "sent"})

    if not dry_run:
        time.sleep(wait)
        for row in _enumerate_agent_pids(trigger=trigger):
            pid = int(row["pid"])
            if _kill_pid(pid, signal.SIGKILL, dry_run=False):
                kills.append({**row, "signal": "KILL", "status": "killed"})

    for port in KILL_PORTS:
        if trigger == "unattended" and port == 13020:
            continue
        kills.extend(_kill_port(port, dry_run=dry_run))

    return kills


def _notify(title: str, body: str, *, modal: bool = False, sound: str = "Basso") -> None:
    try:
        from mac_health_settings_v1 import notifications_enabled  # noqa: WPS433

        if not notifications_enabled():
            return
    except Exception:
        return


def _write_flags(trigger: str) -> dict[str, Any]:
    SINA.mkdir(parents=True, exist_ok=True)
    line = f"mac-health-emergency-stop-v1 · {_now()} · trigger={trigger}\n"
    FREEZE_FLAG.write_text(line, encoding="utf-8")
    PANIC_FLAG.write_text(line, encoding="utf-8")
    return {"factory_freeze": True, "panic_flag": True}


def _kill_sourcea_orphan_scripts(*, dry_run: bool = False, trigger: str = "api") -> list[dict[str, Any]]:
    """Kill stray SourceA python/shell workers — never Mac Health heart."""
    sourcea_scripts = str(SOURCE_A / "scripts")
    kills: list[dict[str, Any]] = []
    try:
        proc = subprocess.run(
            ["ps", "-axo", "pid,command"],
            capture_output=True,
            text=True,
            timeout=8.0,
        )
        if proc.returncode != 0:
            return kills
        for line in (proc.stdout or "").splitlines()[1:]:
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            pid_s, cmd = parts[0], parts[1]
            if sourcea_scripts not in cmd and "/SourceA/scripts/" not in cmd:
                continue
            if _is_protected_cmd(cmd, trigger=trigger):
                continue
            if _protect_landing_tunnel(trigger) and _is_landing_tunnel_row(
                {"pid": int(pid_s), "cmdline": cmd}
            ):
                continue
            if "python" not in cmd.lower() and "zsh" not in cmd.lower() and "bash" not in cmd.lower():
                continue
            try:
                pid = int(pid_s)
            except ValueError:
                continue
            row = {"pid": pid, "cmdline": cmd[:220], "pattern": "sourcea_orphan"}
            if dry_run:
                kills.append({**row, "signal": "DRY", "status": "would_kill"})
            elif _kill_pid(pid, signal.SIGTERM, dry_run=False):
                kills.append({**row, "signal": "TERM", "status": "sent"})
        if not dry_run and kills:
            time.sleep(0.25)
            for row in list(kills):
                pid = int(row["pid"])
                if _pid_alive(pid) and _kill_pid(pid, signal.SIGKILL, dry_run=False):
                    kills.append({**row, "signal": "KILL", "status": "killed"})
    except (OSError, subprocess.TimeoutExpired):
        pass
    return kills


def _revoke_active_plans(*, dry_run: bool = False) -> list[str]:
    lines: list[str] = []
    if dry_run:
        return ["DRY plan revoke"]
    try:
        from plan_revoked_v1 import write_revoked  # noqa: WPS433

        write_revoked("mac_health_panic", reason="emergency_stop")
        lines.append("plan REVOKED — in-flight todos cancelled")
    except Exception as exc:
        lines.append(f"plan revoke warn: {exc}")
    cancel_flag = SINA / "agent-cancel-v1.flag"
    try:
        cancel_flag.write_text(f"mac-health-emergency-stop · {_now()}\n", encoding="utf-8")
        lines.append("agent-cancel flag ON")
    except OSError as exc:
        lines.append(f"cancel flag warn: {exc}")
    return lines


def _guard_belt() -> list[str]:
    lines: list[str] = []
    scripts = str(SOURCE_A / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    try:
        from auto_prompt_guard import disable_auto_feed_everywhere, ensure_kill_on  # noqa: WPS433
        from intelligence_circle import disable_live_agent_automation  # noqa: WPS433

        ensure_kill_on()
        disable_auto_feed_everywhere()
        disable_live_agent_automation()
        lines.append("auto-paste OFF · live automation OFF")
    except Exception as exc:
        lines.append(f"guard warn: {exc}")
    inbox = SINA / "worker-prompt-inbox-v1.json"
    lock = SINA / "goal1-worker-batch-lock-v1.json"
    for path in (inbox, lock):
        if path.is_file():
            try:
                path.unlink()
                lines.append(f"cleared {path.name}")
            except OSError:
                lines.append(f"warn: could not clear {path.name}")
    return lines


def _mac_health_relief(*, fast: bool) -> dict[str, Any]:
    try:
        from mac_health_cpu_relief_v1 import run_wake_cool_down  # noqa: WPS433

        return run_wake_cool_down()
    except Exception as exc:
        return {"ok": False, "detail": str(exc), "fast": fast}


def _kill_summary_lines(kills: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in kills[:20]:
        pid = row.get("pid", "?")
        pat = row.get("pattern", "?")
        sig = row.get("signal", "?")
        status = row.get("status", "")
        short_cmd = (row.get("cmdline") or "")[:60]
        lines.append(f"{sig} pid {pid} ({pat}) {short_cmd}".strip())
    if len(kills) > 20:
        lines.append(f"+{len(kills) - 20} more kills")
    return lines


def _unique_kill_count(kills: list[dict[str, Any]]) -> int:
    return len({int(k["pid"]) for k in kills if k.get("pid") is not None})


def run_mac_health_emergency_stop(
    *,
    trigger: str = "api",
    fast: bool = True,
    notify: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Full panic stop — returns receipt. Safe to call from hotkey daemon."""
    t0 = time.monotonic()
    steps: list[str] = []

    targets_before = _enumerate_agent_pids(trigger=trigger)
    system_ram_before = _system_ram_used_gb()
    cursor_before = _cursor_hot_now()
    cpu_before = float(cursor_before.get("cpu_sum") or 0)
    peak_before = float(cursor_before.get("renderer_peak") or cursor_before.get("peak_cpu") or 0)
    ram_before = float(cursor_before.get("rss_mb") or 0) / 1024

    flags: dict[str, Any] = {}
    if dry_run:
        steps.append("DRY RUN — no flags written · no signals sent")
    else:
        flags = _write_flags(trigger)
        steps.append("factory FREEZE · auto-run disabled")

    modal = trigger in ("ui", "cli", "desktop-stop", "panic-file", "api-get") or trigger.startswith(
        ("hotkey", "menubar")
    )
    if notify and not dry_run:
        _notify("⛔ Mac Health PANIC", "Factory frozen — killing agents…", modal=False)

    launch_lines, launch_kills = _pause_launch_agents(dry_run=dry_run)
    steps.extend(launch_lines)

    swarm_kills = _kill_agent_swarm(fast=fast, dry_run=dry_run, trigger=trigger)
    orphan_kills = _kill_sourcea_orphan_scripts(dry_run=dry_run, trigger=trigger)
    kills = launch_kills + swarm_kills + orphan_kills
    steps.extend(_kill_summary_lines(kills))

    if not dry_run:
        steps.extend(_guard_belt())
        steps.extend(_revoke_active_plans(dry_run=False))

    relief: dict[str, Any] = {}
    # UI / desktop stops must run cool-down NOW — not background queue — or founder sees zero effect.
    sync_cool_triggers = (
        "ui",
        "cli",
        "api-get",
        "desktop-stop",
        "desktop-app",
        "panic-file",
    )
    if not dry_run and (not fast or trigger in sync_cool_triggers or trigger.startswith("hotkey")):
        cool = _mac_health_relief(fast=False)
        relief["wake_cool_down"] = cool
        if cool.get("step_lines"):
            steps.extend(cool["step_lines"][:8])
        elif cool.get("summary"):
            steps.append(str(cool.get("summary"))[:200])
    elif not fast and not dry_run:
        try:
            from emergency_stop import run_emergency_stop  # noqa: WPS433

            relief["hub"] = run_emergency_stop(from_hub=False)
            steps.append("hub emergency_stop")
        except Exception as exc:
            steps.append(f"hub warn: {exc}")
        cool = _mac_health_relief(fast=False)
        relief["wake_cool_down"] = cool
        if cool.get("summary"):
            steps.append(str(cool.get("summary"))[:200])

    cursor_restart: dict[str, Any] = {}
    if not dry_run and _should_restart_cursor(cursor_before, trigger=trigger):
        try:
            from mac_health_cpu_relief_v1 import restart_cursor  # noqa: WPS433

            cursor_restart = restart_cursor()
            relief["cursor_restart"] = cursor_restart
            if cursor_restart.get("ok"):
                steps.append("Cursor: quit · killed hogs · reopening")
            else:
                steps.append(f"Cursor restart: {cursor_restart.get('detail', 'failed')[:120]}")
        except Exception as exc:
            steps.append(f"Cursor restart err: {exc}")

    cursor_after = _cursor_hot_now() if not dry_run else cursor_before
    cpu_after = float(cursor_after.get("cpu_sum") or 0)
    peak_after = float(cursor_after.get("renderer_peak") or cursor_after.get("peak_cpu") or 0)
    ram_after = float(cursor_after.get("rss_mb") or 0) / 1024
    system_ram_after = _system_ram_used_gb() if not dry_run else system_ram_before
    still_running = _top_heavy_processes(8)
    kill_count = _unique_kill_count(kills)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    if dry_run:
        summary = (
            f"DRY RUN ({trigger}) · would kill {len(targets_before)} agent PID(s) · "
            f"{elapsed_ms}ms"
        )
    elif kill_count:
        summary = f"PANIC STOP ({trigger}) · {kill_count} agent kill(s) · {elapsed_ms}ms"
    else:
        summary = (
            f"PANIC STOP ({trigger}) · factory frozen · 0 agents matched · "
            f"Cursor {ram_before:.1f} GB · {elapsed_ms}ms"
        )

    if cursor_restart.get("ok"):
        summary += f" · Cursor restarted · CPU {cpu_before:.0f}%→{cpu_after:.0f}% · RAM {ram_before:.1f}→{ram_after:.1f} GB"
    elif _should_restart_cursor(cursor_before, trigger=trigger) and not dry_run:
        summary += " · Cursor restart failed — try again"

    proof_lines: list[str] = []
    if dry_run:
        if targets_before:
            names = ", ".join(
                f"{t['pid']}:{(t.get('cmdline') or t.get('pattern', '?'))[:28]}"
                for t in targets_before[:5]
            )
            proof_lines.append(f"Would kill: {len(targets_before)} ({names})")
        else:
            proof_lines.append("Would kill: 0 — no factory agents matched right now")
    elif kill_count:
        names = ", ".join(
            f"{k['pid']}:{k.get('pattern', '?')}" for k in kills[:6]
        )
        proof_lines.append(f"Agents killed: {kill_count} ({names})")
    else:
        proof_lines.append("Agents killed: 0 — no factory scripts matched (launchd already off)")
        if still_running:
            top = "; ".join(
                f"{r['comm'][:28]} {r['cpu_pct']:.0f}%/{r['rss_mb']:.0f}MB"
                for r in still_running[:3]
            )
            proof_lines.append(f"Still heavy: {top}")
        if ram_before >= 4.0:
            proof_lines.append(
                f"Cursor RAM {ram_before:.1f} GB unchanged — use Restart Cursor for IDE relief"
            )

    proof_lines.append("Paused: factory freeze + launchd hub/autorun/g7 ✓")
    if _protect_landing_tunnel(trigger):
        proof_lines.append("Landing tunnel kept alive — use full_stop to kill cloudflared")
    proof_lines.append("NOT stopped: Cursor · Terminal · Claude (your work — tap Restart Cursor for IDE relief)")
    if relief.get("wake_cool_down", {}).get("step_lines"):
        cool_bits = [ln for ln in relief["wake_cool_down"]["step_lines"] if ": none" not in ln and ": clear" not in ln]
        if cool_bits:
            proof_lines.append("Cool down: " + " · ".join(cool_bits[:4]))
    proof_lines.append(
        f"Cursor CPU: {cpu_before:.0f}% → {cpu_after:.0f}% · RAM: {ram_before:.1f} → {ram_after:.1f} GB"
    )
    proof_lines.append(
        f"System RAM: {system_ram_before:.1f} → {system_ram_after:.1f} GB"
    )
    if cursor_restart.get("ok"):
        proof_lines.append("Cursor: quit and reopened ✓")
    elif _should_restart_cursor(cursor_before, trigger=trigger) and not dry_run:
        proof_lines.append("Cursor restart: FAILED — " + str(cursor_restart.get("detail", "?"))[:80])

    receipt = {
        "ok": True,
        "schema": "mac-health-emergency-stop-v1",
        "at": _now(),
        "trigger": trigger,
        "fast": fast,
        "dry_run": dry_run,
        "elapsed_ms": elapsed_ms,
        "flags": flags,
        "kills": kills,
        "killed_pids": kills,
        "kill_count": kill_count,
        "targets_before": targets_before,
        "still_running": still_running,
        "steps": steps,
        "summary": summary,
        "proof_lines": proof_lines,
        "founder_line": " · ".join(proof_lines),
        "hotkey": _load_config().get("hotkey", {}).get("label", "⌃⌥⌘S"),
        "relief": relief,
        "cursor_before": cursor_before,
        "cursor_after": cursor_after,
        "system_ram_before_gb": system_ram_before,
        "system_ram_after_gb": system_ram_after,
        "launch_agents_paused": True,
    }
    if not dry_run:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if notify and not dry_run:
        cool_lines = (relief.get("wake_cool_down") or {}).get("step_lines") or []
        cool_done = [ln for ln in cool_lines if ": none" not in ln and ": clear" not in ln and ": was off" not in ln]
        if kill_count:
            done = f"Killed {kill_count} background process(es)"
            if cool_done:
                done += " · " + " · ".join(cool_done[:3])
            done += f" · {elapsed_ms}ms"
            title = "⛔ Background stopped"
        else:
            done = (
                "No factory agents were running. "
                + (" · ".join(cool_done[:3]) if cool_done else "Factory frozen only")
                + f" · Cursor {ram_before:.1f} GB still open"
            )
            title = "⛔ Paused — Cursor still open"
        _notify(title, done, modal=modal)

    return receipt


def _warn_before_panic(
    *,
    streak: int,
    threshold: int,
    cursor: float,
    zombies: int,
    cfg: dict[str, Any],
    last_warn_streak: int,
    last_warn_at: float = 0.0,
) -> tuple[int, float]:
    """Notify founder at configured streak steps before auto-panic — throttled."""
    warn_streaks = cfg.get("warn_streaks") or [6, 12, 18, 22]
    modal_streaks = cfg.get("warn_modal_streaks") or [18, 22]
    min_gap = float(cfg.get("warn_min_sec") or 120)
    try:
        warn_streaks = [int(x) for x in warn_streaks]
    except (TypeError, ValueError):
        warn_streaks = [6, 12, 18, 22]
    try:
        modal_streaks = [int(x) for x in modal_streaks]
    except (TypeError, ValueError):
        modal_streaks = [18, 22]
    now = time.time()
    if now - last_warn_at < min_gap:
        return last_warn_streak, last_warn_at
    pulse_sec = 8
    if streak >= 1 and streak < threshold and streak > last_warn_streak:
        should_warn = streak in warn_streaks or streak in modal_streaks
        if not should_warn:
            return last_warn_streak, last_warn_at
        remaining_pulses = threshold - streak
        eta_sec = remaining_pulses * pulse_sec
        zombie_note = f" · {zombies} queue zombies" if zombies else ""
        cursor_stays = "Cursor stays open — only background agents stop."
        if streak in modal_streaks:
            _notify(
                "⚠️ Mac Health — heads up",
                (
                    f"Cursor {cursor:.0f}% CPU{zombie_note} · "
                    f"background auto-stop in ~{eta_sec}s if load continues. "
                    f"{cursor_stays} Tap Cool Down to clear pressure now."
                ),
                modal=True,
                sound="Glass",
            )
        elif streak >= threshold - 4:
            _notify(
                "⚠️ Mac Health — almost auto-stop",
                (
                    f"Cursor {cursor:.0f}% CPU · ~{eta_sec}s left · "
                    f"{cursor_stays} Mac Health Guard → Cool Down"
                ),
                modal=False,
                sound="Ping",
            )
        else:
            _notify(
                "⚠️ Mac Health — load rising",
                (
                    f"Cursor {cursor:.0f}% CPU{zombie_note} · "
                    f"watching · {cursor_stays} Cool Down anytime."
                ),
                modal=False,
                sound="Purr",
            )
        return streak, now
    return last_warn_streak, last_warn_at


def maybe_cpu_pressure_warn(mp: dict[str, Any] | None, prevention: dict[str, Any] | None = None) -> None:
    """Notify at system + Cursor CPU tiers — silent unless notifications.sounds_enabled."""
    if not mp:
        return
    raw = _load_config()
    cfg = raw.get("cpu_warn") or {}
    if not cfg.get("enabled", False):
        return
        return
    cooldown = float(cfg.get("cooldown_sec") or 300)
    global_cooldown = float(cfg.get("global_cooldown_sec") or 180)
    system_tiers = sorted(int(x) for x in (cfg.get("system_cpu_pct") or [50, 62, 74, 86]))
    cursor_tiers = sorted(int(x) for x in (cfg.get("cursor_cpu_sum_pct") or [150, 190, 230, 270]))

    cpu_pct = float(mp.get("cpu_pct") or 0)
    cores = max(int(mp.get("cpu_cores") or 1), 1)
    load_per_core = float(mp.get("load_1min") or 0) / cores
    cursor = (prevention or {}).get("cursor") or {}
    cursor_sum = float(cursor.get("cpu_sum") or 0)

    state: dict[str, Any] = {"at": _now(), "last": {}, "last_sys_notified": 0, "last_cur_notified": 0}
    if CPU_WARN_STATE_PATH.is_file():
        try:
            state = json.loads(CPU_WARN_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    last = state.get("last") or {}
    now = time.time()
    global_last = float(state.get("global_notify_at") or 0)
    if now - global_last < global_cooldown:
        return
    last_sys_notified = int(state.get("last_sys_notified") or 0)
    last_cur_notified = int(state.get("last_cur_notified") or 0)

    def _tier_key(kind: str, tier: int) -> str:
        return f"{kind}:{tier}"

    def _should_fire(key: str) -> bool:
        prev = last.get(key)
        if prev is None:
            return True
        try:
            return (now - float(prev)) >= cooldown
        except (TypeError, ValueError):
            return True

    fired: list[str] = []
    sys_hit = max((t for t in system_tiers if cpu_pct >= t), default=None)
    cur_hit = max((t for t in cursor_tiers if cursor_sum >= t), default=None)

    if sys_hit is not None and sys_hit > last_sys_notified:
        key = _tier_key("sys", sys_hit)
        if _should_fire(key):
            sound = "Glass" if sys_hit >= 86 else "Ping" if sys_hit >= 74 else "Purr"
            _notify(
                "⚠️ Mac Health — CPU load",
                (
                    f"Body CPU {cpu_pct:.0f}% (tier ≥{sys_hit}%) · load {load_per_core:.1f}/core · "
                    "Cursor stays open · Cool Down clears background only."
                ),
                modal=sys_hit >= 86,
                sound=sound,
            )
            last[key] = now
            last_sys_notified = sys_hit
            global_last = now
            fired.append(key)

    panic_cursor = float((raw.get("unattended") or {}).get("cursor_cpu_panic") or 280)
    if cur_hit is not None and cur_hit < panic_cursor and cur_hit > last_cur_notified:
        key = _tier_key("cursor", cur_hit)
        if _should_fire(key):
            sound = "Ping" if cur_hit >= 230 else "Purr"
            _notify(
                "⚠️ Mac Health — Cursor CPU",
                (
                    f"Cursor {cursor_sum:.0f}% CPU (tier ≥{cur_hit}%) · normal while you work · "
                    "auto-stop only at higher sustained load · Cool Down anytime."
                ),
                modal=cur_hit >= 270,
                sound=sound,
            )
            last[key] = now
            last_cur_notified = cur_hit
            global_last = now
            fired.append(key)

    if fired:
        state["last"] = last
        state["last_sys_notified"] = last_sys_notified
        state["last_cur_notified"] = last_cur_notified
        state["global_notify_at"] = global_last
        state["at"] = _now()
        CPU_WARN_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CPU_WARN_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def build_cpu_warn_state(
    mp: dict[str, Any] | None,
    prevention: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Read-only CPU alarm ladder for UI — no notifications."""
    if not mp:
        return {"schema": "mac-health-cpu-warn-state-v1", "status": "unknown"}
    raw = _load_config()
    cfg = raw.get("cpu_warn") or {}
    system_tiers = sorted(int(x) for x in (cfg.get("system_cpu_pct") or [50, 62, 74, 86]))
    cursor_tiers = sorted(int(x) for x in (cfg.get("cursor_cpu_sum_pct") or [150, 190, 230, 270]))
    cpu_pct = float(mp.get("cpu_pct") or 0)
    cores = max(int(mp.get("cpu_cores") or mp.get("cores") or 1), 1)
    load_per_core = float(mp.get("load_1min") or 0) / cores
    cursor = (prevention or {}).get("cursor") or {}
    cursor_sum = float(cursor.get("cpu_sum") or 0)
    sys_hit = max((t for t in system_tiers if cpu_pct >= t), default=None)
    cur_hit = max((t for t in cursor_tiers if cursor_sum >= t), default=None)
    sys_level = system_tiers.index(sys_hit) + 1 if sys_hit is not None else 0
    cur_level = cursor_tiers.index(cur_hit) + 1 if cur_hit is not None else 0
    max_level = max(sys_level, cur_level)
    if max_level == 0:
        status = "calm"
    elif max_level <= 2:
        status = "watch"
    elif max_level <= 3:
        status = "elevated"
    else:
        status = "hot"
    next_sys = next((t for t in system_tiers if cpu_pct < t), None)
    next_cur = next((t for t in cursor_tiers if cursor_sum < t), None)
    return {
        "schema": "mac-health-cpu-warn-state-v1",
        "status": status,
        "body_cpu_pct": round(cpu_pct, 1),
        "cursor_cpu_sum_pct": round(cursor_sum, 1),
        "load_per_core": round(load_per_core, 2),
        "system_tier_hit": sys_hit,
        "cursor_tier_hit": cur_hit,
        "system_tier_level": sys_level,
        "cursor_tier_level": cur_level,
        "system_tiers": system_tiers,
        "cursor_tiers": cursor_tiers,
        "next_system_tier_pct": next_sys,
        "next_cursor_tier_pct": next_cur,
        "founder_line": (
            f"All clear — body {cpu_pct:.0f}% · Cursor {cursor_sum:.0f}% · guard idle"
            if max_level == 0
            else (
                f"Body {cpu_pct:.0f}% · Cursor {cursor_sum:.0f}% · "
                f"guard tier {max_level}/{max(len(system_tiers), len(cursor_tiers))}"
                + (f" · next body {next_sys}%" if next_sys else "")
            )
        ),
    }


def maybe_unattended_panic(prevention: dict[str, Any] | None) -> dict[str, Any] | None:
    """Auto panic when founder away and runaway agents detected (consecutive pulses)."""
    cfg = _load_config().get("unattended") or {}
    if not cfg.get("auto_panic_on_runaway"):
        return None
    if not prevention or prevention.get("health") == "healthy":
        if STREAK_PATH.is_file():
            STREAK_PATH.unlink(missing_ok=True)
        return None

    cursor = float((prevention.get("cursor") or {}).get("cpu_sum") or 0)
    need_cursor = float(cfg.get("cursor_cpu_panic") or 280)
    need_zombies = int(cfg.get("queue_zombies_panic") or 12)
    threshold = int(cfg.get("consecutive_unhealthy_pulses") or 24)
    cooldown_sec = int(cfg.get("panic_cooldown_sec") or 900)

    streak = 0
    last_warn_streak = 0
    last_warn_at = 0.0
    if STREAK_PATH.is_file():
        try:
            row = json.loads(STREAK_PATH.read_text(encoding="utf-8"))
            streak = int(row.get("count") or 0)
            last_warn_streak = int(row.get("last_warn_streak") or 0)
            last_warn_at = float(row.get("last_warn_at") or 0)
        except (OSError, json.JSONDecodeError, ValueError):
            streak = 0
            last_warn_streak = 0
            last_warn_at = 0.0

    zombies = int(prevention.get("queue_zombies") or 0)
    if cursor >= need_cursor or zombies >= need_zombies:
        streak += 1
    else:
        streak = 0
        last_warn_streak = 0
        last_warn_at = 0.0

    last_warn_streak, last_warn_at = _warn_before_panic(
        streak=streak,
        threshold=threshold,
        cursor=cursor,
        zombies=zombies,
        cfg=cfg,
        last_warn_streak=last_warn_streak,
        last_warn_at=last_warn_at,
    )

    STREAK_PATH.parent.mkdir(parents=True, exist_ok=True)
    STREAK_PATH.write_text(
        json.dumps(
            {
                "count": streak,
                "at": _now(),
                "cursor_cpu": cursor,
                "last_warn_streak": last_warn_streak,
                "last_warn_at": last_warn_at,
                "threshold": threshold,
                "need_cursor": need_cursor,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    if streak < threshold:
        return None
    if PANIC_FLAG.is_file():
        age = time.time() - PANIC_FLAG.stat().st_mtime
        if age < cooldown_sec:
            return None

    _notify(
        "⛔ Mac Health — auto-stop now",
        (
            f"Cursor {cursor:.0f}% CPU sustained {streak} pulses · "
            "stopping background agents only · Cursor stays open"
        ),
        modal=True,
        sound="Basso",
    )
    receipt = run_mac_health_emergency_stop(trigger="unattended", fast=True, notify=True)
    receipt["unattended_streak"] = streak
    STREAK_PATH.write_text(
        json.dumps({"count": 0, "at": _now(), "panicked": True, "last_warn_streak": 0}) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac Health emergency panic stop")
    ap.add_argument("--trigger", default="cli", help="hotkey | api | cli | unattended")
    ap.add_argument("--fast", action="store_true", help="Fast path — skip slow cool down")
    ap.add_argument("--full", action="store_true", help="Include hub emergency_stop (slower)")
    ap.add_argument("--dry-run", action="store_true", help="Enumerate targets only — no kill, no flags")
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    use_fast = args.fast or not args.full
    row = run_mac_health_emergency_stop(
        trigger=args.trigger,
        fast=use_fast,
        notify=not args.no_notify,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("summary"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
