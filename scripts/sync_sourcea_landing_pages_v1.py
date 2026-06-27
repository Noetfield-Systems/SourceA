#!/usr/bin/env python3
"""Sync nav, footer, explore grid, chatbot script across SourceA green-unified HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "SourceA-landing" / "green-unified"

NAV_OLD = """        <a href="/sourcea/platform" data-sa-nav>Platform</a>
        <a href="/sourcea/growth" data-sa-nav>Growth</a>"""

NAV_NEW = """        <a href="/sourcea/platform" data-sa-nav>Platform</a>
        <a href="/sourcea/team" data-sa-nav>Team</a>
        <a href="/sourcea/growth" data-sa-nav>Growth</a>"""

FOOTER_PRODUCT_OLD = """      <a href="/sourcea/platform">Platform</a>
      <a href="/sourcea/growth">Growth system</a>"""

FOOTER_PRODUCT_NEW = """      <a href="/sourcea/platform">Platform</a>
      <a href="/sourcea/offer">Offer</a>
      <a href="/sourcea/case-studies/">Case studies</a>
      <a href="/sourcea/team">Your team</a>
      <a href="/sourcea/growth">Growth system</a>
      <a href="/sourcea/scenario">Scenario</a>
      <a href="/sourcea/proof">Verification</a>
      <a href="/sourcea/compare">Compare</a>
      <a href="/sourcea/pricing">Pricing</a>
      <a href="/sourcea/security">Security &amp; procurement</a>
      <a href="/sourcea/sources">Sources &amp; evidence</a>"""

FOOTER_CASE_STUDIES_BLOCK = """    <nav class="sa-footer-col" aria-label="Case studies">
      <h4>Case studies</h4>
      <a href="/sourcea/case-studies/">All case studies</a>
      <a href="/sourcea/case-studies/pureflow">PureFlow (#1 · trades)</a>
      <a href="/sourcea/case-studies/agentgo">AgentGo (#2 · factory)</a>
    </nav>
"""

FOOTER_BRAND_OLD = "      <p>Proof-backed acquisition systems in 48 hours — built in Canada.</p>"
FOOTER_BRAND_NEW = "      <p>Business Acquisition Systems — proof-backed engines for contracts and recurring revenue.</p>"

FOOTER_BOTTOM_OLD = "© SourceA 2026 · One brand · outcome-first"
FOOTER_BOTTOM_NEW = (
    "© 2026 Noetfield Systems Inc. · SourceA is a product of Noetfield Systems Inc. · "
    '<a href="https://noetfield.com" rel="noopener">noetfield.com</a>'
)

HEADER_SHELL = """<div class="ar-scroll-progress" aria-hidden="true"><div class="ar-scroll-progress-bar"></div></div>
<a class="skip-link" href="#main-content">Skip to content</a>
<div class="ar-nav-backdrop" aria-hidden="true"></div>

<header class="ar-header sa-header">
  <div class="ar-container ar-header-shell">
    <div class="ar-header-inner">
      <a class="ar-logo" href="/" aria-label="SourceA home">
        <span class="ar-logo-text">Source<span class="ar-logo-run sa-logo-run">A</span></span>
      </a>
      <nav class="ar-nav" id="ar-nav" aria-label="Primary">
        <a href="/" data-sa-nav data-sa-nav-home>Home</a>
        <a href="/sourcea/offer" data-sa-nav>Offer</a>
        <a href="/sourcea/pricing" data-sa-nav>Pricing</a>
        <a href="/sourcea/investors" data-sa-nav>Investors</a>
        <a href="/sourcea/kernel/" data-sa-nav>Kernel</a>
        <a class="ar-btn ar-btn-ghost ar-btn-sm ar-nav-signin-mobile" href="/platform">Sign in</a>
        <a class="ar-btn ar-btn-primary ar-btn-sm ar-nav-cta-mobile sa-btn-glow" data-sa-book-cta href="https://cal.com/sourcea/proof-demo">Book a call</a>
      </nav>
      <button type="button" class="ar-nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="ar-nav">
        <span class="ar-nav-toggle-bar"></span>
        <span class="ar-nav-toggle-bar"></span>
        <span class="ar-nav-toggle-bar"></span>
      </button>
      <div class="ar-header-actions">
        <a class="ar-btn ar-btn-ghost ar-btn-sm ar-header-signin" href="/platform">Sign in</a>
        <a class="ar-btn ar-btn-primary ar-btn-sm sa-btn-glow ar-header-cta" data-sa-book-cta href="https://cal.com/sourcea/proof-demo">Book a call</a>
      </div>
    </div>
  </div>
</header>"""

HEADER_RE = re.compile(
    r'<div class="ar-scroll-progress".*?</header>',
    re.DOTALL,
)

NAV_LINKS_EXPECTED = [
    "/",
    "/sourcea/offer",
    "/sourcea/pricing",
    "/sourcea/investors",
    "/sourcea/kernel/",
]

COMMERCIAL_EXPLORE_PAGES = frozenset({"pricing.html"})

COMMERCIAL_PAGES_NO_CASE_FOOTER = frozenset(
    {"index.html", "offer.html", "investors.html", "pricing.html"}
)

KERNEL_HEADER_SKIP = frozenset({"legacy-full-home-v1.html"})

CHATBOT_SCRIPT = '<script src="/sourcea/sourcea-chatbot.js" defer></script>'

EXPLORE_COMMERCIAL = """
  <section class="ar-section ar-section-muted ar-reveal sa-explore">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">Close a deal</p>
        <h2>Book a call or review the offer.</h2>
      </div>
      <div class="sa-explore-grid">
        <a class="sa-explore-card" href="https://cal.com/sourcea/proof-demo"><span class="sa-explore-num">01</span><strong>Book a call</strong><span>Scope your 48-hour system</span></a>
        <a class="sa-explore-card" href="/sourcea/offer"><span class="sa-explore-num">02</span><strong>48-hour offer</strong><span>Deliverables and setup pricing</span></a>
        <a class="sa-explore-card" href="mailto:hello@sourcea.app"><span class="sa-explore-num">03</span><strong>Email</strong><span>hello@sourcea.app</span></a>
      </div>
    </div>
  </section>
"""

EXPLORE_KERNEL_LINK = '<p class="sa-metric-note" style="margin-top:1.25rem;text-align:center">Technical depth: <a href="/sourcea/kernel/">Kernel hub →</a></p>'

BREADCRUMB_LOOP_FIX = re.compile(
    r'(<a href="/sourcea/platform\">Platform</a>)\s*'
    r'(<a href="/sourcea/growth\">Growth system</a><span class="ar-breadcrumb-sep">/</span>)',
    re.MULTILINE,
)

BREADCRUMB_LOOP_REPL = r'\1<span class="ar-breadcrumb-sep">/</span>\n        <a href="/sourcea/loops/">Loops</a><span class="ar-breadcrumb-sep">/</span>'

HEADER_SYNC_SKIP_PREFIXES = ("attach", "reference", "factories", "dist", "downloads", "trust")
SCRIPT_SYNC_SKIP_PREFIXES = ("attach", "reference", "factories", "dist", "downloads", "trust")
HEADER_SYNC_SKIP_NAMES = frozenset(
    {"funnel.html", "home.html", "hub.html", "sandbox.html", "start.html", "changelog.html", "mvp-landing.html"}
)


def skip_header_sync(rel: Path) -> bool:
    if rel.name in HEADER_SYNC_SKIP_NAMES:
        return True
    if rel.parts and rel.parts[0] == "kernel" and rel.name in KERNEL_HEADER_SKIP:
        return True
    if not rel.parts:
        return False
    return rel.parts[0] in HEADER_SYNC_SKIP_PREFIXES


def skip_script_sync(rel: Path) -> bool:
    if not rel.parts:
        return False
    return rel.parts[0] in SCRIPT_SYNC_SKIP_PREFIXES


def inject_chatbot_script(text: str) -> tuple[str, bool]:
    if CHATBOT_SCRIPT in text:
        return text, False
    if "</body>" not in text:
        return text, False
    return text.replace("</body>", f"{CHATBOT_SCRIPT}\n</body>", 1), True


def inject_footer_case_studies(text: str) -> tuple[str, bool]:
    if 'aria-label="Case studies"' in text and "case-studies/" in text:
        return text, False
    marker = '<nav class="sa-footer-col" aria-label="Factory loops">'
    if marker in text:
        return text.replace(marker, FOOTER_CASE_STUDIES_BLOCK + marker, 1), True
    marker2 = '<nav class="sa-footer-col" aria-label="Contact">'
    if marker2 in text and "sa-footer-rich" in text:
        return text.replace(marker2, FOOTER_CASE_STUDIES_BLOCK + marker2, 1), True
    return text, False


def patch_file(path: Path) -> list[str]:
    changes: list[str] = []
    text = path.read_text(encoding="utf-8")
    orig = text

    if NAV_OLD in text:
        text = text.replace(NAV_OLD, NAV_NEW)
        changes.append("nav")

    if FOOTER_PRODUCT_OLD in text:
        text = text.replace(FOOTER_PRODUCT_OLD, FOOTER_PRODUCT_NEW)
        changes.append("footer-product")

    if FOOTER_BRAND_OLD in text:
        text = text.replace(FOOTER_BRAND_OLD, FOOTER_BRAND_NEW)
        changes.append("footer-brand")

    text = text.replace(FOOTER_BOTTOM_OLD, FOOTER_BOTTOM_NEW)

    rel = path.relative_to(ROOT)
    if not skip_header_sync(rel) and HEADER_RE.search(text):
        new_text = HEADER_RE.sub(HEADER_SHELL, text, count=1)
        if new_text != text:
            text = new_text
            changes.append("header-shell")

    if "Get Started" in text:
        text = text.replace("Get Started", "Book proof demo")
        changes.append("cta-legacy")

    if "loops/" in str(path) and "Growth system" in text:
        text = BREADCRUMB_LOOP_FIX.sub(BREADCRUMB_LOOP_REPL, text)
        changes.append("breadcrumb")

    rel_key = str(rel).replace("\\", "/")
    if rel_key in COMMERCIAL_EXPLORE_PAGES:
        old_explore = re.search(
            r'<section class="ar-section ar-section-muted ar-reveal sa-explore">.*?</section>',
            text,
            re.DOTALL,
        )
        if old_explore:
            text = (
                text[: old_explore.start()]
                + EXPLORE_COMMERCIAL.strip()
                + "\n\n"
                + text[old_explore.end() :]
            )
            changes.append("commercial-explore")
        elif "sa-explore" not in text and "<footer" in text:
            marker = "<footer class=\"ar-site-footer"
            text = text.replace(marker, EXPLORE_COMMERCIAL.strip() + "\n\n" + marker, 1)
            changes.append("commercial-explore-inject")

    # Strip legacy 16-card explore from kernel-era pages (platform, growth, etc.)
    if rel_key not in COMMERCIAL_EXPLORE_PAGES and rel.name != "index.html":
        old_big = re.search(
            r'<section class="ar-section ar-section-muted ar-reveal sa-explore">.*?Every story\..*?</section>',
            text,
            re.DOTALL,
        )
        if old_big:
            text = text[: old_big.start()] + text[old_big.end() :]
            if EXPLORE_KERNEL_LINK not in text and "<footer" in text and rel.parts and rel.parts[0] != "kernel":
                text = text.replace(
                    "<footer class=\"ar-site-footer",
                    EXPLORE_KERNEL_LINK + "\n\n<footer class=\"ar-site-footer",
                    1,
                )
            changes.append("strip-legacy-explore")

    if not skip_script_sync(rel):
        rel_key = str(rel).replace("\\", "/")
        if rel_key not in COMMERCIAL_PAGES_NO_CASE_FOOTER:
            text, did = inject_footer_case_studies(text)
            if did:
                changes.append("footer-case-studies")
        text, did = inject_chatbot_script(text)
        if did:
            changes.append("chatbot-script")

    if text != orig:
        path.write_text(text, encoding="utf-8")
    return changes


def validate_headers() -> None:
    """Fail if any canonical page header shell diverges from HEADER_SHELL."""
    canonical = HEADER_SHELL.strip()
    fails: list[str] = []
    validated = 0
    for html in sorted(ROOT.rglob("*.html")):
        rel = html.relative_to(ROOT)
        if skip_header_sync(rel):
            continue
        validated += 1
        text = html.read_text(encoding="utf-8")
        m = HEADER_RE.search(text)
        if not m:
            fails.append(f"{rel}: no header shell")
            continue
        if m.group(0).strip() != canonical:
            fails.append(f"{rel}: header drift")
        if "Get Started" in text:
            fails.append(f"{rel}: legacy Get Started")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        raise SystemExit(1)
    print(f"OK: header validation — {validated} canonical pages")


def main() -> None:
    for html in sorted(ROOT.rglob("*.html")):
        rel = html.relative_to(ROOT)
        if skip_header_sync(rel):
            continue
        ch = patch_file(html)
        if ch:
            print(f"{rel}: {', '.join(ch)}")
    validate_headers()
    print("sync-sourcea-landing-pages-v1: done")


if __name__ == "__main__":
    main()
