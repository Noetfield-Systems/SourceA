#!/usr/bin/env python3
"""Batch-upgrade SourceA landing pages — proof hero, segment router, script shell."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
SKIP_DIRS = {"dist", ".vercel", "reference", "node_modules", "__pycache__"}

SCRIPT_SHELL = """<script src="/sourcea/sourcea-landing-cta.js" defer></script>
<script src="/sourcea/sourcea-public-display-v1.js" defer></script>
<script src="/sourcea/sourcea-site-fallback-v1.js" defer></script>
<script src="/sourcea/sourcea-boot-wire.js" defer></script>
<script src="/sourcea/sourcea-chatbot.js" defer></script>
"""

REPLACEMENTS = [
    (r'data-sa-book-cta href="https://cal\.com/sourcea/proof-demo">Book proof demo', 'data-sa-proof-cta href="/sourcea/proof/live">See live receipt'),
    (r'data-sa-book-cta href="https://cal\.com/sourcea/proof-demo">Book factory-scale demo', 'data-sa-proof-cta href="/sourcea/proof/live">See live receipt'),
    (r'data-sa-book-cta href="https://cal\.com/sourcea/proof-demo">Book 15-min eval', 'data-sa-book-fallback href="https://cal.com/sourcea/proof-demo">Talk to a human'),
    (r'data-sa-book-cta href="https://cal\.com/sourcea/proof-demo">Book walkthrough', 'data-sa-book-fallback href="https://cal.com/sourcea/proof-demo">Talk to a human'),
    (r'>Book proof demo →</a>', '>See live receipt →</a>'),
    (r'>Book proof demo</a>', '>See live receipt</a>'),
    (r'href="mailto:hello@sourcea\.app">Book proof demo', 'href="/sourcea/proof/live">See live receipt'),
    (r'href="mailto:hello@sourcea\.app\?subject=sourcea-boot%20eval">Book proof demo', 'href="/sourcea/proof/live">See live receipt'),
    (r'<h2>Book a call or review the offer\.</h2>', '<h2>See proof or review the offer.</h2>'),
    (
        r'<a class="sa-explore-card" href="https://cal\.com/sourcea/proof-demo"><span class="sa-explore-num">01</span><strong>Book a call</strong><span>Scope your 48-hour system</span></a>',
        '<a class="sa-explore-card" href="/sourcea/proof/live"><span class="sa-explore-num">01</span><strong>See live receipt</strong><span>Verify on the page — no call</span></a>',
    ),
    (r'href="https://cal\.com/sourcea/proof-demo">Book a call</a>', 'href="/sourcea/proof/live">See live receipt</a>'),
    (r'>Book discovery</a>', '>See live proof</a>'),
    (r'data-sa-proof-cta href="/sourcea/forge/terminal">Try Forge Terminal</a>', 'data-sa-proof-cta href="/sourcea/proof/live">See live receipt</a>'),
    (r'live demo on screen-share', 'live proof on the page'),
    (r'on screen-share', 'on the page'),
    (r'Screen-share this', 'Verify this'),
]

FOOTER_LEARN = '<a href="/learn">Learn &amp; build</a>'


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def ensure_scripts(text: str) -> str:
    if "sourcea-landing-cta.js" in text:
        return text
    if "</body>" not in text:
        return text
    return text.replace("</body>", SCRIPT_SHELL + "</body>", 1)


def ensure_footer_learn(text: str) -> str:
    if FOOTER_LEARN in text or "sa-footer-col" not in text:
        return text
    # Add Learn link to first footer nav column after <h4>Start</h4> or Product
    for marker in ("<h4>Start</h4>", "<h4>Product</h4>"):
        if marker in text and FOOTER_LEARN not in text:
            return text.replace(marker, marker + "\n      " + FOOTER_LEARN, 1)
    return text


def upgrade_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    for pat, repl in REPLACEMENTS:
        text = re.sub(pat, repl, text)
    text = ensure_scripts(text)
    text = ensure_footer_learn(text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    n = 0
    for path in sorted(GREEN.rglob("*.html")):
        if should_skip(path):
            continue
        if upgrade_file(path):
            print("upgraded", path.relative_to(ROOT))
            n += 1
    print(f"OK: upgraded {n} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
