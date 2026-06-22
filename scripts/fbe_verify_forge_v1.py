#!/usr/bin/env python3
"""FBE forge verify — W5 Factory 3 proof."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
VERIFY_PATH = SINA / "fbe-forge-verify-receipt-v1.json"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify(*, bay_slug: str = "forge-bay") -> dict:
    headless = os.environ.get("FBE_MODE") == "headless" or os.environ.get("FBE_HOME") == "/app"
    checks: list[dict] = []
    ok = True

    run_r = {}
    run_path = SINA / "fbe-forge-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    checks.append({
        "id": "forge_runner",
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
    ref_ok = len(ref_lines) >= (1 if headless else 3)
    checks.append({"id": "forge_refinery_ledger", "ok": ref_ok, "lines": len(ref_lines), "expected": 1 if headless else 3})
    if not ref_ok:
        ok = False

    asm_ledger = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "ledger.jsonl"
    asm_lines = []
    if asm_ledger.is_file():
        asm_lines = [ln for ln in asm_ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    asm_ok = len(asm_lines) >= (1 if headless else 2)
    checks.append({"id": "forge_assembly_ledger", "ok": asm_ok, "lines": len(asm_lines), "expected": 1 if headless else 2})
    if not asm_ok:
        ok = False

    scaffold = ROOT / "receipts" / "bays" / bay_slug / "refinery" / "forge-scaffold-v1-v1.json"
    checks.append({"id": "scaffold_receipt", "ok": scaffold.is_file(), "path": str(scaffold)})

    inbox_gate = ROOT / "receipts" / "bays" / bay_slug / "refinery" / "forge-inbox-gate-v1-v1.json"
    checks.append({"id": "inbox_gate_receipt", "ok": inbox_gate.is_file(), "path": str(inbox_gate)})

    deploy = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "forge-deploy-pack-v1-v1.json"
    checks.append({"id": "deploy_pack_manifest", "ok": deploy.is_file(), "path": str(deploy)})

    row = {
        "schema": "fbe-forge-verify-v1",
        "ok": ok,
        "at": _now(),
        "wave": "W5",
        "bay_slug": bay_slug,
        "template_id": "forge-app-factory-v1",
        "factory_id": "factory_3",
        "mode": "headless",
        "deliveryMode": "prove_only",
        "checks": checks,
        "proof": "forge_verify PASS" if ok else "forge_verify FAIL",
        "tier_target": "GOLD",
        "tier_achieved": "GOLD" if ok else "BRONZE",
        "proof_class": "G0-G3",
        "w5_honest_cap": "GOLD",
        "w5_note": "Production deploy deferred — prove_only G0-G3 gate",
        "execution_plane": "headless_w5",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    (ROOT / "receipts" / "forge-verify-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="forge-bay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify(bay_slug=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
