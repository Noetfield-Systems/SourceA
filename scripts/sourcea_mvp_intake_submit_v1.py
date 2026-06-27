#!/usr/bin/env python3
"""Business A — 48h MVP service intake (commercial plane only).

Validate · persist disk receipt · optional Resend notify.
Law: data/sourcea-dual-plane-v1.json · NOT brain-os governance.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "sourcea-mvp-intake-schema-v1.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _inbox_dir() -> Path:
    schema = _load_schema()
    rel = str(schema.get("inbox_dir") or "data/commercial-intake/inbox")
    d = ROOT / rel
    d.mkdir(parents=True, exist_ok=True)
    return d


def validate_intake(body: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    schema = _load_schema()
    fields = schema.get("fields") or {}
    errors: list[str] = []
    clean: dict[str, Any] = {}

    for key, spec in fields.items():
        if not isinstance(spec, dict):
            continue
        raw = body.get(key)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            if spec.get("required"):
                errors.append(f"{key}_required")
            continue
        val = str(raw).strip() if not isinstance(raw, str) else raw.strip()
        max_len = int(spec.get("max_len") or 0)
        if max_len and len(val) > max_len:
            errors.append(f"{key}_too_long")
            continue
        ftype = spec.get("type")
        if ftype == "enum":
            allowed = spec.get("values") or []
            if val not in allowed:
                errors.append(f"{key}_invalid")
                continue
        elif ftype == "email":
            if not EMAIL_RE.match(val):
                errors.append(f"{key}_invalid")
                continue
            val = val.lower()
        clean[key] = val

    if not clean.get("building"):
        errors.append("building_required")
    if not clean.get("email"):
        errors.append("email_required")
    if not clean.get("deadline"):
        errors.append("deadline_required")
    if not clean.get("budget"):
        errors.append("budget_required")

    return clean, errors


def _human_deadline(v: str) -> str:
    return {
        "this_week": "This week",
        "two_weeks": "2 weeks",
        "flexible": "Flexible",
    }.get(v, v)


def _human_budget(v: str) -> str:
    return {
        "500_1k": "$500–$1k",
        "1k_3k": "$1k–$3k",
        "3k_10k": "$3k–$10k",
        "lets_talk": "Let's talk",
    }.get(v, v)


def _send_resend(*, intake_id: str, row: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    if not api_key:
        return {"ok": False, "skipped": True, "reason": "RESEND_API_KEY_missing"}

    schema = _load_schema()
    to_addr = str(schema.get("notify_to") or "hello@sourcea.app")
    from_addr = str(schema.get("notify_from") or "SourceA Intake <onboarding@resend.dev>")

    building = row.get("building") or ""
    btype = row.get("building_type") or ""
     = row.get("") or "—"
    subject = f"[48h MVP] {building[:60]}{'…' if len(building) > 60 else ''}"
    text = "\n".join(
        [
            f"Intake ID: {intake_id}",
            f"Building: {building}",
            f"Type: {btype or '—'}",
            f"/example: {}",
            f"Deadline: {_human_deadline(str(row.get('deadline') or ''))}",
            f"Budget: {_human_budget(str(row.get('budget') or ''))}",
            f"Email: {row.get('email')}",
            "",
            "Commercial plane — Business A (48h MVP service)",
        ]
    )
    payload = json.dumps(
        {
            "from": from_addr,
            "to": [to_addr],
            "reply_to": row.get("email"),
            "subject": subject,
            "text": text,
        }
    ).encode("utf-8")
    req = request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "resend_id": body.get("id")}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return {"ok": False, "error": "resend_http_error", "status": exc.code, "detail": detail}
    except Exception as exc:
        return {"ok": False, "error": "resend_failed", "message": str(exc)[:200]}


def submit_mvp_intake(body: dict[str, Any], *, channel: str = "api") -> dict[str, Any]:
    clean, errors = validate_intake(body if isinstance(body, dict) else {})
    if errors:
        return {
            "ok": False,
            "schema": "sourcea-mvp-intake-receipt-v1",
            "errors": errors,
            "end_screen": None,
        }

    intake_id = f"mvp-{uuid.uuid4().hex[:12]}"
    receipt = {
        "schema": "sourcea-mvp-intake-receipt-v1",
        "ok": True,
        "intake_id": intake_id,
        "at": _now(),
        "channel": channel,
        "plane": "commercial",
        "business": "48h-mvp-service",
        "intake": clean,
        "end_screen": _load_schema().get("end_screen"),
    }
    notify = _send_resend(intake_id=intake_id, row=clean)
    receipt["notify"] = notify

    inbox_file = _inbox_dir() / f"{intake_id}.json"
    inbox_file.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["inbox_path"] = str(inbox_file.relative_to(ROOT))
    return receipt


def self_test() -> dict[str, Any]:
    sample = {
        "building": "App Store fitness app with AI coach",
        "building_type": "app",
        "": "https://example.com",
        "deadline": "this_week",
        "budget": "3k_10k",
        "email": "founder@example.com",
    }
    row = submit_mvp_intake(sample, channel="self_test")
    return {"ok": bool(row.get("ok")), "receipt": row}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[mvp-intake] " + (fmt % args) + "\n")

    def _cors(self) -> None:
        origin = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origin or "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/api/commercial/mvp-intake/v1":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            body = {}
        row = submit_mvp_intake(body if isinstance(body, dict) else {}, channel="local_http")
        code = 200 if row.get("ok") else 400
        payload = json.dumps(row, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def serve(*, port: int) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"mvp-intake dev server http://127.0.0.1:{port}/api/commercial/mvp-intake/v1")
    httpd.serve_forever()


def main() -> int:
    ap = argparse.ArgumentParser(description="48h MVP commercial intake")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8192)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        row = self_test()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("OK" if row.get("ok") else "FAIL", row.get("receipt", {}).get("intake_id"))
        return 0 if row.get("ok") else 1

    if args.serve:
        serve(port=args.port)
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
