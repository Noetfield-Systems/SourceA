#!/usr/bin/env python3
"""Disclosure ladder — tiered public voice + outbound audit.

Law: docs/SOURCEA_DISCLOSURE_LADDER_AND_PUBLIC_VOICE_LOCKED_v1.md
SSOT: data/disclosure-ladder-v1.json
Receipt: ~/.sina/disclosure-ladder-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "disclosure-ladder-v1.json"
COMPILE_DIR = ROOT / "data" / "icp-compile"
RECEIPT = SINA / "disclosure-ladder-receipt-v1.json"
ACTIVE_ICP_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory", "forge-product")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read_json(SSOT)


def tier_for_lane(lane: str, *, context: str | None = None) -> str:
    ssot = load_ssot()
    if context == "advisor_pre_call":
        return "T1_advisor"
    key = str(lane or "").strip().lower().replace(" ", "_")
    mapping = ssot.get("lane_tier_map") or {}
    if key in mapping:
        return str(mapping[key])
    for part in (key, key.split("_")[0] if "_" in key else ""):
        if part and part in mapping:
            return str(mapping[part])
    return "T1_icp_buyer"


def _forbidden_for_tier(tier: str, ssot: dict | None = None) -> list[str]:
    ssot = ssot or load_ssot()
    block = ssot.get("forbidden_lead_terms") or {}
    terms: list[str] = []
    for t in (tier, "T1_icp_buyer", "T0_public"):
        terms.extend(block.get(t) or [])
    seen: set[str] = set()
    out: list[str] = []
    for term in terms:
        low = term.lower()
        if low not in seen:
            seen.add(low)
            out.append(term)
    return out


def check_text(text: str, *, tier: str | None = None, lane: str = "", context: str | None = None) -> dict:
    ssot = load_ssot()
    tier_key = tier or tier_for_lane(lane, context=context)
    low = text.lower()
    forbidden_hits: list[str] = []
    for term in _forbidden_for_tier(tier_key, ssot):
        if term.lower() in low:
            forbidden_hits.append(term)

    trans = _read_json(ROOT / "data" / "factory-email-translation-v1.json")
    for term in trans.get("forbidden_in_email_one") or []:
        if term.lower() in low and f"translation:{term}" not in forbidden_hits:
            forbidden_hits.append(f"factory_forbidden:{term}")

    perimeter_any = ssot.get("required_perimeter_phrases_any") or []
    perimeter_soft = ssot.get("perimeter_soft_phrases_any") or [
        "powered by sourcea",
        "advisory only",
        "no custody",
        "no payment initiation",
    ]
    perimeter_ok = any(p.lower() in low for p in perimeter_any + perimeter_soft)

    return {
        "tier": tier_key,
        "lane": lane or None,
        "context": context,
        "forbidden_hits": forbidden_hits,
        "perimeter_ok": perimeter_ok,
        "ok": not forbidden_hits,
    }


def check_outbound_body(
    body: str,
    *,
    lane: str = "w3_commercial",
    context: str | None = None,
    tier: str | None = None,
) -> dict:
    row = check_text(body, lane=lane, context=context, tier=tier)
    hard_fails = [f"disclosure:{h}" for h in row.get("forbidden_hits") or []]
    if not row.get("perimeter_ok") and "Reply **stop**" in body:
        row["perimeter_warning"] = "missing_perimeter_in_footer"
    row["hard_fails"] = hard_fails
    return row


def _body_for_account(account_id: str) -> tuple[str, str]:
    forge_path = COMPILE_DIR / f"{account_id}-v1.json"
    forge = _read_json(forge_path)
    if not forge:
        return "", account_id
    ap = forge.get("approved_body_path")
    if ap:
        p = ROOT / ap
        if p.is_file():
            return p.read_text(encoding="utf-8"), str(ap)
    pack = SINA / "outbound" / f"w3-canada-{account_id}" / "body.txt"
    if pack.is_file():
        return pack.read_text(encoding="utf-8"), str(pack)
    return "", account_id


def audit_icp_fleet(*, accounts: tuple[str, ...] = ACTIVE_ICP_ACCOUNTS) -> list[dict]:
    rows: list[dict] = []
    for account_id in accounts:
        body, src = _body_for_account(account_id)
        if not body.strip():
            rows.append(
                {
                    "account_id": account_id,
                    "source": src,
                    "skipped": True,
                    "ok": True,
                    "reason": "no_body",
                }
            )
            continue
        forge = _read_json(COMPILE_DIR / f"{account_id}-v1.json")
        lane = str(forge.get("brand_route") or forge.get("lane") or "w3_commercial")
        disc = check_outbound_body(
            body,
            lane=lane,
            tier=str(forge.get("disclosure_tier") or "") or None,
        )
        rows.append(
            {
                "account_id": account_id,
                "source": src,
                "lane": lane,
                "tier": disc.get("tier"),
                "ok": disc.get("ok"),
                "perimeter_ok": disc.get("perimeter_ok"),
                "perimeter_warning": disc.get("perimeter_warning"),
                "forbidden_hits": disc.get("forbidden_hits") or [],
                "hard_fails": disc.get("hard_fails") or [],
            }
        )
    return rows


def _disclosure_line(*, icp_rows: list[dict], wired: bool) -> str:
    audited = [r for r in icp_rows if not r.get("skipped")]
    pass_n = sum(1 for r in audited if r.get("ok"))
    total = len(audited) or 0
    icp_part = f"icp={pass_n}/{total} PASS" if total else "icp=—"
    return f"disclosure · {icp_part} · tier=T0–T4 · wired={'YES' if wired else 'NO'}"


def run_tick(*, write: bool = True, audit: bool = True) -> dict:
    ssot = load_ssot()
    icp_rows = audit_icp_fleet() if audit else []
    audited = [r for r in icp_rows if not r.get("skipped")]
    icp_ok = all(r.get("ok") for r in audited) if audited else True

    wired_checks = {
        "ssot": SSOT.is_file(),
        "locked_doc": (ROOT / "docs/SOURCEA_DISCLOSURE_LADDER_AND_PUBLIC_VOICE_LOCKED_v1.md").is_file(),
        "icp_compiler_hook": "disclosure_ladder_v1" in (SCRIPTS / "icp_output_compiler_v1.py").read_text(encoding="utf-8"),
        "disk_live_wire_hook": "disclosure_ladder" in (SCRIPTS / "disk_live_wire_sync_v1.py").read_text(encoding="utf-8"),
    }
    wired = all(wired_checks.values())

    row = {
        "schema": "disclosure-ladder-receipt-v1",
        "ok": icp_ok and wired,
        "at": _now(),
        "law": ssot.get("locked_doc"),
        "one_law": ssot.get("one_law"),
        "public_positioning": ssot.get("public_positioning") or {},
        "audience_one_liners": ssot.get("audience_one_liners") or {},
        "icp_audit": icp_rows,
        "icp_audit_ok": icp_ok,
        "wired_checks": wired_checks,
        "wired": wired,
        "upgrade_ideas": ssot.get("upgrade_ideas") or [],
        "disclosure_line": _disclosure_line(icp_rows=icp_rows, wired=wired),
        "hub_api": "POST /api/disclosure-ladder/tick/v1",
        "command": "python3 scripts/disclosure_ladder_v1.py --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        surfaces_path = SINA / "agent-live-surfaces-v1.json"
        surfaces = _read_json(surfaces_path)
        surfaces["disclosure_line"] = row["disclosure_line"]
        surfaces["disclosure_ladder"] = {
            "receipt": str(RECEIPT),
            "icp_audit_ok": icp_ok,
            "wired": wired,
            "tier_range": "T0–T4",
        }
        surfaces_path.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "disclosure-ladder-receipt-v1":
        row = run_tick(write=True)
    return {
        "schema": "worker-hub-disclosure-ladder-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "disclosure_line": row.get("disclosure_line"),
        "icp_audit_ok": row.get("icp_audit_ok"),
        "wired": row.get("wired"),
        "icp_audit": row.get("icp_audit") or [],
        "public_one_line": (row.get("public_positioning") or {}).get("one_line"),
        "upgrade_ideas": row.get("upgrade_ideas") or [],
        "hub_api": row.get("hub_api"),
    }


def handle_hub_post(body: dict | None = None) -> dict:
    _ = body
    return run_tick(write=True)


def check_disclosure_surfaces() -> dict:
    """Companion check for vocabulary_guard — receipt + live line."""
    row = _read_json(RECEIPT)
    surf = _read_json(SINA / "agent-live-surfaces-v1.json")
    violations: list[str] = []
    if not row or row.get("schema") != "disclosure-ladder-receipt-v1":
        violations.append("disclosure:missing_receipt")
    elif not row.get("wired"):
        violations.append("disclosure:not_fully_wired")
    if not (surf.get("disclosure_line") or "").strip():
        violations.append("disclosure:missing_surfaces_line")
    if row and not row.get("icp_audit_ok"):
        violations.append("disclosure:icp_audit_fail")
    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "disclosure_line": (surf.get("disclosure_line") or "")[:96],
        "surface": "disclosure_ladder",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Disclosure ladder tick + audit")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-text", metavar="PATH", help="Audit a text file at tier T1")
    ap.add_argument("--lane", default="w3_commercial")
    ap.add_argument("--no-audit", action="store_true")
    args = ap.parse_args()

    if args.check_text:
        p = Path(args.check_text)
        body = p.read_text(encoding="utf-8") if p.is_file() else ""
        row = check_outbound_body(body, lane=args.lane)
        if args.json:
            print(json.dumps(row, indent=2, ensure_ascii=False))
        else:
            print(f"ok={row.get('ok')} hits={len(row.get('forbidden_hits') or [])}")
        return 0 if row.get("ok") else 1

    row = run_tick(write=True, audit=not args.no_audit)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("disclosure_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
