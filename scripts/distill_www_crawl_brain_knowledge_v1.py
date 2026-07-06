#!/usr/bin/env python3
"""Auto-crawl all public SourceA www HTML + JSON into Brain knowledge."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_lib_v1 import (  # noqa: E402
    PINNED_STEMS,
    chunk_text,
    extract_html_sections,
    infer_lane,
    json_to_markdown,
    path_to_www_url,
    source_file_hash,
)

WWW_ROOT = ROOT / "sites" / "SourceA-landing" / "green-unified"
DATA_ROOT = WWW_ROOT / "data"
OUT_HTML = ROOT / "data" / "chatbot-knowledge" / "crawled" / "www"
OUT_JSON = ROOT / "data" / "chatbot-knowledge" / "crawled" / "json"
REGISTRY = ROOT / "data" / "brain-chat-crawl-registry-v1.json"

SKIP_DIRS = {"reference", "node_modules", "dist", ".vercel"}
SKIP_FILES = {"legacy-full-home-v1.html", "pulse-founder.html"}


def frontmatter(**kwargs) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["---", f"updated: {now}"]
    for k, v in kwargs.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def should_skip_html(path: Path) -> bool:
    rel = path.relative_to(WWW_ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return True
    if path.name in SKIP_FILES:
        return True
    return False


def _load_prev_registry() -> dict[str, dict]:
    if not REGISTRY.is_file():
        return {}
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    prev: dict[str, dict] = {}
    for section in ("html", "json"):
        for row in data.get(section) or []:
            path = str(row.get("path") or "")
            if path:
                prev[path] = row
    return prev


def crawl_html(*, prev: dict[str, dict] | None = None) -> list[dict]:
    OUT_HTML.mkdir(parents=True, exist_ok=True)
    prev = prev or {}
    results = []
    skipped = 0
    for html in sorted(WWW_ROOT.rglob("*.html")):
        if should_skip_html(html):
            continue
        rel = html.relative_to(ROOT).as_posix()
        rel_www = html.relative_to(WWW_ROOT).as_posix()
        page_hint = html.stem
        if html.name == "index.html":
            page_hint = html.parent.name if html.parent != WWW_ROOT else "home"
        lane = infer_lane(rel_www, page_hint)
        www_url = path_to_www_url(rel_www)
        raw = html.read_text(encoding="utf-8", errors="replace")
        sections = extract_html_sections(raw)
        title = page_hint.replace("-", " ").title()
        body = frontmatter(lane=lane, source_path=rel, public="true", www_url=www_url)
        body += f"# {title}\n\n" + "\n\n".join(sections)
        slug = rel_www.replace("/", "__").replace(".html", "")
        out = OUT_HTML / f"{slug}.md"
        src_hash = source_file_hash(html)
        prior = prev.get(rel)
        if prior and prior.get("source_hash") == src_hash and out.is_file():
            results.append({**prior, "skipped": True})
            skipped += 1
            continue
        out.write_text(body.strip() + "\n", encoding="utf-8")
        results.append(
            {
                "kind": "html",
                "path": rel,
                "output": out.relative_to(ROOT).as_posix(),
                "lane": lane,
                "www_url": www_url,
                "chars": len(body),
                "content_hash": hashlib.sha256(body.encode()).hexdigest()[:16],
                "source_hash": src_hash,
            }
        )
    return results


def crawl_json(*, prev: dict[str, dict] | None = None) -> list[dict]:
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    prev = prev or {}
    results = []
    skipped = 0
    skip_json = {"sourcea-brain-chat-config-v1.json", "sourcea-platform-auth-config-v1.json"}
    for jf in sorted(DATA_ROOT.glob("*.json")):
        if jf.name in skip_json:
            continue
        rel = jf.relative_to(ROOT).as_posix()
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        lane = infer_lane(jf.name, jf.stem)
        title = jf.stem.replace("-", " ").replace("_", " ").title()
        md = json_to_markdown(data, title)
        if len(md) < 80:
            continue
        body = frontmatter(lane=lane, source_path=rel, public="true", kind="json")
        body += md
        out = OUT_JSON / f"{jf.stem}.md"
        src_hash = source_file_hash(jf)
        prior = prev.get(rel)
        if prior and prior.get("source_hash") == src_hash and out.is_file():
            results.append({**prior, "skipped": True})
            skipped += 1
            continue
        out.write_text(body.strip() + "\n", encoding="utf-8")
        results.append(
            {
                "kind": "json",
                "path": rel,
                "output": out.relative_to(ROOT).as_posix(),
                "lane": lane,
                "chars": len(body),
                "content_hash": hashlib.sha256(body.encode()).hexdigest()[:16],
                "source_hash": src_hash,
            }
        )
    if skipped:
        pass  # counted in payload via skipped rows
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    prev = _load_prev_registry()
    html_rows = crawl_html(prev=prev)
    json_rows = crawl_json(prev=prev)
    skipped = sum(1 for r in html_rows + json_rows if r.get("skipped"))
    registry = {
        "schema": "brain-chat-crawl-registry-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "html_count": len(html_rows),
        "json_count": len(json_rows),
        "skipped_unchanged": skipped,
        "html": html_rows,
        "json": json_rows,
    }
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    payload = {
        "ok": True,
        "html": len(html_rows),
        "json": len(json_rows),
        "skipped_unchanged": skipped,
        "registry": str(REGISTRY.relative_to(ROOT)),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"crawl OK — {len(html_rows)} html · {len(json_rows)} json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
