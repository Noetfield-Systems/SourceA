#!/usr/bin/env python3
"""Mac Health Never Again v1 — durable guards against Jun 2026 incidents.

Incidents prevented:
  - 699 GB command-server.log bomb
  - 50+ fbe_motor_delegate storm
  - Playwright film capture under load
  - Cursor DMG sustained heat
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mac_health_edition_v1 import SINA, IS_PERSONAL

RECEIPT_PATH = SINA / "mac-health" / "never-again-latest-v1.json"
CONFIG_PATH = SINA / "config" / "mac-health-never-again-v1.json"

COMMAND_LOG = SINA / "command-server.log"
LAUNCHD_LOG = SINA / "command-server-launchd.log"
LAUNCHD_ERR = SINA / "command-server-launchd.err"
AUTORUN_FLAG = SINA / "auto-run-disabled-v1.flag"
FOUNDER_WORK_FLAG = SINA / "founder-work-mode-v1.flag"
FILM_FREEZE = SINA / "commercial-film-render-frozen-v1.flag"
EMERGENCY_FLAG = SINA / "mac-health-emergency-active-v1.flag"

DEFAULTS: dict[str, Any] = {
    "schema": "mac-health-never-again-v1",
    "log_cap_bytes": 52_428_800,
    "motor_soft_cap": 8,
    "motor_hard_cap": 15,
    "film_default_frozen": True,
    "cursor_dmg_warn": True,
}

# Founder's own SourceA worker-swarm process — never present on a customer's
# machine. Only watched in personal edition; see mac_health_edition_v1.
SOURCEA_MOTOR_PATTERN = "fbe_motor_delegate_v1"

CUSTOM_KILL_LIST_PATH = SINA / "config" / "mac-health-custom-kill-list-v1.json"


def _custom_kill_list() -> tuple[str, ...]:
    """User-opted-in process-name substrings from Settings — empty by default."""
    if not CUSTOM_KILL_LIST_PATH.is_file():
        return ()
    try:
        raw = json.loads(CUSTOM_KILL_LIST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()
    if not isinstance(raw, list):
        return ()
    return tuple(p for p in raw if isinstance(p, str) and p.strip())


def _motor_patterns() -> tuple[str, ...]:
    """Swarm patterns this reaper watches — SourceA's delegate motor (personal
    edition only) plus whatever the user opted into via Settings."""
    extra = (SOURCEA_MOTOR_PATTERN,) if IS_PERSONAL else ()
    return extra + _custom_kill_list()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_config() -> dict[str, Any]:
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.is_file():
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                cfg.update(raw)
        except (OSError, json.JSONDecodeError):
            pass
    return cfg


def _cap_log(path: Path, *, max_bytes: int) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False, "action": "none"}
    try:
        size = path.stat().st_size
    except OSError:
        return {"path": str(path), "exists": False, "action": "stat_fail"}
    if size <= max_bytes:
        return {"path": str(path), "bytes": size, "action": "ok"}
    try:
        with path.open("rb") as fh:
            fh.seek(max(0, size - max_bytes))
            tail = fh.read()
        path.write_bytes(tail)
        return {"path": str(path), "before_bytes": size, "after_bytes": len(tail), "action": "truncated"}
    except OSError as exc:
        return {"path": str(path), "bytes": size, "action": "truncate_fail", "error": str(exc)[:120]}


def enforce_log_caps(*, enabled: bool = True) -> list[dict[str, Any]]:
    cfg = _load_config()
    cap = int(cfg.get("log_cap_bytes") or DEFAULTS["log_cap_bytes"])
    rows = []
    for path in (COMMAND_LOG, LAUNCHD_LOG, LAUNCHD_ERR):
        rows.append(_cap_log(path, max_bytes=cap) if enabled else {"path": str(path), "action": "dry"})
    return rows


def _motor_pids(patterns: tuple[str, ...]) -> set[int]:
    pids: set[int] = set()
    for pat in patterns:
        try:
            out = subprocess.run(
                ["pgrep", "-f", pat],
                capture_output=True,
                text=True,
                timeout=4.0,
            )
            if out.returncode != 0:
                continue
            for line in out.stdout.splitlines():
                line = line.strip()
                if line.isdigit():
                    pids.add(int(line))
        except (OSError, subprocess.TimeoutExpired):
            continue
    return pids


def count_motors() -> int:
    patterns = _motor_patterns()
    if not patterns:
        return 0
    return len(_motor_pids(patterns))


def reaper_motor_surge(*, enabled: bool = True) -> dict[str, Any]:
    if FOUNDER_WORK_FLAG.is_file() and not AUTORUN_FLAG.is_file():
        return {"motors": count_motors(), "action": "founder_work_mode", "paused": True}
    cfg = _load_config()
    soft = int(cfg.get("motor_soft_cap") or DEFAULTS["motor_soft_cap"])
    hard = int(cfg.get("motor_hard_cap") or DEFAULTS["motor_hard_cap"])
    count = count_motors()
    row: dict[str, Any] = {"motors": count, "soft_cap": soft, "hard_cap": hard, "action": "none"}
    if count < soft:
        return row
    if enabled and not AUTORUN_FLAG.is_file() and not FOUNDER_WORK_FLAG.is_file():
        AUTORUN_FLAG.parent.mkdir(parents=True, exist_ok=True)
        AUTORUN_FLAG.write_text(f"never-again motor surge ({count}) · {_now()}\n", encoding="utf-8")
        row["autorun_paused"] = True
    if count >= hard and enabled:
        term_pids: list[int] = []
        for pid in _motor_pids(_motor_patterns()):
            try:
                os.kill(pid, signal.SIGTERM)
                term_pids.append(pid)
            except (ProcessLookupError, PermissionError):
                continue
        killed: list[int] = []
        kill_escalated: list[int] = []
        if term_pids:
            time.sleep(0.25)
            for pid in term_pids:
                try:
                    os.kill(pid, 0)
                except (ProcessLookupError, PermissionError):
                    killed.append(pid)
                    continue
                try:
                    os.kill(pid, signal.SIGKILL)
                    killed.append(pid)
                    kill_escalated.append(pid)
                except (ProcessLookupError, PermissionError):
                    killed.append(pid)
        row["killed"] = killed
        row["kill_escalated"] = kill_escalated
        row["signal_used"] = "TERM+KILL" if kill_escalated else ("TERM" if killed else "none")
        row["action"] = "reaped"
    elif count >= soft:
        row["action"] = "paused_autorun"
    return row


def ensure_film_frozen(*, enabled: bool = True) -> dict[str, Any]:
    cfg = _load_config()
    if not cfg.get("film_default_frozen", True):
        return {"frozen": FILM_FREEZE.is_file(), "action": "policy_off"}
    if FILM_FREEZE.is_file():
        return {"frozen": True, "action": "already"}
    if not enabled:
        return {"frozen": False, "action": "dry"}
    FILM_FREEZE.write_text(
        json.dumps(
            {
                "frozen_at": _now(),
                "reason": "never-again default — no Playwright hero rerenders on Mac",
                "until": "Screen Studio master + critic circle S/A PASS",
                "next_action": "sourcea-commercial-film-ship.sh after ingest",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"frozen": True, "action": "created"}


def detect_cursor_dmg() -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["pgrep", "-fl", "Cursor Installer"],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
        lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    except (OSError, subprocess.TimeoutExpired):
        lines = []
    apps_cursor = Path("/Applications/Cursor.app").is_dir()
    return {
        "from_dmg": len(lines) > 0,
        "dmg_processes": len(lines),
        "in_applications": apps_cursor,
        "fix": "Quit Cursor · open /Applications/Cursor.app" if lines else None,
    }


def run_never_again_probe(*, side_effects: bool = True) -> dict[str, Any]:
    cfg = _load_config()
    logs = enforce_log_caps(enabled=side_effects)
    motors = reaper_motor_surge(enabled=side_effects)
    film = ensure_film_frozen(enabled=side_effects)
    cursor = detect_cursor_dmg() if cfg.get("cursor_dmg_warn", True) else {"skipped": True}
    agent_mandates: dict[str, Any] = {"skipped": True}
    try:
        from mac_health_agent_mandates_v1 import run_agent_mandates_probe  # noqa: WPS433

        agent_mandates = run_agent_mandates_probe(side_effects=side_effects)
    except Exception as exc:
        agent_mandates = {"ok": False, "error": str(exc)[:160]}
    findings: list[dict[str, Any]] = []
    if any(r.get("action") == "truncated" for r in logs):
        findings.append(
            {
                "id": "never_again_log_cap",
                "severity": "high",
                "title": "Hub log capped before bomb",
                "detail": "command-server log exceeded cap — auto-truncated",
            }
        )
    if motors.get("action") in ("reaped", "paused_autorun"):
        findings.append(
            {
                "id": "never_again_motor_surge",
                "severity": "high",
                "title": f"Motor surge ({motors.get('motors')})",
                "detail": str(motors.get("action")),
            }
        )
    if cursor.get("from_dmg"):
        findings.append(
            {
                "id": "never_again_cursor_dmg",
                "severity": "medium",
                "title": "Cursor running from DMG",
                "detail": f"{cursor.get('dmg_processes')} proc — move to Applications",
            }
        )
    for v in agent_mandates.get("violations") or []:
        findings.append(
            {
                "id": f"agent_mandate_{v.get('id', 'violation')}",
                "severity": "high",
                "title": "Agent mandate violation",
                "detail": str(v.get("detail") or v.get("id")),
            }
        )
    row = {
        "schema": "mac-health-never-again-probe-v1",
        "at": _now(),
        "side_effects": side_effects,
        "log_caps": logs,
        "motor_reaper": motors,
        "film_freeze": film,
        "cursor_dmg": cursor,
        "agent_mandates": {
            "ok": agent_mandates.get("ok"),
            "quiet_flag": agent_mandates.get("quiet_flag"),
            "violations": len(agent_mandates.get("violations") or []),
        },
        "findings": findings,
        "autorun_paused": AUTORUN_FLAG.is_file() or FOUNDER_WORK_FLAG.is_file(),
        "emergency_active": EMERGENCY_FLAG.is_file(),
    }
    if side_effects:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac Health never-again guards")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    row = run_never_again_probe(side_effects=not args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"never-again · motors={row['motor_reaper'].get('motors')} · findings={len(row.get('findings') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
