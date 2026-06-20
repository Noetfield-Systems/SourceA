#!/usr/bin/env python3
"""WitnessBC Proof Lab bay — Phase 0 validate-only (sandbox + Noetfield pattern).

Bay slug: witnessbc-proof-lab-bay
Law: data/witnessbc-proof-lab-v1.json · P0-03 · P0-08 · STYLE-B1
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINA = Path.home() / ".sina"
BAY_SLUG = "witnessbc-proof-lab-bay"
BAY_DIR = ROOT / "receipts" / "bays" / BAY_SLUG
FACTORY_ID = "witnessbc-proof-lab-factory-v1"
SPEC_PATH = ROOT / "data" / "factory-specs" / f"{FACTORY_ID}.json"
SSOT_PATH = ROOT / "data" / "witnessbc-proof-lab-v1.json"
CATALOG_PATH = ROOT / "data" / "fbe_catalog_v1.json"
ROUTING_PATH = ROOT / "data" / "commercial-film-routing-v1.json"


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
    )
    return {"label": "spec", "ok": ok, "note": "proof lab factory spec" if ok else "spec mismatch"}


def _check_catalog(cat: dict) -> dict:
    row = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-witnessbc-proof-lab"), None)
    ok = bool(row and row.get("factory_id") == FACTORY_ID and row.get("demo_seconds"))
    return {
        "label": "catalog",
        "ok": ok,
        "catalog_id": "cat-witnessbc-proof-lab",
        "note": "proof lab catalog row" if ok else "catalog missing",
    }


def _check_proof_scenarios() -> dict:
    path = ROOT / "witnessbc-site" / "data" / "proof-scenarios-v1.json"
    data = _read(path)
    scenarios = data.get("scenarios") or []
    has_tamper = any("tamper" in str(s.get("id") or "").lower() for s in scenarios)
    ok = len(scenarios) >= 6 and has_tamper
    return {
        "label": "proof_scenarios",
        "ok": ok,
        "count": len(scenarios),
        "note": "6+ scenarios incl tamper" if ok else "proof scenarios incomplete",
    }


def _check_film_routing(routing: dict) -> dict:
    beats = (routing.get("beats_index") or {}).get("witnessbc_tier_A_hero")
    ok = bool(beats) and (ROOT / str(beats)).is_file()
    return {"label": "style_b1_beats", "ok": ok, "beats": beats, "note": "STYLE-B1 beats on disk" if ok else "beats missing"}


def _check_w1_asset() -> dict:
    mp4 = ROOT / "witnessbc-site" / "assets" / "w1-demo.mp4"
    ok = mp4.is_file() and mp4.stat().st_size > 1_000_000
    return {"label": "w1_demo_film", "ok": ok, "path": str(mp4.relative_to(ROOT)), "note": "W1 embed asset" if ok else "w1-demo.mp4 missing"}


def _check_sandbox_pattern(cat: dict) -> dict:
    sandbox = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-sandbox-demo"), None)
    nf = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-noetfield-freemium"), None)
    ok = bool(sandbox and sandbox.get("status") == "mock_only" and nf and nf.get("status") == "mock_only")
    return {
        "label": "phase0_pattern",
        "ok": ok,
        "note": "sandbox + noetfield freemium mock_only wired" if ok else "phase0 pattern incomplete",
    }


def run_bay(*, work_order_id: str = "") -> dict:
    cat = _read(CATALOG_PATH)
    routing = _read(ROUTING_PATH)
    checks = [
        _check_spec(),
        _check_catalog(cat),
        _check_proof_scenarios(),
        _check_film_routing(routing),
        _check_w1_asset(),
        _check_sandbox_pattern(cat),
    ]
    gate_ok = all(c["ok"] for c in checks)
    BAY_DIR.mkdir(parents=True, exist_ok=True)
    verify_path = BAY_DIR / "verify.json"
    verify_path.write_text(
        json.dumps(
            {
                "schema": "fbe-witnessbc-proof-lab-verify-v1",
                "ok": gate_ok,
                "factory_id": FACTORY_ID,
                "bay_slug": BAY_SLUG,
                "wired_to": "P0-03 · P0-08 · STYLE-B1 · sandbox+noetfield pattern",
                "checks": checks,
                "at": _now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    row = {
        "schema": "fbe-witnessbc-proof-lab-run-receipt-v1",
        "ok": gate_ok,
        "at": _now(),
        "bay_slug": BAY_SLUG,
        "factory_id": FACTORY_ID,
        "work_order_id": work_order_id,
        "verify_path": str(verify_path.relative_to(ROOT)),
        "checks": checks,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "fbe-witnessbc-proof-lab-run-receipt-v1.json").write_text(
        json.dumps(row, indent=2) + "\n", encoding="utf-8"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="WitnessBC Proof Lab Phase 0 bay")
    ap.add_argument("--work-order-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_bay(work_order_id=args.work_order_id)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
