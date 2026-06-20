#!/usr/bin/env python3
"""Minimal FBE motor stub — structural PASS receipt."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_receipt(schema: str, receipt_rel: str, extra: dict | None = None) -> dict:
    receipt_path = Path(receipt_rel.replace("~", str(Path.home())))
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    row = {"schema": schema, "ok": True, "at": _now(), "mode": "w0_structural", "deliveryMode": "prove_only"}
    if extra:
        row.update(extra)
    receipt_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main_schema(schema: str, receipt: str) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = write_receipt(schema, receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(0)
