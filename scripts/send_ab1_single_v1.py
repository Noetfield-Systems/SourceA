#!/usr/bin/env python3
"""AB1 single send — Asset B outreach. Opens Mail draft from hello@sourcea.app."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUT = SINA / "outbound" / "ab1-send-001"
RECEIPT = SINA / "ab1-outbound-send-receipt-v1.json"

# Locked sender — SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md
FROM_EMAIL = "hello@sourcea.app"
FROM_NAME = "SourceA"
COMPANY_URL = "https://sourcea.com"
FOUNDER_NAME = os.environ.get("SOURCEA_FOUNDER_NAME", "Sina Kazemnezhad").strip() or "Sina Kazemnezhad"
OPT_OUT_LINE = 'Reply "stop" and I won\'t follow up.'

VARIANTS: dict[str, dict[str, str]] = {
    "polished_proof_led": {
        "subject": "Can you prove what your agents executed last night?",
        "body": """Hi{name_greeting},

Quick question for teams shipping Cursor agents for clients: when something goes wrong, can you prove what ran, what was blocked, and whether it is safe to run again tomorrow?

We run a self-healing multi-agent factory every day — policy before execution, signed receipts on disk — and build the same for clients:

• Agent Loop Build — one governed loop live in 2–3 weeks ($3–10K project)
• Agent Loop Retainer — weekly proof export + ongoing ops ($2–5K/month)

No deck. Happy to screen-share today's receipts in 15 minutes: PASS/BLOCK gate, export bundle, replay.

Worth a look?

—
{founder_name}
SourceA · governed agentic automation
{from_email}
{company_url}

{opt_out}
""",
    },
    "short_punchy": {
        "subject": "Receipts for your agent loops?",
        "body": """Hi{name_greeting},

Your Cursor agents run. Can you prove what they executed last night?

We ship governed agent loops with signed receipts — $3–10K build or $2–5K/mo retainer. Fifteen-minute screen-share, no deck.

Interested?

—
{founder_name}
SourceA · governed agentic automation
{from_email}
{company_url}

{opt_out}
""",
    },
}

DEFAULT_VARIANT = "polished_proof_led"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _format_body(template: str, *, recipient_name: str) -> str:
    name_greeting = f" {recipient_name.strip()}" if recipient_name.strip() else ""
    return template.format(
        name_greeting=name_greeting,
        founder_name=FOUNDER_NAME,
        from_email=FROM_EMAIL,
        company_url=COMPANY_URL,
        opt_out=OPT_OUT_LINE,
    )


def write_pack(*, to_email: str = "", recipient_name: str = "", variant: str = DEFAULT_VARIANT) -> dict:
    if variant not in VARIANTS:
        raise SystemExit(f"Unknown variant {variant!r} — use: {', '.join(VARIANTS)}")
    spec = VARIANTS[variant]
    subject = spec["subject"]
    body = _format_body(spec["body"], recipient_name=recipient_name)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "subject.txt").write_text(subject + "\n", encoding="utf-8")
    (OUT / "body.txt").write_text(body, encoding="utf-8")
    (OUT / "from.txt").write_text(f"{FROM_NAME} <{FROM_EMAIL}>\n", encoding="utf-8")
    (OUT / "to.txt").write_text((to_email or "PASTE_RECIPIENT@company.com") + "\n", encoding="utf-8")
    meta = {
        "schema": "ab1-outbound-send-pack-v1",
        "lane": "AB1",
        "variant": variant,
        "from_email": FROM_EMAIL,
        "from_name": FROM_NAME,
        "founder_name": FOUNDER_NAME,
        "subject": subject,
        "to": to_email or None,
        "recipient_name": recipient_name or None,
        "casl_opt_out": OPT_OUT_LINE,
        "founder_approved_at": _now(),
        "send_policy": "one_relevant_agency_at_a_time",
        "status": "draft_opened",
        "law": "SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md",
    }
    (OUT / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def record_receipt(meta: dict) -> None:
    receipt = {
        "schema": "ab1-outbound-send-receipt-v1",
        "founder_approved": True,
        "approved_at": meta["founder_approved_at"],
        "sent_by": "agent",
        "send_mode": "mail_draft_opened",
        "from_email": FROM_EMAIL,
        "variant": meta.get("variant"),
        "ab1_status": "awaiting_founder_send_click",
        "pack_dir": str(OUT),
        "subject": meta["subject"],
        "law": "SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md §6",
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
        lane="AB1",
        context="AB1 outbound Mail",
    )


def main() -> int:
    to_email = ""
    recipient_name = ""
    variant = DEFAULT_VARIANT
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("--to", "-t") and i + 1 < len(args):
            to_email = args[i + 1].strip()
            i += 2
        elif args[i] in ("--name", "-n") and i + 1 < len(args):
            recipient_name = args[i + 1].strip()
            i += 2
        elif args[i] == "--variant" and i + 1 < len(args):
            variant = args[i + 1].strip()
            i += 2
        elif args[i] in ("-h", "--help"):
            print("Usage: send_ab1_single_v1.py --to email@co.com --name Alex [--variant polished_proof_led|short_punchy]")
            print(f"Default variant: {DEFAULT_VARIANT} · From: {FROM_EMAIL}")
            return 0
        else:
            if "@" in args[i]:
                to_email = args[i].strip()
            i += 1

    if not recipient_name.strip():
        print("WARN: --name missing — draft will open as 'Hi,' (looks like a blast). Use --name FirstName", file=sys.stderr)

    meta = write_pack(to_email=to_email, recipient_name=recipient_name, variant=variant)
    record_receipt(meta)
    body = (OUT / "body.txt").read_text(encoding="utf-8")
    subject = (OUT / "subject.txt").read_text(encoding="utf-8").strip()
    try:
        open_mail_draft(subject=subject, body=body, to_email=to_email)
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: Mail draft blocked ({exc})", file=sys.stderr)
        print(f"Add {FROM_EMAIL} to Mail.app before AB1 send — never personal Gmail.", file=sys.stderr)
        return 1

    print(f"OK: AB1 draft opened · variant={variant} · from={FROM_EMAIL} · pack={OUT}")
    print("Founder: verify hello@sourcea.app · populate --name · one relevant agency · Send")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
