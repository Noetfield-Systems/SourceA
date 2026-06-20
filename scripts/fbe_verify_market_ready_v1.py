#!/usr/bin/env python3
"""FBE market ready verify — honest tier_achieved from quality contract (W6 lift)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
DATA = ROOT / "data"
CONTRACT_PATH = DATA / "fbe_quality_contract_v1.json"
VERIFY_PATH = SINA / "fbe-market-ready-verify-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _expand(rel: str) -> Path:
    p = Path(rel.replace("~", str(Path.home())))
    return p if p.is_absolute() else ROOT / p


def verify(*, bay_slug: str = "sample-bay") -> dict:
    contract = _read_json(CONTRACT_PATH)
    checks: list[dict] = []
    ok = True

    refinery_v = _read_json(SINA / "fbe-refinery-verify-receipt-v1.json")
    assembly_v = _read_json(SINA / "fbe-assembly-verify-receipt-v1.json")
    refinery_pass = refinery_v.get("proof") == "refinery_verify PASS"
    assembly_pass = assembly_v.get("proof") == "assembly_verify PASS"
    checks.append({"id": "refinery_verify", "ok": refinery_pass})
    checks.append({"id": "assembly_verify", "ok": assembly_pass})

    ledger = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "ledger.jsonl"
    ledger_lines = 0
    if ledger.is_file():
        ledger_lines = len([ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()])
    min_lines = 22
    for chk in contract.get("market_ready_checks") or []:
        if chk.get("id") == "assembly_ledger":
            min_lines = int(chk.get("min_lines") or 22)
    ledger_ok = ledger_lines >= min_lines
    checks.append({"id": "assembly_ledger", "ok": ledger_ok, "lines": ledger_lines, "min_lines": min_lines})

    live_smoke_path = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "church-live-smoke-v1-v1.json"
    live_smoke = _read_json(live_smoke_path)
    live_smoke_npm = live_smoke.get("mode") == "w6_church_npm" and bool(live_smoke.get("ok"))
    checks.append({
        "id": "church_live_smoke",
        "ok": live_smoke_path.is_file() and bool(live_smoke.get("ok")),
        "mode": live_smoke.get("mode"),
        "npm_pass": live_smoke_npm,
    })

    for chk in contract.get("market_ready_checks") or []:
        if chk.get("required") is False:
            checks.append({"id": chk.get("id"), "ok": True, "deferred": True})
            continue
        if chk.get("id") in ("assembly_ledger", "church_live_smoke"):
            continue
        path = chk.get("path") or chk.get("source") or ""
        if path:
            p = _expand(path)
            exists = p.is_file()
            field_ok = True
            if exists and chk.get("field"):
                data = _read_json(p)
                field_ok = bool(data.get(chk["field"]))
            checks.append({"id": chk.get("id"), "ok": exists and field_ok, "path": str(p)})

    wired_pass = refinery_pass and assembly_pass and ledger_ok
    tier_achieved = "BRONZE"
    if wired_pass:
        tier_achieved = contract.get("w6_honest_cap") or contract.get("w3_honest_cap") or "GOLD+assembly_wired"
    elif refinery_pass:
        tier_achieved = contract.get("w2_honest_cap") or "GOLD"

    if wired_pass and live_smoke_npm:
        tier_achieved = "MARKET_READY"

    proof = "market_ready_verify PASS" if wired_pass else "market_ready_verify DEFERRED"
    row = {
        "schema": "fbe-market-ready-verify-v1",
        "ok": wired_pass,
        "at": _now(),
        "wave": "W6" if ledger_lines >= 22 else "W3",
        "bay_slug": bay_slug,
        "tier_target": contract.get("tier_target") or "MARKET_READY",
        "tier_achieved": tier_achieved,
        "w3_honest_cap": contract.get("w3_honest_cap"),
        "w6_honest_cap": contract.get("w6_honest_cap"),
        "checks": checks,
        "proof": proof,
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w6" if ledger_lines >= 22 else "headless_w3",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify(bay_slug=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
