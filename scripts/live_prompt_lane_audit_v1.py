#!/usr/bin/env python3
"""Live-prompt lane audit only — no anti-staleness / find_critical_bugs (other agents own those)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = Path.home() / ".sina" / "live-prompt-lane-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 180) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "stdout": (proc.stdout or "")[-2000:],
            "stderr": (proc.stderr or "")[-500:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def audit(*, write: bool = True) -> dict:
    checks: list[dict] = []

    sys.path.insert(0, str(SCRIPTS))
    try:
        from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

        live = rebuild(write=True, preview=False)
        checks.append({"id": "rebuild", "ok": bool(live.get("ok")), "cursor": live.get("cursor_pos")})
    except Exception as exc:
        checks.append({"id": "rebuild", "ok": False, "error": str(exc)})
        live = {}

    for cid, cmd in (
        ("validate_live_ongoing", ["bash", str(SCRIPTS / "validate-live-ongoing-prompts-v1.sh")]),
        ("validate_pack_live", [sys.executable, str(SCRIPTS / "validate-next-prompt-pack-live-v1.py"), "--strict"]),
        ("e2e", ["bash", str(SCRIPTS / "validate-live-prompt-feed-e2e-v1.sh")]),
    ):
        row = _run(cmd)
        row["id"] = cid
        checks.append(row)

    ok = all(c.get("ok") for c in checks)
    row = {
        "ok": ok,
        "schema": "live-prompt-lane-receipt-v1",
        "at": _now(),
        "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        "checks": checks,
        "live_ongoing": {
            "cursor_pos": live.get("cursor_pos"),
            "turns": live.get("count"),
            "built_at": live.get("built_at"),
        },
        "note": "Worker lane only — does not include anti-staleness or find_critical_bugs",
    }
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = audit()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("PASS" if row.get("ok") else "FAIL")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
