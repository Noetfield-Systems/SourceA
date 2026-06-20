#!/usr/bin/env python3
"""Cursor ultra-light — founder uses Cursor ONLY, one workspace, minimal body load.

Real fix (Jun 2026): 8 extension-hosts = ~5 GB RAM. Disk trim alone does not drop RAM.
Must quit + reopen ONE folder + bootout background launchd stack.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
FLAG = SINA / "cursor-ultra-light-v1.flag"
RECEIPT = SINA / "mac-health" / "cursor-ultra-light-latest-v1.json"
SETTINGS = Path.home() / "Library/Application Support/Cursor/User/settings.json"
CURSOR_SUPPORT = Path.home() / "Library/Application Support/Cursor"
CURSOR_DOT = Path.home() / ".cursor"
DEFAULT_KEEP = Path.home() / "Desktop/SourceA"

# Background stack — not needed when founder is Cursor-only
LAUNCHD_QUIET = (
    "com.sourcea.hub",
    "com.sourcea.autorun-worker",
    "com.sourcea.routing-panel",
    "com.sina.mac-health-panic-listener",
    "com.sina.panic-stop-menubar",
    "com.sina.mac-health-panic-hotkey",
    "com.sourcea.g7-governance-self-heal",
    "com.sina.mac-daily-cleanup",
    "com.sourcea.mac-law",
)

# Extension-host folder slug → keep when trimming .cursor/projects cache
HOST_TO_SLUG = {
    "MacLaw": "Users-sinakazemnezhad-Desktop-MacLaw",
    "SourceA": "Users-sinakazemnezhad-Desktop-SourceA",
    "TrustField": "Users-sinakazemnezhad-Desktop-TrustField-Technologies",
    "VIRLUX": "VIRLUX",
    "empty": "empty-window",
}

ULTRA_LIGHT_SETTINGS: dict[str, Any] = {
    "window.restoreWindows": "none",
    "workbench.editor.restoreEditors": False,
    "window.openFoldersInNewWindow": "off",
    "window.openWithoutArgumentsInNewWindow": "off",
    "workbench.editor.limit.enabled": True,
    "workbench.editor.limit.value": 3,
    "workbench.editor.limit.perEditorGroup": True,
    "workbench.editor.enablePreview": True,
    "workbench.startupEditor": "none",
    "files.hotExit": "off",
    "editor.minimap.enabled": False,
    "editor.smoothScrolling": False,
    "workbench.list.smoothScrolling": False,
    "extensions.autoUpdate": False,
    "extensions.autoCheckUpdates": False,
    "update.mode": "manual",
    "telemetry.telemetryLevel": "off",
    "git.autofetch": False,
    "typescript.tsserver.maxTsServerMemory": 1024,
    "search.maxResults": 300,
    "files.autoSave": "off",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: float = 20.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()
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


def _slug_for_keep(keep: Path) -> str:
    home = Path.home()
    try:
        rel = keep.resolve().relative_to(home)
        return "Users-" + home.name + "-" + "-".join(str(p).replace(" ", "-") for p in rel.parts)
    except ValueError:
        return keep.name.replace(" ", "-")


def probe_before() -> dict[str, Any]:
    from cursor_session_relief_v1 import probe_cursor_session  # noqa: WPS433

    return probe_cursor_session()


def bootout_background_stack() -> dict[str, Any]:
    uid = os.getuid()
    out: list[dict[str, Any]] = []
    for label in LAUNCHD_QUIET:
        code, detail = _run(["launchctl", "bootout", f"gui/{uid}/{label}"], timeout=8.0)
        out.append({"label": label, "ok": code == 0, "detail": detail[:100]})
    return {"ok": True, "bootout": out}


def apply_ultra_light_settings() -> dict[str, Any]:
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    current: dict[str, Any] = {}
    if SETTINGS.is_file():
        try:
            raw = SETTINGS.read_text(encoding="utf-8")
            current = json.loads(re.sub(r"/\*.*?\*/|//.*", "", raw, flags=re.S))
        except (OSError, json.JSONDecodeError):
            current = {}
    merged = {**current, **ULTRA_LIGHT_SETTINGS}
    SETTINGS.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(SETTINGS), "keys_set": len(ULTRA_LIGHT_SETTINGS)}


def trim_disk_bloat(*, keep_slug: str, keep_log_days: int = 1) -> dict[str, Any]:
    """Safe trim while Cursor quit — frees disk; RAM drops after single-window restart."""
    freed = 0
    actions: list[dict[str, Any]] = []
    cutoff = time.time() - keep_log_days * 86400

    logs_dir = CURSOR_SUPPORT / "logs"
    if logs_dir.is_dir():
        for entry in logs_dir.iterdir():
            if not entry.is_dir():
                continue
            try:
                if entry.stat().st_mtime < cutoff:
                    size = _dir_size(entry)
                    shutil.rmtree(entry, ignore_errors=True)
                    freed += size
                    actions.append({"path": str(entry.name), "action": "old_log_dir", "mb": round(size / 1024 / 1024, 1)})
            except OSError:
                pass

    for rel in (
        CURSOR_DOT / "browser-logs",
        CURSOR_SUPPORT / "process-monitor",
        CURSOR_SUPPORT / "CachedData",
        CURSOR_SUPPORT / "Code Cache",
        CURSOR_SUPPORT / "GPUCache",
        CURSOR_SUPPORT / "CachedExtensionVSIXs",
    ):
        if rel.exists():
            size = _dir_size(rel)
            shutil.rmtree(rel, ignore_errors=True)
            if rel.name not in ("CachedData", "Code Cache", "GPUCache", "CachedExtensionVSIXs"):
                rel.mkdir(parents=True, exist_ok=True)
            freed += size
            actions.append({"path": str(rel.name), "action": "cleared", "mb": round(size / 1024 / 1024, 1)})

    snapshots = CURSOR_SUPPORT / "snapshots"
    if snapshots.is_dir():
        size = _dir_size(snapshots)
        shutil.rmtree(snapshots, ignore_errors=True)
        freed += size
        actions.append({"path": "snapshots", "action": "cleared_all", "mb": round(size / 1024 / 1024, 1)})

    projects = CURSOR_DOT / "projects"
    if projects.is_dir():
        for proj in projects.iterdir():
            if not proj.is_dir() or proj.name == keep_slug:
                continue
            for sub in ("mcps", "terminals"):
                target = proj / sub
                if target.is_dir():
                    size = _dir_size(target)
                    shutil.rmtree(target, ignore_errors=True)
                    freed += size
                    actions.append(
                        {"path": f"{proj.name}/{sub}", "action": "cleared_inactive_project", "mb": round(size / 1024 / 1024, 1)}
                    )

    return {"ok": True, "freed_mb": round(freed / 1024 / 1024, 1), "actions": actions}


def quit_cursor() -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    code, out = _run(["osascript", "-e", 'tell application "Cursor" to quit saving yes'], timeout=25.0)
    steps.append({"step": "quit", "ok": code == 0, "detail": out[:120]})
    time.sleep(2.0)
    for pat in ("Cursor Helper (Renderer)", "Cursor Helper (GPU)", "Cursor.app/Contents/MacOS/Cursor"):
        _run(["pkill", "-TERM", "-f", pat], timeout=5.0)
    time.sleep(1.0)
    _run(["pkill", "-9", "-f", "Cursor.app/Contents/MacOS/Cursor"], timeout=5.0)
    time.sleep(0.8)
    return {"ok": True, "steps": steps}


def reopen_single_workspace(keep: Path) -> dict[str, Any]:
    keep = keep.expanduser().resolve()
    if not keep.is_dir():
        return {"ok": False, "error": f"workspace missing: {keep}"}
    app = Path("/Applications/Cursor.app")
    if app.is_dir():
        code, out = _run(["open", "-a", str(app), str(keep)], timeout=15.0)
    else:
        code, out = _run(["open", "-a", "Cursor", str(keep)], timeout=15.0)
    return {
        "ok": code == 0,
        "workspace": str(keep),
        "detail": out[:120] or "launching",
        "founder_line": f"Cursor reopening ONE window: {keep.name} only",
    }


def write_focus_flags() -> dict[str, Any]:
    SINA.mkdir(parents=True, exist_ok=True)
    ts = _now()
    FLAG.write_text(f"cursor-ultra-light-v1 · {ts} · one workspace · background stack off\n", encoding="utf-8")
    freeze = SINA / "auto-run-disabled-v1.flag"
    if not freeze.is_file():
        freeze.write_text(f"cursor-ultra-light · {ts}\n", encoding="utf-8")
    light = SINA / "mac-light-validators-only-v1.flag"
    if not light.is_file():
        light.write_text(f"cursor-ultra-light · {ts}\n", encoding="utf-8")
    return {"ok": True, "flag": str(FLAG)}


def run_ultra_light(
    *,
    keep: Path | None = None,
    restart: bool = True,
    trim: bool = True,
    bootout: bool = True,
    settings: bool = True,
) -> dict[str, Any]:
    keep = (keep or DEFAULT_KEEP).expanduser().resolve()
    keep_slug = _slug_for_keep(keep)
    before = probe_before()
    steps: dict[str, Any] = {"before": before, "keep_workspace": str(keep), "keep_slug": keep_slug}

    hosts = list(before.get("extension_hosts") or [])
    close_these = [h for h in hosts if h not in (keep.name, "SourceA") and h != keep.name]
    if len(hosts) > 1:
        steps["close_these_windows"] = {
            "count": len(hosts) - 1,
            "hosts": hosts,
            "action": f"Restart opens ONLY {keep.name} — do not reopen SourceA / TrustField / VIRLUX",
        }

    if settings:
        steps["settings"] = apply_ultra_light_settings()
    if bootout:
        steps["background"] = bootout_background_stack()
    try:
        from cursor_agent_law_v1 import enforce_flags, reset_cursor_window_state  # noqa: WPS433

        steps["window_state"] = reset_cursor_window_state(keep=keep)
        steps["flags"] = enforce_flags()
    except Exception as exc:
        steps["flags"] = write_focus_flags()
        steps["flags_error"] = str(exc)[:120]

    if restart:
        steps["quit"] = quit_cursor()
        if trim:
            steps["trim"] = trim_disk_bloat(keep_slug=keep_slug)
        steps["reopen"] = reopen_single_workspace(keep)
        time.sleep(4)
        try:
            steps["after"] = probe_before()
        except Exception as exc:
            steps["after"] = {"error": str(exc)[:120]}
    elif trim:
        steps["trim"] = trim_disk_bloat(keep_slug=keep_slug)

    receipt = {
        "schema": "cursor-ultra-light-v1",
        "at": _now(),
        "ok": True,
        "founder_line": (
            f"Ultra-light: ONE window ({keep.name}) · background hub/factory/panic OFF · "
            f"Mac Health pulse 120s · was {before.get('extension_host_count', '?')} extension-hosts"
        ),
        "steps": steps,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Cursor ultra-light — one workspace, minimal Mac load")
    ap.add_argument("--keep", type=Path, default=DEFAULT_KEEP, help="Single workspace folder to reopen")
    ap.add_argument("--no-restart", action="store_true", help="Trim + flags only (no quit)")
    ap.add_argument("--no-trim", action="store_true")
    ap.add_argument("--no-bootout", action="store_true")
    ap.add_argument("--no-settings", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = run_ultra_light(
        keep=args.keep,
        restart=not args.no_restart,
        trim=not args.no_trim,
        bootout=not args.no_bootout,
        settings=not args.no_settings,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line", "done"))
        close = (row.get("steps") or {}).get("close_these_windows")
        if close:
            print(f"  was {close.get('count')} extra windows: {close.get('hosts')}")
        after = (row.get("steps") or {}).get("after") or {}
        if after.get("rss_mb") is not None:
            print(f"  after: {after.get('rss_mb')} MB · {after.get('extension_host_count')} extension-hosts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
