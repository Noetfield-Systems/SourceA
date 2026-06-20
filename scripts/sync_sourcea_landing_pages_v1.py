#!/usr/bin/env python3
"""Sync nav, footer, explore grid across SourceA green-unified HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "SourceA-landing" / "green-unified"

NAV_OLD = """        <a href="/sourcea/platform.html" data-sa-nav>Platform</a>
        <a href="/sourcea/growth.html" data-sa-nav>Growth</a>"""

NAV_NEW = """        <a href="/sourcea/platform.html" data-sa-nav>Platform</a>
        <a href="/sourcea/team.html" data-sa-nav>Team</a>
        <a href="/sourcea/growth.html" data-sa-nav>Growth</a>"""

FOOTER_PRODUCT_OLD = """      <a href="/sourcea/platform.html">Platform</a>
      <a href="/sourcea/growth.html">Growth system</a>"""

FOOTER_PRODUCT_NEW = """      <a href="/sourcea/platform.html">Platform</a>
      <a href="/sourcea/team.html">Your team</a>
      <a href="/sourcea/growth.html">Growth system</a>
      <a href="/sourcea/scenario.html">Scenario</a>
      <a href="/sourcea/proof.html">Proof chain</a>
      <a href="/sourcea/compare.html">Compare</a>
      <a href="/sourcea/pricing.html">Pricing</a>
      <a href="/sourcea/security.html">Security &amp; procurement</a>
      <a href="/sourcea/sources.html">Sources &amp; evidence</a>"""

FOOTER_LOOPS_OLD = """      <h4>Loops</h4>
      <a href="/sourcea/loops/outreach.html">Outreach</a>"""

FOOTER_LOOPS_NEW = """      <h4>Loops</h4>
      <a href="/sourcea/loops/index.html">All loops</a>
      <a href="/sourcea/loops/outreach.html">Outreach</a>"""

FOOTER_BRAND_OLD = "      <p>Governed agent automation — built for platform engineers and agencies who owe their clients proof.</p>"
FOOTER_BRAND_NEW = "      <p>Execution Proof Infrastructure — governed agentic team for platform engineers and revenue agencies.</p>"

FOOTER_BOTTOM_OLD = "© SourceA 2026 · Runtime governance infrastructure"
FOOTER_BOTTOM_NEW = "© SourceA 2026 · Execution Proof Infrastructure"

HEADER_SHELL = """<div class="ar-scroll-progress" aria-hidden="true"><div class="ar-scroll-progress-bar"></div></div>
<a class="skip-link" href="#main-content">Skip to content</a>
<div class="ar-nav-backdrop" aria-hidden="true"></div>

<header class="ar-header sa-header">
  <div class="ar-container ar-header-shell">
    <div class="ar-header-inner">
      <a class="ar-logo" href="/sourcea/" aria-label="SourceA home">
        <span class="ar-logo-text">Source<span class="ar-logo-run sa-logo-run">A</span></span>
      </a>
      <nav class="ar-nav" id="ar-nav" aria-label="Primary">
        <a href="/sourcea/" data-sa-nav>Home</a>
        <a href="/sourcea/platform.html" data-sa-nav>Platform</a>
        <a href="/sourcea/team.html" data-sa-nav>Team</a>
        <a href="/sourcea/growth.html" data-sa-nav>Growth</a>
        <a href="/sourcea/scenario.html" data-sa-nav>Scenario</a>
        <a href="/sourcea/proof.html" data-sa-nav>Proof chain</a>
        <a href="/sourcea/compare.html" data-sa-nav>Compare</a>
        <a href="/sourcea/pricing.html" data-sa-nav>Pricing</a>
        <a class="ar-btn ar-btn-primary ar-btn-sm ar-nav-cta-mobile sa-btn-glow" href="mailto:hello@sourcea.com">Book proof demo</a>
      </nav>
      <button type="button" class="ar-nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="ar-nav">
        <span class="ar-nav-toggle-bar"></span>
        <span class="ar-nav-toggle-bar"></span>
        <span class="ar-nav-toggle-bar"></span>
      </button>
      <a class="ar-btn ar-btn-primary ar-btn-sm sa-btn-glow ar-header-cta" href="mailto:hello@sourcea.com">Book proof demo</a>
    </div>
  </div>
</header>"""

HEADER_RE = re.compile(
    r'<div class="ar-scroll-progress".*?</header>',
    re.DOTALL,
)

NAV_LINKS_EXPECTED = [
    "/sourcea/",
    "/sourcea/platform.html",
    "/sourcea/team.html",
    "/sourcea/growth.html",
    "/sourcea/scenario.html",
    "/sourcea/proof.html",
    "/sourcea/compare.html",
    "/sourcea/pricing.html",
]

EXPLORE = """
  <section class="ar-section ar-section-muted ar-reveal sa-explore">
    <div class="ar-container">
      <div class="ar-section-head ar-section-head-center">
        <p class="ar-kicker">Go deeper</p>
        <h2>Every story. <span class="ar-hero-accent">Its own chapter.</span></h2>
      </div>
      <div class="sa-explore-grid">
        <a class="sa-explore-card" href="/sourcea/growth.html"><span class="sa-explore-num">01</span><strong>Growth system</strong><span>Attract → prove → close → expand</span></a>
        <a class="sa-explore-card" href="/sourcea/loops/index.html"><span class="sa-explore-num">02</span><strong>All loops</strong><span>Outreach · ops · research hub</span></a>
        <a class="sa-explore-card" href="/sourcea/loops/outreach.html"><span class="sa-explore-num">03</span><strong>Outreach loop</strong><span>Your first governed send</span></a>
        <a class="sa-explore-card" href="/sourcea/team.html"><span class="sa-explore-num">04</span><strong>Your team</strong><span>6 agents orbiting your command center</span></a>
        <a class="sa-explore-card" href="/sourcea/scenario.html"><span class="sa-explore-num">05</span><strong>Scenario</strong><span>Screen-share script · governed night</span></a>
        <a class="sa-explore-card" href="/sourcea/proof.html"><span class="sa-explore-num">06</span><strong>Proof chain</strong><span>What you screen-share in five minutes</span></a>
        <a class="sa-explore-card" href="/sourcea/pricing.html"><span class="sa-explore-num">07</span><strong>Pricing</strong><span>$3–10K builds · retainer from $2K</span></a>
        <a class="sa-explore-card" href="/sourcea/#reference"><span class="sa-explore-num">08</span><strong>Reference</strong><span>Why buyers name SourceA first</span></a>
        <a class="sa-explore-card" href="/sourcea/platform.html"><span class="sa-explore-num">09</span><strong>Platform</strong><span>Why the audit trail breaks today</span></a>
        <a class="sa-explore-card" href="/sourcea/compare.html"><span class="sa-explore-num">10</span><strong>Compare</strong><span>How alternatives stack up</span></a>
        <a class="sa-explore-card" href="/sourcea/loops/ops-monitor.html"><span class="sa-explore-num">11</span><strong>Ops monitor</strong><span>When policy says no</span></a>
        <a class="sa-explore-card" href="/sourcea/loops/research.html"><span class="sa-explore-num">12</span><strong>Research</strong><span>Bounded gather with a receipt</span></a>
        <a class="sa-explore-card" href="/sourcea/security.html"><span class="sa-explore-num">13</span><strong>Security</strong><span>Procurement &amp; trust strip</span></a>
        <a class="sa-explore-card" href="/sourcea/sources.html"><span class="sa-explore-num">14</span><strong>Sources</strong><span>Cited evidence &amp; frameworks</span></a>
      </div>
    </div>
  </section>
"""

BREADCRUMB_LOOP_FIX = re.compile(
    r'(<a href="/sourcea/platform\.html">Platform</a>)\s*'
    r'(<a href="/sourcea/growth\.html">Growth system</a><span class="ar-breadcrumb-sep">/</span>)',
    re.MULTILINE,
)

BREADCRUMB_LOOP_REPL = r'\1<span class="ar-breadcrumb-sep">/</span>\n        <a href="/sourcea/loops/index.html">Loops</a><span class="ar-breadcrumb-sep">/</span>'

# Pages with alternate nav shells — skip canonical header inject/validate
HEADER_SYNC_SKIP_PREFIXES = ("attach", "reference", "factories")


def skip_header_sync(rel: Path) -> bool:
    if not rel.parts:
        return False
    return rel.parts[0] in HEADER_SYNC_SKIP_PREFIXES


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

    if FOOTER_LOOPS_OLD in text and "All loops" not in text:
        text = text.replace(FOOTER_LOOPS_OLD, FOOTER_LOOPS_NEW)
        changes.append("footer-loops")

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

    if path.name == "index.html" and path.parent == ROOT:
        # Update home explore grid
        old_explore = re.search(
            r'<section class="ar-section ar-section-muted ar-reveal sa-explore">.*?</section>',
            text,
            re.DOTALL,
        )
        if old_explore:
            text = text[: old_explore.start()] + EXPLORE.strip() + "\n\n" + text[old_explore.end() :]
            changes.append("index-explore")
    elif "sa-explore" not in text and "<main" in text:
        # Insert explore before last cta-band or before footer
        if "<footer class=\"ar-site-footer" in text:
            marker = "<footer class=\"ar-site-footer"
            if "sa-cta-band" in text:
                idx = text.rfind("<section class=\"sa-cta-band")
                if idx != -1:
                    text = text[:idx] + EXPLORE.strip() + "\n\n  " + text[idx:]
                    changes.append("explore-before-cta")
            else:
                text = text.replace(marker, EXPLORE.strip() + "\n\n" + marker, 1)
                changes.append("explore-before-footer")

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
