#!/usr/bin/env python3
"""Open AB1-style outbound draft with AEG forensic proof_url."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUT = SINA / "outbound" / "aeg-proof-send-001"
RECEIPT = SINA / "aeg-outbound-send-receipt-v1.json"
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"

FROM_EMAIL = "hello@sourcea.com"
FROM_NAME = "SourceA"
COMPANY_URL = "https://sourcea.com"
FOUNDER_NAME = os.environ.get("SOURCEA_FOUNDER_NAME", "Sina Kazemnezhad").strip() or "Sina Kazemnezhad"
OPT_OUT_LINE = 'Reply "stop" and I won\'t follow up.'


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_proof_url(explicit: str) -> tuple[str, dict]:
    if explicit:
        return explicit, {"source": "cli"}
    if not AEG_LATEST.is_file():
        raise SystemExit(f"FAIL: no AEG receipt at {AEG_LATEST} — run critic_boot --aeg on BLOCK first")
    manifest = json.loads(AEG_LATEST.read_text(encoding="utf-8"))
    url = str(manifest.get("proof_url") or "")
    if not url:
        raise SystemExit("FAIL: aeg-latest-receipt missing proof_url")
    return url, manifest


def _subject(manifest: dict) -> str:
    blockers = manifest.get("blockers") or []
    hint = blockers[0][:60] if blockers else "governance BLOCK"
    return f"Forensic proof: your stack would BLOCK here — {hint}"


def _body(*, proof_url: str, manifest: dict, recipient_name: str) -> str:
    greeting = f" {recipient_name.strip()}" if recipient_name.strip() else ""
    eid = manifest.get("evidence_id", "aeg")
    blockers = manifest.get("blockers") or ["stale SSOT / gate mismatch"]
    blocker_line = blockers[0]
    return f"""Hi{greeting},

Not a deck — a machine-generated forensic bundle from today's critic_boot BLOCK.

What happened: {blocker_line}
Evidence ID: {eid}

Open the proof page (terminal + UI capture + JSON receipt):
{proof_url}

If the link is local-only, I'll host the bundle on our proof CDN before your call — reply and I'll send the live URL.

Worth 15 minutes to walk through BLOCK → heal → replay?

—
{FOUNDER_NAME}
SourceA · controlled agentic automation
{FROM_EMAIL}
{COMPANY_URL}

{OPT_OUT_LINE}
"""


def write_pack(*, proof_url: str, manifest: dict, to_email: str, recipient_name: str) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    subject = _subject(manifest)
    body = _body(proof_url=proof_url, manifest=manifest, recipient_name=recipient_name)
    (OUT / "subject.txt").write_text(subject + "\n", encoding="utf-8")
    (OUT / "body.txt").write_text(body, encoding="utf-8")
    (OUT / "from.txt").write_text(f"{FROM_NAME} <{FROM_EMAIL}>\n", encoding="utf-8")
    (OUT / "to.txt").write_text((to_email or "PASTE_RECIPIENT@company.com") + "\n", encoding="utf-8")
    meta = {
        "schema": "aeg-outbound-send-pack-v1",
        "lane": "AEG_PROOF",
        "proof_url": proof_url,
        "evidence_id": manifest.get("evidence_id"),
        "aeg_bundle": manifest.get("bundle_dir"),
        "from_email": FROM_EMAIL,
        "subject": subject,
        "to": to_email or None,
        "recipient_name": recipient_name or None,
        "founder_approved_at": _now(),
        "status": "draft_opened",
    }
    (OUT / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def record_receipt(meta: dict) -> None:
    receipt = {
        "schema": "aeg-outbound-send-receipt-v1",
        "founder_approved": True,
        "approved_at": meta["founder_approved_at"],
        "send_mode": "mail_draft_opened",
        "proof_url": meta["proof_url"],
        "evidence_id": meta.get("evidence_id"),
        "pack_dir": str(OUT),
        "status": "awaiting_founder_send_click",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def open_mail_draft(*, subject: str, body: str, to_email: str) -> None:
    from commercial_mail_draft_v1 import open_commercial_mail_draft  # noqa: WPS433

    open_commercial_mail_draft(
        subject=subject,
        body=body,
        to_email=to_email,
        from_email=FROM_EMAIL,
        from_name=FROM_NAME,
        lane="AEG",
        context="AEG proof outbound Mail",
    )


def main() -> int:
    proof_url = ""
    to_email = ""
    recipient_name = ""
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--proof-url" and i + 1 < len(args):
            proof_url = args[i + 1].strip()
            i += 2
        elif args[i] in ("--to", "-t") and i + 1 < len(args):
            to_email = args[i + 1].strip()
            i += 2
        elif args[i] in ("--name", "-n") and i + 1 < len(args):
            recipient_name = args[i + 1].strip()
            i += 2
        elif args[i] in ("-h", "--help"):
            print("Usage: send_aeg_proof_outbound_v1.py [--proof-url URL] [--to email] [--name First]")
            return 0
        else:
            i += 1

    url, manifest = _load_proof_url(proof_url)
    meta = write_pack(proof_url=url, manifest=manifest, to_email=to_email, recipient_name=recipient_name)
    record_receipt(meta)
    subject = (OUT / "subject.txt").read_text(encoding="utf-8").strip()
    body = (OUT / "body.txt").read_text(encoding="utf-8")
    try:
        open_mail_draft(subject=subject, body=body, to_email=to_email)
    except subprocess.CalledProcessError as exc:
        print(f"WARN: Mail draft failed ({exc}) — pack at {OUT}")
        print(f"PROOF_URL={url}")
        return 0

    print(f"OK: AEG outbound draft opened · proof_url={url}")
    print(f"PACK={OUT}")
    print(f"RECEIPT={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
