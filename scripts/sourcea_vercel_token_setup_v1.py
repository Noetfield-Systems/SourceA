#!/usr/bin/env python3
"""Save + verify SourceA Vercel token from dashboard (Gate K).

Usage:
  python3 scripts/sourcea_vercel_token_setup_v1.py --token 'xxx'
  echo 'xxx' | python3 scripts/sourcea_vercel_token_setup_v1.py

Receipt: ~/.sina/sourcea-vercel-token-setup-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-vercel-token-setup-receipt-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_vercel_token_v1 import (  # noqa: E402
    DEFAULT_PROJECT,
    save_sourcea_vercel_token,
    vercel_cli_whoami,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _verify_token(token: str) -> dict:
    req = urllib.request.Request(
        "https://api.vercel.com/v2/user",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        user = data.get("user") or {}
        return {
            "ok": True,
            "username": user.get("username"),
            "email": user.get("email"),
            "user_id": user.get("id"),
        }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": f"http_{exc.code}", "detail": exc.reason}


def main() -> int:
    ap = argparse.ArgumentParser(description="Save SourceA Vercel Gate K token")
    ap.add_argument("--token", help="Classic PAT from vercel.com/account/settings/tokens")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--name", default="SourceA Gate K")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    tok = (args.token or "").strip()
    if not tok:
        tok = sys.stdin.read().strip()
    if not tok:
        who = vercel_cli_whoami()
        row = {
            "ok": bool(who),
            "schema": "sourcea-vercel-token-setup-v1",
            "at": _now(),
            "error": "no_token_provided",
            "cli_oauth": who,
            "founder_line": (
                f"CLI OAuth active as {who} — deploy works without token file"
                if who
                else "Paste token from dashboard Create button"
            ),
            "dashboard": {
                "token_name": "SourceA Gate K",
                "scope": "Full Account",
                "expiration": "No expiration",
                "url": "https://vercel.com/account/settings/tokens",
            },
            "fix": "python3 scripts/sourcea_vercel_token_setup_v1.py --token '<paste-once>'",
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(row.get("founder_line") or row.get("error"))
        return 0 if who else 1

    verify = _verify_token(tok)
    if not verify.get("ok"):
        row = {
            "ok": False,
            "schema": "sourcea-vercel-token-setup-v1",
            "at": _now(),
            "verify": verify,
            "founder_line": "Token invalid — create new classic token on dashboard",
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(row["founder_line"])
        return 1

    saved = save_sourcea_vercel_token(tok, project=args.project, name=args.name)
    row = {
        "ok": True,
        "schema": "sourcea-vercel-token-setup-v1",
        "at": _now(),
        "lane": "sourcea_only",
        "gate_k_ready": True,
        "path": saved.get("path"),
        "project": args.project,
        "verify": verify,
        "founder_line": (
            f"SourceA Vercel token saved · user={verify.get('username')} · "
            f"project={args.project} · run gate_k_vercel_start_v1.py"
        ),
        "next": "python3 scripts/gate_k_vercel_start_v1.py --json",
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["founder_line"])
        print(f"  Next: {row['next']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
