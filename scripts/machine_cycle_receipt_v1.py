#!/usr/bin/env python3
"""Roll up all machine loop receipts into one heartbeat (LP-RECEIPT-PROOF)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
LOOPS_SSOT = ROOT / "data" / "machine-process-loops-v1.json"
RECEIPT = ROOT / "receipts" / "proof" / "machine-cycle-latest-v1.json"
PENDING = ROOT / "receipts" / "cloud" / "autorun-pending" / "pending-latest-v1.json"
KAIZEN = ROOT / "receipts" / "cloud" / "kaizen" / "kaizen-pick-latest-v1.json"
RETIREMENT = ROOT / "data" / "founder-trigger-retirement-registry-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def aggregate() -> dict[str, Any]:
    ssot = _read(LOOPS_SSOT)
    loops_out: list[dict[str, Any]] = []
    all_ok = True
    for loop in ssot.get("loops") or []:
        if not isinstance(loop, dict):
            continue
        rpath = ROOT / loop.get("receipt_path", "")
        row = _read(rpath)
        ok = bool(row.get("ok", False)) if row else False
        if not row:
            ok = False
        if not ok:
            all_ok = False
        loops_out.append(
            {
                "loop_id": loop.get("loop_id"),
                "name": loop.get("name"),
                "ok": ok,
                "receipt_path": str(loop.get("receipt_path")),
                "at": row.get("at", ""),
            }
        )

    pending = _read(PENDING)
    retirement = _read(RETIREMENT)
    candidates = [
        t.get("trigger_id")
        for t in retirement.get("triggers") or []
        if isinstance(t, dict)
        and t.get("status") == "active"
        and int(t.get("consecutive_green") or 0) >= int(t.get("green_receipts_required") or 999)
    ]

    doc = {
        "schema": "machine-cycle-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": all_ok,
        "loops": loops_out,
        "founder_blocked_count": int(pending.get("p0_count") or pending.get("count") or 0),
        "kaizen_pick": _read(KAIZEN).get("report_line", ""),
        "retirement_candidates_ready": candidates,
        "report_line": (
            f"machine_cycle PASS · {sum(1 for l in loops_out if l.get('ok'))}/{len(loops_out)} loops green"
            if all_ok
            else f"machine_cycle PARTIAL · {sum(1 for l in loops_out if l.get('ok'))}/{len(loops_out)} loops green"
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "machine-cycle-latest-v1.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = aggregate()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
