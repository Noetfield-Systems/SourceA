#!/usr/bin/env python3
"""Mac Health Log Shield v1 — runaway log detection without reading whole files."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
STATE_PATH = SINA / "mac-health" / "log-shield-state-v1.json"
RECEIPT_PATH = SINA / "mac-health" / "log-shield-latest-v1.json"

COMMAND_LOG = SINA / "command-server.log"
WARN_BYTES = 100 * 1024 * 1024
CRITICAL_BYTES = 1024 * 1024 * 1024
OTHER_LOG_BYTES = 500 * 1024 * 1024
TAIL_BYTES = 4096
STUCK_LOG_BYTES = 100 * 1024 * 1024
TRUNCATE_BYTES = 100 * 1024 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _human_bytes(n: int) -> str:
    if n >= 1024**3:
        return f"{n / 1024**3:.1f} GB"
    if n >= 1024**2:
        return f"{n / 1024**2:.0f} MB"
    if n >= 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n} B"


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _tail_text(path: Path, max_bytes: int = TAIL_BYTES) -> str:
    try:
        size = path.stat().st_size
        if size <= 0:
            return ""
        with path.open("rb") as fh:
            fh.seek(max(0, size - max_bytes))
            return fh.read(max_bytes).decode("utf-8", errors="replace")
    except OSError:
        return ""


def _load_state() -> dict[str, Any]:
    if STATE_PATH.is_file():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def _save_state(row: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _health_json(url: str, timeout: float = 1.5) -> tuple[bool, bool, dict[str, Any]]:
    """Returns (reachable, ok, body_or_error)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            body = json.loads(raw)
            return True, bool(body.get("ok")), body
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8", errors="replace")
            body = json.loads(raw)
            return True, bool(body.get("ok")), body
        except (OSError, json.JSONDecodeError, ValueError):
            return True, False, {"error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError) as exc:
        return False, False, {"error": str(exc)[:200]}


def probe_hub_truth() -> dict[str, Any]:
    hub_reachable, hub_health_ok, hub_body = _health_json("http://127.0.0.1:13020/health")
    rebuild_reachable, hub_rebuild_ok, rebuild_body = _health_json("http://127.0.0.1:13030/health")
    hub_online = hub_reachable
    hub_error = ""
    if hub_reachable and not hub_health_ok:
        hub_error = str(hub_body.get("error") or hub_body)[:200]
    elif not hub_reachable:
        hub_error = str(hub_body.get("error") or "unreachable")[:200]
    badge = "Healthy"
    if not hub_reachable:
        badge = "Down"
    elif hub_reachable and not hub_health_ok:
        badge = "Port-only"
    return {
        "hub_online": hub_online,
        "hub_health_ok": hub_health_ok,
        "hub_rebuild_ok": hub_rebuild_ok if rebuild_reachable else False,
        "hub_rebuild_reachable": rebuild_reachable,
        "hub_error": hub_error,
        "hub_truth_badge": badge,
        "hub_body": {k: hub_body.get(k) for k in ("ok", "service", "port", "error") if k in hub_body},
        "rebuild_body": {k: rebuild_body.get(k) for k in ("ok", "service", "port", "error") if k in rebuild_body},
    }


def scan_sina_logs() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if SINA.is_dir():
        for path in SINA.rglob("*.log"):
            try:
                if not path.is_file():
                    continue
                size = path.stat().st_size
                if size < 1024 * 1024:
                    continue
                rows.append(
                    {
                        "path": str(path),
                        "name": path.name,
                        "bytes": size,
                        "human": _human_bytes(size),
                        "is_command_log": path.name == "command-server.log",
                    }
                )
            except OSError:
                continue
    rows.sort(key=lambda r: r["bytes"], reverse=True)
    cmd_bytes = _file_size(COMMAND_LOG)
    level = "ok"
    if cmd_bytes >= CRITICAL_BYTES:
        level = "critical"
    elif cmd_bytes >= WARN_BYTES:
        level = "warn"
    for row in rows:
        if not row["is_command_log"] and row["bytes"] >= OTHER_LOG_BYTES and level == "ok":
            level = "warn"
    prev = _load_state()
    growth_mb_per_min = None
    prev_bytes = int(prev.get("command_log_bytes") or 0)
    prev_at = prev.get("at")
    if prev_at and prev_bytes >= 0 and cmd_bytes > prev_bytes:
        try:
            dt = datetime.fromisoformat(prev_at.replace("Z", "+00:00"))
            age_min = max(0.01, (datetime.now(timezone.utc) - dt).total_seconds() / 60.0)
            growth_mb_per_min = round((cmd_bytes - prev_bytes) / (1024 * 1024) / age_min, 2)
        except ValueError:
            pass
    _save_state({"at": _now(), "command_log_bytes": cmd_bytes})
    return {
        "schema": "mac-health-log-shield-v1",
        "at": _now(),
        "command_log_bytes": cmd_bytes,
        "command_log_human": _human_bytes(cmd_bytes),
        "level": level,
        "critical": level == "critical",
        "warn": level in ("warn", "critical"),
        "log_growth_mb_per_min": growth_mb_per_min,
        "largest_sina_logs": rows[:8],
        "tail_snippet": _tail_text(COMMAND_LOG)[:500] if cmd_bytes > 0 else "",
    }


def detect_stuck_log_readers() -> list[dict[str, Any]]:
    stuck: list[dict[str, Any]] = []
    try:
        out = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=8.0,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return stuck
    patterns = (
        r"\bcat\b.*command-server\.log",
        r"\bwc\b.*command-server\.log",
        r"\btail\b.*command-server\.log",
        r"\bgrep\b.*command-server\.log",
    )
    for line in out.splitlines()[1:]:
        parts = line.split(None, 10)
        if len(parts) < 11:
            continue
        pid_s, cpu_s, cmd = parts[1], parts[2], parts[10]
        if not any(re.search(p, cmd, re.I) for p in patterns):
            continue
        try:
            pid = int(pid_s)
            cpu = float(cpu_s)
        except ValueError:
            continue
        log_match = re.search(r"(/[^\s]+command-server\.log)", cmd)
        log_path = Path(log_match.group(1)) if log_match else COMMAND_LOG
        log_size = _file_size(log_path)
        if log_size >= STUCK_LOG_BYTES or cpu >= 5.0:
            stuck.append(
                {
                    "pid": pid,
                    "cpu": cpu,
                    "cmd": cmd[:160],
                    "log_bytes": log_size,
                    "log_human": _human_bytes(log_size),
                }
            )
    return stuck


def count_factory_motors() -> dict[str, Any]:
    try:
        out = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=8.0,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {"fbe_motor_delegate_count": 0, "factory_python_count": 0}
    motor = 0
    factory = 0
    factory_patterns = (
        "fbe_motor_delegate",
        "anti_staleness_auto_wire",
        "governance_zero_drift",
        "agentic_layer_pipeline",
        "auto_run_worker_batch",
    )
    for line in out.splitlines()[1:]:
        cmd = line.split(None, 10)[-1] if len(line.split(None, 10)) >= 11 else line
        if "fbe_motor_delegate" in cmd:
            motor += 1
        if any(p in cmd for p in factory_patterns):
            factory += 1
    return {
        "fbe_motor_delegate_count": motor,
        "factory_python_count": factory,
    }


def apply_factory_storm_guard(*, hub_health_ok: bool, enabled: bool = True) -> dict[str, Any]:
    counts = count_factory_motors()
    motor = int(counts.get("fbe_motor_delegate_count") or 0)
    factory = int(counts.get("factory_python_count") or 0)
    storm = (not hub_health_ok) and (motor >= 5 or factory >= 15)
    motor_surge = motor >= 8
    flag = SINA / "auto-run-disabled-v1.flag"
    touched = False
    if motor_surge and enabled and not flag.is_file():
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(f"log-shield motor surge ({motor}) · {_now()}\n", encoding="utf-8")
        touched = True
    if storm and enabled and not flag.is_file():
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(f"log-shield factory storm · {_now()}\n", encoding="utf-8")
        touched = True
    return {
        "factory_storm": storm or motor_surge,
        "motor_surge": motor_surge,
        "freeze_touched": touched,
        **counts,
    }


def log_shield_findings(shield: dict[str, Any], hub: dict[str, Any], stuck: list[dict]) -> list[dict]:
    findings: list[dict] = []
    if shield.get("critical"):
        findings.append(
            {
                "id": "log_shield_command_bomb",
                "severity": "critical",
                "title": f"Runaway hub log ({shield.get('command_log_human')})",
                "detail": "command-server.log exceeds 1 GB — disk I/O and RAM cache pressure.",
                "fix": "Mac Health → Relieve disk · or truncate log",
            }
        )
    elif shield.get("warn"):
        findings.append(
            {
                "id": "log_shield_command_warn",
                "severity": "high",
                "title": f"Large hub log ({shield.get('command_log_human')})",
                "detail": "command-server.log is growing — rotate before it becomes a bomb.",
                "fix": "Relieve disk in Log Shield",
            }
        )
    if hub.get("hub_online") and not hub.get("hub_health_ok"):
        findings.append(
            {
                "id": "log_shield_hub_lie",
                "severity": "critical",
                "title": "Hub port open but /health failing",
                "detail": hub.get("hub_error") or "JSON ok!=true",
                "fix": "Restart hub · check command-server.fail-snippet.log",
            }
        )
    if stuck:
        findings.append(
            {
                "id": "log_shield_stuck_readers",
                "severity": "high",
                "title": f"{len(stuck)} stuck log reader(s)",
                "detail": "cat/wc/grep hammering a huge log at high CPU.",
                "fix": "Kill stuck readers · Relieve disk",
            }
        )
    storm = apply_factory_storm_guard(hub_health_ok=bool(hub.get("hub_health_ok")), enabled=False)
    if storm.get("factory_storm"):
        findings.append(
            {
                "id": "log_shield_factory_storm",
                "severity": "high",
                "title": "Factory running while hub sick",
                "detail": f"motors={storm.get('fbe_motor_delegate_count')} factory_procs={storm.get('factory_python_count')}",
                "fix": "Auto guard freeze · Stop background agents",
            }
        )
    return findings


def _probe_never_again(*, side_effects: bool) -> dict[str, Any]:
    try:
        if str(Path(__file__).resolve().parents[1] / "scripts") not in sys.path:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from mac_health_never_again_v1 import run_never_again_probe  # noqa: WPS433

        return run_never_again_probe(side_effects=side_effects)
    except Exception as exc:
        return {"error": str(exc)[:120], "findings": []}


def _probe_film_render() -> dict[str, Any]:
    try:
        sys_path = Path(__file__).resolve().parents[1] / "scripts"
        if str(sys_path) not in sys.path:
            sys.path.insert(0, str(sys_path))
        from commercial_film_render_guard_v1 import probe_active_renders  # noqa: WPS433

        probe = probe_active_renders()
        frozen = bool((probe.get("freeze") or {}).get("frozen"))
        active = bool(probe.get("active"))
        probe["violation"] = frozen and active
        probe["film_render_frozen"] = frozen
        return probe
    except Exception as exc:
        return {
            "processes": 0,
            "active": False,
            "film_render_frozen": False,
            "violation": False,
            "error": str(exc)[:120],
        }


def build_log_shield_probe(*, side_effects: bool = True) -> dict[str, Any]:
    hub = probe_hub_truth()
    shield = scan_sina_logs()
    stuck = detect_stuck_log_readers()
    storm = apply_factory_storm_guard(
        hub_health_ok=bool(hub.get("hub_health_ok")),
        enabled=side_effects,
    )
    film_render = _probe_film_render()
    never_again = _probe_never_again(side_effects=side_effects)
    findings = log_shield_findings(shield, hub, stuck)
    if film_render.get("violation"):
        findings.append(
            {
                "id": "log_shield_film_render_violation",
                "severity": "high",
                "title": "Film capture running while frozen",
                "detail": (
                    f"{film_render.get('processes', 0)} proc · "
                    f"{film_render.get('cpu_sum', 0)}% CPU · "
                    f"{film_render.get('rss_mb', 0)} MB RAM"
                ),
                "fix": "Kill film renders · commercial_film_render_guard_v1.py kill-active",
            }
        )
    for finding in never_again.get("findings") or []:
        findings.append({**finding, "id": finding.get("id", "never_again")})
    sina_log_bomb = {
        "level": shield.get("level"),
        "critical": shield.get("critical"),
        "bytes": shield.get("command_log_bytes"),
        "human": shield.get("command_log_human"),
        "growth_mb_per_min": shield.get("log_growth_mb_per_min"),
    }
    return {
        **hub,
        "sina_log_bomb": sina_log_bomb,
        "log_growth_mb_per_min": shield.get("log_growth_mb_per_min"),
        "largest_sina_logs": shield.get("largest_sina_logs") or [],
        "stuck_log_readers": stuck,
        "stuck_log_reader_count": len(stuck),
        "factory_storm": storm,
        "film_render": film_render,
        "film_render_frozen": film_render.get("film_render_frozen"),
        "film_render_active": film_render.get("active"),
        "never_again": never_again,
        "log_shield_findings": findings,
        "schema": "mac-health-log-shield-probe-v1",
        "at": _now(),
    }


def kill_stuck_log_readers() -> dict[str, Any]:
    killed: list[int] = []
    for row in detect_stuck_log_readers():
        pid = int(row.get("pid") or 0)
        if pid <= 1:
            continue
        try:
            subprocess.run(["kill", "-9", str(pid)], timeout=3.0, check=False)
            killed.append(pid)
        except OSError:
            pass
    receipt = {"ok": True, "killed": killed, "count": len(killed), "at": _now()}
    _write_receipt("kill_stuck_log_readers", receipt)
    return receipt


def truncate_runaway_logs(*, min_bytes: int = TRUNCATE_BYTES) -> dict[str, Any]:
    truncated: list[dict[str, Any]] = []
    targets = [COMMAND_LOG]
    if SINA.is_dir():
        for path in SINA.rglob("*.log"):
            if path.is_file() and _file_size(path) >= min_bytes:
                if path not in targets:
                    targets.append(path)
    for path in targets:
        size = _file_size(path)
        if size < min_bytes:
            continue
        try:
            path.write_text("", encoding="utf-8")
            truncated.append({"path": str(path), "bytes_before": size, "human": _human_bytes(size)})
        except OSError:
            continue
    receipt = {
        "ok": True,
        "truncated": truncated,
        "count": len(truncated),
        "at": _now(),
    }
    _write_receipt("truncate_runaway_logs", receipt)
    return receipt


def _write_receipt(action: str, body: dict[str, Any]) -> None:
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {"action": action, **body}
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def handle_log_shield_action(body: dict[str, Any]) -> dict[str, Any]:
    action = (body.get("action") or "").strip().lower()
    if action in ("truncate_runaway_logs", "relieve_disk", "log_shield_relieve"):
        return {"ok": True, **truncate_runaway_logs()}
    if action in ("kill_stuck_log_readers", "log_shield_kill_readers"):
        return {"ok": True, **kill_stuck_log_readers()}
    if action in ("log_shield_probe", "log_shield"):
        return {"ok": True, "probe": build_log_shield_probe(side_effects=False)}
    return {"ok": False, "error": f"unknown log shield action: {action}"}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Mac Health Log Shield v1")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    row = build_log_shield_probe()
    if args.json or args.probe:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps({"ok": True, "level": row["sina_log_bomb"]["level"]}, indent=2))


if __name__ == "__main__":
    main()
