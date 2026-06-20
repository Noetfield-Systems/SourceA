#!/usr/bin/env python3
"""Mac focus cleanup — cool Mac · no auto screenshot · trim agent debug noise.

Law: MAC_HEALTH_AGENT_MANDATES_LOCKED.md · MAC_NO_AUTO_SCREENSHOT_LOCKED.md
Receipt: ~/.sina/mac-focus-cleanup-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "mac-focus-cleanup-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 60) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or ""
    except (subprocess.TimeoutExpired, OSError) as e:
        return 1, str(e)


def cleanup(*, write: bool = True) -> dict:
    actions: list[dict] = []

    # No auto screenshot + visual proof off
    code, out = _run(["python3", str(ROOT / "scripts/no_auto_screenshot_v1.py"), "--enforce", "--json"])
    actions.append({"step": "no_auto_screenshot_enforce", "ok": code == 0, "detail": out[:200]})

    # Trim SourceA agent debug logs (not hub command-server — log shield handles that)
    removed: list[str] = []
    for p in (ROOT / ".cursor").glob("debug-*.log"):
        try:
            p.unlink()
            removed.append(str(p.name))
        except OSError:
            pass
    actions.append({"step": "trim_cursor_debug_logs", "ok": True, "removed": removed})

    # Process snapshot (informational)
    counts: dict[str, int] = {}
    for pat in ("anti_staleness_auto_wire", "fbe_motor", "screencapture", "playwright"):
        code, out = _run(["pgrep", "-c", "-f", pat])
        try:
            counts[pat] = int(out.strip()) if code == 0 else 0
        except ValueError:
            counts[pat] = 0

    flags = {
        "no_auto_screenshot": (SINA / "no-auto-screenshot-v1.flag").is_file(),
        "autorun_disabled": (SINA / "auto-run-disabled-v1.flag").is_file(),
        "film_frozen": (SINA / "commercial-film-render-frozen-v1.flag").is_file(),
        "mac_health_quiet": (SINA / "mac-health-quiet-v1.flag").is_file(),
        "mac_control_plane": (SINA / "mac-control-plane-v1.flag").is_file(),
    }

    row = {
        "schema": "mac-focus-cleanup-receipt-v1",
        "at": _now(),
        "ok": all(a.get("ok", True) for a in actions) and flags["no_auto_screenshot"],
        "one_law": "Mac = control panel · no auto screenshot · no heavy local factory · cloud executes",
        "actions": actions,
        "process_counts": counts,
        "flags": flags,
        "mac_focus_line": (
            f"mac-focus · screenshot=OFF · autorun={'OFF' if flags['autorun_disabled'] else 'ON'} · "
            f"anti_staleness={counts.get('anti_staleness_auto_wire', 0)} · "
            f"screencapture={counts.get('screencapture', 0)} · motors={counts.get('fbe_motor', 0)}"
        ),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac focus cleanup v1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = cleanup()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("mac_focus_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
