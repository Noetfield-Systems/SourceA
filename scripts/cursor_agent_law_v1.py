#!/usr/bin/env python3
"""Mac Cursor Agent Law v1 — probe caps, enforce flags, window-state reset."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
LAW = Path.home() / "Desktop/MacLaw/MAC_CURSOR_AGENT_LAW_LOCKED_v1.md"
RECEIPT = SINA / "mac-health" / "cursor-agent-law-latest-v1.json"
ULTRA_FLAG = SINA / "cursor-ultra-light-v1.flag"
CLOUD_FLAG = SINA / "mac-cloud-body-only-v1.flag"
CURSOR_SUPPORT = Path.home() / "Library/Application Support/Cursor"
STORAGE = CURSOR_SUPPORT / "User/globalStorage/storage.json"

MAX_PROCESSES = 15
WARN_PROCESSES = 12
MAX_EXTENSION_HOSTS = 1
MAX_RSS_MB = 2500


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: float = 12.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)[:200]


def probe_caps() -> dict[str, Any]:
    from cursor_session_relief_v1 import probe_cursor_session  # noqa: WPS433

    p = probe_cursor_session()
    proc = int(p.get("processes") or 0)
    hosts = int(p.get("extension_host_count") or 0)
    rss = float(p.get("rss_mb") or 0)
    violations: list[dict[str, str]] = []
    if proc > MAX_PROCESSES:
        violations.append({"id": "cursor_process_storm", "detail": f"{proc} processes (max {MAX_PROCESSES})"})
    elif proc > WARN_PROCESSES:
        violations.append({"id": "cursor_process_warn", "detail": f"{proc} processes (warn {WARN_PROCESSES})"})
    if hosts > MAX_EXTENSION_HOSTS:
        violations.append({"id": "too_many_extension_hosts", "detail": f"{hosts} hosts (max {MAX_EXTENSION_HOSTS})"})
    if rss > MAX_RSS_MB:
        violations.append({"id": "cursor_ram_bloat", "detail": f"{rss:.0f} MB (max {MAX_RSS_MB})"})
    ok = not any(v["id"] not in ("cursor_process_warn",) for v in violations)
    return {
        "schema": "cursor-agent-law-probe-v1",
        "at": _now(),
        "ok": ok,
        "caps": {
            "max_processes": MAX_PROCESSES,
            "max_extension_hosts": MAX_EXTENSION_HOSTS,
            "max_rss_mb": MAX_RSS_MB,
        },
        "probe": p,
        "violations": violations,
        "founder_line": (
            f"Cursor law: {proc} proc · {hosts} hosts · {rss/1024:.1f} GB"
            + (" · VIOLATION" if violations else " · OK")
        ),
        "fix": "bash ~/Desktop/SourceA/scripts/founder-mac-fresh-start-v1.sh",
    }


def enforce_flags() -> dict[str, Any]:
    SINA.mkdir(parents=True, exist_ok=True)
    ts = _now()
    for path, line in (
        (ULTRA_FLAG, f"cursor-agent-law-v1 · {ts}\n"),
        (CLOUD_FLAG, f"mac-cloud-body-only-v1 · {ts} · ACT on cloud only\n"),
        (SINA / "auto-run-disabled-v1.flag", f"cursor-agent-law · {ts}\n"),
        (SINA / "mac-light-validators-only-v1.flag", f"cursor-agent-law · {ts}\n"),
        (SINA / "cli-disabled-v1.flag", f"cursor-agent-law · {ts} · local CLI off\n"),
    ):
        if not path.is_file():
            path.write_text(line, encoding="utf-8")
    return {"ok": True, "flags": [str(ULTRA_FLAG), str(CLOUD_FLAG)]}


def reset_cursor_window_state(*, keep: Path) -> dict[str, Any]:
    """Stop Cursor restoring 8 windows — single folder only."""
    keep_uri = keep.expanduser().resolve().as_uri()
    if not STORAGE.is_file():
        return {"ok": True, "skipped": "no storage.json"}
    try:
        raw = STORAGE.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:120]}
    data["backupWorkspaces"] = {
        "workspaces": [],
        "folders": [{"folderUri": keep_uri}],
        "emptyWindows": [],
    }
    STORAGE.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    return {"ok": True, "keep_uri": keep_uri, "path": str(STORAGE)}


def run_enforce(*, write_receipt: bool = True) -> dict[str, Any]:
    caps = probe_caps()
    row = {
        "schema": "cursor-agent-law-enforce-v1",
        "at": _now(),
        "law_ok": LAW.is_file(),
        "flags": enforce_flags(),
        "caps": caps,
        "cap_violations": caps.get("violations") or [],
    }
    row["ok"] = bool(row["law_ok"] and row["flags"].get("ok"))
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac Cursor Agent Law v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--enforce", action="store_true")
    ap.add_argument("--reset-window-state", type=Path, metavar="KEEP")
    args = ap.parse_args()
    if args.reset_window_state:
        row = reset_cursor_window_state(keep=args.reset_window_state)
    elif args.enforce:
        row = run_enforce()
    else:
        row = probe_caps()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("fix") or "done")
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
