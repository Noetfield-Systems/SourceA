#!/usr/bin/env python3
"""Wire all founder-glance cockpit apps — sync bundles + validate + receipt."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "founder-glance-cockpit-wire-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 120) -> dict:
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
        "stdout_tail": (proc.stdout or "")[-600:],
        "stderr_tail": (proc.stderr or "")[-300:],
    }


def _ensure_server(script: str, port: int) -> None:
    import urllib.error
    import urllib.request

    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
        return
    except Exception:
        pass
    subprocess.Popen(
        ["bash", str(ROOT / "scripts" / script)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
            return
        except Exception:
            __import__("time").sleep(0.3)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Founder glance cockpit ecosystem wire")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-sync", action="store_true")
    args = parser.parse_args()

    steps: list[dict] = []
    for script, port in (
        ("serve-mac-health-guard.sh", 13024),
        ("serve-chat-unify.sh", 13023),
        ("serve-apple-health.sh", 13025),
        ("serve-n8n-integration.sh", 13026),
    ):
        try:
            _ensure_server(script, port)
            steps.append({"cmd": [script], "ok": True, "port": port})
        except Exception as e:
            steps.append({"cmd": [script], "ok": False, "error": str(e), "port": port})

    if not args.skip_sync:
        steps.append(_run(["bash", "scripts/sync-standalone-apps-to-bundles-v1.sh"], timeout=90))

    steps.append(_run(["bash", "scripts/validate-mac-daily-cleanup-wire-v1.sh"], timeout=120))

    steps.append(_run(["bash", "scripts/validate-founder-glance-cockpit-apps-v1.sh"], timeout=180))
    steps.append(_run(["python3", "scripts/mac_health_founder_glance_wire_v1.py", "--skip-sync", "--tier", "session"], timeout=120))

    from founder_glance_cockpit_v1 import build_ui_contract, load_registry  # noqa: WPS433

    overall = all(s.get("ok") for s in steps if "ok" in s)
    receipt = {
        "schema": "founder-glance-cockpit-wire-v1",
        "at": _now(),
        "overall_ok": overall,
        "registry": "data/founder-glance-cockpit-apps-v1.json",
        "law_doc": "brain-os/law/enforcement/SINA_FOUNDER_GLANCE_COCKPIT_APPS_LOCKED_v1.md",
        "apps": {aid: build_ui_contract(aid) for aid in (load_registry().get("apps") or {})},
        "steps": steps,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"founder-glance-cockpit-wire-v1: {'PASS' if overall else 'FAIL'} · {RECEIPT}")

    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
