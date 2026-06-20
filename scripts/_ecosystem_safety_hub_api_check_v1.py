#!/usr/bin/env python3
"""Hub API smoke — /api/action must not empty-reply (UnboundLocalError class)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    base = "http://127.0.0.1:13020"
    health = urllib.request.urlopen(f"{base}/health", timeout=5)
    if health.status != 200:
        print(f"FAIL: health status {health.status}", file=sys.stderr)
        return 1

    req = urllib.request.Request(
        f"{base}/api/action",
        data=json.dumps({"id": "__ecosystem_smoke_unknown__"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = json.loads(exc.read().decode())
    except urllib.error.URLError as exc:
        print(f"FAIL: /api/action unreachable: {exc}", file=sys.stderr)
        return 1

    if body.get("ok") is not False or "error" not in body:
        print(f"FAIL: unexpected /api/action body: {body}", file=sys.stderr)
        return 1

    sync = json.loads(
        urllib.request.urlopen(f"{base}/api/hub-sync", timeout=15).read().decode()
    )
    if not sync.get("ok") or not sync.get("built_at"):
        print(f"FAIL: /api/hub-sync: {sync}", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    shell_path = root / "agent-control-panel" / "command-data-shell.json"
    try:
        shell = json.loads(shell_path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"FAIL: shell read: {exc}", file=sys.stderr)
        return 1

    hfv = shell.get("home_founder_view") or {}
    actions = [a.get("id") for a in hfv.get("actions") or []]
    if "founder-ecosystem-safety" not in actions:
        print(f"FAIL: home missing Safety check button: {actions}", file=sys.stderr)
        return 1

    print(
        f"hub_api: action_ok error={str(body.get('error'))[:40]} "
        f"sync={sync.get('built_at')[:19]} safety=shell"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
