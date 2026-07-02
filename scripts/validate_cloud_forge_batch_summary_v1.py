#!/usr/bin/env python3
"""Validate batch summary cloud_sec_range against actual plan IDs — fail closed."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLOUD_RE = re.compile(r"CLOUD-SEC-(\d+)")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cloud_num(plan_id: str) -> int | None:
    m = CLOUD_RE.search(str(plan_id or ""))
    return int(m.group(1)) if m else None


def validate_batch_doc(doc: dict[str, Any]) -> dict[str, Any]:
    plans = doc.get("plans") or []
    cloud_ids = sorted(n for p in plans if (n := _cloud_num(str(p.get("id") or ""))) is not None)
    summary = doc.get("summary") or {}
    claimed = str(summary.get("cloud_sec_range") or "")
    m = re.match(r"CLOUD-SEC-(\d+)\.\.CLOUD-SEC-(\d+)", claimed)
    errors: list[str] = []
    if not cloud_ids:
        errors.append("no_cloud_sec_plan_ids")
    if not m:
        errors.append(f"invalid_summary_range:{claimed!r}")
    else:
        lo_claim, hi_claim = int(m.group(1)), int(m.group(2))
        lo_actual, hi_actual = cloud_ids[0], cloud_ids[-1]
        if lo_claim != lo_actual or hi_claim != hi_actual:
            errors.append(
                f"range_mismatch claimed=CLOUD-SEC-{lo_claim:04d}..CLOUD-SEC-{hi_claim:04d} "
                f"actual=CLOUD-SEC-{lo_actual:04d}..CLOUD-SEC-{hi_actual:04d}"
            )
        expected = set(range(lo_actual, hi_actual + 1))
        actual = set(cloud_ids)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            errors.append(f"missing_ids_in_plans:{len(missing)} first={missing[:5]}")
        if extra:
            errors.append(f"extra_ids_in_plans:{len(extra)} first={extra[:5]}")
    return {
        "ok": not errors,
        "schema": "cloud-forge-batch-summary-validate-v1",
        "at": _now(),
        "batch_id": summary.get("batch_id"),
        "claimed_range": claimed,
        "actual_range": f"CLOUD-SEC-{cloud_ids[0]:04d}..CLOUD-SEC-{cloud_ids[-1]:04d}" if cloud_ids else None,
        "cloud_plan_count": len(cloud_ids),
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("batch_json", type=Path, nargs="?", help="Batch JSON path")
    ap.add_argument("--batch-id", type=int, help="Resolve data/secondary-cloud-forge-run-batch-{id}-locked-v1.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    path = args.batch_json
    if path is None and args.batch_id is not None:
        path = ROOT / "data" / f"secondary-cloud-forge-run-batch-{args.batch_id}-locked-v1.json"
    if path is None:
        print("FAIL: provide batch_json or --batch-id", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"FAIL: missing {path}", file=sys.stderr)
        return 2
    doc = json.loads(path.read_text(encoding="utf-8"))
    row = validate_batch_doc(doc)
    row["path"] = str(path)
    if args.json:
        print(json.dumps(row, indent=2))
    elif row["ok"]:
        print(f"PASS batch-summary-validate {row.get('claimed_range')} · {row['cloud_plan_count']} ids")
    else:
        print(f"FAIL batch-summary-validate {path.name}: {row['errors']}", file=sys.stderr)
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
