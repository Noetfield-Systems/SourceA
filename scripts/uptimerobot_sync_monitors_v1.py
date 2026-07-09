#!/usr/bin/env python3
"""Sync UptimeRobot monitors from data/noos-external-monitors-v1.json (GET health only)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "noos-external-monitors-v1.json"
API = "https://api.uptimerobot.com/v2"


def load_env() -> None:
    for path in (
        Path.home() / ".sourcea-secrets" / "portfolio-spine.env",
        Path.home() / ".sina" / "secrets.env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def api_call(api_key: str, payload: dict) -> dict:
    body = urllib.parse.urlencode({**payload, "api_key": api_key, "format": "json"}).encode()
    req = urllib.request.Request(API + "/" + payload.pop("_endpoint"), data=body, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def collect_monitors(ssot: dict) -> list[dict]:
    rows = list(ssot.get("monitors") or [])
    rows.extend(ssot.get("sina_gateway_additions") or [])
    out = []
    for row in rows:
        url = row.get("url")
        if not url:
            continue
        out.append(
            {
                "id": row["id"],
                "url": url,
                "friendly_name": f"SourceA · {row['id']}",
                "keyword": row.get("keyword"),
                "optional": bool(row.get("optional")),
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    load_env()
    api_key = (os.environ.get("UPTIMEROBOT_API_KEY") or "").strip()
    if not api_key and not args.dry_run:
        print("FAIL: set UPTIMEROBOT_API_KEY in ~/.sourcea-secrets or ~/.sina/secrets.env", file=sys.stderr)
        return 1

    ssot = json.loads(SSOT.read_text(encoding="utf-8"))
    desired = collect_monitors(ssot)
    interval = int(ssot.get("interval_seconds") or ssot.get("interval_minutes", 5) * 60)

    existing_by_url: dict[str, dict] = {}
    if api_key and not args.dry_run:
        listing = api_call(api_key, {"_endpoint": "getMonitors", "logs": "0"})
        for mon in listing.get("monitors") or []:
            existing_by_url[str(mon.get("url") or "")] = mon

    actions = []
    for row in desired:
        url = row["url"]
        if args.dry_run or not api_key:
            actions.append({"action": "would_sync", **row})
            continue
        if url in existing_by_url:
            actions.append({"action": "exists", "id": row["id"], "url": url})
            continue
        monitor_type = 2 if row.get("keyword") else 1
        payload = {
            "_endpoint": "newMonitor",
            "type": monitor_type,
            "url": url,
            "friendly_name": row["friendly_name"],
            "interval": interval,
        }
        if row.get("keyword"):
            payload["keyword_value"] = row["keyword"]
            payload["keyword_type"] = 2
        result = api_call(api_key, payload)
        actions.append(
            {
                "action": "created",
                "id": row["id"],
                "url": url,
                "uptimerobot_id": (result.get("monitor") or {}).get("id"),
                "stat": result.get("stat"),
            }
        )

    receipt = {
        "ok": True,
        "schema": "uptimerobot-sync-v1",
        "dry_run": args.dry_run,
        "desired_count": len(desired),
        "actions": actions,
        "interval_seconds": interval,
        "law": ssot.get("one_law"),
    }
    out_path = Path.home() / ".sina" / "uptimerobot-sync-receipt-v1.json"
    try:
        out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        receipt_path = str(out_path)
    except OSError:
        receipt_path = None

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: uptimerobot_sync — {len(desired)} monitors" + (f" · receipt {receipt_path}" if receipt_path else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
