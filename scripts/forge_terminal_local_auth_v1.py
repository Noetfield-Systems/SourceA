#!/usr/bin/env python3
"""Local auth token for Forge Terminal standalone — localhost POST guard."""
from __future__ import annotations

import json
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
TOKEN_PATH = SINA / "forge-terminal-local-token-v1.json"
SCHEMA = "forge-terminal-local-token-v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_token_doc() -> dict:
    if not TOKEN_PATH.is_file():
        return {}
    try:
        return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_token() -> str:
    return str(load_token_doc().get("token") or "").strip()


def ensure_token(*, force: bool = False) -> str:
    doc = load_token_doc()
    token = str(doc.get("token") or "").strip()
    if token and not force:
        return token
    token = secrets.token_urlsafe(32)
    doc = {
        "schema": SCHEMA,
        "token": token,
        "created_at": doc.get("created_at") or _now(),
        "updated_at": _now(),
        "id": doc.get("id") or str(uuid.uuid4()),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    try:
        TOKEN_PATH.chmod(0o600)
    except OSError:
        pass
    return token


def auth_enabled() -> bool:
    return bool(load_token()) or bool(
        __import__("os").environ.get("FORGE_TERMINAL_STANDALONE", "").strip()
    )


def verify_request(headers: dict | None) -> tuple[bool, str]:
    """Return (ok, error_code). Disabled when no standalone flag and no token file."""
    import os

    standalone = os.environ.get("FORGE_TERMINAL_STANDALONE", "").strip() in ("1", "true", "yes")
    token = load_token()
    if not token:
        if standalone:
            token = ensure_token()
        else:
            return True, ""
    got = ""
    if headers:
        got = str(headers.get("X-Forge-Token") or headers.get("x-forge-token") or "").strip()
    if got == token:
        return True, ""
    return False, "forge_auth_required"


def health_auth_payload() -> dict:
    import os

    if os.environ.get("FORGE_TERMINAL_STANDALONE", "").strip() not in ("1", "true", "yes"):
        return {}
    return {"forge_local_token": ensure_token()}
