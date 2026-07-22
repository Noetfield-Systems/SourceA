#!/usr/bin/env python3
"""TrustField freemium sandbox bay — Phase 0 validate-only for sandbox-mock-factory-v1.

Bay slug: sandbox-bay · compile order: NF attract → TF shadow sandbox reference
Law: data/phase0-freemium-sandbox-reference-v1.json · P0-01 · P0-02
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINA = Path.home() / ".sina"
BAY_SLUG = "sandbox-bay"
BAY_DIR = ROOT / "receipts" / "bays" / BAY_SLUG
FACTORY_ID = "sandbox-mock-factory-v1"
SPEC_PATH = ROOT / "data" / "factory-specs" / f"{FACTORY_ID}.json"
CATALOG_PATH = ROOT / "data" / "fbe_catalog_v1.json"
PN_PATH = ROOT / "data" / "platform-neutral-world-model-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _check_spec() -> dict:
    spec = _read(SPEC_PATH)
    runtime = spec.get("runtime") or {}
    ok = (
        spec.get("factory_id") == FACTORY_ID
        and runtime.get("bay_slug") == BAY_SLUG
        and runtime.get("execution_mode") == "CLOUD_ONLY"
        and runtime.get("cloud_entry") == "--validate-only"
    )
    return {"label": "spec", "ok": ok, "note": "CLOUD_ONLY validate-only sandbox spec" if ok else "spec mismatch"}


def _check_catalog(cat: dict) -> dict:
    row = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-sandbox-demo"), None)
    ok = bool(row and row.get("factory_id") == FACTORY_ID and row.get("status") == "mock_only")
    return {"label": "catalog", "ok": ok, "catalog_id": "cat-sandbox-demo", "note": "mock_only demo" if ok else "catalog row missing"}


def _check_trustfield_lane(pn: dict) -> dict:
    routes = pn.get("product_routes") or []
    ok = any(r.get("lane") == "trustfield" for r in routes)
    return {"label": "trustfield_lane", "ok": ok, "note": "TrustField product route on disk" if ok else "missing trustfield lane"}


def _check_compile_order() -> dict:
    nf = SINA / "fbe-noetfield-freemium-run-receipt-v1.json"
    ok = nf.is_file() and _read(nf).get("ok")
    return {"label": "compile_order", "ok": ok, "note": "NF bay PASS before TF sandbox" if ok else "NF attract receipt missing"}


def run_bay(*, work_order_id: str = "") -> dict:
    checks = [
        _check_spec(),
        _check_catalog(_read(CATALOG_PATH)),
        _check_trustfield_lane(_read(PN_PATH)),
        _check_compile_order(),
    ]
    gate_ok = all(c["ok"] for c in checks)
    BAY_DIR.mkdir(parents=True, exist_ok=True)
    verify_path = BAY_DIR / "verify.json"
    verify_path.write_text(
        json.dumps(
            {
                "schema": "fbe-trustfield-sandbox-verify-v1",
                "ok": gate_ok,
                "factory_id": FACTORY_ID,
                "bay_slug": BAY_SLUG,
                "checks": checks,
                "at": _now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    row = {
        "schema": "fbe-trustfield-sandbox-run-receipt-v1",
        "ok": gate_ok,
        "at": _now(),
        "bay_slug": BAY_SLUG,
        "factory_id": FACTORY_ID,
        "work_order_id": work_order_id,
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "cloud_stub": False,
        "validate_only": True,
        "checks": checks,
        "verify_path": str(verify_path.relative_to(ROOT)),
    }
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-order-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_bay(work_order_id=args.work_order_id)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
