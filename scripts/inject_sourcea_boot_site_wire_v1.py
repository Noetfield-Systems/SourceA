#!/usr/bin/env python3
"""Wire sourcea-boot eval links + trust scripts across all green-unified HTML pages."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-boot-site-wire-v1.json"

BOOT_FOOTER_SNIPPET = (
    ' · <a href="/eval">sourcea-boot eval</a>'
    ' · <a href="https://github.com/kazemnezhadsina144-dot/sourcea-boot" data-trust-github-link target="_blank" rel="noopener">GitHub</a>'
)
WIRE_SCRIPT = '<script src="/sourcea/sourcea-boot-wire.js" defer></script>'
TRUST_SCRIPT = '<script src="/sourcea/sourcea-trust-bar.js" defer></script>'

SKIP_DIRS = {"dist", "reference", "attach", "unify", "unify-demo"}
SKIP_FILES = {"sourcea-landing-mock-v1.html"}


def _needs_wire(text: str) -> bool:
    return "sourcea-boot" not in text and "/eval" not in text


def _inject_footer(text: str) -> tuple[str, bool]:
    if not _needs_wire(text):
        return text, False
    m = re.search(r'(<div class="ar-container sa-footer-bottom">\s*<p>)(.*?)(</p>)', text, re.DOTALL)
    if m and "sourcea-boot" not in m.group(2):
        new_p = m.group(1) + m.group(2).rstrip() + BOOT_FOOTER_SNIPPET + m.group(3)
        return text[: m.start()] + new_p + text[m.end() :], True
    m2 = re.search(r'(<footer class="ar-footer"[^>]*>.*?<p[^>]*>)(.*?)(</p>)', text, re.DOTALL)
    if m2 and "sourcea-boot" not in m2.group(2):
        new_p = m2.group(1) + m2.group(2).rstrip() + BOOT_FOOTER_SNIPPET + m2.group(3)
        return text[: m2.start()] + new_p + text[m2.end() :], True
    if "</body>" in text:
        strip = (
            '\n<div class="sa-boot-wire-fallback" style="text-align:center;padding:1rem;font-size:0.85rem;color:var(--ar-text-muted)">'
            '<a href="/eval">sourcea-boot eval</a> · '
            '<a href="https://github.com/kazemnezhadsina144-dot/sourcea-boot" data-trust-github-link target="_blank" rel="noopener">GitHub</a>'
            "</div>\n"
        )
        return text.replace("</body>", strip + "</body>", 1), True
    return text, False


def _inject_scripts(text: str) -> tuple[str, bool]:
    changed = False
    if "sourcea-boot-wire.js" not in text and "</body>" in text:
        text = text.replace("</body>", WIRE_SCRIPT + "\n</body>", 1)
        changed = True
    if "[data-sa-trust-bar]" in text and "sourcea-trust-bar.js" not in text and "</body>" in text:
        text = text.replace("</body>", TRUST_SCRIPT + "\n</body>", 1)
        changed = True
    return text, changed


def wire_all() -> dict:
    changed: list[str] = []
    for path in sorted(GREEN.rglob("*.html")):
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        raw = path.read_text(encoding="utf-8")
        new = raw
        new, _ = _inject_footer(new)
        new, _ = _inject_scripts(new)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return {"ok": True, "changed": changed, "count": len(changed)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire sourcea-boot across landing HTML")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = wire_all()
    row["at"] = datetime.now(timezone.utc).isoformat()
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: wired {row['count']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
