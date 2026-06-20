#!/usr/bin/env python3
"""Mac Health live pulse — real-time body rhythm + H1 bridge sync."""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
LIVE_PULSE = SINA / "mac-health" / "live-pulse-v1.json"
H1_BRIDGE = SINA / "mac-health-h1-bridge-v1.json"
H1_BOOT = SINA / "worker-hub-boot-v1.json"
SOURCE_A = Path(__file__).resolve().parents[1]
H1_BOOT_PANEL = SOURCE_A / "agent-control-panel" / "worker-hub" / "boot.json"

LIVE_MAX_SEC = 45
LIVE_MAX_RAM_CRITICAL_SEC = 120
PULSE_INTERVAL_SEC = 8


def _live_max_sec(*, mp: dict[str, Any] | None = None) -> int:
    try:
        from mac_health_ram_pressure_v1 import is_ram_critical  # noqa: WPS433

        if is_ram_critical(mp=mp):
            return LIVE_MAX_RAM_CRITICAL_SEC
    except Exception:
        pass
    return LIVE_MAX_SEC


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_age_sec(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except ValueError:
        return None


def _read_h1_boot() -> dict:
    """Disk-only — never HTTP-fetch worker-hub during pulse (avoids hub↔live deadlock)."""
    for path in (H1_BOOT, H1_BOOT_PANEL):
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
    return {}


def _live_status(*, live_age: float | None, pressure_age: float | None, score: int, mp: dict, heart_ok: bool) -> str:
    if not heart_ok:
        return "OFFLINE"
    ghosts = int(mp.get("ghost_terminals") or 0)
    qz = int(mp.get("queue_zombies") or 0)
    disk = mp.get("disk_root_pct") or 0
    if score < 55 or ghosts >= 3 or qz >= 20 or disk >= 90:
        return "SICK"
    if live_age is None or pressure_age is None:
        return "STALE"
    if live_age > LIVE_MAX_SEC or pressure_age > LIVE_MAX_SEC:
        return "STALE"
    return "LIVE"


def build_live_snapshot(
    *,
    sync_h1: bool = True,
    side_effects: bool = True,
) -> dict:
    from mac_health_guard import (  # noqa: WPS433
        SCAN_PATH,
        _grade_for_score,
        _iso_age_sec as guard_age,
        _machine_pressure,
        _refresh_live_domains,
        analyze_scan,
        append_heartbeat,
        compute_live_score,
        compute_score,
        read_heartbeat_history,
        _ensure_knowledge,
    )

    scan: dict[str, Any] = {}
    if SCAN_PATH.is_file():
        try:
            scan = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
            scan = _refresh_live_domains(scan)
        except (OSError, json.JSONDecodeError):
            scan = {}
    mp = _machine_pressure()
    kb = _ensure_knowledge()
    findings, _agents = analyze_scan(scan, kb) if scan.get("domains") else ([], [])
    security_score = compute_score(findings)
    score = compute_live_score(findings, mp)
    grade = _grade_for_score(score)
    live_at = scan.get("live_refreshed_at")
    live_age = guard_age(live_at)
    pressure_age = guard_age(mp.get("at"))
    heart_ok = True
    status = _live_status(live_age=live_age, pressure_age=pressure_age, score=score, mp=mp, heart_ok=heart_ok)
    append_heartbeat(
        score=score,
        security_score=security_score,
        grade=grade,
        mp=mp,
        live_status=status,
        source="pulse",
    )
    h1 = _read_h1_boot()
    domains = scan.get("domains") or {}
    fw = domains.get("firewall") or {}

    prevention: dict[str, Any] = {"health": "unknown"}
    try:
        from mac_health_prevention_v1 import analyze_prevention, maybe_auto_prevent  # noqa: WPS433
        from mac_health_ram_pressure_v1 import skip_heavy_probes  # noqa: WPS433

        if side_effects and not skip_heavy_probes(mp=mp):
            prevention = maybe_auto_prevent(mp)
        else:
            prevention = analyze_prevention(mp)
    except Exception:
        try:
            from mac_health_prevention_v1 import analyze_prevention  # noqa: WPS433

            prevention = analyze_prevention(mp)
        except Exception:
            pass

    if side_effects:
        try:
            from mac_health_emergency_stop_v1 import maybe_cpu_pressure_warn, maybe_unattended_panic  # noqa: WPS433

            maybe_cpu_pressure_warn(mp, prevention if isinstance(prevention, dict) else None)
            panic = maybe_unattended_panic(prevention if isinstance(prevention, dict) else None)
            if panic and isinstance(prevention, dict):
                prevention = {**prevention, "unattended_panic": panic}
        except Exception:
            pass

    stranger_agent: dict[str, Any] = {}
    try:
        mon_path = SINA / "stranger-agent-monitor-v1.json"
        if mon_path.is_file():
            stranger_agent = json.loads(mon_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        stranger_agent = {}

    cpu_warn_state: dict[str, Any] = {}
    try:
        from mac_health_emergency_stop_v1 import build_cpu_warn_state  # noqa: WPS433

        cpu_warn_state = build_cpu_warn_state(
            mp, prevention if isinstance(prevention, dict) else None
        )
    except Exception:
        cpu_warn_state = {}

    cursor_session: dict[str, Any] = {}
    try:
        from mac_health_ram_pressure_v1 import skip_heavy_probes  # noqa: WPS433

        if not skip_heavy_probes(mp=mp):
            from cursor_session_relief_v1 import probe_cursor_session  # noqa: WPS433

            cursor_session = probe_cursor_session()
    except Exception:
        cursor_session = {}

    row = {
        "ok": True,
        "schema": "mac-health-live-v1",
        "at": _now(),
        "live_status": status,
        "prevention": prevention,
        "cpu_warn_state": cpu_warn_state,
        "cursor_session": cursor_session,
        "daily_cleanup_receipt": str(SINA / "mac-daily-cleanup-latest-v1.json"),
        "truth": "LIVE=real-time monitor · STALE=sick signal · SICK=body needs heal",
        "score": score,
        "security_score": security_score,
        "grade": _grade_for_score(score),
        "cursor_emergency": "cursor_hot" in ((prevention or {}).get("modes") or []),
        "body_mood": (
            "cursor_hot"
            if "cursor_hot" in ((prevention or {}).get("modes") or [])
            else _grade_for_score(score).lower().replace(" ", "_")
        ),
        "machine_pressure": mp,
        "firewall_enabled": bool(fw.get("enabled")),
        "domains_live": {
            "firewall": fw,
            "disk": domains.get("disk") or {},
        },
        "wired": {
            "live_refreshed_at": live_at,
            "live_age_sec": round(live_age, 1) if live_age is not None else None,
            "pressure_age_sec": round(pressure_age, 1) if pressure_age is not None else None,
            "live_ok": status == "LIVE",
            "pulse_interval_sec": (
                __import__("mac_health_ram_pressure_v1", fromlist=["pulse_interval_sec"]).pulse_interval_sec(mp=mp)
            ),
        },
        "h1_sync": {
            "ok": bool(h1.get("ok")),
            "url": "http://127.0.0.1:13020/",
            "task_id": h1.get("queue_sa_id") or h1.get("task_id"),
            "queue_role": h1.get("queue_role"),
            "honest_ok": h1.get("honest_ok"),
            "valid_yes": h1.get("valid_yes"),
            "built_at": h1.get("built_at"),
        },
        "history": read_heartbeat_history(36),
        "stranger_agent": {
            "one_line": stranger_agent.get("one_line"),
            "trust_tier": stranger_agent.get("trust_tier"),
            "risk_score": stranger_agent.get("risk_score"),
            "stranger_active_count": stranger_agent.get("stranger_active_count"),
            "hostile_count": stranger_agent.get("hostile_count"),
            "hub_tile": stranger_agent.get("hub_tile"),
        },
    }
    SINA.mkdir(parents=True, exist_ok=True)
    LIVE_PULSE.parent.mkdir(parents=True, exist_ok=True)
    LIVE_PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if not side_effects:
        quiet_path = SINA / "mac-health-quiet-pulse-receipt-v1.json"
        quiet_path.write_text(
            json.dumps(
                {
                    "schema": "mac-health-quiet-pulse-receipt-v1",
                    "at": _now(),
                    "side_effects": False,
                    "notify": False,
                    "prevention_side_effects": False,
                    "live_status": status,
                    "grade": grade,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    try:
        from ecosystem_pressure_v1 import write_snapshot  # noqa: WPS433

        write_snapshot()
    except Exception:
        pass
    if sync_h1:
        write_h1_bridge(row)
    return row


def write_h1_bridge(live: dict) -> dict:
    mp = live.get("machine_pressure") or {}
    h1 = live.get("h1_sync") or {}
    bridge = {
        "schema": "mac-health-h1-bridge-v1",
        "at": live.get("at") or _now(),
        "live_status": live.get("live_status"),
        "score": live.get("score"),
        "security_score": live.get("security_score"),
        "grade": live.get("grade"),
        "firewall_enabled": live.get("firewall_enabled"),
        "loadavg": mp.get("loadavg"),
        "load_1min": mp.get("load_1min"),
        "cpu_pct": mp.get("cpu_pct"),
        "cpu_cores": mp.get("cpu_cores"),
        "ram_gb": mp.get("ram_gb"),
        "ram_used_pct": mp.get("ram_used_pct"),
        "ram_used_gb": mp.get("ram_used_gb"),
        "memory_pressure_level": mp.get("memory_pressure_level"),
        "thermal_pressure": mp.get("thermal_pressure"),
        "gpu_note": mp.get("gpu_note"),
        "disk_root_pct": mp.get("disk_root_pct"),
        "ghost_terminals": mp.get("ghost_terminals"),
        "queue_zombies": mp.get("queue_zombies"),
        "heart_url": "http://127.0.0.1:13024/",
        "heart_ok": live.get("ok"),
        "wired": live.get("wired"),
        "h1": h1,
        "founder_line": _founder_line(live),
    }
    H1_BRIDGE.write_text(json.dumps(bridge, indent=2) + "\n", encoding="utf-8")
    return bridge


def _founder_line(live: dict) -> str:
    st = live.get("live_status") or "?"
    score = live.get("score") or "—"
    mp = live.get("machine_pressure") or {}
    cores = mp.get("cpu_cores") or "?"
    cpu = mp.get("cpu_pct")
    ram = mp.get("ram_used_pct")
    load = mp.get("load_1min") or "—"
    h1 = live.get("h1_sync") or {}
    task = h1.get("task_id") or "—"
    cpu_s = f"CPU {cpu}%" if cpu is not None else "CPU —"
    ram_s = f"RAM {ram}%" if ram is not None else "RAM —"
    return f"Mac Heart {st} · score {score} · {cpu_s} · {ram_s} · load {load}/{cores} · H1 {task}"


def pulse_once() -> dict:
    return build_live_snapshot(sync_h1=True, side_effects=True)


def _read_cached_live() -> dict[str, Any] | None:
    if not LIVE_PULSE.is_file():
        return None
    try:
        return json.loads(LIVE_PULSE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def refresh_live_display(row: dict[str, Any]) -> dict[str, Any]:
    """Refresh numbers for UI polls — no macOS notifications or auto-apply."""
    from mac_health_guard import _machine_pressure  # noqa: WPS433

    mp = _machine_pressure()
    out = {**row, "machine_pressure": mp, "at": _now()}
    prev = row.get("prevention") if isinstance(row.get("prevention"), dict) else {}
    try:
        from mac_health_prevention_v1 import analyze_prevention  # noqa: WPS433

        out["prevention"] = analyze_prevention(mp)
    except Exception:
        out["prevention"] = prev
    try:
        from mac_health_emergency_stop_v1 import build_cpu_warn_state  # noqa: WPS433

        out["cpu_warn_state"] = build_cpu_warn_state(mp, out.get("prevention"))
    except Exception:
        pass
    wired = dict(out.get("wired") or {})
    pulse_at = row.get("at")
    pulse_age = _iso_age_sec(pulse_at)
    pressure_age = _iso_age_sec(mp.get("at"))
    wired["pressure_age_sec"] = round(pressure_age, 1) if pressure_age is not None else None
    wired["live_age_sec"] = round(pulse_age, 1) if pulse_age is not None else None
    wired["api_refresh"] = True
    out["wired"] = wired
    try:
        from cursor_session_relief_v1 import probe_cursor_session  # noqa: WPS433

        out["cursor_session"] = probe_cursor_session()
    except Exception:
        pass
    return out


def get_live_api_row(*, sync_h1: bool = False) -> dict:
    """UI poll path — serve cached pulse; never fire notification storms."""
    import time as _time

    from mac_health_debug_bab1ff_v1 import dbg

    t0 = _time.monotonic()
    path_taken = "unknown"
    cached = _read_cached_live()
    cached_mp = (cached or {}).get("machine_pressure") or {}
    max_sec = _live_max_sec(mp=cached_mp)
    if cached and cached.get("ok"):
        age = _iso_age_sec(cached.get("at"))
        if age is not None and age <= max_sec:
            path_taken = "cached"
            row = refresh_live_display(cached)
            if sync_h1:
                write_h1_bridge(row)
            # #region agent log
            dbg(
                hypothesis_id="B",
                location="mac_health_live_v1.py:get_live_api_row",
                message="live_row",
                data={"path": path_taken, "ms": round((_time.monotonic() - t0) * 1000, 1), "age_sec": age},
            )
            # #endregion
            return row
    try:
        from mac_health_ram_pressure_v1 import is_ram_critical  # noqa: WPS433

        if cached and cached.get("ok") and is_ram_critical(mp=cached_mp):
            path_taken = "cached_ram_critical_stale_ok"
            row = refresh_live_display(cached)
            row["live_status"] = "SICK"
            row["ram_pressure_serve_stale"] = True
            if sync_h1:
                write_h1_bridge(row)
            return row
    except Exception:
        pass
    path_taken = "build_snapshot"
    row = build_live_snapshot(sync_h1=sync_h1, side_effects=False)
    try:
        from mac_health_ram_pressure_v1 import skip_heavy_probes  # noqa: WPS433

        if not skip_heavy_probes(mp=row.get("machine_pressure") or {}):
            from cursor_session_relief_v1 import probe_cursor_session  # noqa: WPS433

            row["cursor_session"] = probe_cursor_session()
    except Exception:
        pass
    # #region agent log
    dbg(
        hypothesis_id="B",
        location="mac_health_live_v1.py:get_live_api_row",
        message="live_row",
        data={
            "path": path_taken,
            "ms": round((_time.monotonic() - t0) * 1000, 1),
            "live_status": row.get("live_status"),
        },
    )
    # #endregion
    return row


def read_bridge() -> dict:
    if H1_BRIDGE.is_file():
        try:
            return json.loads(H1_BRIDGE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def main() -> int:
    import argparse
    import time

    p = argparse.ArgumentParser(description="Mac Health live pulse")
    p.add_argument("--json", action="store_true")
    p.add_argument("--loop", action="store_true", help="Run pulse loop (daemon)")
    p.add_argument("--interval", type=int, default=PULSE_INTERVAL_SEC)
    args = p.parse_args()
    if args.loop:
        while True:
            try:
                pulse_once()
            except Exception:
                pass
            time.sleep(max(3, args.interval))
    row = pulse_once()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"LIVE: {row.get('live_status')} score={row.get('score')} h1={((row.get('h1_sync') or {}).get('task_id'))}")
    return 0 if row.get("live_status") == "LIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
