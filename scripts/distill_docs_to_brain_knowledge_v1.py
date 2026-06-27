#!/usr/bin/env python3
"""Distill allowlisted public docs into Brain knowledge (expanded allowlist)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_lib_v1 import chunk_text, infer_lane, strip_secrets  # noqa: E402

MANIFEST = ROOT / "data" / "CHATBOT_KNOWLEDGE_MANIFEST.json"
ALLOWLIST = ROOT / "data" / "brain-chat-public-docs-allowlist-v1.json"
OUT_DIR = ROOT / "data" / "chatbot-knowledge" / "crawled" / "docs"


def frontmatter(lane: str, source: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"---\nlane: {lane}\nupdated: {now}\nsource_path: {source}\npublic: true\n---\n\n"


def distill_file(path: Path, lane: str) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    raw = strip_secrets(path.read_text(encoding="utf-8", errors="replace"))
    chunks = chunk_text(raw, max_chars=8000)
    body = frontmatter(lane, rel) + (chunks[0] if chunks else raw[:8000])
    slug = rel.replace("/", "__")
    out = OUT_DIR / f"{slug}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body.strip() + "\n", encoding="utf-8")
    return {
        "path": rel,
        "output": out.relative_to(ROOT).as_posix(),
        "chars": len(body),
        "content_hash": hashlib.sha256(body.encode()).hexdigest()[:16],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    allow = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    paths: list[str] = allow.get("paths", [])
    prefix_allow = allow.get("prefixes", [])
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prefix_allow.extend(manifest.get("public_safe_doc_allowlist_prefixes", []))

    seen: set[str] = set()
    results = []
    for p in paths:
        fp = ROOT / p
        if fp.is_file() and p not in seen:
            seen.add(p)
            results.append(distill_file(fp, infer_lane(p)))

    docs_dir = ROOT / "docs"
    if docs_dir.is_dir():
        for md in sorted(docs_dir.glob("SOURCEA_*.md")):
            rel = md.relative_to(ROOT).as_posix()
            if rel in seen:
                continue
            if not any(rel.startswith(pref) for pref in prefix_allow):
                continue
            if any(x in rel.lower() for x in ("incident", "internal", "locked_v0", "draft")):
                # still allow LOCKED public positioning docs
                if not any(x in rel for x in ("POSITIONING", "UI_STANDARD", "DISCLOSURE", "ORIENTATION", "FREEMIUM", "TERMINOLOGY", "DUAL_PLANE", "LANDING_DEPLOY")):
                    continue
            seen.add(rel)
            results.append(distill_file(md, infer_lane(rel)))

    payload = {"ok": True, "count": len(results), "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"docs distill OK — {len(results)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
