#!/usr/bin/env python3
"""Detect phantom assets on the live site.

Why this exists
---------------
Cloudflare Pages serves the SPA fallback (HTML, HTTP 200) for any file that is
not in the deployment. A missing stylesheet or script therefore returns **200**,
not 404, so uptime checks and status sweeps report the site as healthy while the
page is silently broken.

This is not hypothetical. `sourcea-forge-terminal-demo.js`,
`sourcea-platform-auth-v1.js` and three other files were dropped from a deploy
and served HTML for hours. Forge Terminal had no send handler and platform
sign-in was dead, while every path still returned 200.

The original loss had a second cause worth encoding: the crawler that built the
deploy matched asset references with `\\.(css|js|...)$`, which does not match a
versioned reference such as `/sourcea/app.js?v=1.4.1`. Those files were never
collected. The regex below deliberately tolerates a query string.

Exit codes: 0 = all assets sound, 1 = at least one phantom asset.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import re
import sys
import urllib.error
import urllib.request

BASE_DEFAULT = "https://sourcea.app"

PAGES = [
    "/", "/forge/terminal", "/start", "/eval", "/sandbox", "/platform",
    "/pricing", "/audit", "/sourcea/proof/live", "/sourcea/offer",
    "/sourcea/security", "/sourcea/kernel/", "/decision-brief",
]

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    )
}

EXT = r"(?:css|js|mjs|json|svg|png|jpe?g|webp|gif|mp4|webm|woff2?|ttf|ico|xml|pdf)"
# NOTE: the `(?:\?[^"]*)?` is the whole point. Do not "simplify" it away.
ASSET_RE = re.compile(r'(?:href|src)="(/[^"?#]+\.' + EXT + r')(?:\?[^"]*)?"', re.I)

EXPECTED = {
    "css": "text/css",
    "js": "javascript",
    "mjs": "javascript",
    "json": "json",
    "svg": "svg",
    "png": "image/",
    "jpg": "image/",
    "jpeg": "image/",
    "webp": "image/",
    "gif": "image/",
    "ico": "image/",
    "mp4": "video/",
    "webm": "video/",
    "woff": "font",
    "woff2": "font",
    "ttf": "font",
    "xml": "xml",
    "pdf": "pdf",
}


def fetch(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers.get("Content-Type", ""), resp.status


def collect_assets(base: str) -> set[str]:
    found: set[str] = set()
    for path in PAGES:
        try:
            body, _, _ = fetch(base + path)
        except Exception as exc:  # page-level failure is reported separately
            print(f"WARN  could not read page {path}: {exc}", file=sys.stderr)
            continue
        found.update(m.group(1) for m in ASSET_RE.finditer(body.decode("utf-8", "ignore")))
    return found


def check_asset(base: str, path: str):
    ext = path.rsplit(".", 1)[-1].lower()
    want = EXPECTED.get(ext)
    try:
        _, ctype, status = fetch(base + path)
    except urllib.error.HTTPError as exc:
        return path, f"HTTP {exc.code}", True
    except Exception as exc:
        return path, f"ERROR {exc}", True

    ctype_l = ctype.lower()
    # the signature failure: a non-HTML asset answered with the HTML fallback
    if "text/html" in ctype_l:
        return path, f"PHANTOM (200 but text/html) [{status}]", True
    if want and want not in ctype_l:
        return path, f"unexpected content-type {ctype}", True
    return path, ctype, False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    assets = sorted(collect_assets(args.base))
    if not assets:
        print("FAIL: no assets discovered; the page fetch itself is broken")
        return 1

    broken = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for path, detail, bad in pool.map(lambda p: check_asset(args.base, p), assets):
            if bad:
                broken.append((path, detail))
            elif not args.quiet:
                print(f"ok    {path}  [{detail}]")

    print(f"\nchecked {len(assets)} assets across {len(PAGES)} pages on {args.base}")
    if broken:
        print(f"FAIL: {len(broken)} phantom or mistyped asset(s)")
        for path, detail in broken:
            print(f"  {path}  ->  {detail}")
        return 1
    print("PASS: every referenced asset serves its real content type")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
