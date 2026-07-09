#!/usr/bin/env python3
"""Pulse SourceA.app W2 — site-score-1000 slice-01 progress."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = Path.home() / ".sina" / "sourcea-site-score-w2-pulse-receipt-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_site_score_w2_plan_v1 import pulse_w2  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = pulse_w2(sync_registry=True)
    receipt = {"schema": "sourcea-site-score-w2-pulse-receipt-v1", "at": _now(), **row}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    surfaces = Path.home() / ".sina" / "agent-live-surfaces-v1.json"
    if surfaces.is_file() and row.get("ok"):
        surf = json.loads(surfaces.read_text(encoding="utf-8"))
        surf["sourcea_site_w2_line"] = row.get("line")
        surf["sourcea_site_w2_head"] = row.get("head_id")
        surfaces.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(row.get("line", row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
