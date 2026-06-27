#!/usr/bin/env python3
"""Sanitize hub projection JSON — P5-PROJECTION poison (realtime SSOT replacements).

Law: SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md
Ship window only — not Mac founder session pre-reply marathon.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
PANEL = ROOT / "agent-control-panel"
RECEIPT = Path.home() / ".sina" / "projection-poison-sanitize-receipt-v1.json"

sys.path.insert(0, str(SCRIPTS))
from anti_poison_lib_v1 import (  # noqa: E402
    _now,
    mac_founder_session,
    sanitize_projection_file,
    scan_repo,
    ship_window_active,
)


def default_targets() -> list[Path]:
    paths: list[Path] = []
    paths.extend(PANEL.glob("command-data*.json"))
    boot = PANEL / "worker-hub" / "boot.json"
    if boot.is_file():
        paths.append(boot)
    return paths


def run(*, dry_run: bool = False, force: bool = False) -> dict:
    if mac_founder_session() and not force and not ship_window_active():
        return {
            "schema": "projection-poison-sanitize-v1",
            "at": _now(),
            "ok": True,
            "skipped": "mac_founder_session — use --force with ASF ship window only",
            "touched": [],
        }
    before = scan_repo(projection=True)
    touched: list[dict] = []
    for path in default_targets():
        touched.append(sanitize_projection_file(path, dry_run=dry_run))
    after = scan_repo(projection=True) if not dry_run else before
    report = {
        "schema": "projection-poison-sanitize-v1",
        "at": _now(),
        "dry_run": dry_run,
        "hits_before": len(before),
        "hits_after": len(after),
        "touched": touched,
        "ok": len(after) == 0 or dry_run,
    }
    try:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Sanitize hub projection poison")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="Allow on Mac only with ASF ship window")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = run(dry_run=args.dry_run, force=args.force)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"PROJECTION_SANITIZE ok={report.get('ok')} before={report.get('hits_before')} after={report.get('hits_after')}")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
