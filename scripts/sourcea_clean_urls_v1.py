#!/usr/bin/env python3
"""SourceA landing — extensionless clean URLs (anti-poison routing).

- Internal links: /sourcea/foo.html → /sourcea/foo
- _redirects: 200 rewrite to .html on disk + 301 strip .html from browser bar
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"

# Short public aliases → extensionless canonical paths under /sourcea/
SHORT_ALIASES: tuple[tuple[str, str], ...] = (
    ("/start", "/sourcea/start"),
    ("/48h-mvp", "/sourcea/48h-mvp"),
    ("/kernel", "/sourcea/"),
    ("/kernel/", "/sourcea/"),
    ("/sourcea", "/sourcea/"),
    ("/proof", "/sourcea/proof"),
    ("/platform-story", "/sourcea/platform"),
    ("/scenario", "/sourcea/scenario"),
    ("/pricing", "/sourcea/pricing"),
    ("/team", "/sourcea/team"),
    ("/growth", "/sourcea/growth"),
    ("/compare", "/sourcea/compare"),
    ("/security", "/sourcea/security"),
    ("/forge", "/sourcea/forge/"),
    ("/forge/", "/sourcea/forge/"),
    ("/forge/terminal", "/sourcea/forge/terminal"),
    ("/forge/terminal/signin", "/sourcea/forge/terminal/signin"),
    ("/forge/terminal/signup", "/sourcea/forge/terminal/signup"),
    ("/forge/terminal/profile", "/sourcea/forge/terminal/profile"),
    ("/forge/terminal/workspace", "/sourcea/forge/terminal/workspace"),
    ("/unify", "/unify/"),
    ("/unify-demo", "/unify-demo/"),
    ("/downloads", "/downloads/"),
    ("/changelog", "/sourcea/changelog"),
    ("/funnel", "/sourcea/funnel"),
    ("/sandbox", "/sourcea/sandbox"),
    ("/learn", "/sourcea/learn"),
    ("/pulse-founder", "/sourcea/pulse-founder"),
    ("/operating-brain-install", "/sourcea/operating-brain-install"),
    ("/ai-value-governance", "/sourcea/ai-value-governance"),
    ("/enterprise-ai-control-plane", "/sourcea/enterprise-ai-control-plane"),
)

# Contract SKU clean URLs — 200 rewrite (no 302 chain; regional + external monitors expect 200)
CONTRACT_REWRITE_200: tuple[tuple[str, str], ...] = (
    ("/operating-brain-install", "/sourcea/operating-brain-install.html"),
    ("/ai-value-governance", "/sourcea/ai-value-governance.html"),
    ("/enterprise-ai-control-plane", "/sourcea/enterprise-ai-control-plane.html"),
)

# Permanent redirects — retired duplicate URLs (ORD: URL-checkable)
REDIRECT_301: tuple[tuple[str, str], ...] = (
    ("/mvp", "/start"),
    ("/mvp/", "/start"),
    ("/agent-run", "/platform"),
    ("/agent-run/", "/platform"),
    ("/sourcea-boot", "/eval"),
    ("/sourcea-boot/", "/eval"),
    ("/sourcea/home", "/"),
    ("/sourcea/home/", "/"),
    ("/sourcea/factories/try-factory-demo", "/sourcea/sandbox"),
    ("/sourcea/factories/try-factory-demo/", "/sourcea/sandbox"),
    ("/sourcea/platform/sign-in", "/auth/sign-in"),
    ("/sourcea/platform/sign-up", "/auth/sign-up"),
    ("/sourcea/platform/profile", "/sourcea/forge/terminal/profile"),
    ("/sourcea/platform/workspace", "/sourcea/forge/terminal/workspace"),
    ("/platform/sign-in", "/auth/sign-in"),
    ("/platform/sign-up", "/auth/sign-up"),
    ("/platform/profile", "/sourcea/forge/terminal/profile"),
    ("/platform/workspace", "/sourcea/forge/terminal/workspace"),
)

SOURCEA_HTML_PATH_RE = re.compile(
    r'(/sourcea/(?:[^"\s<>#?]+/)*[^"\s<>#?]+)\.html(#[^"\s<>]*)?',
)

# Static assets under /sourcea/ — never append .html (truth gate JSON must stay JSON)
STATIC_ASSET_SUFFIXES = frozenset(
    {".json", ".js", ".css", ".svg", ".webp", ".png", ".jpg", ".jpeg", ".mp4", ".dmg"}
)


def path_to_clean(m: re.Match[str]) -> str:
    base = m.group(1)
    frag = m.group(2) or ""
    if base.endswith("/index"):
        base = base[: -len("index")]
    return base + frag


def strip_sourcea_html_paths(text: str) -> str:
    """Extensionless /sourcea/ paths — keeps #fragments, drops .html."""
    return SOURCEA_HTML_PATH_RE.sub(path_to_clean, text)


def clean_url_for_html(rel_posix: str) -> str:
    """Map dist-relative path to extensionless public URL."""
    rel = rel_posix.lstrip("/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel.endswith(".html"):
        return "/" + rel[: -len(".html")]
    return "/" + rel


def write_redirects(dist: Path, *, html_rewrites: bool = False) -> list[str]:
    """Write Cloudflare Pages _redirects.

    Default html_rewrites=False — CF Pages Pretty URLs already serves
    ``platform.html`` at ``/sourcea/platform``. Adding 200 rewrites to ``.html``
    causes infinite 308 loops with Pretty URLs enabled.
    """
    lines: list[str] = []
    seen: set[str] = set()

    def add(rule: str) -> None:
        if rule not in seen:
            seen.add(rule)
            lines.append(rule)

    if html_rewrites:
        for html in sorted(dist.rglob("*.html")):
            rel = html.relative_to(dist).as_posix()
            file_url = "/" + rel
            clean = clean_url_for_html(rel)
            if clean == file_url:
                continue
            add(f"{clean}  {file_url}  200")

    contract_srcs = {src for src, _ in CONTRACT_REWRITE_200}
    for src, dest in CONTRACT_REWRITE_200:
        add(f"{src}  {dest}  200")

    for src, dest in SHORT_ALIASES:
        if src in contract_srcs:
            continue
        add(f"{src}  {dest}  302")

    # /forge/cursor-bridge, /forge/try, etc. — without this, Pages serves root index.html
    add("/forge/*  /sourcea/forge/:splat  302")
    add("/attach/*  /sourcea/attach/:splat  200")
    add("/loops/*  /sourcea/loops/:splat  200")
    add("/case-studies/*  /sourcea/case-studies/:splat  200")

    for src, dest in REDIRECT_301:
        add(f"{src}  {dest}  301")

    text = "\n".join(lines) + "\n"
    (dist / "_redirects").write_text(text, encoding="utf-8")
    return lines


def parse_redirect_lines(lines: list[str]) -> list[tuple[str, str]]:
    """Extract (src, dest) pairs from `_redirects` lines."""
    pairs: list[tuple[str, str]] = []
    for line in lines:
        if not line or line.startswith("#"):
            continue
        parts = [part for part in line.split() if part]
        if len(parts) >= 2:
            pairs.append((parts[0], parts[1]))
    return pairs


def _clean_route(route: str) -> str:
    route = route.strip().split("?", 1)[0].split("#", 1)[0]
    if not route.startswith("/"):
        route = "/" + route
    route = re.sub(r"/+", "/", route).rstrip("/")
    return route


def _resolve_redirect_target(base_dir: Path, dest: str) -> Path | None:
    cleaned = _clean_route(dest)
    if cleaned == "/":
        return base_dir / "index.html"
    rel = cleaned.lstrip("/")
    if not rel:
        return base_dir / "index.html"

    file_candidate = base_dir / f"{rel}.html"
    if file_candidate.is_file():
        return file_candidate

    index_candidate = base_dir / rel / "index.html"
    if index_candidate.is_file():
        return index_candidate

    directory_candidate = base_dir / rel
    if directory_candidate.is_file():
        return directory_candidate

    return None


def materialize_extensionless_aliases(
    base_dir: Path,
    *,
    redirect_pairs: list[tuple[str, str]] | None = None,
) -> dict[str, int]:
    """Create extensionless directory aliases (e.g., /foo/index.html from /foo.html).

    Returns counts for visibility in build/deploy output.
    """
    created = 0
    updated = 0
    skipped = 0

    for html in sorted(base_dir.rglob("*.html")):
        if html.name == "index.html":
            continue
        alias_dir = html.with_suffix("")
        alias_file = alias_dir / "index.html"
        if alias_file == html:
            continue
        alias_dir.mkdir(parents=True, exist_ok=True)
        if alias_file.exists():
            alias_file.unlink()
            updated += 1
        else:
            created += 1
        shutil.copy2(html, alias_file)

    for src, dest in redirect_pairs or []:
        if "*" in src or "*" in dest:
            continue
        src_clean = _clean_route(src)
        if not src_clean or src_clean == "/" or src_clean == "/sourcea":
            continue
        target = _resolve_redirect_target(base_dir, dest)
        if target is None:
            continue
        alias_file = (base_dir / src_clean.lstrip("/")) / "index.html"
        if alias_file == target:
            continue
        alias_file.parent.mkdir(parents=True, exist_ok=True)
        if alias_file.exists():
            alias_file.unlink()
            updated += 1
        else:
            created += 1
        shutil.copy2(target, alias_file)

    return {"created": created, "updated": updated, "skipped": skipped}


def strip_internal_html_links(root: Path | None = None) -> dict:
    """Remove .html from internal /sourcea/ paths in HTML, JS, and catalog JSON."""
    base = root or GREEN
    changed: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".js", ".json"}:
            continue
        if "dist" in path.parts or path.name == "sourcea_clean_urls_v1.py":
            continue
        raw = path.read_text(encoding="utf-8")
        new = strip_sourcea_html_paths(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return {"ok": True, "changed": changed, "count": len(changed)}


def is_static_asset_url(path: str) -> bool:
    """True when URL already names a static file (e.g. /sourcea/data/boot-proof.json)."""
    clean = path.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    if not clean:
        return False
    suffix = Path(clean).suffix.lower()
    return suffix in STATIC_ASSET_SUFFIXES


def vercel_rewrites() -> list[dict[str, str]]:
    """Vercel Hobby — extensionless HTML only; never rewrite .json/.js/.css assets."""
    rows = [{"source": src, "destination": f"{dest}.html"} for src, dest in SHORT_ALIASES]
    # Each path segment must be extensionless — excludes /sourcea/data/*.json truth gate
    rows.append(
        {
            "source": "/sourcea/:path((?:[^/.]+/)*[^/.]+)",
            "destination": "/sourcea/:path.html",
        }
    )
    return rows


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(description="SourceA clean URL helpers")
    p.add_argument("--strip-links", action="store_true")
    p.add_argument("--write-redirects", type=Path, metavar="DIST")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out: dict = {}
    if args.strip_links:
        out["strip"] = strip_internal_html_links()
    if args.write_redirects:
        out["redirects"] = {"lines": len(write_redirects(args.write_redirects))}
    if args.json:
        print(json.dumps(out, indent=2))
    elif not out:
        p.print_help()
    else:
        print(out)
