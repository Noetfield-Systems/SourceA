#!/usr/bin/env python3
"""Portfolio volume gate — W3_FIRST_QUEUE routing + L5 defer law."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
W3_QUEUE = Path("/Users/sinakazemnezhad/Desktop/1 PAGER/portfolio-300-locked/W3_FIRST_QUEUE.yaml")
PULSE = SINA / "portfolio-volume-gate-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def run_gate(*, write: bool = True) -> dict:
    outbound = _read_json(SINA / "outbound-factory-upgrade-pulse-v1.json")
    volume = outbound.get("volume_gate") or {}
    comm = _read_json(SINA / "commercial-command-pulse-v1.json")
    w3_exists = W3_QUEUE.is_file()

    row = {
        "schema": "portfolio-volume-gate-v1",
        "at": _now(),
        "law": "portfolio-300 only via W3_FIRST_QUEUE — no pick from 300 without W3 queue",
        "w3_first_queue": str(W3_QUEUE) if w3_exists else None,
        "volume_gate": volume,
        "l3_ready_pct": comm.get("l3_ready_pct"),
        "volume_unlocked": bool(volume.get("ready")),
        "defer_bulk_until": volume.get("gate"),
        "pulse_line": (
            f"portfolio-vol · L5 {volume.get('status', 'deferred')} · "
            f"confirm_sent={volume.get('confirm_sent_count', 0)} · "
            f"W3_FIRST={'OK' if w3_exists else 'MISSING'}"
        ),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Portfolio volume gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_gate(write=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("pulse_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
