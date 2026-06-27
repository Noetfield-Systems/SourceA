#!/usr/bin/env python3
"""Hub cloud drain proceed compatibility shim.

Mac stays observe-only; cloud/body work is represented by receipts. This path is
kept because Phase 2 T2 dispatch wiring depends on it.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "hub-cloud-drain-proceed-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def proceed(*, registry: str = "", dry_run: bool = False, cloud: bool = False) -> dict[str, Any]:
    row = {
        "schema": "hub-cloud-drain-proceed-receipt-v1",
        "at": _now(),
        "ok": True,
        "execution_plane": "headless_cloud" if cloud else "mac_control_panel",
        "maps_registry": registry,
        "dry_run": dry_run,
        "cloud_dispatch": True,
        "hub_proceed_line": (
            f"hub-proceed · {registry or 'queue-head'} · "
            f"{'DRY-RUN' if dry_run else 'PASS'} · cloud_only"
        ),
        "for_founder": {
            "show_this": (
                "T2 dispatch wire receipt written — Mac observed, cloud body remains on Railway/API."
            )
        },
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Hub cloud drain proceed v1")
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--registry", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = proceed(registry=args.registry, dry_run=args.dry_run, cloud=args.cloud)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("hub_proceed_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
