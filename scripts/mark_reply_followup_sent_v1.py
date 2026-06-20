#!/usr/bin/env python3
"""Mark proof follow-up sent → pipeline proof_viewed (founder tap after Mail Send)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "reply-qualification-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_followup_sent(*, row_id: str = "", screenshot: str = "") -> dict:
    receipt = {}
    if RECEIPT.is_file():
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    rid = row_id.strip() or str(receipt.get("row_id") or "")
    if not rid:
        results = receipt.get("results") or []
        for r in reversed(results):
            if r.get("phase") == "replied" and r.get("row_id"):
                rid = str(r["row_id"])
                break
    if not rid:
        raise SystemExit("FAIL: row_id required — pass --row-id or run reply agent first")

    proof_url = str(receipt.get("proof_url") or "")
    pack_dir = ""
    for r in receipt.get("results") or []:
        if str(r.get("row_id")) == rid:
            proof_url = str(r.get("proof_url") or proof_url)
            pack_dir = str(r.get("pack_dir") or "")
            r["followup_status"] = "sent"
            r["phase"] = "proof_viewed"
            break
    if not pack_dir:
        short = rid.replace("cp-", "")[:10]
        guess = SINA / "outbound" / f"reply-followup-{short}"
        if guess.is_dir():
            pack_dir = str(guess)
    if not proof_url:
        aeg = SINA / "aeg-latest-receipt-v1.json"
        if aeg.is_file():
            proof_url = str(json.loads(aeg.read_text()).get("proof_url") or "")

    sys.path.insert(0, str(ROOT / "scripts"))
    from commercial_pipeline_v1 import pipeline_glance_payload, transition  # noqa: WPS433

    updated = transition(
        rid,
        status="proof_viewed",
        proof_url=proof_url or None,
        next_action="Book 15 min eval · eval booking agent",
        last_agent="mark_reply_followup_sent_v1",
        notes="qualified_by: agentic · proof_followup_sent",
    )

    receipt["followup_status"] = "sent"
    receipt["sent_at"] = _now()
    receipt["send_mode"] = "founder_confirmed_send"
    receipt["row_id"] = rid
    receipt["pipeline_status"] = "proof_viewed"
    if screenshot:
        receipt["screenshot_path"] = screenshot
    if pack_dir:
        receipt["pack_dir"] = pack_dir
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    glance = pipeline_glance_payload()
    return {
        "ok": True,
        "row_id": rid,
        "pipeline": updated,
        "receipt": receipt,
        "glance_headline": glance.get("headline"),
        "founder_line": f"Proof viewed · {updated.get('company')} · ready for eval booking",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mark reply proof follow-up sent")
    ap.add_argument("--row-id", default="")
    ap.add_argument("--screenshot", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = mark_followup_sent(row_id=args.row_id, screenshot=args.screenshot)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: {result['row_id']} → proof_viewed")
        print(result.get("founder_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
