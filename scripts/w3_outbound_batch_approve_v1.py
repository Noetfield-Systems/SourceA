#!/usr/bin/env python3
"""W3 outbound batch — hub Approve outbound card (9.07 A · no send without founder tap)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "w3-outbound-batch-receipt-v1.json"
BATCH_ID = "W3-OUTREACH-BATCH-001"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scripts_path() -> None:
    p = str(ROOT / "scripts")
    if p not in sys.path:
        sys.path.insert(0, p)


def hub_card_visible() -> bool:
    """Show card when RT LIVE pass, form clear, factory not frozen."""
    _scripts_path()
    try:
        from rt_live_gate_v1 import receipt_pass  # noqa: WPS433
        from live_founder_decision_form_v1 import payload as form_payload  # noqa: WPS433
        from factory_control_v1 import load_factory_now  # noqa: WPS433
    except Exception:
        return False
    if not receipt_pass():
        return False
    form = form_payload()
    if int(form.get("open_questions_count") or 0) > 0 or form.get("awaiting_founder_picks"):
        return False
    fn = load_factory_now()
    return not bool(fn.get("kill_flag"))


def _read_receipt() -> dict:
    if not RECEIPT_PATH.is_file():
        return {}
    try:
        return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _spine_has_queued() -> bool:
    spine = SINA / "governance-event-spine-v1.jsonl"
    if not spine.is_file():
        return False
    for line in spine.read_text(encoding="utf-8", errors="replace").splitlines()[-300:]:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = row.get("payload") or {}
        if payload.get("event") in ("outbound_queued", "outbound_approved"):
            return True
        if payload.get("outbound_queued"):
            return True
    return False


def card_status() -> dict:
    rec = _read_receipt()
    approved = rec.get("founder_approved") is True
    queued = _spine_has_queued() or rec.get("dry_run_queued")
    count = int(rec.get("target_count") or 5)
    if approved:
        summary = f"Batch {BATCH_ID} approved — dry-run receipt on disk"
        status = "approved"
    elif queued:
        summary = f"{count} NF outreach drafts queued — tap Approve before send"
        status = "queued"
    else:
        summary = f"W3 batch {BATCH_ID} dry-run ready — tap Approve outbound batch"
        status = "dry_run_ready"
    return {
        "batch_id": BATCH_ID,
        "status": status,
        "founder_approved": approved,
        "queued_count": count,
        "summary": summary,
        "why": (
            "9.07 A · agents draft+queue · you approve before send — "
            "not Resend.com research · not resend_digests · not manual email"
        ),
    }


def approve(*, dry_run: bool = True) -> dict:
    _scripts_path()
    from governance_event_spine_v1 import append_event  # noqa: WPS433

    if not hub_card_visible():
        return {"ok": False, "error": "W3 approve card not active — RT LIVE + form clear required"}

    if card_status().get("founder_approved"):
        return {"ok": True, "message": "Already approved", "receipt": _read_receipt()}

    ev = append_event(
        event_type="FOUNDER_SIGNAL",
        object_id=BATCH_ID,
        object_kind="system",
        agent_id="founder",
        payload={
            "event": "outbound_approved",
            "batch_id": BATCH_ID,
            "dry_run": dry_run,
            "law": "9.07 A · AGENTIC_W3_OUTREACH_WORKFLOW_SPEC_v1.md",
            "send_policy": "no_send_without_hub_approve",
        },
        gate="W3-OUTREACH",
        proof="founder_hub_tap",
        validator_set=["validate-p0-portfolio-automation-law-v1.sh"],
    )

    receipt = {
        "schema": "w3-outbound-batch-receipt-v1",
        "batch_id": BATCH_ID,
        "founder_approved": True,
        "approved_at": _now(),
        "dry_run": dry_run,
        "target_count": 5,
        "dry_run_queued": True,
        "spine_event_id": ev.get("event_id"),
        "law": "no_send_without_hub_approve",
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "message": "Approve outbound batch — dry-run receipt recorded (no auto-send)",
        "receipt": receipt,
        "spine": ev,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="W3 outbound batch approve card")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--approve", action="store_true")
    args = ap.parse_args()

    if args.approve:
        out = approve()
    else:
        out = {"ok": True, "visible": hub_card_visible(), **card_status()}

    text = json.dumps(out, indent=2) if (args.json or args.status) else (out.get("message") or json.dumps(out))
    print(text)
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
