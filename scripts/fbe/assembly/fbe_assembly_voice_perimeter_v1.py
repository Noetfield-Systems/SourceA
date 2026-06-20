#!/usr/bin/env python3
"""MSB voice perimeter gate — structural stub until CHURCH wires check:voice-perimeter."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "assembly"))
from fbe_assembly_lib_v1 import append_ledger, write_receipt  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_voice_perimeter(*, bay_slug: str, tenant: str) -> dict:
    node_id = "exchange-voice-perimeter-v1"
    row = {
        "schema": "fbe-assembly-step-receipt-v1",
        "ok": True,
        "at": _now(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "mode": "msb_advisory_stub",
        "deliveryMode": "prove_only",
        "note": "MSB advisory perimeter — structural PASS until CHURCH check:voice-perimeter wired",
    }
    write_receipt(bay_slug, node_id, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": True, "mode": "stub"})
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="trustfield-bay")
    ap.add_argument("--tenant", default="trustfield")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_voice_perimeter(bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
