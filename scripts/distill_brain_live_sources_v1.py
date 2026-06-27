#!/usr/bin/env python3
"""Index and distill ALL public live sources for Brain (112+ files target)."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_lib_v1 import (  # noqa: E402
    extract_html_sections,
    infer_lane,
    json_to_markdown,
    path_to_www_url,
    strip_secrets,
)
from distill_www_crawl_brain_knowledge_v1 import crawl_html, crawl_json, WWW_ROOT  # noqa: E402

ALLOWLIST = ROOT / "data/brain-public-data-allowlist-v1.json"
OUT_DATA = ROOT / "data/chatbot-knowledge/crawled/data"
INDEX_OUT = ROOT / "data/brain-live-source-index-v1.json"

WWW_ROOTS = [
    ROOT / "sites/SourceA-landing/green-unified",
    ROOT / "SourceA-landing/green-unified",
]
SKIP_DIRS = {"reference", "node_modules", "dist", ".vercel"}


def frontmatter(**kwargs) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["---", f"updated: {now}"]
    for k, v in kwargs.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def crawl_public_data_json() -> list[dict]:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    allow = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    forbidden = allow.get("forbidden_prefixes", [])
    results = []
    paths = set(allow.get("paths", []))
    for jf in (ROOT / "data").glob("sourcea*.json"):
        rel = jf.relative_to(ROOT).as_posix()
        if any(rel.startswith(p) for p in forbidden):
            continue
        if rel not in paths and "catalog" not in jf.name and "landing" not in jf.name:
            if "public" not in jf.name and "orient" not in jf.name and "dual-plane" not in jf.name:
                continue
        paths.add(rel)

    for rel in sorted(paths):
        fp = ROOT / rel
        if not fp.is_file():
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        lane = infer_lane(rel, fp.stem)
        md = json_to_markdown(data, fp.stem.replace("-", " ").title())
        if len(md) < 60:
            continue
        body = frontmatter(lane=lane, source_path=rel, public="true", kind="json")
        body += md
        slug = rel.replace("/", "__")
        out = OUT_DATA / f"{slug}.md"
        out.write_text(body.strip() + "\n", encoding="utf-8")
        results.append(
            {
                "kind": "public_data",
                "path": rel,
                "output": out.relative_to(ROOT).as_posix(),
                "lane": lane,
                "content_hash": hashlib.sha256(body.encode()).hexdigest()[:16],
            }
        )
    return results


def dedupe_www_roots() -> list[dict]:
    """Crawl primary www; skip duplicate SourceA-landing mirror if same hash."""
    return crawl_html()


def build_index(*sections) -> dict:
    all_rows = []
    for rows in sections:
        all_rows.extend(rows)
    unique_paths = {r["path"] for r in all_rows}
    return {
        "schema": "brain-live-source-index-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_file_count": len(unique_paths),
        "distill_row_count": len(all_rows),
        "target_minimum": 112,
        "meets_target": len(unique_paths) >= 112,
        "sources": all_rows,
    }


def main() -> int:
    html_rows = dedupe_www_roots()
    json_rows = crawl_json()
    data_rows = crawl_public_data_json()
    index = build_index(html_rows, json_rows, data_rows)
    INDEX_OUT.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "source_files": index["source_file_count"],
                "meets_112": index["meets_target"],
                "html": len(html_rows),
                "json": len(json_rows),
                "public_data": len(data_rows),
                "index": str(INDEX_OUT.relative_to(ROOT)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
