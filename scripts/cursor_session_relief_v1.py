#!/usr/bin/env python3
"""Cursor session relief — diagnose + trim bloat after long work days.

Root causes on this Mac:
  - Renderer + extension-host RAM grows all day (agent chat context)
  - Too many Cursor windows / workspaces open at once
  - Running from DMG installer (slower, more RAM)
  - Log + snapshot cache growth under ~/Library/Application Support/Cursor
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "mac-health" / "cursor-session-relief-latest-v1.json"
CURSOR_SUPPORT = Path.home() / "Library/Application Support/Cursor"
CURSOR_DOT = Path.home() / ".cursor"
APPLICATIONS_CURSOR = Path("/Applications/Cursor.app")
DMG_VOLUME = Path("/Volumes/Cursor Installer/Cursor.app")

# Restart when probe crosses these (founder can override with --force-restart)
RESTART_RENDERER_MB = 2800
RESTART_TOTAL_MB = 5500
RESTART_EXTENSION_HOSTS = 4


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: float = 30.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)[:200]


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    try:
        if path.is_file():
            return path.stat().st_size
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
    except OSError:
        return 0
    return total


def _cursor_app_path() -> Path | None:
    if APPLICATIONS_CURSOR.is_dir():
        return APPLICATIONS_CURSOR
    if DMG_VOLUME.is_dir():
        return DMG_VOLUME
    code, out = _run(["mdfind", "kMDItemCFBundleIdentifier == 'com.todesktop.230313mzl4w4u92'"], timeout=8.0)
    if code == 0 and out.strip():
        first = Path(out.splitlines()[0].strip())
        if first.is_dir():
            return first
    return None


def probe_cursor_session() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    renderer_mb = 0.0
    workspaces_mb = 0.0
    renderer_count = 0
    extension_hosts: list[str] = []
    proc_count = 0
    cpu_sum = 0.0
    rss_kb = 0

    code, out = _run(["ps", "aux", "-m"], timeout=8.0)
    if code == 0:
        for line in out.splitlines()[1:]:
            if "Cursor" not in line:
                continue
            parts = line.split(None, 10)
            if len(parts) < 11:
                continue
            try:
                cpu_sum += float(parts[2])
                rss_kb += int(parts[5])
            except ValueError:
                continue
            cmd = parts[10]
            mb = int(parts[5]) / 1024.0
            proc_count += 1
            if "Cursor Helper (Renderer)" in cmd:
                renderer_mb += mb
                renderer_count += 1
            elif "extension-host" in cmd:
                workspaces_mb += mb
                m = re.search(r"extension-host(?:\s+\([^)]+\))?\s+(\S+)", cmd)
                extension_hosts.append(m.group(1) if m else "?")

    app = _cursor_app_path()
    from_dmg = bool(app and str(app).startswith("/Volumes/"))
    in_apps = APPLICATIONS_CURSOR.is_dir()

    support_mb = round(_dir_size(CURSOR_SUPPORT) / 1024 / 1024, 1)
    dot_mb = round(_dir_size(CURSOR_DOT) / 1024 / 1024, 1)
    logs_mb = round(_dir_size(CURSOR_SUPPORT / "logs") / 1024 / 1024, 1)
    snapshots_mb = round(_dir_size(CURSOR_SUPPORT / "snapshots") / 1024 / 1024, 1)

    total_mb = round(rss_kb / 1024, 1)
    needs_restart = (
        renderer_mb >= RESTART_RENDERER_MB
        or total_mb >= RESTART_TOTAL_MB
        or len(extension_hosts) >= RESTART_EXTENSION_HOSTS
    )

    findings: list[dict[str, str]] = []
    if from_dmg:
        findings.append(
            {
                "id": "cursor_dmg",
                "severity": "high",
                "detail": "Cursor running from DMG — copy to /Applications/Cursor.app and reopen",
            }
        )
    if not in_apps:
        findings.append(
            {
                "id": "cursor_not_in_applications",
                "severity": "high",
                "detail": "/Applications/Cursor.app missing — install properly for stable RAM",
            }
        )
    if len(extension_hosts) >= RESTART_EXTENSION_HOSTS:
        findings.append(
            {
                "id": "too_many_extension_hosts",
                "severity": "medium",
                "detail": f"{len(extension_hosts)} extension-hosts — close extra Cursor windows",
            }
        )
    if renderer_mb >= RESTART_RENDERER_MB:
        findings.append(
            {
                "id": "renderer_bloat",
                "severity": "medium",
                "detail": f"Chat renderer {renderer_mb:.0f} MB — restart Cursor to drop agent context RAM",
            }
        )
    if logs_mb >= 150:
        findings.append(
            {
                "id": "log_bloat",
                "severity": "low",
                "detail": f"Cursor logs {logs_mb:.0f} MB — safe to trim with --trim",
            }
        )

    founder_line = (
        f"Cursor {total_mb/1024:.1f} GB · {proc_count} proc · "
        f"{len(extension_hosts)} extension-hosts · "
        f"{'DMG' if from_dmg else 'Applications' if in_apps else 'unknown path'}"
    )
    if needs_restart:
        founder_line += " · restart recommended"

    return {
        "schema": "cursor-session-relief-probe-v1",
        "at": _now(),
        "processes": proc_count,
        "cpu_sum_pct": round(cpu_sum, 1),
        "rss_mb": total_mb,
        "renderer_mb": round(renderer_mb, 1),
        "renderer_count": renderer_count,
        "workspaces_mb": round(workspaces_mb, 1),
        "extension_hosts": extension_hosts,
        "extension_host_count": len(extension_hosts),
        "cursor_app": str(app) if app else None,
        "from_dmg": from_dmg,
        "in_applications": in_apps,
        "cache_mb": {
            "support": support_mb,
            "dot_cursor": dot_mb,
            "logs": logs_mb,
            "snapshots": snapshots_mb,
        },
        "needs_restart": needs_restart,
        "findings": findings,
        "founder_line": founder_line,
        "fix_hint": (
            "bash ~/Desktop/SourceA/scripts/cursor-day-relief-v1.sh --trim"
            + (" --restart" if needs_restart else "")
        ),
    }


def trim_cursor_caches(*, keep_log_days: int = 2) -> dict[str, Any]:
    """Safe disk trim — never touches chats, workspaceStorage, or snapshots."""
    freed = 0
    actions: list[dict[str, Any]] = []

    logs_dir = CURSOR_SUPPORT / "logs"
    if logs_dir.is_dir():
        cutoff = time.time() - keep_log_days * 86400
        for entry in logs_dir.iterdir():
            if not entry.is_dir():
                continue
            try:
                if entry.stat().st_mtime < cutoff:
                    size = _dir_size(entry)
                    shutil.rmtree(entry, ignore_errors=True)
                    freed += size
                    actions.append({"path": str(entry), "action": "removed_log_dir", "bytes": size})
            except OSError:
                pass

    for rel in (
        CURSOR_DOT / "browser-logs",
        CURSOR_SUPPORT / "process-monitor",
    ):
        if rel.is_dir():
            size = _dir_size(rel)
            shutil.rmtree(rel, ignore_errors=True)
            rel.mkdir(parents=True, exist_ok=True)
            actions.append({"path": str(rel), "action": "cleared", "bytes": size})
            freed += size

    return {
        "ok": True,
        "freed_mb": round(freed / 1024 / 1024, 1),
        "actions": actions,
    }


def restart_cursor(*, force: bool = False) -> dict[str, Any]:
    """Quit and reopen Cursor — prefers /Applications/Cursor.app over DMG."""
    probe = probe_cursor_session()
    if not force and not probe.get("needs_restart") and probe.get("rss_mb", 0) < 3000:
        return {
            "ok": True,
            "skipped": True,
            "reason": "Cursor RAM below restart threshold — use --force-restart to restart anyway",
            "probe": probe,
        }

    app = _cursor_app_path()
    steps: list[dict[str, Any]] = []

    code, out = _run(
        ["osascript", "-e", 'tell application "Cursor" to quit saving yes'],
        timeout=25.0,
    )
    steps.append({"step": "quit", "ok": code == 0, "detail": (out or "sent")[:120]})
    time.sleep(2.0)
    for pat in (
        "Cursor Helper (Renderer)",
        "Cursor Helper (GPU)",
        "Cursor.app/Contents/MacOS/Cursor",
    ):
        _run(["pkill", "-TERM", "-f", pat], timeout=6.0)
    time.sleep(1.0)
    _run(["pkill", "-9", "-f", "Cursor.app/Contents/MacOS/Cursor"], timeout=6.0)
    time.sleep(0.8)

    if app and app.is_dir():
        open_code, open_out = _run(["open", "-a", str(app)], timeout=15.0)
        reopen_target = str(app)
    else:
        open_code, open_out = _run(["open", "-a", "Cursor"], timeout=15.0)
        reopen_target = "Cursor (default)"

    steps.append(
        {
            "step": "reopen",
            "ok": open_code == 0,
            "target": reopen_target,
            "detail": (open_out or "launching")[:120],
        }
    )
    warn = None
    if probe.get("from_dmg") and not APPLICATIONS_CURSOR.is_dir():
        warn = "Still on DMG — drag Cursor.app to /Applications for permanent fix"

    return {
        "ok": open_code == 0,
        "steps": steps,
        "reopen_target": reopen_target,
        "warning": warn,
        "detail": "Cursor restarting — reopen your chat when the window returns",
        "before": {"rss_mb": probe.get("rss_mb"), "extension_hosts": probe.get("extension_host_count")},
    }


def run_cursor_session_relief(
    *,
    trim: bool = False,
    restart: bool = False,
    force_restart: bool = False,
) -> dict[str, Any]:
    probe = probe_cursor_session()
    row: dict[str, Any] = {"probe": probe, "at": _now()}
    if trim:
        row["trim"] = trim_cursor_caches()
    if restart:
        row["restart"] = restart_cursor(force=force_restart)
        time.sleep(3)
        row["after_probe"] = probe_cursor_session()
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Cursor session relief — long-day slowdown fix")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--trim", action="store_true", help="Clear old logs + browser-logs")
    ap.add_argument("--restart", action="store_true", help="Restart Cursor if thresholds met")
    ap.add_argument("--force-restart", action="store_true", help="Restart even if RAM looks OK")
    ap.add_argument("--probe", action="store_true", help="Probe only (default if no action)")
    args = ap.parse_args()

    if not args.trim and not args.restart:
        args.probe = True

    row = run_cursor_session_relief(
        trim=args.trim,
        restart=args.restart,
        force_restart=args.force_restart,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        p = row["probe"]
        print(p.get("founder_line", ""))
        for f in p.get("findings") or []:
            print(f"  · {f.get('detail')}")
        if row.get("trim"):
            print(f"trim: freed {row['trim'].get('freed_mb')} MB")
        if row.get("restart"):
            r = row["restart"]
            print(r.get("detail") or r.get("reason") or r.get("skipped"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
