#!/usr/bin/env python3
"""Light public API smoke for sourcea.app branded Cloudflare routes."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

BASE = "https://sourcea.app"

CHECKS = [
    {
        "id": "app_health",
        "url": f"{BASE}/health",
        "schema": None,
    },
    {
        "id": "route_manifest",
        "url": f"{BASE}/api/sourcea/routes/v1",
        "schema": "sourcea-public-api-routes-v1",
    },
    {
        "id": "site_pulse",
        "url": f"{BASE}/api/site/pulse/v1",
        "schema": "sourcea-site-pulse-v1",
    },
    {
        "id": "site_pulse_status",
        "url": f"{BASE}/api/site/status/v1",
        "schema": "sourcea-site-pulse-status-v1",
    },
    {
        "id": "site_stats",
        "url": f"{BASE}/api/site/stats/v1",
        "schema": "sourcea-site-stats-public-v1",
    },
    {
        "id": "brain_chat_status",
        "url": f"{BASE}/api/brain/chat/v1",
        "schema": "sourcea-brain-chat-status-v1",
    },
    {
        "id": "brain_product_status",
        "url": f"{BASE}/api/brain/status/v1",
        "schema": "sourcea-brain-chat-status-v1",
    },
    {
        "id": "auto_runtime_health",
        "url": f"{BASE}/api/cloud-forge-run/health/v1",
        "schema": "sourcea-auto-runtime-health-v1",
    },
    {
        "id": "auto_runtime_status",
        "url": f"{BASE}/api/cloud-forge-run/status/v1",
        "schema": "sourcea-auto-runtime-status-v1",
    },
    {
        "id": "cloud_forge_run_queue",
        "url": f"{BASE}/api/cloud-forge-run/queue/v1",
        "schema": "cloud-forge-run-queue-head-v1",
    },
    {
        "id": "api_not_found_json",
        "url": f"{BASE}/api/sourcea/__missing__/v1",
        "schema": "sourcea-public-api-error-v1",
        "expect_status": 404,
    },
]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_json(url: str, timeout: int = 12) -> tuple[int, str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "sourcea-public-api-smoke-v1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        status = err.code
        content_type = err.headers.get("Content-Type", "")
        body = err.read().decode("utf-8", errors="replace")
    except Exception as err:  # noqa: BLE001 - smoke output should explain network failures.
        return 0, "", {"ok": False, "error": "fetch_failed", "message": str(err)}

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {"ok": False, "error": "invalid_json", "body_prefix": body[:120]}
    return status, content_type, parsed


def check(row: dict[str, Any]) -> dict[str, Any]:
    status, content_type, body = fetch_json(row["url"])
    expected_status = int(row.get("expect_status") or 200)
    schema = row.get("schema")
    is_json = "json" in content_type.lower() or not isinstance(body, dict) or body.get("error") != "invalid_json"
    ok = status == expected_status and is_json
    if schema:
        ok = ok and isinstance(body, dict) and body.get("schema") == schema
    return {
        "id": row["id"],
        "ok": ok,
        "status": status,
        "expected_status": expected_status,
        "content_type": content_type,
        "schema": body.get("schema") if isinstance(body, dict) else None,
        "url": row["url"],
        "error": body.get("error") if isinstance(body, dict) else None,
    }


def main() -> int:
    checks = [check(row) for row in CHECKS]
    out = {
        "schema": "sourcea-public-api-smoke-v1",
        "ok": all(row["ok"] for row in checks),
        "at": now(),
        "checks": checks,
    }
    print(json.dumps(out, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
