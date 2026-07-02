#!/usr/bin/env python3
"""SourceA-only Cloudflare Pages token loader — optional Gate K path.

Default Gate K: Vercel Hobby (gate_k_vercel_start_v1.py) — free, no Cloudflare.
CF Pages is also $0 (free tier, not paid) if you prefer Cloudflare hosting.

Law: SourceA ≠ TrustField ≠ Noetfield ≠ WitnessBC.
Never use ~/.sina/secrets.env CF_API_TOKEN (TrustField zone scope).

Canonical: ~/.sina/cf-pages-token-v1.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
TOKEN_FILE = SINA / "cf-pages-token-v1.json"
DEFAULT_PROJECT = os.environ.get("SOURCEA_PAGES_PROJECT", "sourcea-landing")
DEFAULT_ZONE = "sourcea.com"

FORBIDDEN_TOKEN_SOURCES = (
    "secrets.env CF_API_TOKEN",
    "TrustField zone token",
    "Noetfield zone token",
    "WitnessBC zone token",
)


def load_sourcea_cf_config() -> dict[str, Any]:
    """Load SourceA Pages token — fail closed if missing."""
    ci_token = str(os.environ.get("CLOUDFLARE_API_TOKEN") or "").strip()
    if ci_token and os.environ.get("GITHUB_ACTIONS") == "true":
        return {
            "ok": True,
            "api_token": ci_token,
            "account_id": str(os.environ.get("CLOUDFLARE_ACCOUNT_ID") or "0d0b967b77e2e5535455d39ff3dae72c").strip(),
            "zone_name": DEFAULT_ZONE,
            "project": str(os.environ.get("SOURCEA_PAGES_PROJECT") or DEFAULT_PROJECT).strip(),
            "path": "env:CLOUDFLARE_API_TOKEN",
            "schema": "sourcea-cf-pages-token-v1",
            "auth_mode": "github_actions_secret",
        }
    if not TOKEN_FILE.is_file():
        return {
            "ok": False,
            "error": "missing_sourcea_token_file",
            "path": str(TOKEN_FILE),
            "founder_line": (
                "Optional CF Pages path — SourceA Cloudflare token file missing. "
                "Default Gate K is Vercel Hobby (free): gate_k_vercel_start_v1.py"
            ),
            "fix_steps": [
                "Preferred (no Cloudflare): python3 scripts/gate_k_vercel_start_v1.py --json",
                "Or CF Pages free tier ($0, not paid): log into SourceA Cloudflare account",
                "My Profile → API Tokens → Create Token",
                "Permissions: Account · Cloudflare Pages · Edit + Account · Account Settings · Read",
                f"Save ONLY to {TOKEN_FILE}",
                'Format: {"schema":"sourcea-cf-pages-token-v1","api_token":"...","account_id":"...","zone_name":"sourcea.com","project":"sourcea-landing"}',
                "Never reuse TrustField CF_API_TOKEN from secrets.env",
                "Then: python3 scripts/gate_k_pages_start_v1.py --json",
            ],
            "fix_url": "https://dash.cloudflare.com/profile/api-tokens",
        }
    try:
        row = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "error": "invalid_token_file",
            "path": str(TOKEN_FILE),
            "detail": str(exc),
            "founder_line": f"Gate K blocked — fix {TOKEN_FILE} JSON",
        }

    tok = str(row.get("api_token") or row.get("token") or "").strip()
    if not tok:
        return {
            "ok": False,
            "error": "empty_api_token",
            "path": str(TOKEN_FILE),
            "founder_line": "Gate K blocked — api_token missing in cf-pages-token-v1.json",
        }

    zone = str(row.get("zone_name") or DEFAULT_ZONE).strip()
    allowed_zones = {"sourcea.com", "www.sourcea.com", "sourcea.app", "www.sourcea.app"}
    if zone and zone not in allowed_zones:
        return {
            "ok": False,
            "error": "wrong_zone",
            "zone_name": zone,
            "founder_line": f"Gate K blocked — token file zone must be sourcea.com or sourcea.app (got {zone})",
        }

    return {
        "ok": True,
        "api_token": tok,
        "account_id": str(row.get("account_id") or "").strip() or None,
        "zone_name": zone or DEFAULT_ZONE,
        "zone_id": str(row.get("zone_id") or "").strip() or None,
        "project": str(row.get("project") or DEFAULT_PROJECT).strip() or DEFAULT_PROJECT,
        "path": str(TOKEN_FILE),
        "schema": str(row.get("schema") or "sourcea-cf-pages-token-v1"),
    }


def wrangler_env() -> dict[str, str]:
    cfg = load_sourcea_cf_config()
    if not cfg.get("ok"):
        raise SystemExit(cfg.get("founder_line") or "FAIL: SourceA CF token missing")
    env = dict(os.environ)
    env["CLOUDFLARE_API_TOKEN"] = str(cfg["api_token"])
    if cfg.get("account_id"):
        env["CLOUDFLARE_ACCOUNT_ID"] = str(cfg["account_id"])
    return env


def api_token() -> str | None:
    cfg = load_sourcea_cf_config()
    return str(cfg["api_token"]) if cfg.get("ok") else None
