#!/usr/bin/env python3
"""FBE motor registry sync — index delegate · federate · adapter paths."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY_PATH = SINA / "fbe-motor-registry-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.receipts_v1 import MOTOR_RECEIPT_PATHS, now_utc, write_json  # noqa: E402


def sync() -> dict:
    row = {
        "schema": "fbe-motor-registry-v1",
        "ok": True,
        "at": now_utc(),
        "wave": "W1",
        "receipt_paths": [{"key": k, "path": p} for k, p in MOTOR_RECEIPT_PATHS],
        "delegate": "scripts/fbe_motor_delegate_v1.py",
        "federate": "scripts/fbe_receipt_federate_v1.py",
        "cloud_adapter": "scripts/fbe/lib/cloud_adapter_v1.py",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    write_json(REGISTRY_PATH, row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sync()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
