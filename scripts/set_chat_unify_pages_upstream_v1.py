#!/usr/bin/env python3
"""Set CHAT_UNIFY_UPSTREAM_URL on Cloudflare Pages + sync web config JSON.

Reads upstream from ~/.sina/chat-unify-cloud-deploy-receipt-v1.json or --url.
Receipt: ~/.sina/chat-unify-pages-upstream-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
DEPLOY_RECEIPT = SINA / "chat-unify-cloud-deploy-receipt-v1.json"
OUT_RECEIPT = SINA / "chat-unify-pages-upstream-receipt-v1.json"
CONFIG = ROOT / "data" / "chat_unify_cloud_config_v1.json"
WEB_CONFIG = ROOT / "sites" / "SourceA-landing" / "green-unified" / "data" / "chat-unify-web-config-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _wrangler() -> list[str]:
    from shutil import which

    return ["wrangler"] if which("wrangler") else ["npx", "--yes", "wrangler"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Railway upstream base URL (no trailing slash)")
    parser.add_argument("--project", default="sourcea-com")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    url = (args.url or "").strip().rstrip("/")
    if not url and DEPLOY_RECEIPT.is_file():
        url = str(_read(DEPLOY_RECEIPT).get("upstream_url") or _read(DEPLOY_RECEIPT).get("url") or "").rstrip("/")
    if not url:
        cfg = _read(CONFIG)
        url = str(cfg.get("worker_url") or "").rstrip("/")
    if not url:
        print("FAIL: no upstream URL — deploy Railway first or pass --url", file=sys.stderr)
        return 1

    wr = _wrangler()
    proc = subprocess.run(
        wr + ["pages", "secret", "put", "CHAT_UNIFY_UPSTREAM_URL", "--project-name", args.project],
        input=url + "\n",
        text=True,
        capture_output=True,
    )
    row = {
        "schema": "chat-unify-pages-upstream-receipt-v1",
        "at": _now(),
        "ok": proc.returncode == 0,
        "project": args.project,
        "upstream_url": url,
        "env_key": "CHAT_UNIFY_UPSTREAM_URL",
        "wrangler_code": proc.returncode,
        "wrangler_tail": (proc.stdout or proc.stderr or "")[-600:],
    }
    if row["ok"]:
        for path in (CONFIG, WEB_CONFIG):
            if path.is_file():
                live = _read(path)
                live["worker_url"] = url
                live["api_upstream_default"] = url
                live["saved_at"] = _now()
                path.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
    OUT_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row, indent=2))
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
