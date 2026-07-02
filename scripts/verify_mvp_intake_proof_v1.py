#!/usr/bin/env python3
"""Synthetic MVP intake POST + KV read-back proof — black-box verification."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
RECEIPT = SINA / "mvp-intake-proof-receipt-v1.json"
DEFAULT_URL = "https://sourcea.com/api/commercial/mvp-intake/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _post(url: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "sourcea-mvp-intake-proof/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return int(resp.status), json.loads(resp.read().decode("utf-8"))


def _get(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-mvp-intake-proof/1.0"}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return int(resp.status), json.loads(resp.read().decode("utf-8"))


def verify(*, base_url: str = DEFAULT_URL) -> dict:
    token = uuid.uuid4().hex[:8]
    payload = {
        "building": f"Buyer-proof synthetic intake {token}",
        "building_type": "saas",
        "deadline": "2026-07-15",
        "budget": "under-10k",
        "email": f"proof+{token}@sourcea.app",
    }
    row: dict = {"schema": "mvp-intake-proof-v1", "at": _now(), "post_url": base_url}
    try:
        post_code, post_body = _post(base_url, payload)
        row["post"] = {"ok": post_code == 200 and post_body.get("ok"), "code": post_code, "body": post_body}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        row["post"] = {"ok": False, "error": str(exc)[:200]}
        row["ok"] = False
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    intake_id = str(post_body.get("intake_id") or "")
    read_url = f"{base_url.rstrip('/')}/{intake_id}"
    row["read_url"] = read_url
    try:
        read_code, read_body = _get(read_url)
        read_ok = (
            read_code == 200
            and read_body.get("ok")
            and read_body.get("intake_id") == intake_id
            and (read_body.get("intake") or {}).get("building") == payload["building"]
        )
        row["read_back"] = {"ok": read_ok, "code": read_code, "body": read_body}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        if isinstance(exc, urllib.error.HTTPError) and exc.code == 404:
            row["read_back"] = {"ok": False, "code": 404, "error": "not_found"}
        else:
            row["read_back"] = {"ok": False, "error": str(exc)[:200]}

    storage_ok = bool((post_body.get("storage") or {}).get("ok"))
    row["ok"] = bool(row["post"]["ok"] and row.get("read_back", {}).get("ok") and storage_ok)
    row["intake_id"] = intake_id
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify(base_url=args.url)
    if args.json:
        print(json.dumps(row, indent=2))
    elif row.get("ok"):
        print(f"PASS mvp-intake-proof intake_id={row.get('intake_id')}")
    else:
        print(f"FAIL mvp-intake-proof post={row.get('post')} read={row.get('read_back')}", file=sys.stderr)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
