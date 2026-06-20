#!/usr/bin/env python3
"""NW1 single send — founder approved. Opens Mail draft; records vault receipt."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUT = SINA / "outbound" / "nw1-send-001"
RECEIPT = SINA / "nw1-outbound-send-receipt-v1.json"

SUBJECT = "Copilot governance receipt — design partner"

BODY = """Every Microsoft Copilot action your team executes leaves no verifiable trail. If something goes wrong — wrong output, unauthorized action, policy violation — you have no cryptographic proof of what happened.
We fix that in 30 days. Delivery records for every Copilot action. Invalid actions blocked before execution. Tamper detected immediately.
Pilot: CAD $2K deposit. Refund if we don't deliver. 15 minutes?

Happy to walk the full governance receipt chain live on {demo_date} — 15 minutes. Open in shadow mode now; we can confirm a live demo slot when you reply.

Pilot overview: https://www.noetfield.com/copilot/pilot/
Compliance demo: https://project-gc7lm.vercel.app/copilot/demo/

—
Noetfield Systems Inc.
operations@noetfield.com
"""

VAULT_ONEPAGER = (
    Path.home()
    / "Projects/noetfeld-os/docs/_NOOS_AGENT/[NOOS-AGENT-20260615-011]_FOUNDING_PILOT_ONEPAGER_EXTERNAL_v1.md"
)
HTML_ONEPAGER = SINA / "noetfield-pilot-onepager-external-v1.html"
ATTACH = Path(os.environ.get("NOETFIELD_NW1_ONEPAGER", str(ROOT / "brain-os/law/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_MERGED_EXTERNAL_v1.md")))
if "--html" in sys.argv:
    sys.argv = [a for a in sys.argv if a != "--html"]
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_commercial_onepager_html_v1.py"), "noetfield"], check=True)
    if HTML_ONEPAGER.is_file():
        ATTACH = HTML_ONEPAGER
elif os.environ.get("NOETFIELD_NW1_HTML") == "1" and HTML_ONEPAGER.is_file():
    ATTACH = HTML_ONEPAGER
if not ATTACH.is_file():
    ATTACH = ROOT / "brain-os/law/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md"
if not ATTACH.is_file():
    ATTACH = VAULT_ONEPAGER if VAULT_ONEPAGER.is_file() else ATTACH


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _demo_date() -> str:
    # Next Thursday from run date (founder-friendly live slot)
    today = datetime.now(timezone.utc).date()
    days_ahead = (3 - today.weekday()) % 7  # Thursday
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).strftime("%A %B %-d, %Y")


def write_pack(*, demo_date: str, to_email: str = "") -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    body = BODY.format(demo_date=demo_date)
    (OUT / "subject.txt").write_text(SUBJECT + "\n", encoding="utf-8")
    (OUT / "body.txt").write_text(body, encoding="utf-8")
    (OUT / "to.txt").write_text((to_email or "PASTE_RECIPIENT@company.com") + "\n", encoding="utf-8")
    meta = {
        "schema": "nw1-outbound-send-pack-v1",
        "lane": "NW1",
        "subject": SUBJECT,
        "attach": str(ATTACH),
        "demo_date": demo_date,
        "to": to_email or None,
        "founder_approved_at": _now(),
        "send_policy": "founder_tap_approve_do_it",
        "status": "draft_opened",
    }
    (OUT / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def record_receipt(meta: dict) -> None:
    receipt = {
        "schema": "nw1-outbound-send-receipt-v1",
        "founder_approved": True,
        "approved_at": meta["founder_approved_at"],
        "sent_by": "agent",
        "send_mode": "mail_draft_opened",
        "nw1_status": "awaiting_founder_send_click",
        "pack_dir": str(OUT),
        "subject": SUBJECT,
        "attach": str(ATTACH),
        "demo_date": meta["demo_date"],
        "law": "SSOT Day 1 §19 · NW1 battle card verbatim + one-pager",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def open_mail_draft(*, body: str, to_email: str) -> None:
    from commercial_mail_draft_v1 import open_commercial_mail_draft  # noqa: WPS433

    if not ATTACH.is_file():
        raise SystemExit(f"FAIL: attachment missing {ATTACH}")
    open_commercial_mail_draft(
        subject=SUBJECT,
        body=body,
        to_email=to_email,
        from_email="operations@noetfield.com",
        from_name="Noetfield Systems Inc.",
        lane="NW1",
        attachments=[ATTACH],
        context="NW1 outbound Mail",
    )


def main() -> int:
    to_email = ""
    if len(sys.argv) > 1:
        to_email = sys.argv[1].strip()
    demo_date = _demo_date()
    meta = write_pack(demo_date=demo_date, to_email=to_email)
    record_receipt(meta)
    body = (OUT / "body.txt").read_text(encoding="utf-8")
    try:
        open_mail_draft(body=body, to_email=to_email)
    except subprocess.CalledProcessError as exc:
        print(f"WARN: Mail draft failed ({exc}) — pack at {OUT}")
        print("Open Mail manually; attach one-pager from pack.json")
        return 1
    print(f"OK: NW1 Mail draft opened · receipt {RECEIPT}")
    print(f"    Pack: {OUT}")
    print("    Action: paste recipient if empty → Send → screenshot Sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
