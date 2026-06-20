#!/usr/bin/env python3
"""Wire Mac Health Founder Glance SSOT across ecosystem — one command, zero founder steps."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "mac-health-founder-glance-wire-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 180) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**dict(**__import__("os").environ), "PYTHONPATH": f"{ROOT}/scripts"},
    )
    return {
        "cmd": cmd,
        "ok": proc.returncode == 0,
        "stdout_tail": (proc.stdout or "")[-800:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Mac Health founder-glance ecosystem wire")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--tier", choices=("session", "full"), default="session")
    args = parser.parse_args()

    steps: list[dict] = []

    if not args.skip_sync:
        steps.append(_run(["bash", "scripts/sync-standalone-apps-to-bundles-v1.sh"], timeout=60))

    steps.append(_run(["bash", "scripts/validate-mac-health-founder-glance-v1.sh"], timeout=120))

    if args.tier == "full":
        steps.append(_run(["bash", "scripts/validate-mac-health-wire-live-v1.sh"], timeout=180))
        steps.append(_run(["python3", "scripts/disk_live_wire_sync_v1.py", "--json"], timeout=240))

    from mac_health_founder_glance_ui_v1 import build_ui_contract  # noqa: WPS433
    from mac_health_version_v1 import MAC_HEALTH_VERSION  # noqa: WPS433

    overall = all(s.get("ok") for s in steps)
    receipt = {
        "schema": "mac-health-founder-glance-wire-v1",
        "at": _now(),
        "version": MAC_HEALTH_VERSION,
        "ui_mode": "founder_glance",
        "overall_ok": overall,
        "ui_contract": build_ui_contract(),
        "steps": steps,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        status = "PASS" if overall else "FAIL"
        print(f"mac-health-founder-glance-wire-v1: {status} · receipt {RECEIPT}")

    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
