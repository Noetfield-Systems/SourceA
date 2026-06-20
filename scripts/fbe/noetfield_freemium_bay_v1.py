#!/usr/bin/env python3
"""Noetfield freemium bay — Phase 0 headless acceptance for noetfield-freemium-factory-v1.

Bay slug: noetfield-freemium-bay
Law: data/phase0-freemium-sandbox-reference-v1.json · P0-05 · P0-09 · Q-GATH-04 A
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINA = Path.home() / ".sina"
BAY_SLUG = "noetfield-freemium-bay"
BAY_DIR = ROOT / "receipts" / "bays" / BAY_SLUG
RECEIPT_PATH = SINA / "fbe-noetfield-freemium-run-receipt-v1.json"
FACTORY_ID = "noetfield-freemium-factory-v1"
SPEC_PATH = ROOT / "data" / "factory-specs" / f"{FACTORY_ID}.json"
PN_PATH = ROOT / "data" / "platform-neutral-world-model-v1.json"
CATALOG_PATH = ROOT / "data" / "fbe_catalog_v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _check_p0_05(pn: dict) -> dict:
    routes = pn.get("product_routes") or []
    lane_ok = any(r.get("lane") == "noetfield" for r in routes)
    policy = pn.get("platform_neutral_policy") or {}
    tpl = str(policy.get("stripe_buyer_copy_template") or "")
    mac_free = "mac" not in tpl.lower()
    ok = lane_ok and mac_free and bool(tpl)
    return {
        "label": "P0-05",
        "ok": ok,
        "lane_ok": lane_ok,
        "mac_free_copy": mac_free,
        "note": "noetfield route + platform-neutral copy" if ok else "route or Mac-only framing",
    }


def _check_p0_09(pn: dict) -> dict:
    policy = pn.get("platform_neutral_policy") or {}
    tpl = str(policy.get("stripe_buyer_copy_template") or "")
    billing = policy.get("stripe_billing") or {}
    ok = (
        bool(tpl)
        and "mac" not in tpl.lower()
        and billing.get("statement_descriptor") == "NOETFIELD SYSTEMS"
        and billing.get("statement_descriptor_short") == "NFS"
    )
    return {
        "label": "P0-09",
        "ok": ok,
        "descriptor": billing.get("statement_descriptor"),
        "descriptor_short": billing.get("statement_descriptor_short"),
        "note": "NFS stripe billing SSOT" if ok else "buyer copy or NFS descriptor missing",
    }


def _check_catalog(cat: dict) -> dict:
    row = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-noetfield-freemium"), None)
    ok = bool(
        row
        and row.get("factory_id") == FACTORY_ID
        and row.get("status") == "mock_only"
        and row.get("demo_seconds")
    )
    return {
        "label": "catalog",
        "ok": ok,
        "catalog_id": "cat-noetfield-freemium",
        "note": "cat-noetfield-freemium mock_only" if ok else "catalog row missing or not mock_only",
    }


def _check_spec() -> dict:
    spec = _read(SPEC_PATH)
    bay_slug = (spec.get("runtime") or {}).get("bay_slug")
    ok = bool(spec.get("factory_id") == FACTORY_ID and bay_slug == BAY_SLUG and SPEC_PATH.is_file())
    return {
        "label": "spec",
        "ok": ok,
        "bay_slug": bay_slug,
        "spec_path": str(SPEC_PATH.relative_to(ROOT)),
        "note": "factory spec + bay_slug match" if ok else "spec missing or bay_slug mismatch",
    }


def run_bay(*, upgrade_id: str = "P0-13", work_order_id: str = "") -> dict:
    pn = _read(PN_PATH)
    cat = _read(CATALOG_PATH)
    checks = [
        _check_p0_05(pn),
        _check_p0_09(pn),
        _check_catalog(cat),
        _check_spec(),
    ]
    gate_ok = all(c["ok"] for c in checks)
    wired = [
        "data/platform-neutral-world-model-v1.json",
        "data/fbe_catalog_v1.json",
        str(SPEC_PATH.relative_to(ROOT)),
        "scripts/fbe/noetfield_freemium_bay_v1.py",
    ]

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
                "schema": "fbe-noetfield-freemium-verify-v1",
                "ok": gate_ok,
                "upgrade_id": upgrade_id,
                "factory_id": FACTORY_ID,
                "bay_slug": BAY_SLUG,
                "wired_to": "phase0_noetfield · Q-GATH-04 A",
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
        "schema": "fbe-noetfield-freemium-run-receipt-v1",
        "ok": gate_ok,
        "at": _now(),
        "bay_slug": BAY_SLUG,
        "factory_id": FACTORY_ID,
        "upgrade_id": upgrade_id,
        "work_order_id": work_order_id,
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "wired": wired,
        "checks": checks,
        "verify_path": str(verify_path.relative_to(ROOT)),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Noetfield freemium Phase 0 headless bay")
    ap.add_argument("--upgrade-id", default="P0-13")
    ap.add_argument("--work-order-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_bay(upgrade_id=args.upgrade_id, work_order_id=args.work_order_id)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
