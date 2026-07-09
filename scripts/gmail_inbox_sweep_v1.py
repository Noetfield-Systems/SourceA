#!/usr/bin/env python3
"""Gmail inbox sweep → Supabase gmail_inbox_signals (migration 0012).

Auth: service account (Gmail API) or IMAP fallback via portfolio vault app passwords.
"""
from __future__ import annotations

import argparse
import base64
import email
import imaplib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.header import decode_header
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data/gmail-sweep-ssot-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _supabase_cfg() -> tuple[str, str]:
    _load_secrets()
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return url, key


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _decode_header(value: str | None) -> str:
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


def _load_service_account() -> dict[str, Any] | None:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    ssot = _read_json(SSOT)
    rel = str(ssot.get("service_account", {}).get("file_path") or "").replace("~", str(Path.home()))
    path = Path(rel)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _sa_access_token(sa: dict[str, Any], scopes: list[str]) -> str:
    try:
        import jwt  # type: ignore
    except ImportError:
        subprocess = __import__("subprocess")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyJWT", "cryptography", "-q"], check=False)
        import jwt  # type: ignore

    now = int(time.time())
    claim = {
        "iss": sa["client_email"],
        "sub": os.environ.get("GMAIL_DELEGATED_USER", "").strip()
        or _read_json(SSOT).get("service_account", {}).get("default_delegated_user", ""),
        "scope": " ".join(scopes),
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }
    assertion = jwt.encode(claim, sa["private_key"], algorithm="RS256")
    data = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        row = json.loads(resp.read().decode("utf-8"))
    token = row.get("access_token")
    if not token:
        raise RuntimeError(f"gmail_sa_token_failed:{row}")
    return str(token)


def _gmail_list_messages(token: str, user: str, query: str, max_results: int = 25) -> list[str]:
    import urllib.parse

    params = urllib.parse.urlencode({"q": query, "maxResults": str(max_results)})
    url = f"https://gmail.googleapis.com/gmail/v1/users/{urllib.parse.quote(user)}/messages?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        row = json.loads(resp.read().decode("utf-8"))
    return [str(m.get("id")) for m in (row.get("messages") or []) if m.get("id")]


def _gmail_get_message(token: str, user: str, msg_id: str) -> dict[str, Any]:
    import urllib.parse

    url = f"https://gmail.googleapis.com/gmail/v1/users/{urllib.parse.quote(user)}/messages/{msg_id}?format=full"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extract_body(payload: dict[str, Any]) -> str:
    def walk(part: dict[str, Any]) -> str:
        mime = part.get("mimeType", "")
        body = part.get("body") or {}
        data = body.get("data")
        if data and mime.startswith("text/"):
            try:
                return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
            except (ValueError, UnicodeDecodeError):
                return ""
        for child in part.get("parts") or []:
            if isinstance(child, dict):
                text = walk(child)
                if text:
                    return text
        return ""

    return walk(payload)[:12000]


def _imap_fetch_mailbox(mailbox: str, password: str, *, max_messages: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(mailbox, password)
    conn.select("INBOX")
    _typ, data = conn.search(None, "UNSEEN")
    ids = (data[0] or b"").split()[-max_messages:]
    for num in ids:
        _typ, msg_data = conn.fetch(num, "(RFC822)")
        if not msg_data or not msg_data[0]:
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body = payload.decode("utf-8", errors="replace")[:12000]
                        break
        else:
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                body = payload.decode("utf-8", errors="replace")[:12000]
        rows.append(
            {
                "gmail_message_id": f"imap-{mailbox}-{num.decode()}",
                "mailbox": mailbox,
                "thread_id": msg.get("Message-ID", ""),
                "subject": _decode_header(msg.get("Subject")),
                "from_addr": _decode_header(msg.get("From")),
                "snippet": (body or "")[:280],
                "body_text": body,
                "received_at": _decode_header(msg.get("Date")) or _now(),
                "sweep_source": "imap_fallback",
            }
        )
    conn.logout()
    return rows


def _vault_password(vault_tag: str) -> str:
    for path in (Path.home() / ".sina/secrets.env", Path.home() / ".sourcea-secrets/portfolio-spine.env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, _, v = s.partition("=")
            if k.strip() == vault_tag:
                return v.strip().strip('"').strip("'")
    return ""


def _load_mailboxes() -> list[dict[str, str]]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from portfolio_mail_hub_v1 import load_mailboxes  # noqa: WPS433

    out: list[dict[str, str]] = []
    for row in load_mailboxes():
        tag = str(row.get("vault_tag") or "")
        pwd = _vault_password(tag)
        if pwd:
            out.append({"address": str(row.get("address")), "vault_tag": tag, "password": pwd})
    return out


def _insert_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    url, key = _supabase_cfg()
    if not url or not key:
        return {"ok": False, "error": "supabase_not_configured", "inserted": 0}
    if not rows:
        return {"ok": True, "inserted": 0, "skipped": 0}
    payload = []
    for r in rows:
        payload.append(
            {
                "gmail_message_id": r["gmail_message_id"],
                "mailbox": r["mailbox"],
                "thread_id": r.get("thread_id"),
                "subject": r.get("subject"),
                "from_addr": r.get("from_addr"),
                "snippet": r.get("snippet"),
                "body_text": r.get("body_text"),
                "received_at": r.get("received_at"),
                "sweep_source": r.get("sweep_source", "gmail_api"),
                "processed": False,
            }
        )
    req = urllib.request.Request(
        f"{url}/rest/v1/gmail_inbox_signals",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "resolution=ignore-duplicates,return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            inserted = body if isinstance(body, list) else [body]
            return {"ok": True, "inserted": len(inserted)}
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        if exc.code == 409 or "duplicate" in err.lower():
            return {"ok": True, "inserted": 0, "duplicates": True}
        return {"ok": False, "status": exc.code, "error": err[:400], "inserted": 0}


def run_sweep(*, max_per_mailbox: int = 25) -> dict[str, Any]:
    ssot = _read_json(SSOT)
    collected: list[dict[str, Any]] = []
    mode = "none"
    errors: list[str] = []

    sa = _load_service_account()
    if sa:
        mode = "service_account"
        user = os.environ.get("GMAIL_DELEGATED_USER", "").strip() or str(
            ssot.get("service_account", {}).get("default_delegated_user", "")
        )
        scopes = list(ssot.get("service_account", {}).get("scopes") or ["https://www.googleapis.com/auth/gmail.readonly"])
        try:
            token = _sa_access_token(sa, scopes)
            query = str(ssot.get("sweep", {}).get("query") or "is:unread newer_than:7d")
            for msg_id in _gmail_list_messages(token, user, query, max_results=max_per_mailbox):
                full = _gmail_get_message(token, user, msg_id)
                headers = {h["name"]: h["value"] for h in full.get("payload", {}).get("headers", []) if h.get("name")}
                body = _extract_body(full.get("payload") or {})
                collected.append(
                    {
                        "gmail_message_id": msg_id,
                        "mailbox": user,
                        "thread_id": full.get("threadId"),
                        "subject": headers.get("Subject", ""),
                        "from_addr": headers.get("From", ""),
                        "snippet": str(full.get("snippet") or "")[:280],
                        "body_text": body,
                        "received_at": _now(),
                        "sweep_source": "gmail_api",
                    }
                )
        except Exception as exc:
            errors.append(f"service_account:{exc}"[:200])
            mode = "service_account_failed"

    if not collected:
        mode = "imap_fallback" if mode.startswith("service_account") else "imap_fallback"
        for mb in _load_mailboxes()[: int(ssot.get("sweep", {}).get("max_mailboxes_per_tick") or 8)]:
            try:
                collected.extend(
                    _imap_fetch_mailbox(
                        mb["address"],
                        mb["password"],
                        max_messages=max_per_mailbox,
                    )
                )
            except Exception as exc:
                errors.append(f"imap:{mb['address']}:{exc}"[:120])

    insert = _insert_rows(collected)
    production_connected = mode == "service_account"
    return {
        "schema": "gmail-inbox-sweep-v1",
        "ok": bool(insert.get("ok")),
        "at": _now(),
        "mode": mode,
        "production_connected": production_connected,
        "swept": len(collected),
        "insert": insert,
        "errors": errors,
        "report_line": (
            f"gmail_sweep · {mode} · swept={len(collected)} inserted={insert.get('inserted', 0)}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-per-mailbox", type=int, default=25)
    args = ap.parse_args()
    row = run_sweep(max_per_mailbox=args.max_per_mailbox)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
