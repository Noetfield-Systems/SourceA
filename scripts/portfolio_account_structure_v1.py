#!/usr/bin/env python3
"""Portfolio account structure — SSOT sync to receipt + surfaces (always in reports).

Law: data/portfolio-account-structure-v1.json
Receipt: ~/.sina/portfolio-account-structure-v1.json
Surfaces: portfolio_account_structure_line
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "portfolio-account-structure-v1.json"
RECEIPT = SINA / "portfolio-account-structure-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
MAIL_SSOT = SINA / "commercial-mail-from-ssot-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _lane_summary(lane: dict) -> str:
    lid = str(lane.get("id") or "")
    gmails = lane.get("gmail_logins") or []
    short = gmails[0].split("@")[0] if gmails else lid
    if len(gmails) > 1 and lid == "main_lane":
        return "main=kazemnezhadsina144+sinakazemnezhad.ca"
    if lid == "witnessbc_lane":
        return "wbc=witness.bc"
    return f"{lid}={short}"


def _send_from_summary(ssot: dict) -> str:
    parts: list[str] = []
    for lane in ssot.get("lanes") or []:
        lid = str(lane.get("id") or "lane")
        tag = "wbc" if lid == "witnessbc_lane" else "main"
        for row in lane.get("official_send_from") or []:
            addr = str(row.get("address") or "")
            brand = str(row.get("brand") or tag)
            if addr:
                parts.append(f"{brand.lower().replace(' ', '')}:{addr}")
    return ",".join(parts[:8]) if parts else "unknown"


def compose_line(ssot: dict, *, mail_ssot: dict | None = None) -> str:
    lanes = ssot.get("lanes") or []
    parts = [_lane_summary(ln) for ln in lanes[:2]]
    send = _send_from_summary(ssot)
    line = f"accounts · {' · '.join(parts)} · send={send}"
    if mail_ssot:
        confirmed = bool(mail_ssot.get("founder_confirmed"))
        accts = mail_ssot.get("accounts") or []
        configured = sum(1 for a in accts if a.get("configured"))
        total = len(accts)
        if total:
            line += f" · mail-from {configured}/{total}{'✓' if confirmed else ''}"
    return line


def build_report(*, mail_ssot: dict | None = None) -> dict:
    ssot = _read(SSOT)
    if not ssot:
        return {
            "schema": "portfolio-account-structure-v1",
            "at": _now(),
            "ok": False,
            "error": f"missing SSOT: {SSOT}",
            "portfolio_account_structure_line": "accounts · RED · ssot-missing",
        }
    line = compose_line(ssot, mail_ssot=mail_ssot or _read(MAIL_SSOT))
    lanes_out = []
    for lane in ssot.get("lanes") or []:
        lanes_out.append(
            {
                "id": lane.get("id"),
                "label": lane.get("label"),
                "gmail_logins": lane.get("gmail_logins"),
                "chrome_profile": lane.get("chrome_profile"),
                "modules": lane.get("modules"),
                "official_send_from": [r.get("address") for r in lane.get("official_send_from") or []],
            }
        )
    return {
        "schema": "portfolio-account-structure-v1",
        "at": _now(),
        "ok": True,
        "portfolio_account_structure_line": line,
        "one_law": ssot.get("one_law"),
        "lanes": lanes_out,
        "forbidden_cross_lane": ssot.get("forbidden_cross_lane"),
        "known_drift": ssot.get("known_drift"),
        "ssot": str(SSOT.relative_to(ROOT)),
        "human_doc": ssot.get("human_doc"),
    }


def wire(*, mail_ssot: dict | None = None) -> dict:
    row = build_report(mail_ssot=mail_ssot)
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    surfaces = _read(SURFACES)
    line = str(row.get("portfolio_account_structure_line") or "")
    surfaces["portfolio_account_structure_line"] = line
    surfaces["portfolio_account_structure"] = {
        "ok": bool(row.get("ok")),
        "at": row.get("at"),
        "receipt": str(RECEIPT),
        "ssot": str(SSOT),
    }
    SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--wire", action="store_true", help="Write receipt + surfaces line")
    args = ap.parse_args()
    row = wire() if args.wire else build_report()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("portfolio_account_structure_line") or row)
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
