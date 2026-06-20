#!/usr/bin/env python3
"""Reply qualification agent — personalized_sent → replied (+ proof follow-up pack).

Law: FOUNDER_AGENTIC_COMMERCIAL — agent qualifies · drafts proof follow-up · founder sends.
Targets: AB1/NW1 pipeline rows in personalized_sent after outbound sent (or --stage watch).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"
RECEIPT = SINA / "reply-qualification-receipt-v1.json"
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"


def _w1_proof_page() -> str:
    from commercial_recipient_guard_v1 import resolve_w1_proof_url  # noqa: WPS433

    return resolve_w1_proof_url()


FROM_EMAIL = "hello@sourcea.com"
FROM_NAME = "SourceA"
FOUNDER_NAME = os.environ.get("SOURCEA_FOUNDER_NAME", "Sina Kazemnezhad").strip() or "Sina Kazemnezhad"

LANE_RECEIPTS = {
    "AB1": SINA / "ab1-outbound-send-receipt-v1.json",
    "NW1": SINA / "nw1-outbound-send-receipt-v1.json",
}
LANE_PACKS = {
    "AB1": SINA / "outbound" / "ab1-send-001",
    "NW1": SINA / "outbound" / "nw1-send-001",
}

DISQUALIFY_PHRASES = (
    "stop",
    "unsubscribe",
    "not interested",
    "no thanks",
    "remove me",
    "don't contact",
    "do not contact",
)
POSITIVE_PHRASES = (
    "yes",
    "interested",
    "sounds good",
    "worth",
    "schedule",
    "call",
    "demo",
    "look",
    "tell me more",
    "copilot",
    "agents",
    "proof",
    "walk",
    "thursday",
    "slot",
    "15 min",
    "15-minute",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _latest_proof_url() -> str:
    manifest = _read_json(AEG_LATEST)
    return str(manifest.get("proof_url") or "").strip()


def _outbound_sent(lane: str) -> tuple[bool, dict[str, Any]]:
    receipt = _read_json(LANE_RECEIPTS.get(lane.upper(), Path()))
    status_key = "ab1_status" if lane.upper() == "AB1" else "nw1_status"
    status = str(receipt.get(status_key) or receipt.get("status") or "")
    sent = status == "sent" or bool(receipt.get("sent_at"))
    return sent, receipt


def _pick_rows(row_id: str | None = None, all_personalized: bool = False) -> list[dict[str, Any]]:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_pipeline_v1 import load_rows  # noqa: WPS433

    rows = load_rows()
    if row_id:
        row = rows.get(row_id)
        if not row:
            raise SystemExit(f"FAIL: unknown pipeline row {row_id}")
        if row.get("status") != "personalized_sent":
            raise SystemExit(f"FAIL: row {row_id} status={row.get('status')} — need personalized_sent")
        return [row]
    eligible = [r for r in rows.values() if r.get("status") == "personalized_sent"]
    eligible.sort(key=lambda r: (-int(r.get("icp_score") or 0), str(r.get("updated_at") or "")))
    if not eligible:
        raise SystemExit("FAIL: no personalized_sent rows — run pipeline sync first")
    if all_personalized:
        return eligible
    return [eligible[0]]


def qualify_reply(text: str) -> dict[str, Any]:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    if not norm:
        return {"qualified": False, "score": 0, "verdict": "empty", "reason": "no reply text"}
    for phrase in DISQUALIFY_PHRASES:
        if phrase in norm:
            return {"qualified": False, "score": 0, "verdict": "disqualified", "reason": phrase}
    hits = [p for p in POSITIVE_PHRASES if p in norm]
    score = min(100, 40 + len(hits) * 12 + (10 if "?" in text else 0))
    qualified = score >= 50 or len(hits) >= 2
    verdict = "qualified" if qualified else "nurture"
    return {
        "qualified": qualified,
        "score": score,
        "verdict": verdict,
        "reason": f"signals: {', '.join(hits[:5]) or 'weak'}",
        "signals": hits,
    }


def _followup_subject(row: dict[str, Any], lane: str) -> str:
    company = str(row.get("company") or "your team").replace("(draft)", "").strip()
    if lane == "NW1":
        return f"Re: Copilot governance — proof walk for {company}"
    return f"Re: agent receipts — live proof for {company}"


def _followup_body(*, row: dict[str, Any], lane: str, proof_url: str, inbound: str, nw1_receipt: dict, w1_url: str) -> str:
    company = str(row.get("company") or "your team").replace("(draft)", "").strip()
    proof_block = ""
    if proof_url.startswith("http"):
        proof_block = f"""
Live proof from today (not a mockup):
{proof_url}

~60s demo film if you want the arc first:
{w1_url}
"""
    if lane == "NW1":
        demo_date = str(nw1_receipt.get("demo_date") or "this week")
        return f"""Thanks for getting back to me — glad this landed.

Happy to do **15 minutes live** on the Copilot receipt chain (screen-share, no deck):
{proof_block}
**{demo_date}** still works on our side — or send two times that suit you.

Pilot overview: https://www.noetfield.com/copilot/pilot/

—
Noetfield Systems Inc.
operations@noetfield.com

Reply "stop" and I won't follow up.
"""
    return f"""Thanks for the reply — I appreciate you taking a look.

Here's the live proof if you want to skim before we talk:
{proof_block}
Worth **15 minutes** to screen-share what ran, what got blocked, and whether it's safe to run again tomorrow?

—
{FOUNDER_NAME}
SourceA · governed agentic automation
{FROM_EMAIL}
https://sourcea.com

Reply "stop" and I won't follow up.
"""


def write_followup_pack(
    *,
    row: dict[str, Any],
    lane: str,
    proof_url: str,
    qualification: dict[str, Any],
    inbound: str,
    nw1_receipt: dict,
    to_email: str,
) -> tuple[Path, dict[str, Any]]:
    short = str(row.get("id") or "row").replace("cp-", "")[:10]
    out_dir = SINA / "outbound" / f"reply-followup-{short}"
    out_dir.mkdir(parents=True, exist_ok=True)
    subject = _followup_subject(row, lane)
    w1_url = _w1_proof_page()
    body = _followup_body(row=row, lane=lane, proof_url=proof_url, inbound=inbound, nw1_receipt=nw1_receipt, w1_url=w1_url)
    (out_dir / "subject.txt").write_text(subject + "\n", encoding="utf-8")
    (out_dir / "body.txt").write_text(body, encoding="utf-8")
    from_line = "Noetfield Systems Inc. <operations@noetfield.com>" if lane == "NW1" else f"{FROM_NAME} <{FROM_EMAIL}>"
    (out_dir / "from.txt").write_text(from_line + "\n", encoding="utf-8")
    (out_dir / "to.txt").write_text((to_email or "PASTE_RECIPIENT@company.com") + "\n", encoding="utf-8")
    if inbound.strip():
        (out_dir / "inbound_reply.txt").write_text(inbound.strip() + "\n", encoding="utf-8")
    meta = {
        "schema": "reply-followup-pack-v1",
        "at": _now(),
        "row_id": row.get("id"),
        "company": row.get("company"),
        "lane": lane,
        "proof_url": proof_url,
        "w1_film_url": w1_url,
        "qualification": qualification,
        "followup_status": "awaiting_founder_send_click",
        "qualified_by": "agentic",
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
        context="reply follow-up Mail",
    )


def run_reply_agent(
    *,
    row_id: str | None = None,
    reply_text: str = "",
    reply_file: str = "",
    to_email: str = "",
    stage: bool = False,
    all_personalized: bool = False,
    open_mail: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_pipeline_v1 import pipeline_glance_payload, transition  # noqa: WPS433

    inbound = reply_text.strip()
    if reply_file:
        inbound = Path(reply_file).read_text(encoding="utf-8").strip()
    targets = _pick_rows(row_id, all_personalized=all_personalized)
    proof_url = _latest_proof_url()
    results: list[dict[str, Any]] = []

    for row in targets:
        lane = str(row.get("lane") or "AB1").upper()
        sent, lane_receipt = _outbound_sent(lane)
        if not sent and not stage and not force:
            results.append(
                {
                    "row_id": row.get("id"),
                    "ok": False,
                    "phase": "awaiting_outbound_sent",
                    "founder_line": f"Mark {lane} sent first · mark_outbound_sent_v1.py --lane {lane.lower()}",
                }
            )
            transition(
                str(row["id"]),
                status="personalized_sent",
                next_action=f"Await outbound sent · then paste reply · {lane} pack ready",
                last_agent="commercial_reply_qualification_agent_v1",
                notes=f"outbound_sent={sent}",
            )
            continue

        if stage and not inbound:
            transition(
                str(row["id"]),
                status="personalized_sent",
                proof_url=proof_url if proof_url.startswith("http") else "",
                next_action="Await inbound reply · agent watches Mail",
                last_agent="commercial_reply_qualification_agent_v1",
                notes=f"reply_watch · outbound_sent={sent}",
            )
            results.append(
                {
                    "row_id": row.get("id"),
                    "ok": True,
                    "phase": "watch",
                    "outbound_sent": sent,
                    "company": row.get("company"),
                }
            )
            continue

        if not inbound:
            raise SystemExit(
                f"FAIL: --reply-text or --reply-file required for {row.get('id')} "
                "(or use --stage to arm watch only)"
            )

        qualification = qualify_reply(inbound)
        nw1_receipt = lane_receipt if lane == "NW1" else {}
        out_dir, pack = write_followup_pack(
            row=row,
            lane=lane,
            proof_url=proof_url,
            qualification=qualification,
            inbound=inbound,
            nw1_receipt=nw1_receipt,
            to_email=to_email,
        )

        if qualification["verdict"] == "disqualified":
            updated = transition(
                str(row["id"]),
                status="lost",
                next_action="Disqualified · no follow-up",
                last_agent="commercial_reply_qualification_agent_v1",
                notes=f"reply: {qualification.get('reason')}",
            )
            phase = "lost"
        elif qualification["qualified"]:
            updated = transition(
                str(row["id"]),
                status="replied",
                proof_url=proof_url if proof_url.startswith("http") else "",
                next_action="Founder send proof follow-up · Mail draft in outbound pack",
                last_agent="commercial_reply_qualification_agent_v1",
                notes=f"qualified score={qualification.get('score')} · pack={out_dir.name}",
            )
            phase = "replied"
        else:
            updated = transition(
                str(row["id"]),
                status="personalized_sent",
                proof_url=proof_url if proof_url.startswith("http") else "",
                next_action="Nurture follow-up · low signal reply",
                last_agent="commercial_reply_qualification_agent_v1",
                notes=f"nurture score={qualification.get('score')} · pack={out_dir.name}",
            )
            phase = "nurture"

        entry = {
            "row_id": row.get("id"),
            "ok": True,
            "phase": phase,
            "pipeline_status": updated.get("status"),
            "qualification": qualification,
            "pack_dir": str(out_dir),
            "proof_url": proof_url,
        }
        results.append(entry)

        if open_mail and phase in ("replied", "nurture"):
            from commercial_recipient_guard_v1 import is_placeholder_to  # noqa: WPS433

            if is_placeholder_to(to_email):
                raise SystemExit(
                    "FAIL: --open-mail requires --to prospect@company.com (not your personal me@)"
                )
            open_mail_draft(
                subject=pack.get("subject") or _followup_subject(row, lane),
                body=(out_dir / "body.txt").read_text(encoding="utf-8"),
                to_email=to_email,
                lane=lane,
            )

    primary = results[-1] if results else {}
    receipt = {
        "schema": "reply-qualification-receipt-v1",
        "at": _now(),
        "ok": all(r.get("ok", False) for r in results) if results else False,
        "qualified_by": "agentic",
        "proof_url": proof_url,
        "results": results,
        "row_id": primary.get("row_id"),
        "pipeline_status": primary.get("pipeline_status"),
        "phase": primary.get("phase"),
        "pack_dir": primary.get("pack_dir"),
        "founder_line": primary.get("founder_line")
        or f"Reply agent · {len(results)} row(s) · phase={primary.get('phase', 'watch')}",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    glance = pipeline_glance_payload()
    return {**receipt, "glance_headline": glance.get("headline")}


def main() -> int:
    ap = argparse.ArgumentParser(description="Reply qualification agent — personalized_sent → replied")
    ap.add_argument("--row-id", help="Pipeline row (default: highest icp personalized_sent)")
    ap.add_argument("--all-personalized", action="store_true", help="Stage/watch all personalized_sent rows")
    ap.add_argument("--reply-text", default="", help="Inbound reply paste from Mail")
    ap.add_argument("--reply-file", default="", help="File with inbound reply")
    ap.add_argument("--to", "-t", default="", help="Recipient email for follow-up")
    ap.add_argument("--stage", action="store_true", help="Arm watch rows without reply text")
    ap.add_argument("--force", action="store_true", help="Qualify even if outbound not marked sent")
    ap.add_argument("--open-mail", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        result = run_reply_agent(
            row_id=args.row_id,
            reply_text=args.reply_text,
            reply_file=args.reply_file,
            to_email=args.to,
            stage=args.stage,
            all_personalized=args.all_personalized,
            open_mail=args.open_mail,
            force=args.force,
        )
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: Mail draft — {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: reply agent · {len(result.get('results', []))} row(s)")
        print(f"RECEIPT={RECEIPT}")
        for r in result.get("results", []):
            print(f"  {r.get('row_id')}\t{r.get('phase')}\t{r.get('company', '')}")
        print(f"NEXT: paste reply → re-run with --reply-text · then mark_reply_followup_sent_v1.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
