#!/usr/bin/env python3
"""Commercial Command pulse — unified founder-facing commercial SSOT.

Unifies: salvage spec · w3-canada-send-approvals · nerve ship_gates · w3_founder_review
Writes: ~/.sina/commercial-command-pulse-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PULSE = SINA / "commercial-command-pulse-v1.json"
APPROVALS = ROOT / "data" / "commercial" / "w3-canada-send-approvals-v1.json"
SALVAGE = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"
DEPOSIT_TARGET_CAD = 2000
PHASE1_DAYS = 30


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _w3_review_artifact(w3_review: dict | None, account_id: str) -> dict:
    """Resolve w3-founder-review artifact — scores live under artifacts[].scores."""
    rev = w3_review or {}
    for art in rev.get("artifacts") or []:
        if str(art.get("account_id") or "") == account_id:
            scores = art.get("scores") or {}
            return {
                "sina_read_score_pct": scores.get("sina_read_score_pct"),
                "sina_read_pending": scores.get("sina_read_pending"),
                "status": art.get("status"),
            }
    legacy = (rev.get("accounts") or {})
    if isinstance(legacy, dict):
        row = legacy.get(account_id) or {}
        if row:
            return row
    if isinstance(legacy, list):
        row = next((r for r in legacy if r.get("id") == account_id), {})
        if row:
            return row
    return {}


def _account_row(account: dict, *, nerve_art: dict | None, w3_review: dict | None) -> dict:
    aid = str(account.get("id") or "")
    art = nerve_art or {}
    rev_row = _w3_review_artifact(w3_review, aid)

    sina_read = rev_row.get("sina_read_score_pct") if rev_row else None
    if sina_read == "PENDING" or sina_read is None:
        sina_read_pct = None
    else:
        try:
            sina_read_pct = int(sina_read)
        except (TypeError, ValueError):
            sina_read_pct = None

    return {
        "id": aid,
        "company": account.get("company"),
        "lane": account.get("lane"),
        "sku": account.get("sku"),
        "pipeline_send_slot": account.get("pipeline_send_slot"),
        "compile_order": account.get("compile_order"),
        "oqg_pct": art.get("output_clean_now") or art.get("output_clean_pct"),
        "oqg_pass": bool(art.get("oqg_pass")),
        "rrl_pass": bool(art.get("rrl_pass")),
        "sina_read_pct": sina_read_pct,
        "sina_read_pass": bool(sina_read_pct and sina_read_pct >= 90),
        "confirm_sent": bool(account.get("confirm_sent_at") or account.get("sent_at")),
        "blockers": _blockers(account, art, sina_read_pct),
    }


def _blockers(account: dict, art: dict, sina_read_pct: int | None) -> list[str]:
    blockers: list[str] = []
    if not art.get("oqg_pass"):
        blockers.append("oqg")
    if sina_read_pct is None:
        blockers.append("sina_read_pending")
    elif sina_read_pct < 90:
        blockers.append("sina_read_below_90")
    if not account.get("confirm_sent_at") and not account.get("sent_at"):
        blockers.append("confirm_sent")
    return blockers


def run_pulse(*, write: bool = True) -> dict:
    approvals = _read_json(APPROVALS)
    salvage = _read_json(SALVAGE)
    nerve = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    ship = nerve.get("ship_gates") or {}
    w3_review = _read_json(SINA / "w3-founder-review-v1.json")

    art_by_id = {str(a.get("account_id") or ""): a for a in (ship.get("w3_artifacts") or [])}

    commercial_accounts = [a for a in (approvals.get("accounts") or []) if a.get("compile_order") == 1]
    account_rows = [
        _account_row(a, nerve_art=art_by_id.get(str(a.get("id") or "")), w3_review=w3_review)
        for a in commercial_accounts
    ]
    active_rows = [r for r in account_rows if not r.get("confirm_sent")]

    mail_from_ok = bool(ship.get("w3_mail_from_configured"))
    if not mail_from_ok:
        bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
        for c in bl.get("ship_checks") or bl.get("checks") or []:
            if c.get("id") == "w3_mail_from":
                mail_from_ok = bool(c.get("ok"))

    w3_send_ready = bool(ship.get("w3_send_ready"))
    if not w3_send_ready:
        bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
        for c in bl.get("ship_checks") or bl.get("checks") or []:
            if c.get("id") == "w3_send_ready":
                w3_send_ready = bool(c.get("ok"))

    l3_gates = {
        "w3_oqg": all(r.get("oqg_pass") for r in account_rows) if account_rows else bool(ship.get("w3_oqg_pass")),
        "w3_sina_read": all(r.get("sina_read_pass") for r in active_rows) if active_rows else bool(ship.get("w3_sina_read_pass")),
        "w3_mail_from": mail_from_ok,
        "w3_confirm_sent": all(r.get("confirm_sent") for r in active_rows) if active_rows else w3_send_ready,
    }
    l3_done = sum(1 for v in l3_gates.values() if v)
    l3_pct = round(100 * l3_done / len(l3_gates)) if l3_gates else 0

    row = {
        "schema": "commercial-command-pulse-v1",
        "at": _now(),
        "one_law": salvage.get("one_law"),
        "compile_sequence": approvals.get("compile_sequence"),
        "founder_review_bundle_order": approvals.get("founder_review_bundle_order"),
        "commercial_kpi": "one thoughtful human reply → deposit ≥ $2K CAD",
        "deposit_target_cad": DEPOSIT_TARGET_CAD,
        "days_to_deposit_target": PHASE1_DAYS,
        "l3_gates": l3_gates,
        "l3_ready_pct": l3_pct,
        "l3_ready": l3_pct >= 100,
        "ship_gates": {
            "w3_oqg_pass": ship.get("w3_oqg_pass"),
            "w3_sina_read_pass": ship.get("w3_sina_read_pass"),
            "w3_mail_from_configured": mail_from_ok,
            "w3_send_ready": w3_send_ready,
        },
        "accounts": account_rows,
        "pulse_line": (
            f"commercial-cmd · L3 {l3_pct}% · "
            f"accounts={len(account_rows)} · "
            f"mail_from={'OK' if mail_from_ok else 'RED'} · "
            f"send={'ready' if l3_pct >= 75 else 'blocked'}"
        ),
        "commands": {
            "founder_show": "python3 scripts/w3_founder_review_v1.py --show",
            "fleet_compile": "python3 scripts/icp_output_compiler_v1.py --fleet --json",
            "nerve": "python3 scripts/agent_nerve_system_v1.py --json",
        },
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    receipt = _read_json(PULSE)
    if not receipt:
        receipt = run_pulse(write=True)
    return {
        "schema": "worker-hub-commercial-command-v1",
        "ok": True,
        "at": receipt.get("at"),
        "pulse_line": receipt.get("pulse_line"),
        "l3_ready_pct": receipt.get("l3_ready_pct"),
        "accounts": receipt.get("accounts"),
        "l3_gates": receipt.get("l3_gates"),
        "law": "data/commercial/w3-canada-send-approvals-v1.json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Commercial Command pulse")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--hub", action="store_true")
    args = ap.parse_args()
    if args.hub:
        row = hub_slice()
    else:
        row = run_pulse(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("pulse_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
