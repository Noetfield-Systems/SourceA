#!/usr/bin/env python3
"""FBE exchange verify — W4 Factory 2 proof."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
VERIFY_PATH = SINA / "fbe-exchange-verify-receipt-v1.json"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify(*, bay_slug: str = "trustfield-bay") -> dict:
    checks: list[dict] = []
    ok = True

    run_r = {}
    run_path = SINA / "fbe-exchange-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    checks.append({
        "id": "exchange_runner",
        "ok": bool(run_r.get("ok")),
        "steps_executed": run_r.get("steps_executed"),
        "steps_total": run_r.get("steps_total"),
    })
    if not run_r.get("ok"):
        ok = False

    ref_ledger = ROOT / "receipts" / "bays" / bay_slug / "refinery" / "ledger.jsonl"
    ref_lines = []
    if ref_ledger.is_file():
        ref_lines = [ln for ln in ref_ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    ref_ok = len(ref_lines) >= 6
    checks.append({"id": "exchange_refinery_ledger", "ok": ref_ok, "lines": len(ref_lines), "expected": 6})
    if not ref_ok:
        ok = False

    asm_ledger = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "ledger.jsonl"
    asm_lines = []
    if asm_ledger.is_file():
        asm_lines = [ln for ln in asm_ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    asm_ok = len(asm_lines) >= 7
    checks.append({"id": "exchange_assembly_ledger", "ok": asm_ok, "lines": len(asm_lines), "expected": 7})
    if not asm_ok:
        ok = False

    voice = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "exchange-voice-perimeter-v1-v1.json"
    checks.append({"id": "voice_perimeter_stub", "ok": voice.is_file(), "path": str(voice)})

    dealer = ROOT / "receipts" / "bays" / bay_slug / "refinery" / "exchange-dealer-bridge-v1-v1.json"
    dealer_data = {}
    if dealer.is_file():
        dealer_data = json.loads(dealer.read_text(encoding="utf-8"))
    platinum_eligible = bool(dealer_data.get("platinum_eligible"))
    checks.append({
        "id": "dealer_bridge",
        "ok": dealer.is_file(),
        "platinum_eligible": platinum_eligible,
        "dealer_score": dealer_data.get("dealer_score"),
    })

    row = {
        "schema": "fbe-exchange-verify-v1",
        "ok": ok,
        "at": _now(),
        "wave": "W4",
        "bay_slug": bay_slug,
        "template_id": "exchange-factory-v1",
        "factory_id": "factory_2",
        "mode": "headless",
        "deliveryMode": "prove_only",
        "checks": checks,
        "proof": "exchange_verify PASS" if ok else "exchange_verify FAIL",
        "tier_target": "PLATINUM",
        "tier_achieved": "PLATINUM" if (ok and platinum_eligible) else ("GOLD" if ok else "BRONZE"),
        "w4_honest_cap": "GOLD",
        "w6_note": "PLATINUM when CREED dealer 15/15 + verify-16-steps PASS",
        "execution_plane": "headless_w4",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    (ROOT / "receipts" / "exchange-verify-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="trustfield-bay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify(bay_slug=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
