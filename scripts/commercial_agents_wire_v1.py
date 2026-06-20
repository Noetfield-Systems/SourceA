#!/usr/bin/env python3
"""Commercial agent taps — reply qualification · eval booking (hub + server wire)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
REPLY_RECEIPT = SINA / "reply-qualification-receipt-v1.json"
EVAL_RECEIPT = SINA / "eval-booking-receipt-v1.json"

LANE_COMPANY = {
    "AB1": "AB1 prospect (draft)",
    "NW1": "NW1 design partner (draft)",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def row_id_for_lane(lane: str) -> str | None:
    import sys
    from pathlib import Path as P

    root = P(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    from commercial_pipeline_v1 import load_rows  # noqa: WPS433

    company = LANE_COMPANY.get(lane.upper())
    if not company:
        return None
    for rid, row in load_rows().items():
        if str(row.get("company")) == company:
            return rid
    return None


def next_agent_for_row(row: dict[str, Any]) -> str:
    status = str(row.get("status") or "")
    next_action = str(row.get("next_action") or "").lower()
    if status == "personalized_sent":
        if "await inbound" in next_action or "reply" in next_action:
            return "reply_qualification_agent"
        return "mark_outbound_sent"
    if status == "replied":
        return "reply_followup_sent"
    if status == "proof_viewed":
        return "eval_booking_agent"
    if status == "eval_scheduled":
        return "await_prospect_slot"
    return ""


def commercial_agent_payload(glance: dict[str, Any] | None = None) -> dict[str, Any]:
    if glance is None:
        import sys
        from pathlib import Path as P

        root = P(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from commercial_pipeline_v1 import pipeline_glance_payload  # noqa: WPS433

        glance = pipeline_glance_payload(refresh=False)

    counts = glance.get("counts") or {}
    taps: list[dict[str, Any]] = []
    for r in glance.get("top_next") or []:
        agent = next_agent_for_row(r)
        rid = str(r.get("id") or "")
        company = str(r.get("company") or "—").replace("(draft)", "").strip()
        if agent == "reply_qualification_agent":
            taps.append(
                {
                    "id": f"reply-watch-{rid}",
                    "action": "reply_stage",
                    "row_id": rid,
                    "lane": r.get("lane"),
                    "label": f"Arm reply watch · {company}",
                    "founder_line": f"Paste NW1/AB1 reply in Worker chat when Mail lands",
                }
            )
        elif agent == "reply_followup_sent":
            taps.append(
                {
                    "id": f"reply-followup-{rid}",
                    "action": "reply_followup_sent",
                    "row_id": rid,
                    "lane": r.get("lane"),
                    "label": f"Mark proof follow-up sent · {company}",
                    "founder_line": "After Mail Send on proof follow-up",
                }
            )
        elif agent == "eval_booking_agent":
            taps.append(
                {
                    "id": f"eval-book-{rid}",
                    "action": "eval_booking",
                    "row_id": rid,
                    "lane": r.get("lane"),
                    "label": f"Open eval booking · {company}",
                    "founder_line": "15-min eval invite with proof URL + W1 film",
                }
            )

    bottleneck = ""
    if int(counts.get("replied") or 0) == 0 and int(counts.get("personalized_sent") or 0) > 0:
        bottleneck = "reply_qualification"
    elif int(counts.get("eval_scheduled") or 0) == 0 and int(counts.get("proof_viewed") or 0) > 0:
        bottleneck = "eval_booking"

    reply_receipt = _read_json(REPLY_RECEIPT)
    eval_receipt = _read_json(EVAL_RECEIPT)

    return {
        "schema": "commercial-agents-v1",
        "bottleneck": bottleneck,
        "taps": taps[:4],
        "reply_receipt_ok": reply_receipt.get("schema") == "reply-qualification-receipt-v1",
        "eval_receipt_ok": eval_receipt.get("schema") == "eval-booking-receipt-v1",
        "scripts": {
            "reply_agent": "scripts/commercial_reply_qualification_agent_v1.py",
            "reply_followup": "scripts/mark_reply_followup_sent_v1.py",
            "eval_booking": "scripts/commercial_eval_booking_agent_v1.py",
            "prospect_reel": "scripts/commercial_video_factory_v1.py",
            "eval_sent": "scripts/mark_eval_booking_sent_v1.py",
        },
    }


def run_commercial_action(action: str, *, row_id: str = "", reply_text: str = "") -> dict[str, Any]:
    import sys
    from pathlib import Path as P

    root = P(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))

    if action == "reply_stage":
        from commercial_reply_qualification_agent_v1 import run_reply_agent  # noqa: WPS433

        return run_reply_agent(row_id=row_id or None, stage=True, all_personalized=not row_id)
    if action == "reply_qualify":
        if not reply_text.strip():
            return {"ok": False, "error": "reply_text required"}
        from commercial_reply_qualification_agent_v1 import run_reply_agent  # noqa: WPS433

        return run_reply_agent(row_id=row_id or None, reply_text=reply_text, force=True)
    if action == "reply_followup_sent":
        from mark_reply_followup_sent_v1 import mark_followup_sent  # noqa: WPS433

        return mark_followup_sent(row_id=row_id)
    if action == "eval_booking":
        from commercial_eval_booking_agent_v1 import run_eval_booking  # noqa: WPS433

        result = run_eval_booking(row_id=row_id or None, open_mail=False)
        rid = str(result.get("row_id") or row_id or "")
        if rid and result.get("ok"):
            try:
                from commercial_video_factory_v1 import run_video_factory  # noqa: WPS433

                reel = run_video_factory(row_id=rid, attach_pack=True)
                result["prospect_reel"] = reel
            except SystemExit:
                result["prospect_reel"] = {"ok": False, "skipped": "render failed"}
        return result
    if action == "prospect_reel":
        from commercial_video_factory_v1 import run_video_factory  # noqa: WPS433

        if not row_id:
            return {"ok": False, "error": "row_id required for prospect_reel"}
        return run_video_factory(row_id=row_id, attach_pack=True)
    if action == "eval_sent":
        from mark_eval_booking_sent_v1 import mark_eval_sent  # noqa: WPS433

        return mark_eval_sent()
    return {"ok": False, "error": f"unknown action {action}"}
