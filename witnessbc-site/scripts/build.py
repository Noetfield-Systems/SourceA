#!/usr/bin/env python3
"""Witness AI site — assemble pages, inject refs, build self-contained bundle."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"
DATA = ROOT / "data" / "references.json"
SINA = Path.home() / ".sina"
ARCHIVE = ROOT.parent / "archive" / "attachments" / "commercial"

FORBIDDEN_LINE = re.compile(
    r"sourcea|zenity|nomotic|notenic|witness bc|witnessai|witness\.ai|noetfield",
    re.I,
)
ALLOW_LINE = re.compile(
    r"witnessbc\.com|brand-disambiguation|operations@noetfield\.com|class=\"brand-other\"|not WitnessAI|lane-router|noetfield\.com/copilot",
    re.I,
)
CITE_RE = re.compile(r'href="(?:[^"]*#)?ref-(\d+)"')
SEND_PAGES = {
    "proof": "proof.html",
    "pricing": "pricing.html",
    "faq": "faq.html",
}


def _run(script: str, *args: str) -> None:
    path = ROOT / "scripts" / script
    subprocess.run([sys.executable, str(path), *args], check=True, cwd=ROOT, capture_output=True)


def _assemble() -> None:
    _run("render_toolkits_v1.py")
    _run("assemble_pages.py")


def _inject_refs() -> None:
    _run("inject_refs.py", "--quiet")


def _validate_ref_integrity(html: str, *, require_gartner: bool = True) -> None:
    if not DATA.exists():
        raise SystemExit("FAIL build: missing data/references.json")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ref_ids = {r["id"] for r in data["refs"]}
    cited = {int(m) for m in CITE_RE.findall(html)}
    missing = cited - ref_ids
    if missing:
        raise SystemExit(f"FAIL build: HTML cites missing ref ids: {sorted(missing)}")
    if require_gartner:
        gartner = data.get("gartner_primary_url", "")
        if gartner and gartner not in html:
            raise SystemExit("FAIL build: Gartner primary URL missing from HTML")


def _inline_favicon(html: str) -> str:
    favicon = ASSETS / "favicon.svg"
    if not favicon.exists():
        return html
    svg = favicon.read_text(encoding="utf-8").strip()
    svg = svg.replace('"', "'")
    data_uri = "data:image/svg+xml," + svg.replace("#", "%23").replace("<", "%3C").replace(">", "%3E")
    html = re.sub(
        r'<link rel="icon"[^>]*>',
        f'<link rel="icon" href="{data_uri}" type="image/svg+xml" />',
        html,
        count=1,
    )
    return html


def _inline_bundle(page: Path) -> str:
    html = page.read_text(encoding="utf-8")

    tokens = (ASSETS / "tokens.css").read_text(encoding="utf-8")
    styles = (ASSETS / "styles.css").read_text(encoding="utf-8")
    motion = (ASSETS / "motion.css").read_text(encoding="utf-8")

    html = re.sub(r'\s*<link rel="stylesheet" href="assets/tokens\.css" />\s*', "", html)
    html = re.sub(r'\s*<link rel="stylesheet" href="assets/styles\.css" />\s*', "", html)
    html = re.sub(r'\s*<link rel="stylesheet" href="assets/motion\.css" />\s*', "", html)

    js_parts: list[str] = []
    script_map = {
        "control-plane": ASSETS / "control-plane.js",
        "trust-signals": ASSETS / "trust-signals.js",
        "proof-demo": ASSETS / "proof-demo.js",
        "site": ASSETS / "site.js",
    }
    for name, path in script_map.items():
        tag = f'<script src="assets/{name}.js"></script>'
        if tag in html and path.exists():
            js_parts.append(path.read_text(encoding="utf-8"))
        html = re.sub(rf'\s*<script src="assets/{re.escape(name)}\.js"></script>\s*', "", html)

    css_bundle = tokens + "\n" + styles + "\n" + motion
    js_bundle = "\n".join(js_parts)

    html = html.replace("</head>", f"<style>{css_bundle}</style>\n</head>", 1)
    html = _inline_favicon(html)
    if js_bundle:
        html = html.replace("</body>", f"<script>{js_bundle}</script>\n</body>", 1)
    return html


def validate_html(html: str, label: str, *, require_gartner: bool = True) -> None:
    for line in html.splitlines():
        if FORBIDDEN_LINE.search(line) and not ALLOW_LINE.search(line):
            raise SystemExit(f"FAIL {label}: forbidden third-party brand reference found")
    _validate_ref_integrity(html, require_gartner=require_gartner)


def build_page_bundle(slug: str) -> dict[str, str]:
    if slug not in SEND_PAGES:
        raise SystemExit(f"FAIL build: unknown page slug {slug!r} (use: {', '.join(SEND_PAGES)})")
    page_file = SEND_PAGES[slug]
    page_path = ROOT / page_file
    if not page_path.is_file():
        raise SystemExit(f"FAIL build: missing assembled page {page_file}")

    bundle = _inline_bundle(page_path)
    label = f"witnessbc-site-{slug}-v1"
    validate_html(bundle, label, require_gartner=False)

    DIST.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    SINA.mkdir(parents=True, exist_ok=True)

    paths = {
        "dist": str(DIST / f"{label}.html"),
        "sina": str(SINA / f"{label}.html"),
        "archive": str(ARCHIVE / f"{label}.html"),
    }
    for path in paths.values():
        Path(path).write_text(bundle, encoding="utf-8")
    return paths


def build() -> dict[str, str]:
    _inject_refs()
    _assemble()

    DIST.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    SINA.mkdir(parents=True, exist_ok=True)

    bundle = _inline_bundle(ROOT / "index.html")
    validate_html(bundle, "witnessbc-site-v1")

    paths = {
        "dist": str(DIST / "witnessbc-site-v1.html"),
        "sina": str(SINA / "witnessbc-site-v1.html"),
        "archive": str(ARCHIVE / "witnessbc-site-v1.html"),
    }
    for path in paths.values():
        Path(path).write_text(bundle, encoding="utf-8")

    send_paths: dict[str, dict[str, str]] = {}
    for slug in SEND_PAGES:
        send_paths[slug] = build_page_bundle(slug)

    for stale in ("witnessbc-site-light-v1.html", "witnessbc-site-dark-v1.html"):
        stale_path = DIST / stale
        if stale_path.exists():
            stale_path.unlink()

    return {"index": paths, "send": send_paths}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    p.add_argument("--open", action="store_true", help="Open index.html in browser")
    p.add_argument("--skip-inject", action="store_true", help="Skip reference injection (assemble only)")
    p.add_argument(
        "--page",
        choices=tuple(SEND_PAGES.keys()),
        help="Build single-page send bundle only (after full assemble)",
    )
    args = p.parse_args()
    if args.skip_inject:
        _assemble()
        if args.json:
            print(json.dumps({"ok": True, "skipped": "inject"}, indent=2))
        return 0
    if args.page:
        _inject_refs()
        _assemble()
        paths = build_page_bundle(args.page)
        if args.json:
            print(json.dumps({"ok": True, "page": args.page, "paths": paths}, indent=2))
        else:
            for v in paths.values():
                print(v)
        return 0
    result = build()
    if args.json:
        print(json.dumps({"ok": True, "paths": result}, indent=2))
    else:
        for v in result["index"].values():
            print(v)
        for slug, paths in result["send"].items():
            for v in paths.values():
                print(v)
    if args.open:
        subprocess.run(["open", str(ROOT / "index.html")], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
