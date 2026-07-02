#!/usr/bin/env python3
"""Light PyPI probe for sourcea-boot — honest install truth for eval flip."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

PACKAGE = "sourcea-boot"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE}/json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe() -> dict:
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        info = body.get("info") or {}
        version = str(info.get("version") or "")
        return {
            "ok": True,
            "package": PACKAGE,
            "pypi_ok": True,
            "http_status": resp.status,
            "version": version,
            "summary": info.get("summary"),
            "at": utc_now(),
        }
    except urllib.error.HTTPError as exc:
        return {
            "ok": True,
            "package": PACKAGE,
            "pypi_ok": False,
            "http_status": exc.code,
            "version": None,
            "at": utc_now(),
        }
    except urllib.error.URLError as exc:
        return {"ok": False, "package": PACKAGE, "pypi_ok": False, "error": str(exc), "at": utc_now()}


def main() -> int:
    result = probe()
    print(json.dumps(result, indent=2))
    if not result.get("ok"):
        return 2
    return 0 if result.get("pypi_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
