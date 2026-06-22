#!/usr/bin/env python3
"""Portfolio Mail Hub — unified inbox + send for all 15 Google Workspace mailboxes."""
from __future__ import annotations

import email
import imaplib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from email.header import decode_header
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

try:
    import aiosmtplib
except ImportError:
    aiosmtplib = None  # type: ignore[assignment,misc]

SOURCE_A = Path(__file__).resolve().parents[1]
SSOT = SOURCE_A / "data" / "portfolio-vault-email-tags-v1.json"
RECEIPT = Path.home() / ".sina" / "portfolio-inbox-check-v1.json"
VAULT_FILES = (
    Path.home() / ".sina" / "secrets.env",
    Path.home() / "Desktop/SinaPromptOS/secrets.env",
)

FORBIDDEN_BODY = re.compile(
    r"google\s*workspace|google_workspace|smtp\s*lock|provider\s*:|msb\s*wave|app\s*password",
    re.I,
)

DOMAIN_ACCENT = {
    "trustfield.ca": "#0d9488",
    "noetfield.com": "#6366f1",
    "sourcea.com": "#4f46e5",
    "virlux.com": "#059669",
    "witnessbc.com": "#c2410c",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_vault_key(key: str) -> str:
    for path in VAULT_FILES:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, _, v = s.partition("=")
            if k.strip() == key:
                return v.strip().strip('"').strip("'")
    return ""


def _dec_header(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out: list[str] = []
    for frag, enc in parts:
        if isinstance(frag, bytes):
            out.append(frag.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(str(frag))
    return "".join(out)


def _parse_when(raw: str | None) -> str:
    if not raw:
        return "?"
    try:
        return parsedate_to_datetime(raw).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OverflowError):
        return raw or "?"


def load_mailboxes() -> list[dict[str, Any]]:
    data = json.loads(SSOT.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for dom in data.get("domains") or []:
        domain = str(dom.get("domain") or "")
        brand = str(dom.get("brand") or "")
        brand_code = str(dom.get("brand_code") or "")
        lane_id = str(dom.get("lane_id") or "")
        for mb in dom.get("mailboxes") or []:
            local = str(mb.get("localpart") or "").lower()
            address = f"{local}@{domain}"
            rows.append(
                {
                    "address": address,
                    "domain": domain,
                    "brand": brand,
                    "brand_code": brand_code,
                    "lane_id": lane_id,
                    "role": mb.get("role"),
                    "vault_tag": mb.get("vault_tag"),
                    "export_env": mb.get("export_env"),
                    "accent": DOMAIN_ACCENT.get(domain, "#64748b"),
                }
            )
    return rows


def password_for(row: dict[str, Any]) -> str:
    env = str(row.get("export_env") or "")
    pw = os.environ.get(env, "").strip() or _read_vault_key(str(row.get("vault_tag") or ""))
    if pw:
        return pw
    if row.get("address") == "hello@trustfield.ca":
        return (
            os.environ.get("GOOGLE_WORKSPACE_APP_PASSWORD", "").strip()
            or _read_vault_key("GOOGLE_WORKSPACE_APP_PASSWORD")
            or _read_vault_key("TF-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD")
        )
    return ""


def _find_mailbox(address: str) -> dict[str, Any] | None:
    want = address.strip().lower()
    for row in load_mailboxes():
        if row["address"].lower() == want:
            return row
    return None


def fetch_inbox(address: str, limit: int = 20) -> dict[str, Any]:
    row = _find_mailbox(address)
    if not row:
        return {"ok": False, "error": "unknown mailbox", "address": address}
    pw = password_for(row)
    if not pw:
        return {
            "ok": False,
            "error": "no app password in vault",
            "address": address,
            "vault_tag": row.get("vault_tag"),
            "status": "skip",
        }
    result: dict[str, Any] = {
        "ok": False,
        "address": address,
        "brand": row.get("brand"),
        "role": row.get("role"),
        "accent": row.get("accent"),
        "messages_total": 0,
        "messages": [],
        "status": "fail",
    }
    try:
        client = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        client.login(address, pw)
        client.select("INBOX")
        _typ, data = client.search(None, "ALL")
        ids = data[0].split() if data and data[0] else []
        result["messages_total"] = len(ids)
        for num in reversed(ids[-max(1, limit) :]):
            _typ, msg_data = client.fetch(num, "(RFC822)")
            if _typ != "OK" or not msg_data or not msg_data[0]:
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            body_preview = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_preview = payload.decode("utf-8", errors="replace")[:400]
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body_preview = payload.decode("utf-8", errors="replace")[:400]
            result["messages"].append(
                {
                    "when": _parse_when(msg.get("Date")),
                    "from": _dec_header(msg.get("From"))[:240],
                    "subject": _dec_header(msg.get("Subject"))[:240],
                    "preview": body_preview.strip(),
                }
            )
        client.logout()
        result["ok"] = True
        result["status"] = "ok"
    except imaplib.IMAP4.error as exc:
        result["error"] = f"IMAP: {exc}"
    except OSError as exc:
        result["error"] = f"network: {exc}"
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
    return result


def overview(limit: int = 6, wire: bool = True) -> dict[str, Any]:
    mailboxes: list[dict[str, Any]] = []
    summary = {"total": 0, "ok": 0, "skip": 0, "fail": 0}
    for row in load_mailboxes():
        summary["total"] += 1
        pw = password_for(row)
        entry = {**row, "status": "skip", "messages_total": 0, "recent": [], "wired": bool(pw)}
        if not pw:
            summary["skip"] += 1
            mailboxes.append(entry)
            continue
        inbox = fetch_inbox(row["address"], limit=limit)
        entry["status"] = inbox.get("status", "fail")
        entry["messages_total"] = inbox.get("messages_total", 0)
        entry["recent"] = inbox.get("messages", [])
        if inbox.get("ok"):
            summary["ok"] += 1
        else:
            summary["fail"] += 1
            entry["error"] = inbox.get("error")
        mailboxes.append(entry)

    report = {
        "schema": "portfolio-mail-hub-v1",
        "checked_at": _now(),
        "ssot": str(SSOT),
        "summary": summary,
        "domains": _group_by_domain(mailboxes),
        "mailboxes": mailboxes,
    }
    if wire:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _group_by_domain(mailboxes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_domain: dict[str, dict[str, Any]] = {}
    for mb in mailboxes:
        d = mb["domain"]
        if d not in by_domain:
            by_domain[d] = {
                "domain": d,
                "brand": mb.get("brand"),
                "brand_code": mb.get("brand_code"),
                "accent": mb.get("accent"),
                "lane_id": mb.get("lane_id"),
                "mailboxes": [],
            }
        by_domain[d]["mailboxes"].append(mb)
    return list(by_domain.values())


def _from_header(row: dict[str, Any]) -> str:
    brand = str(row.get("brand") or "Portfolio")
    return f"{brand} <{row['address']}>"


async def send_message(
    *,
    from_address: str,
    to: str,
    subject: str,
    body: str,
    html: str | None = None,
) -> dict[str, Any]:
    if aiosmtplib is None:
        return {"ok": False, "error": "aiosmtplib not installed"}
    row = _find_mailbox(from_address)
    if not row:
        return {"ok": False, "error": "unknown from address"}
    pw = password_for(row)
    if not pw:
        return {"ok": False, "error": "no app password for sender"}
    to = to.strip()
    subject = subject.strip()
    body = body.strip()
    if not to or "@" not in to:
        return {"ok": False, "error": "invalid recipient"}
    if not subject or not body:
        return {"ok": False, "error": "subject and body required"}
    if FORBIDDEN_BODY.search(subject) or FORBIDDEN_BODY.search(body):
        return {"ok": False, "error": "remove internal stack words from outbound copy"}

    msg = EmailMessage()
    msg["From"] = _from_header(row)
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            username=from_address,
            password=pw,
            start_tls=True,
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}

    mid = uuid.uuid4().hex[:16]
    result = {
        "ok": True,
        "from": _from_header(row),
        "to": to,
        "subject": subject,
        "dispatch_ref": f"pmh:{mid}",
        "sent_at": _now(),
    }
    try:
        from portfolio_mail_integration_wire_v1 import notify_mail_sent  # noqa: WPS433

        result["integration"] = notify_mail_sent(result)
    except Exception as exc:  # noqa: BLE001
        result["integration"] = {"ok": False, "error": str(exc)}
    return result


def handle_get(query: dict[str, list[str]]) -> dict[str, Any]:
    address = (query.get("address") or [""])[0].strip()
    limit_s = (query.get("limit") or ["6"])[0]
    try:
        limit = max(1, min(50, int(limit_s)))
    except ValueError:
        limit = 6
    if address:
        return fetch_inbox(address, limit=limit)
    return overview(limit=limit, wire=True)


async def handle_post(body: dict[str, Any]) -> dict[str, Any]:
    return await send_message(
        from_address=str(body.get("from_address") or body.get("from") or ""),
        to=str(body.get("to") or ""),
        subject=str(body.get("subject") or ""),
        body=str(body.get("body") or body.get("text") or ""),
        html=str(body.get("html") or "") or None,
    )


def integration_status() -> dict[str, Any]:
    try:
        from portfolio_mail_integration_wire_v1 import wire_status  # noqa: WPS433

        return wire_status()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "wired": False, "error": str(exc)}


def integration_wire(*, import_cursor: bool = False) -> dict[str, Any]:
    from portfolio_mail_integration_wire_v1 import wire_all  # noqa: WPS433

    return wire_all(import_cursor=import_cursor)
