#!/usr/bin/env python3
"""Deep E2E: crawl every WitnessBC page, extract every link, verify HTTP + CSS + markers."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag

DEFAULT_BASE = "https://witnessbc-commercial.pages.dev"

SEED_PATHS = [
    "/index.html",
    "/platform.html",
    "/lifecycle.html",
    "/proof.html",
    "/compare.html",
    "/policy.html",
    "/pricing.html",
    "/faq.html",
    "/sources.html",
    "/learn.html",
    "/toolkits.html",
    "/toolkits/sandbox/",
    "/toolkits/free/sourcing/",
    "/toolkits/free/corrections/",
    "/toolkits/free/privacy/",
    "/toolkits/free/public-record/",
    "/toolkits/free/story-template/",
    "/toolkits/free/action-map/",
    "/toolkits/training/",
    "/toolkits/training/evidence-literacy-101/",
    "/toolkits/training/privacy-first-publishing/",
]

REQUIRED_MARKERS = {
    "/index.html": ["brand-disambiguation", "proof@witnessbc.com", "layout-ultra-v12"],
    "/proof.html": ["Proof Lab", "layout-ultra-v12"],
    "/toolkits.html": ["Education only", "data-buy=", "layout-ultra-v12"],
    "/toolkits/free/sourcing/": ["toolkit-textarea", 'href="/assets/styles.css"', "data-buy="],
    "/toolkits/training/": ["Courses", "layout-ultra-v12", "data-buy="],
}

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []  # (attr, href)
        self.scripts: list[str] = []
        self.styles: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k: (v or "") for k, v in attrs}
        if tag == "a" and d.get("href"):
            self.links.append(("a", d["href"]))
        elif tag == "link" and d.get("href"):
            rel = d.get("rel", "")
            if "stylesheet" in rel or d.get("href", "").endswith(".css"):
                self.styles.append(d["href"])
            else:
                self.links.append(("link", d["href"]))
        elif tag == "script" and d.get("src"):
            self.scripts.append(d["src"])
        elif tag in ("img", "source", "video") and d.get("src"):
            self.links.append((tag, d["src"]))


def fetch(url: str, timeout: int = 20) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": "witnessbc-e2e/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, body, headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body, {}


def norm_path(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if path != "/" and not path.endswith("/") and "." not in path.split("/")[-1]:
        path += "/"
    return path


def is_internal(base: str, href: str) -> bool:
    if not href or href.startswith(SKIP_SCHEMES) or href.startswith("#"):
        return False
    if href.startswith("//"):
        return urlparse("https:" + href).netloc == urlparse(base).netloc
    if href.startswith("http"):
        return urlparse(href).netloc == urlparse(base).netloc
    return not href.startswith("http")


def resolve(base_url: str, href: str) -> str:
    href, _ = urldefrag(href)
    return urljoin(base_url, href)


def path_key(url: str) -> str:
    p = urlparse(url).path or "/"
    if p.endswith("/index.html"):
        p = p[: -len("index.html")]
    return p or "/"


def crawl(base: str, seeds: list[str]) -> dict:
    base = base.rstrip("/")
    queue: list[str] = []
    seen_pages: set[str] = set()
    seen_assets: set[str] = set()

    for s in seeds:
        queue.append(base + s)

    page_results: dict[str, dict] = {}
    link_checks: list[dict] = []
    asset_checks: list[dict] = []
    failures: list[str] = []

    while queue:
        page_url = queue.pop(0)
        pk = path_key(page_url)
        if pk in seen_pages:
            continue
        seen_pages.add(pk)

        code, body, _ = fetch(page_url)
        result = {
            "url": page_url,
            "path": pk,
            "status": code,
            "bytes": len(body),
            "links_found": 0,
            "styles_found": 0,
            "scripts_found": 0,
            "markers_ok": True,
            "missing_markers": [],
        }

        if code != 200:
            failures.append(f"PAGE HTTP {code}: {pk}")
            page_results[pk] = result
            continue

        parser = LinkParser()
        parser.feed(body)
        result["links_found"] = len(parser.links)
        result["styles_found"] = len(parser.styles)
        result["scripts_found"] = len(parser.scripts)

        # markers
        for marker_path, markers in REQUIRED_MARKERS.items():
            check_path = marker_path
            if pk.rstrip("/") == marker_path.rstrip("/") or pk == marker_path:
                for m in markers:
                    if m not in body:
                        result["markers_ok"] = False
                        result["missing_markers"].append(m)
                        failures.append(f"MARKER missing '{m}' on {pk}")

        if "layout-ultra-v12" not in body:
            result["markers_ok"] = False
            result["missing_markers"].append("layout-ultra-v12")
            failures.append(f"MARKER missing layout-ultra-v12 on {pk}")

        if "assets/styles.css" not in body and '/assets/styles.css' not in body:
            failures.append(f"CSS link missing on {pk}")

        # noetfield leak
        if re.search(r"noetfield", body, re.I) and not re.search(r"brand-other|lane-router", body, re.I):
            failures.append(f"LEAK noetfield on {pk}")

        page_results[pk] = result

        # check styles + scripts from this page
        for href in parser.styles + parser.scripts:
            asset_url = resolve(page_url, href)
            if urlparse(asset_url).netloc != urlparse(base).netloc:
                continue
            ak = path_key(asset_url)
            if ak in seen_assets:
                continue
            seen_assets.add(ak)
            ac, _, _ = fetch(asset_url)
            asset_checks.append({"from": pk, "asset": ak, "status": ac, "type": "style/script"})
            if ac != 200:
                failures.append(f"ASSET HTTP {ac}: {ak} (from {pk})")

        # check all internal links
        for attr, href in parser.links:
            if not is_internal(base, href):
                continue
            target = resolve(page_url, href)
            if urlparse(target).netloc != urlparse(base).netloc:
                continue
            tk = path_key(target)
            lc, _, _ = fetch(target)
            link_checks.append({
                "from": pk,
                "attr": attr,
                "href": href,
                "resolved": tk,
                "status": lc,
            })
            if lc != 200:
                failures.append(f"LINK HTTP {lc}: {pk} → {href} ({tk})")

            # enqueue HTML pages for further crawl
            if lc == 200 and (tk.endswith(".html") or tk.endswith("/")) and tk not in seen_pages:
                if "/principles" not in tk:  # excluded coexistence path
                    queue.append(target)

    # dedupe failures
    unique_failures = list(dict.fromkeys(failures))

    # group link failures by source page
    broken_by_page: dict[str, list[str]] = defaultdict(list)
    for lc in link_checks:
        if lc["status"] != 200:
            broken_by_page[lc["from"]].append(f'{lc["href"]} → HTTP {lc["status"]}')

    return {
        "base": base,
        "pages_checked": len(page_results),
        "assets_checked": len(asset_checks),
        "links_checked": len(link_checks),
        "failures": unique_failures,
        "fail_count": len(unique_failures),
        "pass": len(unique_failures) == 0,
        "pages": page_results,
        "broken_links_by_page": dict(broken_by_page),
        "asset_failures": [a for a in asset_checks if a["status"] != 200],
        "link_summary": {
            "ok": sum(1 for x in link_checks if x["status"] == 200),
            "fail": sum(1 for x in link_checks if x["status"] != 200),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default=DEFAULT_BASE)
    p.add_argument("--json", action="store_true")
    p.add_argument("--receipt", default="")
    args = p.parse_args()

    report = crawl(args.base, SEED_PATHS)

    if args.receipt:
        from pathlib import Path
        Path(args.receipt).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        # trim verbose page bodies for json output
        slim = {k: v for k, v in report.items() if k != "pages"}
        slim["page_paths"] = sorted(report["pages"].keys())
        print(json.dumps(slim, indent=2))
    else:
        print(f"=== DEEP E2E — {report['base']} ===\n")
        print(f"Pages:  {report['pages_checked']}")
        print(f"Assets: {report['assets_checked']}")
        print(f"Links:  {report['links_checked']} ({report['link_summary']['ok']} ok · {report['link_summary']['fail']} fail)\n")

        print("--- every page ---")
        for path in sorted(report["pages"].keys()):
            pr = report["pages"][path]
            flag = "OK" if pr["status"] == 200 and pr.get("markers_ok", True) else "FAIL"
            miss = f" missing={pr['missing_markers']}" if pr.get("missing_markers") else ""
            print(f"  {flag}  {path}  HTTP {pr['status']}  links={pr['links_found']} css={pr['styles_found']} js={pr['scripts_found']}{miss}")

        if report["asset_failures"]:
            print("\n--- broken assets ---")
            for a in report["asset_failures"]:
                print(f"  FAIL  {a['asset']} HTTP {a['status']} (from {a['from']})")

        if report["broken_links_by_page"]:
            print("\n--- broken links by page ---")
            for pg, items in sorted(report["broken_links_by_page"].items()):
                print(f"  {pg}:")
                for it in items:
                    print(f"    FAIL  {it}")

        if report["failures"]:
            print(f"\n--- all failures ({report['fail_count']}) ---")
            for f in report["failures"]:
                print(f"  FAIL  {f}")
            print(f"\nFAIL: deep E2E — {report['fail_count']} issues")
            return 1

        print(f"\nPASS: deep E2E — {report['pages_checked']} pages · {report['links_checked']} links · {report['assets_checked']} assets")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
