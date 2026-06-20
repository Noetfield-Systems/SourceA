#!/usr/bin/env python3
"""Outbound FDG+ICP bay — headless execution for icp4_one_product_line upgrades (U029+).

Bay slug: outbound-fdg-icp
Law: data/outbound-factory-100-upgrade-plan-v1.json · docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINA = Path.home() / ".sina"
BAY_SLUG = "outbound-fdg-icp"
BAY_DIR = ROOT / "receipts" / "bays" / BAY_SLUG
RECEIPT_PATH = SINA / "fbe-outbound-fdg-icp-run-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sample_bodies() -> list[tuple[str, str]]:
    """Compile-time samples — single-product bodies must PASS; two-para must FAIL."""
    return [
        ("single_product", "Hi — quick note on Noetfield.\n\nNoetfield helps teams ship controlled outbound."),
        ("two_product", "Noetfield helps teams ship controlled outbound.\n\nTrustField adds verification layer."),
    ]


def run_bay(*, upgrade_id: str = "U029", work_order_id: str = "") -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from icp_one_product_line_gate_v1 import check_one_product_line  # noqa: WPS433

    checks: list[dict] = []
    for label, body in _sample_bodies():
        row = check_one_product_line(body)
        expect_ok = label == "single_product"
        checks.append(
            {
                "label": label,
                "ok": bool(row.get("ok")) == expect_ok,
                "gate": row,
                "expect_ok": expect_ok,
            }
        )

    wired = [
        "scripts/icp_one_product_line_gate_v1.py",
        "scripts/icp_output_compiler_v1.py",
        "scripts/best_loop_oqg_score_v1.py",
    ]
    gate_ok = all(c["ok"] for c in checks)
    BAY_DIR.mkdir(parents=True, exist_ok=True)
    ledger = BAY_DIR / "ledger.jsonl"
    ledger_line = json.dumps(
        {
            "at": _now(),
            "upgrade_id": upgrade_id,
            "work_order_id": work_order_id,
            "gate_ok": gate_ok,
            "checks": len(checks),
        }
    )
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(ledger_line + "\n")

    verify_path = BAY_DIR / "verify.json"
    verify_path.write_text(
        json.dumps(
            {
                "schema": "fbe-outbound-fdg-icp-verify-v1",
                "ok": gate_ok,
                "upgrade_id": upgrade_id,
                "wired_to": "icp4_one_product_line",
                "checks": checks,
                "wired": wired,
                "at": _now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    row = {
        "schema": "fbe-outbound-fdg-icp-run-receipt-v1",
        "ok": gate_ok,
        "at": _now(),
        "bay_slug": BAY_SLUG,
        "upgrade_id": upgrade_id,
        "work_order_id": work_order_id,
        "execution_plane": "headless_w2",
        "wired": wired,
        "checks": checks,
        "verify_path": str(verify_path.relative_to(ROOT)),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound FDG+ICP headless bay")
    ap.add_argument("--upgrade-id", default="U029")
    ap.add_argument("--work-order-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_bay(upgrade_id=args.upgrade_id, work_order_id=args.work_order_id)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
