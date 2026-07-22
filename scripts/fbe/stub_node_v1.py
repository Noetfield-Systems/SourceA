#!/usr/bin/env python3
"""FBE W0 stub node — structural PASS receipt on disk."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINA = Path.home() / ".sina"
STUBS = SINA / "fbe-stubs"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    ap = argparse.ArgumentParser(description="FBE stub node W0")
    ap.add_argument("--node", required=True)
    ap.add_argument("--line", default="refinery")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    STUBS.mkdir(parents=True, exist_ok=True)
    safe = args.node.replace("/", "_")
    receipt_path = STUBS / f"{safe}-v1.json"
    row = {
        "schema": "fbe-stub-node-receipt-v1",
        "ok": True,
        "at": _now(),
        "node_id": args.node,
        "line": args.line,
        "mode": "w0_stub",
        "deliveryMode": "prove_only",
        "note": "W0 structural stub — cloud execution W1+",
    }
    receipt_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
