#!/usr/bin/env python3
"""Replace footer entity placeholders with confirmed Noetfield legal line."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
SKIP_DIRS = {"reference", "dist"}

# Founder-confirmed · matches founder-home.html + security.html
ENTITY_LINE = (
    "© 2026 Noetfield Systems Inc. · SourceA is a product of Noetfield Systems Inc. · "
    '<a href="https://noetfield.com" rel="noopener">noetfield.com</a>'
)
NEUTRAL_STUB = "© SourceA 2026"


def main() -> None:
    changed: list[str] = []
    for path in sorted(GREEN.rglob("*.html")):
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if "{ENTITY}" not in text and NEUTRAL_STUB not in text:
            continue
        new = text.replace("{ENTITY} · ", f"{ENTITY_LINE} · ")
        new = new.replace("{ENTITY}", ENTITY_LINE)
        new = new.replace(f"{NEUTRAL_STUB} · ", f"{ENTITY_LINE} · ")
        new = new.replace(NEUTRAL_STUB, ENTITY_LINE)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(GREEN)))
    print(f"fix-sourcea-entity-placeholder-v1: {len(changed)} files")
    for c in changed:
        print(f"  · {c}")


if __name__ == "__main__":
    main()
