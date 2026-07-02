#!/usr/bin/env python3
"""Machine-verify a client-proof URL artifact — content markers, not HTTP 200 alone.

SPA fallback on sourcea.app returns shell HTML for unknown paths; always grep markers.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Any


def fetch(url: str, *, timeout: float = 20.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-client-proof-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return int(exc.code), body


def verify(*, url: str, markers: list[str], forbidden: list[str] | None = None) -> dict[str, Any]:
    forbidden = forbidden or []
    code, body = fetch(url)
    missing = [m for m in markers if m not in body]
    hits = [f for f in forbidden if f in body]
    ok = code == 200 and not missing and not hits
    return {
        "ok": ok,
        "url": url,
        "http_code": code,
        "markers_required": markers,
        "markers_missing": missing,
        "forbidden_hits": hits,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--marker", action="append", default=[], dest="markers")
    ap.add_argument("--forbidden", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.markers:
        print("FAIL: at least one --marker required", file=sys.stderr)
        return 2
    row = verify(url=args.url, markers=list(args.markers), forbidden=list(args.forbidden))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if row["ok"]:
            print(f"PASS client-proof-artifact {args.url}")
        else:
            print(
                f"FAIL client-proof-artifact {args.url} "
                f"code={row['http_code']} missing={row['markers_missing']} forbidden={row['forbidden_hits']}",
                file=sys.stderr,
            )
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
