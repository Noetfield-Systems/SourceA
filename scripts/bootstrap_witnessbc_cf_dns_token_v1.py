#!/usr/bin/env python3
"""One-shot bootstrap: open witness.bc Cloudflare DNS-edit token form in system browser.

After founder clicks Create Token, paste secret into:
  ~/.sina/witnessbc-cf-dns-token-v1.json
  {"schema":"witnessbc-cf-dns-token-v1","api_token":"...","zone_id":"fbaba5b3d756fa9c2d6e5e6368df4414"}

Then run:
  python3 scripts/dns_cutover_witnessbc_vercel_main_v1.py --apply --json

Receipt: ~/.sina/witnessbc-cf-dns-token-bootstrap-receipt-v1.json
"""
from __future__ import annotations

import json
import subprocess
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ZONE_ID = "fbaba5b3d756fa9c2d6e5e6368df4414"
ZONE_NAME = "witnessbc.com"
TOKEN_FILE = Path.home() / ".sina/witnessbc-cf-dns-token-v1.json"
RECEIPT = Path.home() / ".sina/witnessbc-cf-dns-token-bootstrap-receipt-v1.json"
SECRETS = Path.home() / ".sina/secrets.env"

# DNS edit · single zone witnessbc.com
PERMS = json.dumps([{"key": "dns", "type": "edit"}], separators=(",", ":"))
TOKEN_URL = (
    "https://dash.cloudflare.com/profile/api-tokens"
    f"?permissionGroupKeys={urllib.parse.quote(PERMS)}"
    f"&accountId=*&zoneId={ZONE_ID}&name=WitnessBC-DNS-Cutover-Agent"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sync_secrets(token: str) -> None:
    lines: list[str] = []
    if SECRETS.is_file():
        lines = SECRETS.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    seen_token = seen_zone = False
    for ln in lines:
        if ln.startswith("WITNESSBC_CF_API_TOKEN="):
            out.append(f"WITNESSBC_CF_API_TOKEN={token}")
            seen_token = True
        elif ln.startswith("WITNESSBC_CF_ZONE_ID="):
            out.append(f"WITNESSBC_CF_ZONE_ID={ZONE_ID}")
            seen_zone = True
        else:
            out.append(ln)
    if not seen_token:
        out.append(f"WITNESSBC_CF_API_TOKEN={token}")
    if not seen_zone:
        out.append(f"WITNESSBC_CF_ZONE_ID={ZONE_ID}")
    SECRETS.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    if TOKEN_FILE.is_file():
        row = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
        tok = row.get("api_token") or row.get("token")
        if tok:
            _sync_secrets(str(tok))
            receipt = {"schema": "witnessbc-cf-dns-token-bootstrap-receipt-v1", "at": _now(), "ok": True, "source": "token_file", "path": str(TOKEN_FILE)}
            RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(receipt, indent=2))
            return 0

    subprocess.run(["open", TOKEN_URL], check=False)
    receipt = {
        "schema": "witnessbc-cf-dns-token-bootstrap-receipt-v1",
        "at": _now(),
        "ok": False,
        "opened_url": TOKEN_URL,
        "zone_id": ZONE_ID,
        "zone_name": ZONE_NAME,
        "next": f"Save token to {TOKEN_FILE} then re-run this script",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
