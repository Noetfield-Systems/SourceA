#!/usr/bin/env python3
"""Apply client-facing copy replacements to SourceA green-unified HTML (public voice)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
VOICE = ROOT / "data" / "sourcea-landing-client-voice-v1.json"

SKIP_DIRS = {"reference", "dist", "attach"}


def main() -> None:
    row = json.loads(VOICE.read_text(encoding="utf-8"))
    pairs: list[tuple[str, str]] = [(a, b) for a, b in row.get("replacements", [])]
    changed: list[str] = []
    for html in sorted(GREEN.rglob("*.html")):
        rel = html.relative_to(GREEN)
        if rel.parts and rel.parts[0] in SKIP_DIRS:
            continue
        text = html.read_text(encoding="utf-8")
        orig = text
        for old, new in pairs:
            if old in text:
                text = text.replace(old, new)
        if text != orig:
            html.write_text(text, encoding="utf-8")
            changed.append(str(rel))
    print(f"apply-sourcea-client-voice-v1: {len(changed)} files")
    for c in changed[:40]:
        print(f"  · {c}")
    if len(changed) > 40:
        print(f"  … +{len(changed) - 40} more")


if __name__ == "__main__":
    main()
