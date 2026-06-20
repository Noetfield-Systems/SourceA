#!/usr/bin/env python3
"""Brand route forbid bleed checker — per-body lane isolation (U027).

Acceptance: NF body mentioning TrustField = fail (unless explicit separation context).
Wired to: icp_output_compiler_v1 · best_loop_oqg_score_v1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brand-route-forbid-bleed-receipt-v1.json"

# Explicit separation phrases that allow cross-brand mention
SEPARATION_CTX = re.compile(
    r"\b(separate|not the same|different (brand|lane|thread)|never blend|one brand per)\b",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_bleed(*, body: str, lane: str) -> dict:
    """Return pass/fail + issues for a single email body."""
    t = (body or "").lower()
    lane_norm = str(lane or "").strip()
    issues: list[str] = []

    if lane_norm in ("Noetfield", "noetfield", "NF"):
        if "trustfield" in t and not SEPARATION_CTX.search(body or ""):
            issues.append("trustfield_bleed_nf")
        if "fintrac kyb pack" in t and "not " not in t:
            issues.append("fintrac_kyb_claim_nf")
    elif lane_norm in ("TrustField", "trustfield", "TF"):
        if "noetfield" in t and not SEPARATION_CTX.search(body or ""):
            issues.append("noetfield_bleed_tf")
        if "nf-rd" in t or "copilot governance receipt" in t:
            issues.append("nf_vocabulary_in_tf")
    elif lane_norm in ("SourceA", "fbe_sourcea", "sourcea-factory", "sourcea"):
        if "noetfield" in t and "trustfield" in t and not SEPARATION_CTX.search(body or ""):
            issues.append("dual_brand_bleed_sa")
        if "nf-rd" in t and "tf-kyb" in t:
            issues.append("sku_cross_bleed_sa")

    return {
        "ok": len(issues) == 0,
        "lane": lane_norm,
        "issues": issues,
        "hard_fail": len(issues) > 0,
    }


def check_account_pack(account_id: str, *, lane: str) -> dict:
    """Load pack body from icp-compile or outbound dir."""
    compile_dir = ROOT / "data" / "icp-compile"
    body = ""
    source = ""
    for name in (f"{account_id}-approved-v1.txt", f"{account_id}-v1.json"):
        p = compile_dir / name
        if p.is_file():
            if name.endswith(".txt"):
                body = p.read_text(encoding="utf-8")
            else:
                row = json.loads(p.read_text(encoding="utf-8"))
                body = str(row.get("body") or row.get("approved_body") or "")
            source = str(p)
            break
    if not body:
        pack = SINA / "outbound" / f"w3-canada-{account_id}" / "body.txt"
        if pack.is_file():
            body = pack.read_text(encoding="utf-8")
            source = str(pack)
    result = check_bleed(body=body, lane=lane)
    result["account_id"] = account_id
    result["source"] = source
    return result


def run_fleet_check() -> dict:
    accounts = [
        ("fundmore", "Noetfield"),
        ("ocree", "TrustField"),
    ]
    rows = [check_account_pack(aid, lane=lane) for aid, lane in accounts]
    ok = all(r.get("ok") for r in rows)
    return {
        "schema": "brand-route-forbid-bleed-receipt-v1",
        "at": _now(),
        "ok": ok,
        "upgrade_id": "U027",
        "accounts": rows,
        "line": f"brand-bleed · {'PASS' if ok else 'FAIL'} · {sum(1 for r in rows if r.get('ok'))}/{len(rows)} clean",
    }


def validate_brand_bleed_acceptance() -> dict:
    """U027 acceptance — NF body mentioning TrustField = fail."""
    nf_fail = check_bleed(body="We rely on TrustField for examiner replay.", lane="noetfield")
    nf_pass = check_bleed(body="Noetfield replay under mortgage board pressure.", lane="noetfield")
    fleet = run_fleet_check()
    acceptance_ok = (
        not nf_fail.get("ok")
        and "trustfield_bleed_nf" in (nf_fail.get("issues") or [])
        and nf_pass.get("ok")
        and fleet.get("ok")
    )
    return {
        "ok": acceptance_ok,
        "nf_trustfield_mention": nf_fail,
        "nf_clean": nf_pass,
        "fleet": fleet,
        "acceptance": "NF body mentioning TrustField = fail",
        "upgrade": "U027",
        "check": "python3 scripts/brand_route_forbid_bleed_v1.py --check-acceptance --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Brand route forbid bleed checker (U027)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--body", help="Raw body text to check")
    ap.add_argument("--lane", default="Noetfield")
    ap.add_argument("--fleet", action="store_true")
    ap.add_argument("--check-acceptance", action="store_true", help="U027 — NF body mentioning TrustField = fail")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if args.check_acceptance:
        row = validate_brand_bleed_acceptance()
        if args.write:
            SINA.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(row.get("fleet") or row, indent=2) + "\n", encoding="utf-8")
    elif args.fleet:
        row = run_fleet_check()
        if args.write:
            SINA.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    elif args.body:
        row = check_bleed(body=args.body, lane=args.lane)
    else:
        row = run_fleet_check()
        if args.write:
            SINA.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line", "done"))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
