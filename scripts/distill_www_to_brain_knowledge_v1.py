#!/usr/bin/env python3
"""Distill SourceA www HTML pages into public Brain knowledge markdown chunks."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "CHATBOT_KNOWLEDGE_MANIFEST.json"
OUT_DIR = ROOT / "data" / "chatbot-knowledge" / "distilled"

STRIP_PATTERNS = [
    re.compile(r"<script[\s\S]*?</script>", re.I),
    re.compile(r"<style[\s\S]*?</style>", re.I),
    re.compile(r"<!--[\s\S]*?-->"),
]
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def strip_html(html: str) -> str:
    text = html
    for pat in STRIP_PATTERNS:
        text = pat.sub(" ", text)
    text = unescape(TAG_RE.sub(" ", text))
    return WS_RE.sub(" ", text).strip()


def extract_sections(html: str) -> list[str]:
    """Pull h1-h3 anchored text blocks for chunking."""
    blocks: list[str] = []
    for m in re.finditer(r"<h[1-3][^>]*>([\s\S]*?)</h[1-3]>", html, re.I):
        heading = strip_html(m.group(1))
        if heading:
            blocks.append(f"## {heading}")
    body = strip_html(html)
    if body:
        # cap raw body excerpt for safety
        blocks.append(body[:4000])
    return blocks


def frontmatter(lane: str, source: str, public: bool, www_url: str | None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f"lane: {lane}",
        f"updated: {now}",
        f"source_path: {source}",
        f"public: {'true' if public else 'false'}",
    ]
    if www_url:
        lines.append(f"www_url: {www_url}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def distill_source(entry: dict) -> dict:
    src = ROOT / entry["path"]
    out = ROOT / entry["output"]
    if not src.exists():
        return {"id": entry["id"], "ok": False, "error": "source_missing", "path": str(src)}
    html = src.read_text(encoding="utf-8", errors="replace")
    sections = extract_sections(html)
    title = entry["id"].replace("-", " ").title()
    body = frontmatter(entry.get("lane", "core"), entry["path"], entry.get("public", True), entry.get("www_url"))
    body += f"# {title}\n\n"
    body += "\n\n".join(sections[:12])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body.strip() + "\n", encoding="utf-8")
    content_hash = hashlib.sha256(body.encode()).hexdigest()[:16]
    return {
        "id": entry["id"],
        "ok": True,
        "output": str(out.relative_to(ROOT)),
        "chars": len(body),
        "content_hash": content_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = []
    for entry in manifest.get("sources", []):
        if entry.get("distill") != "www":
            continue
        results.append(distill_source(entry))
    payload = {"schema": "distill-www-to-brain-knowledge-v1", "results": results, "ok": all(r.get("ok") for r in results)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            status = "OK" if r.get("ok") else f"FAIL {r.get('error')}"
            print(f"{r.get('id')}: {status}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
