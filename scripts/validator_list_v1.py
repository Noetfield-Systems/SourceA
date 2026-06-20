#!/usr/bin/env python3
"""Road map 1→1000 — ordered list, Worker + Broker proof columns (SSOT: monitor_honesty_lib_v1)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
AUDIT_JSON = SINA / "ROADMAP_1000_AUDIT.json"

sys.path.insert(0, str(SCRIPTS))
from monitor_honesty_lib_v1 import audit_monitor  # noqa: E402

# Re-export for callers that imported private helpers
from monitor_honesty_lib_v1 import queue_context as _queue_context  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_list(*, filter_mode: str = "road") -> dict:
    data = audit_monitor(filter_mode=filter_mode)
    data["schema"] = "roadmap-v2-honest"
    data["at"] = _now()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data["audit_csv"] = str(SINA / f"audits/REGISTRY_ALL_1000_VALIDATION_{stamp}.csv")
    return data


def write_audit_snapshot(data: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--filter",
        choices=("road", "all", "queue", "attention", "done"),
        default="road",
    )
    args = p.parse_args()
    filt = "road" if args.filter == "all" else args.filter
    data = build_list(filter_mode=filt)
    write_audit_snapshot(data)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        y = data["you_are_here"]
        prog = data.get("progress") or {}
        print(
            f"roadmap Valid YES {prog.get('valid_yes', '?')}/{data['total']} · "
            f"receipts {data.get('receipt_done', '?')} · "
            f"HERE {y.get('sa_id')} · rows={len(data['rows'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
