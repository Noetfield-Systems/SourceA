#!/usr/bin/env python3
"""Ensure sourcea-public-display-v1.js loads before trust-bar / boot-wire on landing HTML."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
TAG = '<script src="/sourcea/sourcea-public-display-v1.js" defer></script>'
SKIP_DIRS = {"reference", "dist", "attach"}
DEV_MARKER = 'data-sa-dev-ui="1"'

TARGETS = ("sourcea-trust-bar.js", "sourcea-boot-wire.js")


def main() -> None:
    changed: list[str] = []
    for path in sorted(GREEN.rglob("*.html")):
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if TAG in text or DEV_MARKER in text:
            continue
        if not any(t in text for t in TARGETS):
            continue
        for target in TARGETS:
            needle = f'<script src="/sourcea/{target}" defer></script>'
            if needle in text and TAG not in text:
                text = text.replace(needle, TAG + "\n" + needle, 1)
                changed.append(str(path.relative_to(GREEN)))
                break
        path.write_text(text, encoding="utf-8")
    print(f"wire-sourcea-public-display-v1: {len(changed)} files")
    for c in changed:
        print(f"  · {c}")


if __name__ == "__main__":
    main()
