#!/usr/bin/env python3
"""Distill public positioning markdown from machine SSOT JSON — sole writer for positioning-public.md."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSITIONING = ROOT / "sites/SourceA-landing/green-unified/data/sourcea-positioning-v1.json"
OUT = ROOT / "data/chatbot-knowledge/manual/positioning-public.md"


def main() -> int:
    if not POSITIONING.is_file():
        print(json.dumps({"ok": False, "error": f"missing {POSITIONING}"}))
        return 1
    pos = json.loads(POSITIONING.read_text(encoding="utf-8"))
    one_line = str(pos.get("one_line") or "").strip()
    if not one_line:
        print(json.dumps({"ok": False, "error": "one_line empty in positioning JSON"}))
        return 1
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = f"""---
lane: core
kind: positioning
updated: {now}
source_path: sites/SourceA-landing/green-unified/data/sourcea-positioning-v1.json
public: true
pinned: true
www_url: https://sourcea.app/
---

# SourceA positioning (public)

## One line

{one_line}

## What SourceA is NOT

- Not "just records" or verification-only software
- Not a generic ChatGPT wrapper
- Not a pitch that opens with dollar amounts

## What Forge is

Forge Terminal is the execution desk — try it at `/sourcea/forge/terminal`. It is a product feature, not the SourceA tagline.

## Primary CTAs

| Intent | URL |
|--------|-----|
| Try in browser | `/sourcea/forge/terminal` |
| Live proof | `/sourcea/proof/live` |
| Talk to human (escalation only) | `https://cal.com/sourcea/proof-demo` |
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body.strip() + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(OUT.relative_to(ROOT)), "one_line": one_line, "chars": len(body)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
