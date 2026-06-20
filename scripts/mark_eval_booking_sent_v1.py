#!/usr/bin/env python3
"""Mark eval booking sent → pipeline eval_scheduled (founder tap after Mail Send)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "eval-booking-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pack_dir_for_row(row_id: str) -> Path:
    short = row_id.replace("cp-", "")[:10]
    return SINA / "outbound" / f"eval-booking-{short}"


def _load_pack_meta(row_id: str) -> dict:
    pack_dir = _pack_dir_for_row(row_id)
    pack_json = pack_dir / "pack.json"
    if pack_json.is_file():
        return json.loads(pack_json.read_text(encoding="utf-8"))
    return {}


def mark_eval_sent(*, row_id: str = "", screenshot: str = "") -> dict:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8")) if RECEIPT.is_file() else {}
    rid = row_id.strip() or str(receipt.get("row_id") or "")
    if not rid:
        raise SystemExit("FAIL: pass --row-id cp-... (AB1 or NW1) after Send in Mail")

    sys.path.insert(0, str(ROOT / "scripts"))
    from commercial_pipeline_v1 import load_rows, pipeline_glance_payload, transition  # noqa: WPS433

    rows = load_rows()
    base = rows.get(rid)
    if not base:
        raise SystemExit(f"FAIL: unknown pipeline row {rid}")
    if base.get("status") == "eval_scheduled":
        glance = pipeline_glance_payload()
        return {
            "ok": True,
            "already": True,
            "row_id": rid,
            "pipeline": base,
            "glance_headline": glance.get("headline"),
            "founder_line": f"Already eval_scheduled · {base.get('company')} — pick next proof_viewed row",
        }

    pack = _load_pack_meta(rid)
    proof_url = str(pack.get("proof_url") or receipt.get("proof_url") or base.get("proof_url") or "")

    updated = transition(
        rid,
        status="eval_scheduled",
        proof_url=proof_url or None,
        next_action="Await prospect slot · prep BLOCK live screen-share",
        last_agent="mark_eval_booking_sent_v1",
        notes="booked_by: agentic · founder_send_confirmed",
    )

    pack_dir = str(pack.get("pack_dir") or _pack_dir_for_row(rid))
    results = list(receipt.get("results") or [])
    found = False
    for entry in results:
        if str(entry.get("row_id")) == rid:
            entry["eval_status"] = "sent"
            entry["pipeline_status"] = "eval_scheduled"
            entry["sent_at"] = _now()
            found = True
            break
    if not found:
        results.append(
            {
                "row_id": rid,
                "eval_status": "sent",
                "pipeline_status": "eval_scheduled",
                "pack_dir": pack_dir,
                "proof_url": proof_url,
                "sent_at": _now(),
            }
        )

    receipt = {
        "schema": "eval-booking-receipt-v1",
        "at": receipt.get("at") or _now(),
        "ok": True,
        "row_id": rid,
        "pipeline_status": "eval_scheduled",
        "eval_status": "sent",
        "booked_by": "agentic",
        "pack_dir": pack_dir,
        "proof_url": proof_url,
        "results": results,
        "sent_at": _now(),
        "send_mode": "founder_confirmed_send",
        "founder_line": f"Eval scheduled · {updated.get('company')} · booked_by agentic",
    }
    if screenshot:
        receipt["screenshot_path"] = screenshot
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    glance = pipeline_glance_payload()
    return {
        "ok": True,
        "row_id": rid,
        "pipeline": updated,
        "receipt": receipt,
        "glance_headline": glance.get("headline"),
        "founder_line": receipt["founder_line"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mark eval booking invite sent")
    ap.add_argument("--row-id", required=True, help="cp-32ddb1794d (AB1) or cp-0b9b8c4eff (NW1)")
    ap.add_argument("--screenshot", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = mark_eval_sent(row_id=args.row_id, screenshot=args.screenshot)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: {result['row_id']} → eval_scheduled")
        print(result.get("founder_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
