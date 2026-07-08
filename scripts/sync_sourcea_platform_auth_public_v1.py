#!/usr/bin/env python3
"""Emit public SourceA platform auth config (Supabase URL + anon key only).

Law: never write service_role or DB passwords to the landing tree.
Secrets: ~/.sourcea-secrets/portfolio-spine.env
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SourceA-landing" / "green-unified" / "data" / "sourcea-platform-auth-config-v1.json"
SECRETS = Path.home() / ".sourcea-secrets" / "portfolio-spine.env"


def _parse_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Z0-9_]+)=(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
        out[key] = val
    return out


def sync() -> dict:
    env = _parse_env(SECRETS)
    url = (env.get("SUPABASE_URL") or "").rstrip("/")
    anon = env.get("SUPABASE_ANON_KEY") or env.get("SUPABASE_PUBLISHABLE_KEY") or ""
    row = {
        "schema": "sourcea-platform-auth-config-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "configured": bool(url and anon),
        "venture": "sourcea",
        "supabase_url": url,
        "supabase_anon_key": anon,
        "callback_path": "/auth/callback",
        "redirect_path": "/auth/sign-in",
        "redirect_urls": [
            "https://sourcea.app/auth/callback",
            "https://sourcea.app/auth/sign-in",
            "https://sourcea.app/auth/sign-up",
            "https://sourcea.app/auth/sign-out",
            "https://sourcea.app/sourcea/forge/terminal/signin",
            "https://sourcea.app/sourcea/forge/terminal/signup",
            "https://sourcea.app/sourcea/forge/terminal/profile",
            "https://sourcea.app/sourcea/forge/terminal/workspace",
        ],
        "supabase_callback_url": f"{url}/auth/v1/callback" if url else "",
        "site_url": "https://sourcea.app",
        "oauth_providers": ["google", "github"],
        "auth_features": ["oauth", "email_password", "magic_link", "password_reset"],
        "tier": "portfolio-spine",
        "cross_domain_ssot": "data/cross-domain-auth-surfaces-v1.json",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(OUT), "configured": row["configured"]}


def main() -> int:
    row = sync()
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
