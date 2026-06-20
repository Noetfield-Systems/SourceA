#!/usr/bin/env python3
"""Check SourceA-only Cloudflare token for Gate K Pages deploy.

Receipt: ~/.sina/cf-pages-token-check-v1.json
Law: Never TrustField / Noetfield / WitnessBC tokens for SourceA.
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
RECEIPT = SINA / "cf-pages-token-check-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_cf_pages_token_v1 import load_sourcea_cf_config  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _api(token: str, path: str) -> dict:
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def check() -> dict:
    cfg = load_sourcea_cf_config()
    if not cfg.get("ok"):
        row = {
            "schema": "cf-pages-token-check-v1",
            "at": _now(),
            "lane": "sourcea_only",
            "gate_k_ready": False,
            "ok": False,
            **cfg,
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    token = str(cfg["api_token"])
    row: dict = {
        "schema": "cf-pages-token-check-v1",
        "at": _now(),
        "lane": "sourcea_only",
        "token_source": cfg.get("path"),
        "project": cfg.get("project"),
        "zone_name": cfg.get("zone_name"),
        "account_id": cfg.get("account_id"),
    }

    try:
        verify = _api(token, "/user/tokens/verify")
        row["token_active"] = verify.get("result", {}).get("status") == "active"
    except urllib.error.HTTPError as exc:
        row["token_active"] = False
        row["verify_error"] = exc.code

    account_id = cfg.get("account_id")
    if not account_id:
        try:
            acc = _api(token, "/accounts")
            if acc.get("success") and acc.get("result"):
                account_id = acc["result"][0].get("id")
                row["account_id"] = account_id
                row["accounts_list_ok"] = True
        except urllib.error.HTTPError as exc:
            row["accounts_error"] = exc.code

    pages_ok = False
    if account_id:
        try:
            pages = _api(token, f"/accounts/{account_id}/pages/projects")
            pages_ok = bool(pages.get("success"))
            row["pages_project_count"] = len(pages.get("result") or [])
            names = [p.get("name") for p in (pages.get("result") or [])]
            row["pages_projects"] = names[:10]
        except urllib.error.HTTPError as exc:
            row["pages_error"] = exc.code

    zone_ok = False
    zone_id = cfg.get("zone_id")
    zone_name = cfg.get("zone_name") or "sourcea.com"
    if zone_id:
        try:
            zone = _api(token, f"/zones/{zone_id}")
            zone_ok = bool(zone.get("success"))
            if zone_ok:
                row["zone_name"] = zone.get("result", {}).get("name")
        except urllib.error.HTTPError:
            zone_ok = False
    else:
        try:
            zones = _api(token, f"/zones?name={zone_name}")
            if zones.get("success") and zones.get("result"):
                zone_ok = True
                row["zone_id"] = zones["result"][0].get("id")
                row["zone_name"] = zones["result"][0].get("name")
        except urllib.error.HTTPError as exc:
            row["zones_error"] = exc.code

    gate_k_ready = pages_ok
    row["ok"] = gate_k_ready
    row["gate_k_ready"] = gate_k_ready
    row["zone_ok"] = zone_ok

    if gate_k_ready:
        row["founder_line"] = (
            f"Gate K SourceA token OK · project={cfg.get('project')} · "
            f"zone={row.get('zone_name', zone_name)} · run gate_k_pages_start_v1.py"
        )
    else:
        row["founder_line"] = (
            "Gate K blocked — SourceA Cloudflare token lacks Pages deploy scope. "
            "Create a SourceA-only token (not TrustField)."
        )
        row["fix_steps"] = cfg.get("fix_steps") or [
            "Cloudflare account for sourcea.com only",
            f"Save token to {cfg.get('path')}",
            "Permissions: Account · Cloudflare Pages · Edit",
            "python3 scripts/gate_k_pages_start_v1.py --json",
        ]
        row["fix_url"] = "https://dash.cloudflare.com/profile/api-tokens"

    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA-only CF Pages token check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = check()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("error"))
        for step in row.get("fix_steps") or []:
            print(f"  · {step}")
    return 0 if row.get("gate_k_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
