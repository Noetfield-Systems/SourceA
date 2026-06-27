#!/usr/bin/env python3
"""Eval booking agent — proof_viewed → eval_scheduled (founder one-tap Mail only).

Law: FOUNDER_AGENTIC_COMMERCIAL — agent drafts · founder sends · booked_by: agentic on mark.
Targets: commercial pipeline rows in proof_viewed or replied with proof_url.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"
RECEIPT = SINA / "eval-booking-receipt-v1.json"
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"


def _w1_proof_page() -> str:
    from commercial_recipient_guard_v1 import resolve_w1_proof_url  # noqa: WPS433

    return resolve_w1_proof_url()


BOOKING_URL = os.environ.get(
    "SOURCEA_BOOKING_URL",
    "mailto:hello@sourcea.app?subject=SourceA%20%E2%80%94%2015-min%20live%20proof%20eval",
)
FROM_EMAIL = "hello@sourcea.app"
FROM_NAME = "SourceA"
NW1_FROM_EMAIL = "operations@noetfield.com"
NW1_FROM_NAME = "Noetfield Systems Inc."
FOUNDER_NAME = os.environ.get("SOURCEA_FOUNDER_NAME", "Sina Kazemnezhad").strip() or "Sina Kazemnezhad"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _latest_proof_url(*, lane: str = "AB1", fallback: str = "") -> str:
    from commercial_recipient_guard_v1 import resolve_demo_proof_url  # noqa: WPS433

    try:
        return resolve_demo_proof_url(lane=lane)
    except SystemExit:
        pass
    manifest = _read_json(AEG_LATEST)
    url = str(manifest.get("proof_url") or fallback).strip()
    return url


def _pick_row(row_id: str | None = None) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_pipeline_v1 import load_rows  # noqa: WPS433

    rows = load_rows()
    if row_id:
        row = rows.get(row_id)
        if not row:
            raise SystemExit(f"FAIL: unknown pipeline row {row_id}")
        return row
    eligible = [
        r
        for r in rows.values()
        if r.get("status") in ("proof_viewed", "replied") and str(r.get("proof_url") or "").startswith("http")
    ]
    eligible.sort(
        key=lambda r: (
            0 if r.get("founder_pick") else 1,
            0 if r.get("status") == "proof_viewed" else 1,
            -int(r.get("icp_score") or 0),
        )
    )
    if not eligible:
        raise SystemExit("FAIL: no proof_viewed/replied rows with proof_url — run AEG + pipeline sync first")
    return eligible[0]


def _subject(row: dict[str, Any]) -> str:
    lane = str(row.get("lane") or "AB1").upper()
    if lane == "NW1":
        return "Re: Copilot governance — 15 min live walk?"
    return "Worth 15 minutes to walk through the proof live?"


def _body_ab1(*, proof_url: str, booking_url: str, recipient_name: str, w1_url: str) -> str:
    greeting = recipient_name.strip() or "there"
    if greeting != "there":
        greeting = recipient_name.strip()
    hi = f"Hi {greeting}," if greeting != "there" else "Hi,"
    return f"""{hi}

Thanks for taking a look at the proof link — I appreciate it.

If it's useful, I'd like to offer **15 minutes on a screen-share** (no deck). We'd walk through what actually ran today, what got blocked, and whether it's safe to run again tomorrow — same receipts we use in our own factory every morning.

**Live proof from today** (not a mockup):
{proof_url}

**~60s demo film** if you want the full arc first (allow · block · tamper check):
{w1_url}

Reply with two times that work for you, or use this link:
{booking_url}

If it's not a fit, just say stop — I won't follow up.

—
{FOUNDER_NAME}
SourceA · controlled agentic automation
{FROM_EMAIL}
https://sourcea.com

Reply "stop" and I won't follow up.
"""


def _body_nw1(*, proof_url: str, booking_url: str, recipient_name: str, demo_date: str, w1_url: str) -> str:
    greeting = recipient_name.strip()
    hi = f"Hi {greeting}," if greeting else "Hi,"
    slot = demo_date or "this week"
    return f"""{hi}

Good to connect on the Copilot governance thread.

I'd like to offer **15 minutes live** — screen-share only, no slide deck. We walk the receipt chain: what Copilot executed, what we block before it runs, and how tamper shows up immediately.

**Proof bundle** (machine-generated from today's run):
{proof_url}

**Short demo film** (~60s):
{w1_url}

**{slot}** still works on our side if that helps — otherwise reply with two times.

Pilot overview: https://www.noetfield.com/copilot/pilot/

Reply with a slot or use:
{booking_url}

Not useful? Say stop — no more notes from me.

—
Noetfield Systems Inc.
{NW1_FROM_EMAIL}

Reply "stop" and I won't follow up.
"""


def _body(*, row: dict[str, Any], proof_url: str, booking_url: str, recipient_name: str, w1_url: str) -> str:
    lane = str(row.get("lane") or "AB1").upper()
    if lane == "NW1":
        nw1 = _read_json(SINA / "nw1-outbound-send-receipt-v1.json")
        return _body_nw1(
            proof_url=proof_url,
            booking_url=booking_url,
            recipient_name=recipient_name,
            demo_date=str(nw1.get("demo_date") or ""),
            w1_url=w1_url,
        )
    return _body_ab1(proof_url=proof_url, booking_url=booking_url, recipient_name=recipient_name, w1_url=w1_url)


def write_pack(
    *,
    row: dict[str, Any],
    proof_url: str,
    to_email: str,
    recipient_name: str,
    booking_url: str,
) -> tuple[Path, dict[str, Any]]:
    short = str(row.get("id") or "row").replace("cp-", "")[:10]
    out_dir = SINA / "outbound" / f"eval-booking-{short}"
    out_dir.mkdir(parents=True, exist_ok=True)
    subject = _subject(row)
    w1_url = _w1_proof_page()
    body = _body(row=row, proof_url=proof_url, booking_url=booking_url, recipient_name=recipient_name, w1_url=w1_url)
    lane_u = str(row.get("lane") or "AB1").upper()
    from_email = NW1_FROM_EMAIL if lane_u == "NW1" else FROM_EMAIL
    from_name = NW1_FROM_NAME if lane_u == "NW1" else FROM_NAME
    (out_dir / "subject.txt").write_text(subject + "\n", encoding="utf-8")
    (out_dir / "body.txt").write_text(body + "\n", encoding="utf-8")
    (out_dir / "from.txt").write_text(f"{from_name} <{from_email}>\n", encoding="utf-8")
    (out_dir / "to.txt").write_text((to_email or "PASTE_RECIPIENT@company.com") + "\n", encoding="utf-8")
    meta = {
        "schema": "eval-booking-pack-v1",
        "at": _now(),
        "row_id": row.get("id"),
        "company": row.get("company"),
        "lane": row.get("lane"),
        "proof_url": proof_url,
        "w1_film_url": w1_url,
        "booking_url": booking_url,
        "booking_status": "awaiting_founder_send_click",
        "booked_by": "agentic",
        "from_email": from_email,
        "subject": subject,
        "to": to_email or None,
        "recipient_name": recipient_name or None,
        "pack_dir": str(out_dir),
    }
    (out_dir / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return out_dir, meta


def open_mail_draft(*, subject: str, body: str, to_email: str, lane: str = "AB1") -> None:
    from commercial_mail_draft_v1 import lane_from, open_commercial_mail_draft  # noqa: WPS433

    from_name, from_email = lane_from(lane)
    open_commercial_mail_draft(
        subject=subject,
        body=body,
        to_email=to_email,
        from_email=from_email,
        from_name=from_name,
        lane=lane,
        context="eval booking Mail",
    )


def run_eval_booking(
    *,
    row_id: str | None = None,
    to_email: str = "",
    recipient_name: str = "",
    proof_url: str = "",
    booking_url: str = "",
    open_mail: bool = False,
) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_pipeline_v1 import pipeline_glance_payload, transition  # noqa: WPS433

    row = _pick_row(row_id)
    lane_u = str(row.get("lane") or "AB1").upper()
    proof = (
        proof_url.strip()
        or _latest_proof_url(lane=lane_u)
        or str(row.get("proof_url") or "")
    )
    if not proof.startswith("http"):
        raise SystemExit("FAIL: proof_url required — run host_aeg_bundle_v1.py or pass --proof-url")
    book = booking_url.strip() or BOOKING_URL

    out_dir, pack = write_pack(
        row=row,
        proof_url=proof,
        to_email=to_email,
        recipient_name=recipient_name,
        booking_url=book,
    )

    updated = transition(
        str(row["id"]),
        status=str(row.get("status") or "proof_viewed"),
        proof_url=proof,
        next_action="Founder send eval invite · Mail draft in outbound pack",
        last_agent="commercial_eval_booking_agent_v1",
        notes=f"eval pack: {out_dir.name}",
    )

    receipt = {
        "schema": "eval-booking-receipt-v1",
        "at": _now(),
        "ok": True,
        "row_id": row.get("id"),
        "pipeline_status": updated.get("status"),
        "eval_status": "awaiting_founder_send_click",
        "booked_by": "agentic",
        "pack_dir": str(out_dir),
        "proof_url": proof,
        "w1_film_url": pack.get("w1_film_url"),
        "booking_url": book,
        "founder_line": f"Eval booking pack ready · {row.get('company')} · tap Send in Mail",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if open_mail:
        lane_u = str(row.get("lane") or "AB1").upper()
        from commercial_recipient_guard_v1 import is_placeholder_to  # noqa: WPS433

        if is_placeholder_to(to_email):
            raise SystemExit(
                "FAIL: --open-mail requires --to prospect@company.com (not your personal me@)"
            )
        open_mail_draft(
            subject=pack["subject"],
            body=(out_dir / "body.txt").read_text(encoding="utf-8"),
            to_email=to_email,
            lane=lane_u,
        )

    glance = pipeline_glance_payload()
    return {**receipt, "glance_headline": glance.get("headline"), "pack": pack}


def main() -> int:
    ap = argparse.ArgumentParser(description="Eval booking agent — proof_viewed → eval invite pack")
    ap.add_argument("--row-id", help="Pipeline row id (default: founder_pick proof_viewed)")
    ap.add_argument("--to", "-t", default="", help="Recipient email")
    ap.add_argument("--name", default="", help="Recipient name")
    ap.add_argument("--proof-url", default="")
    ap.add_argument("--booking-url", default="")
    ap.add_argument("--open-mail", action="store_true", help="Open macOS Mail draft")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        result = run_eval_booking(
            row_id=args.row_id,
            to_email=args.to,
            recipient_name=args.name,
            proof_url=args.proof_url,
            booking_url=args.booking_url,
            open_mail=args.open_mail,
        )
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: Mail draft — {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: eval booking pack · row={result.get('row_id')}")
        print(f"PACK={result.get('pack_dir')}")
        print(f"RECEIPT={RECEIPT}")
        print(f"NEXT: founder Send in Mail → python3 scripts/mark_eval_booking_sent_v1.py --json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
