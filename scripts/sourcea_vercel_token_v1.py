#!/usr/bin/env python3
"""SourceA-only Vercel Hobby auth — Gate K free path (no paid Cloudflare).

Auth order: ~/.sina/sourcea-vercel-token-v1.json → Vercel CLI OAuth session.
Law: FOUNDER_NO_CREDIT_CARD_INFRA — Vercel Hobby allowed · $0 · no card.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
TOKEN_FILE = SINA / "sourcea-vercel-token-v1.json"
DEFAULT_PROJECT = os.environ.get("SOURCEA_VERCEL_PROJECT", "source-a")
DEFAULT_SCOPE = os.environ.get("SOURCEA_VERCEL_SCOPE", "the-777-foundation")
TRIAL_SCOPE = "noetfield-systems"
TRIAL_WHOAMI_PREFIX = "noetfield"


def _vercel_cmd() -> list[str]:
    from shutil import which

    if which("vercel"):
        return ["vercel"]
    return ["npx", "--yes", "vercel"]


def vercel_cli_whoami() -> str | None:
    """Return Vercel username/team slug if CLI OAuth session is active."""
    try:
        proc = subprocess.run(
            _vercel_cmd() + ["whoami"],
            capture_output=True,
            text=True,
            timeout=45,
        )
        if proc.returncode != 0:
            return None
        for line in (proc.stdout or "").splitlines():
            line = line.strip()
            if line and not line.startswith("Vercel CLI"):
                return line
    except (OSError, subprocess.TimeoutExpired):
        return None
    return None


def load_sourcea_vercel_config() -> dict[str, Any]:
    if TOKEN_FILE.is_file():
        try:
            row = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"ok": False, "error": "invalid_json", "detail": str(exc), "path": str(TOKEN_FILE)}

        tok = str(row.get("token") or row.get("vercel_token") or "").strip()
        if tok:
            return {
                "ok": True,
                "auth_mode": "token_file",
                "token": tok,
                "project": str(row.get("project") or DEFAULT_PROJECT).strip() or DEFAULT_PROJECT,
                "scope": str(row.get("scope") or DEFAULT_SCOPE).strip() or DEFAULT_SCOPE,
                "path": str(TOKEN_FILE),
                "schema": str(row.get("schema") or "sourcea-vercel-token-v1"),
                "cost": "free_hobby",
            }

    who = vercel_cli_whoami()
    if who:
        trial_cli = who.lower().startswith(TRIAL_WHOAMI_PREFIX)
        scope = DEFAULT_SCOPE
        ok = True
        note = "Vercel CLI OAuth session — main team the-777-foundation"
        if trial_cli:
            ok = False
            note = (
                f"CLI still on TRIAL ({who}) — run: bash scripts/switch_vercel_cli_main_v1.sh"
            )
        return {
            "ok": ok,
            "auth_mode": "cli_oauth",
            "token": None,
            "whoami": who,
            "project": DEFAULT_PROJECT,
            "scope": scope,
            "path": None,
            "cost": "free_hobby",
            "trial_cli": trial_cli,
            "note": note,
            "error": "trial_cli_logged_in" if trial_cli else None,
        }

    return {
        "ok": False,
        "error": "missing_vercel_auth",
        "path": str(TOKEN_FILE),
        "founder_line": (
            "Gate K (free) — create Vercel token on dashboard OR run vercel login"
        ),
        "fix_steps": [
            "Main account (kazemnezhadsina144@gmail.com · the-777-foundation):",
            "  bash scripts/switch_vercel_cli_main_v1.sh --terminal",
            "  OR create token: https://vercel.com/account/settings/tokens",
            "  bash scripts/switch_vercel_cli_main_v1.sh --token '<paste-once>'",
            "Then: python3 scripts/gate_k_vercel_start_v1.py --json",
        ],
        "fix_url": "https://vercel.com/account/settings/tokens",
    }


def save_sourcea_vercel_token(
    token: str,
    *,
    project: str = DEFAULT_PROJECT,
    name: str = "SourceA Gate K",
) -> dict[str, Any]:
    tok = token.strip()
    if not tok:
        return {"ok": False, "error": "empty_token"}
    row = {
        "schema": "sourcea-vercel-token-v1",
        "name": name,
        "token": tok,
        "project": project,
        "scope": os.environ.get("SOURCEA_VERCEL_SCOPE", DEFAULT_SCOPE),
        "lane": "sourcea_only",
        "cost": "free_hobby",
    }
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    os.chmod(TOKEN_FILE, 0o600)
    return {"ok": True, "path": str(TOKEN_FILE), "project": project}
