#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "sourcea-automation-catalog-v1.json"
RECEIPT_PATH = ROOT / "receipts" / "cloud" / "kaizen" / "kaizen-automation-catalog-miss-latest-v1.json"
TARGET_COVERAGE_PCT = 100


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    items = catalog.get("catalog")
    if not isinstance(items, list) or not items:
        raise SystemExit("catalog must contain a non-empty catalog array")

    required = {"id", "title", "cadence", "kind", "status", "sourcea_target", "workflow_hint"}
    seen: set[str] = set()
    missing_fields: list[dict[str, Any]] = []
    mapped = 0

    for item in items:
        if not isinstance(item, dict):
            raise SystemExit("catalog entries must be objects")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise SystemExit("catalog entries need a stable string id")
        if item_id in seen:
            raise SystemExit(f"duplicate automation id: {item_id}")
        seen.add(item_id)
        missing = sorted(field for field in required if not str(item.get(field, "")).strip())
        if missing:
            missing_fields.append({"id": item_id, "missing": missing})
        else:
            mapped += 1

    coverage_pct = round((mapped / len(items)) * 100, 2)
    return {
        "schema": catalog.get("schema"),
        "version": catalog.get("version"),
        "catalog_size": len(items),
        "mapped_count": mapped,
        "coverage_pct": coverage_pct,
        "missing_fields": missing_fields,
        "pass": coverage_pct >= TARGET_COVERAGE_PCT and not missing_fields,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    catalog = load_catalog()
    report = validate_catalog(catalog)
    report["checked_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    report["threshold_pct"] = TARGET_COVERAGE_PCT

    if args.write_receipt and not report["pass"]:
        write_receipt({
            "schema": "kaizen-automation-catalog-miss-v1",
            "written_at": report["checked_at"],
            "status": "drift",
            "coverage_pct": report["coverage_pct"],
            "threshold_pct": report["threshold_pct"],
            "catalog_size": report["catalog_size"],
            "mapped_count": report["mapped_count"],
            "missing_fields": report["missing_fields"],
        })

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"coverage_pct={report['coverage_pct']}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
